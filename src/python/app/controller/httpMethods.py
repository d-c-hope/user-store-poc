import asyncio
import base64
import sys
import functools

from accessRights import authenticator
from persistance import datastore, couchbaseWrapper
from controller import router, pathMatcher
from controller.gql import gqlHandler
from utils import paths
from controller.ptpHandling import mapPTP, checkTenancy
from persistance.datastore import IndexDocsException, AlreadyExistsException
from events import jsonProducer
import logging
logger = logging.getLogger("applogger")


class ForbiddenException(Exception):
    pass

class SchemaException(Exception):
    pass

class InvalidRequestException(Exception):
    pass

class NotFoundException(Exception):
    pass


class HTTPHandlerUtils:
    @staticmethod
    def headersValidationDecorator(func):
        @functools.wraps(func)
        async def wrapper(*args,**kwargs):
            headers = args[-1]
            basicAuth = args[-2]
            try:
                checkTenancy(headers)
                authenticator.checkForAgentHeader(basicAuth, headers)
            except:
                raise InvalidRequestException()

            r = await func(*args, **kwargs)
            return r
        return wrapper

    @staticmethod
    def getResourceStrings(pathList):
        """Returns ('profile.<id>.optouts', 'profile.34.optouts')"""

        dotPathForm = ".".join([node.pathString for node in pathList])
        dotValueForm = ".".join([node.pathVal for node in pathList])
        return (dotPathForm, dotValueForm)

    @staticmethod
    async def authAndGetID(method, normNodeList, token, basicAuth, ptp):
        try:

            rootID = "me"
            if len(normNodeList) > 1:
                rootID = normNodeList[1].pathVal
            resourcePath, resourceVal = HTTPHandlerUtils.getResourceStrings(normNodeList.copy())  # tuple, second one has value
            rootID = await authenticator.authenticateAndAuthorise(token, basicAuth, [resourcePath], method, rootID, ptp)
            # normalisedList[1].pathVal = rootID
            # update resource now we have an id out of the token
            return rootID
        except Exception as e:
            raise ForbiddenException("Authentication failed")

    @staticmethod
    def handleSchema(node, jsonDoc):
        try:
            node.schema(jsonDoc)
        except:
            logger.debug("Schema failed to validate")
            raise SchemaException("Schema didn't validate")


@HTTPHandlerUtils.headersValidationDecorator
async def dataGet(urlpath, token, basicAuth, headers):

        try:
            ptp = mapPTP(headers)
            matchNodeList, normalisedList, outerPathList = router.processPath(urlpath)
        except Exception as e:
            raise InvalidRequestException()

        rootID = await HTTPHandlerUtils.authAndGetID("GET", normalisedList, token, basicAuth, ptp)
        normalisedList[1].pathVal = rootID

        # is the path to a root node like /persona with lots of personas underneath
        try:
            isMultiGet = router.isMultiDoc(matchNodeList, normalisedList)
            if isMultiGet:
                default = matchNodeList[-1].defaultType
                r = await datastore.getAll(matchNodeList, normalisedList, ptp)
            else:
                r = await datastore.get(normalisedList, ptp)
            return {"status": 200, "body": r}
        except:
            raise NotFoundException()


@HTTPHandlerUtils.headersValidationDecorator
async def dataPost(urlpath, jsonDoc, token, basicAuth, headers):
    """
    For Creating a new document e.g. a profile or profile opt-outs
    Posts create a uuid when POSTing to an ID root. PUTs do not.
    Cant post with missing vals in path, i.e. parent resource must exist, can't add a pesona
        to a profile when no profile doc
    """

    try:
        ptp = mapPTP(headers)
        matchNodeList, normalisedList, outerPathList = router.processPath(urlpath)
    except Exception as e:
        raise InvalidRequestException()

    rootID = await HTTPHandlerUtils.authAndGetID("CREATE", normalisedList, token, basicAuth, ptp)
    normalisedList[1].pathVal = rootID

    HTTPHandlerUtils.handleSchema(matchNodeList[-1], jsonDoc) # raises SchemaException

    try:
        await router.postAllowed(matchNodeList, normalisedList, outerPathList, ptp)
    except Exception as e:
        logger.debug("Post not allowed for path")
        raise ForbiddenException()

    router.RouterUtils.addID(normalisedList)

    try:
        # and finally actually persist it
        await datastore.create(normalisedList, jsonDoc, ptp)
        key = HTTPHandlerUtils.getResourceStrings(normalisedList)[1]

    except AlreadyExistsException as e:
        raise e
    except IndexDocsException as e:
        raise e
    except Exception as e:
        raise e

    try:
        jsonProducer.createAuditEventForCreate(key, jsonDoc, ptp)
    except Exception as e:
        raise Exception()

    return {"status": 200, "body": {key: jsonDoc}}



@HTTPHandlerUtils.headersValidationDecorator
async def dataPut(urlpath, jsonDoc, token, basicAuth, headers):
    """Controller for a data update (or a PUT to a known path)"""

    try:
        ptp = mapPTP(headers)
        matchNodeList, normalisedList, outerPathList = router.processPath(urlpath)
    except Exception as e:
        raise InvalidRequestException()

    rootID = await HTTPHandlerUtils.authAndGetID("UPDATE", normalisedList, token, basicAuth, ptp)
    normalisedList[1].pathVal = rootID

    HTTPHandlerUtils.handleSchema(normalisedList[-1], jsonDoc)

    try:
        await router.putAllowed(matchNodeList, normalisedList, outerPathList, ptp)
    except:
        raise ForbiddenException("Put not allowed for path")

    try:
        # and finally actually persist it
        (oldDoc, newDoc) = await datastore.update(normalisedList, jsonDoc, ptp)
        key = HTTPHandlerUtils.getResourceStrings(normalisedList)[1]
    except IndexDocsException as e:
        raise e
    except Exception as e:
        raise e

    try:
        jsonProducer.createAuditEventForUpdate(key, jsonDoc, oldDoc, ptp)
    except Exception as e:
        raise Exception()

    return {"status": 200, "body": {key: jsonDoc}}


@HTTPHandlerUtils.headersValidationDecorator
async def dataDelete(urlpath, token, basicAuth, headers):

    try:
        ptp = mapPTP(headers)
        matchNodeList, normalisedList, outerPathList = router.processPath(urlpath)
    except Exception as e:
        raise InvalidRequestException()

    rootID = await HTTPHandlerUtils.authAndGetID("DELETE", normalisedList, token, basicAuth, ptp)
    normalisedList[1].pathVal = rootID

    try:
        await router.deleteAllowed(matchNodeList, normalisedList, outerPathList, ptp)
    except:
        raise ForbiddenException("Delete not allowed for path")

    try:
        r = await datastore.deleteSingle(matchNodeList, ptp)
    except Exception as e:
        raise e

    try:
        key = HTTPHandlerUtils.getResourceStrings(normalisedList)[1]
        jsonProducer.createAuditEventForDelete(key, ptp)
    except Exception as e:
        raise Exception()

    return {"status": 200, "body": {}}


# @HTTPHandlerUtils.headersValidationDecorator
async def graphql(queryStr, token, basicAuth, headers, loop):
    """

    """
    ptp = mapPTP(headers)
    r = await gqlHandler.executeQuery(queryStr, token, basicAuth, ptp, loop)

    return {"status": 200, "body": r}


async def revokelist(jsonDoc, basicAuth, headers):
    try:
        ptp = mapPTP(headers)
    except Exception as e:
        raise InvalidRequestException()

    authenticator.authenticateRevokeList(basicAuth)

    try:
        r = await couchbaseWrapper.upsert("revokelist", jsonDoc, ptp)
    except:
        raise Exception("Failure writing revoke list")

    return {"status": 200, "body": {}}



async def initialise(path=None):
    authenticator.loadUsersAndRights()
    router.initialise()
    pathMatcher.initialise()
    jsonProducer.initialise()
    await datastore.initialise()

if __name__ == "__main__":
    paths.configPath = sys.path[0] + '/../config'
    # initialise()
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImliUzAyYzJPdkZMQWMwSVdoQnB5MjdrOWZ6YlhJejRmaEpOd3lkLWNVa2MifQ.eyJleHRyYSI6ImV5SmhiR2NpT2lKQk1qVTJTMWNpTENKbGJtTWlPaUpCTWpVMlEwSkRMVWhUTlRFeUluMC5BanJIaDBTVENnOTZOeHVEVFdzbVVJbEtucF9nY3JsVS1BcGNyd1VTWGQtY2pIcFZPV1dTazVIQWpMa2c2czdaUkpNRDBUNG5KZzNta0Q3TUJXVkp1YVZKODFudjVkT3gueE5GcHBGMG9QaW50QklpQXlfcnNhQS5uUU9rRUdNWGhmY0pyeFBqc2s4MEZ2b3ZUWVhGVDFtSWwzZENxWE5WZDI0TnRIQUZ0WEx5YkgydUJIRVNhdnhwN3dablZQZ3lidVNXaUlmcXhaYTFvUHVQSUI4blpoNThNd2xrUjRjSTkxcUZqVzV0Z1ZMNUZudmVyN3lMRkxvRGlGN3NuRUZneWJnaVN5TkJtLXB5VWJpUmozTzdyQW0xVGZ3VVZGa3RZNXFSVEJZQmxSemZsMGxBUjZCWnJEbTM4U21mdjBITnd1QWhHMU0tbkpaT1ZBLl9xT1BmNVFBTzQyenJJZ014aXpuem9IV1hvRWpwZWVoRFJqaXVkNUhWek0iLCJqdGkiOiJhYWFhYmJiYiIsIm90aGVySURzIjp7ImhvdXNlaG9sZCI6IjQ1NiJ9LCJwcHQiOnsicHJvcCI6IlNLWUdPIiwicHJvdiI6IlNLWSIsInRlciI6IkdCIn0sInN1YiI6IjIzIiwidHlwZSI6InByb2ZpbGUifQ.tTgDzWu_IJrynMomxQB9QMrUGBwZuloo0kIrxoWcIXTP9-QuAKZnuJJHt_h964V3M0-H1q_9qnIEMluiKmVeJQ"
    hhtoken = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImliUzAyYzJPdkZMQWMwSVdoQnB5MjdrOWZ6YlhJejRmaEpOd3lkLWNVa2MifQ.eyJleHRyYSI6ImV5SmhiR2NpT2lKQk1qVTJTMWNpTENKbGJtTWlPaUpCTWpVMlEwSkRMVWhUTlRFeUluMC53cHNBc0JsanptTTlySkJLRVZNUFF6RXNkcnR2czU1Ym1ZRGJRVXd6aVZQV2FFc0hFN1hJZ2tIZFgwREZQdmdLVFEtMHFsT0NXNUNSeFVDc1ZPX013MXdTWU13S0ZZc1AuOWRTVDI3blpqeXZhT293U1Fock9NUS52MnhTcUVZMVlKM21ZNDZiN1BhUWZOb2VsOVQyMXdpTFU1ZWE2b1dSSjdxVUxzUVhiMWdza1o3TkVJTUVWVjh3ZXZWRjBLSXljUlhPY0RTQmtDRDFzUFhHbksyQkktYklCWVl0RFZZVGhnbjRWWmtmSHJIN2pmTVZOaGh3V2pld3ZWRjRvTjBCRlowWGF0UWYzZ0lfVkVRbzF6NmFUaDhmNW51VkFNZ1FlMmhjazltRjBuT01IUkprZnV6Ri1iSXcuZGp5RGpVMW9QYS1scDg2N1JhUDF3UzBlVWJaNEhPY2phenRhUUVYVVVIayIsImp0aSI6IjEyM2FiYyIsInBwdCI6eyJwcm9wIjoiU0tZR08iLCJwcm92IjoiU0tZIiwidGVyIjoiR0IifSwic3ViIjoiMjM2NyIsInR5cGUiOiJob3VzZWhvbGQifQ.kWPxn2spdczwVcTxz6rdYKnwLOLCQ9Hmj566ff6REHhLam79ejqh7fF4JeD-erPoHjcEuZtdESVhX-DgN4dL9Q"

    def genBasicAuth(user, password):
        baBytes = (base64.b64encode("{}:{}".format(user, password).encode())).decode()
        basicAuth = "Basic {}".format(baBytes)
        return basicAuth


    ba = genBasicAuth("sas", "password")
    baPriv = genBasicAuth("sas_privileged", "password")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialise())

    def runTest(func, errorMessage):
        try:
            result = loop.run_until_complete(func())
            print("result was {}".format(result))
            return result
        except Exception as e:
            print("{} {}".format(errorMessage, e))

    def getPersonaIDs(result):
        personaIds = list(result.keys())
        personaId = personaIds[0].split(".")[-1]
        print("Perona ID is {}".format(personaId))
        return personaId

    headers = {"Provider" : "SKY", "Territory":"GB", "Proposition": "SKYGO"}
    # Example 1
    ex1 = lambda: runTest(lambda: dataPost("profile", {"email": "david"}, token, ba, headers), "Create core profile failed")
    ex1b = lambda: runTest(lambda: dataPost("household", {"email": "david"}, token, ba, headers),
                          "Create core household failed")
    ex1c = lambda: runTest(lambda: dataPost("household", {"email": "david"}, hhtoken, ba, headers),
                           "Create core household failed")
    ex1d = lambda: runTest(lambda: dataPost("profile", {"email": "david"}, hhtoken, ba, headers),
                           "Create core household failed")
    ex1eNoTok = lambda: runTest(lambda: dataPut("profile/23/device/3456", {'deviceName': "device x"}, None, baPriv, headers),
                           "Put with no token, priv user failed")
    ex2 = lambda: runTest(lambda: dataGet("profile/me", token, ba, headers), "Get core profile failed")
    ex3 = lambda: runTest(lambda: dataPost("profile/24/optouts", {"rand":4}, token, ba, headers), "Attempt to use wrong profile ID failed as expected")
    ex4 = lambda: runTest(lambda: dataPost("profile/23/optouts", {"marketing": True, "pushNotifications": True},
                                                    token, ba, headers), "Create opt-outs failed")
    ex5 = lambda: runTest(lambda: dataPost("profile/23/optouts", {"marketing":True, "pushNotifications": True},
                                                     token, ba, headers), "Create opt-outs failed")
    ex6 = lambda: runTest(lambda: dataPost("profile/23/persona", {"displayName":"david"}, token, ba, headers), "Create persona failed")
    ex6b = lambda: runTest(lambda: dataGet("profile/23/persona", token, ba, headers), "Create persona failed")
    ex7 = lambda pID: runTest(lambda: dataPut("profile/23/persona/{}".format(pID), {"displayName":"mark"}, token, ba, headers),
                    "Update core persona failed")
    ex8 = lambda pID: runTest(lambda: dataPut("profile/23/persona/{}/skykids".format(pID),
                                                     {'age': "2016-04-22", "avatar": "spongebob"},
                                                     token, ba, headers), "Update persona sky kids failed")
    ex9a = lambda: runTest(lambda: dataPut("profile/23/device/56", {'deviceName': "device one"},
                                                     token, ba, headers), "Add device failed")
    ex9b = lambda: runTest(lambda: dataPut("profile/23/device/86", {'deviceName': "device two"},
                                                     token, ba, headers), "Add device failed")
    ex9c = lambda: runTest(lambda: dataPut("profile/23/device/86/settings", {'volume': 23},
                                           token, ba, headers), "Update device failed")
    ex9d = lambda: runTest(lambda: dataPost("profile/23/device/86/settings/video", {'ratio': "16/9"},
                                           token, ba, headers), "Update device failed")
    ex9e = lambda: runTest(lambda: dataPut("profile/23/device/86/settings/video", {'ratio': "4/3"},
                                            token, ba, headers), "Update device failed")
    ex10 = lambda:runTest(lambda: dataGet("profile/23/device", token, ba, headers), "Get devices failed")
    ex11 = lambda: runTest(lambda: dataDelete("profile/23/device/56", token, ba, headers), "Delete device failed")
    ex12 = lambda: runTest(lambda: dataDelete("profile/23/device/86/settings", token, ba, headers), "Delete device failed")
    ex13 = lambda: runTest(lambda: dataDelete("profile/23/device/86/settings", token,
                                              genBasicAuth("nowTVCRM", "password"), headers), "Failed as expected due to no agent header")


    # ex1()
    # ex1b()
    # ex1c()
    # ex1d()
    # ex1eNoTok()
    # ex2()
    # ex3()
    # ex4()
    # ex5()
    # ex6()
    # res = ex6b()
    # pID = getPersonaIDs(res["body"])
    # # ex7(pID)
    # ex8(pID)
    ex9a()
    # ex9b()
    # ex9c()
    # ex9d()
    # ex9e()
    # ex10()
    ex11()
    # ex12()
    # ex13()


    queryString = '''
                query profiles {
                    profile(ids: ["23"]) {
                        coreprofile {
                            email
                        }
                        optouts {
                            marketing
                        }
                        personas {
                            core {
                                displayName
                            }
                        }
                    }
                }
            '''
    f = lambda: graphql(queryString, token, ba, headers, loop)

    # runTest(f, "gql failed")

    baRev = genBasicAuth("id_priv", "password")
    ex20Rev = lambda: runTest(lambda: revokelist({'revokedTokens': ['aaaabbbb']}, baRev, headers), "Update revoke failed")
    ex20Revb = lambda: runTest(lambda: revokelist({'revokedTokens': []}, baRev, headers), "Update revoke failed")
    # ex20Rev()
    # ex20Revb()



    # def run
    # try:
    #     result = loop.run_until_complete(f())
    #     print("result was {}".format(result))
    # except Exception as e:
    #     print("{} {}".format(errorMessage, e))

    # r = graphql(queryString, token, ba, headers)
    # print(r)

# result = loop.run_until_complete(dataGet("profile/23/persona", token, ba))
