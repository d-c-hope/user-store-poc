import casbin
from casbin import util
from utils import paths
import accessRights.tokenHandler as tokenHandler
import json
import sys
import base64
import time
import logging
from persistance import tenancySelector, couchbaseWrapper
from controller import ptpHandling
logger = logging.getLogger("applogger")

class AuthenticationException(Exception):
    pass

class ScopesMissingException(AuthenticationException):
    pass

class BAFailureException(AuthenticationException):
    pass

class TokenInvalidException(AuthenticationException):
    pass

class AgentMissingException(AuthenticationException):
    pass

class TenancyMismatchException(AuthenticationException):
    pass



revokeList = {
    'time': 0,
    'data': {'revokedTokens': {}}
}

async def authenticateAndAuthorise(token, basicAuth, resources, method, rootID, ptp):

    for resource in resources:
        # checkedIdVal = resource[0].split(".")[0]
        try:
            if basicAuth == None:
                user, password = ("public" , "none")
            else:
                user, password = decodeBasicAuth(basicAuth)

            # Check the basic auth password
            userType = isAuthenticated(user, password)
            if userType == "privileged" and token == None:
                authenticateAndAuthorisePrivileged(user, resource, method)
                checkedIdVal = rootID
            else:
                checkedIdVal = await authenticateAndAuthoriseWithToken(token, user, resource, method, rootID, ptp)
        except Exception as e:
            logger.debug("Authentication failed with exception: {}".format(type(e)))
            raise Exception()
        return checkedIdVal


async def authenticateGQL(token, basicAuth, ptp):

    try:
        if basicAuth == None:
            user, password = ("public" , "none")
        else:
            user, password = decodeBasicAuth(basicAuth)

        tokenClaims = None
        try:
            if not token==None:
                tokenClaims = await validateToken(token, ptp)
        except:
            raise Exception()

    except Exception as e:
        # print("Authentication failed with exception: {}".format(type(e)))
        raise Exception()
    return user, tokenClaims


def authenticateRevokeList(basicAuth):

    try:
        if basicAuth == None:
            user, password = ("public" , "none")
        else:
            user, password = decodeBasicAuth(basicAuth)

        userType = isAuthenticated(user, password)
        # isBAUserAuthorised(user, "tokenlist", "UPDATE")
        if not isBAUserAuthorised(user, "revlist", "UPDATE"):
            raise BAFailureException()

    except Exception as e:
        print("Authentication failed with exception: {}".format(type(e)))
        raise Exception()
    return True


async def authenticateAndAuthoriseWithToken(token, user, resource, method, rootID, ptp):

    try:
        tokenClaims = await validateToken(token, ptp)
    except:
        raise Exception()

    # Then check the backend basic auth user has access to the APIs
    if not isBAUserAuthorised(user, resource, method):
        raise BAFailureException()

    resourceType = resource.split(".")[0]

    # Then check the access token gives access to the top level resource ID
    # (e.g. profile or hh ID, second thing in the path)
    # resourceID = resource[1].split(".")[1]
    checkedIdVal = doesTokenIdMatch(rootID, resourceType, tokenClaims)
    if checkedIdVal == False:
        raise Exception


    # Finally check the access token gives access to the API
    if not isTokenAuthorised(tokenClaims["extra"]["scopes"], resource, method):
        raise ScopesMissingException()

    return checkedIdVal



def authenticateAndAuthorisePrivileged(user, resource, method):

    # Then check the backend basic auth user has access to the APIs
    if not isBAUserAuthorised(user, resource, method):
        raise Exception()
    else:
        return True

def decodeBasicAuth(basicAuthHeader):
    try:
        userpass = base64.b64decode(basicAuthHeader.split()[1]).decode("utf8").split(":")
        user = userpass[0]
        password = userpass[1]
        return user, password
    except:
        raise Exception()


def loadUsersAndRights(path=None):
    global e, users, eScopes
    e = casbin.Enforcer(paths.configPath + "/casbin_model.conf", paths.configPath + "/casbin_policy.csv")
    e.add_function("KeyMatch2", util.key_match2)
    eScopes = casbin.Enforcer(paths.configPath + "/casbin_model.conf", paths.configPath + "/casbin_token_policy.csv")
    eScopes.add_function("KeyMatch2", util.key_match2)

    if path == None:
        path = paths.configPath + "/users.json"
    with open(path) as f:
        contents = f.read()
        users = json.loads(contents)["users"]

    tokenHandler.loadKeys()
users = None
e = None


async def validateToken(token, ptp):
    tokenClaims = tokenHandler.validateAndGetToken(token)

    tenancyMatch = doesTokenPTPMatchPTP(tokenClaims, ptp)
    if tenancyMatch == False:
        raise TenancyMismatchException()

    tokenRevoked = await isTokenRevoked(tokenClaims, ptp)
    if tokenRevoked == True:
        raise RevokedException()


    return tokenClaims


#TODO need to get tenancy for revoke list and have cache by tenancy
async def isTokenRevoked(tokenClaims, ptp):
    try:
        timenow = time.time()
        global revokeList
        if timenow - revokeList['time'] > 3:
            rtokens = await couchbaseWrapper.getData("revokelist", ptp)
            revokeList = {
                'time': timenow,
                'data' : rtokens
            }
        rtokens = revokeList['data']['revokedTokens']
        if tokenClaims['jti'] in rtokens:
            return True
        else:
            return False
    except:
        return False



def doesTokenIdMatch(idVal, resType, claims):
    subject = claims["sub"]
    if claims["type"] != resType:
        extra = claims["extra"]
        otherIDs = extra["otherIDs"]
        if resType in otherIDs:
            subject = claims["extra"]["otherIDs"][resType]
        else:
            return False

    if idVal == "me" or idVal == "<id>":
        return subject
    elif idVal != claims["sub"]:
        return False
    else:
        return claims["sub"]

def doesTokenPTPMatchPTP(tokenClaims, ptp):
    try:
        tokenPTP = ptpHandling.mapPTP(tokenClaims['ppt'], ("prov", "ter", "prop"))
        ptpTenancy = tenancySelector.getTenancy(ptp)
        tokenPtpTenancy = tenancySelector.getTenancy(tokenPTP)
        print(ptpTenancy)
        if ptpTenancy != tokenPtpTenancy:
            return False
        else:
            return True
    except:
        return False

def isAuthenticated(user, providedPassword):
    global users
    password = users[user]["password"]
    if providedPassword != password:
        raise Exception()
    if "isPrivileged" in users[user] and users[user]["isPrivileged"] == True:
        return "privileged"
    else:
        return "normal"

def isBAUserAuthorised(role, resource, action):

    global e
    if e.enforce(role, resource, action):

        return True
    else:
        return False

# def isTokenIdTypeAuthorised(tokenClaims, idType):
#     if idType in tokenClaims["extra"]["scopes"]:
#         return True
#     else:
#         raise Exception()

def isTokenAuthorised(scopes, resource, action):
    global eScopes
    anyMatch = False
    for scope in scopes:
        if eScopes.enforce(scope, resource, action):
            logger.debug("Token Access OK")
            anyMatch = True
    return anyMatch

def checkForAgentHeader(basicAuth, headers):
    global users
    user, password = decodeBasicAuth(basicAuth)
    agentNeeded = user in users[user] and "agentRequired" in users[user]
    if agentNeeded and "agent" not in headers:
        raise AgentMissingException()


if __name__ == "__main__":
    """This acts as basic tests, needs moving into proper unit tests"""
    paths.configPath = sys.path[0] + '/../config'
    loadUsersAndRights()

    # p, persona_all, / persona /: id / *, (GET) | (POST) | (PUT) | (DELETE)
    # p, persona_read, / persona /: id / *, (GET)
    # p, core_read, / coreprofile, GET
    # p, core_all, / coreprofile, (GET) | (POST) | (PUT) | (DELETE)
    # p, optouts_read, / optouts, GET
    # p, optouts_all, / optouts, (GET) | (POST) | (PUT) | (DELETE)
    sub = "umv"  # the user that wants to access a resource.
    obj = "/persona/23/persona1"  # the resource that is going to be accessed.
    act = "GET"  # the operation that the user performs on the resource.
    # e.rm.(*defaultrolemanager.RoleManager).AddMatchingFunc("KeyMatch2", util.KeyMatch2)
    # casbin.util.
    # e.add_function("KeyMatch2", util.key_match2)

    # roles = e.get_roles("alice")
    if e.enforce(sub, obj, act):
        # permit alice to read data1
        print("access rights success")
    else:
        # deny the request, show an error
        print("access rights failure")

    sub = "umv"  # the user that wants to access a resource.
    obj = "/coreprofile"  # the resource that is going to be accessed.
    act = "GET"  # the operation that the user performs on the resource.

    # roles = e.get_roles("alice")
    if e.enforce(sub, obj, act):
        # permit alice to read data1
        print("access rights success")
    else:
        # deny the request, show an error
        print("access rights failure")

    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImliUzAyYzJPdkZMQWMwSVdoQnB5MjdrOWZ6YlhJejRmaEpOd3lkLWNVa2MifQ.eyJleHRyYSI6ImV5SmhiR2NpT2lKQk1qVTJTMWNpTENKbGJtTWlPaUpCTWpVMlEwSkRMVWhUTlRFeUluMC4tSDJfVDZCMDB1dm9TVnhLUzlKZHlvbTJaRVVKdUpsZHQtMHRkYUQtei10UGhveTlXVVBpdnAwR3ZaRmtZTHpBcGhsUFFhZWNMOG1DZlJielpfblVpYTNwV3Zxcl94aXouYmFFYmJ1bmxld1FuSmwzcGNfQXVDQS5ZcVV5SUh5NGxzR1o0UEVUdTR2dTc2eklNdVBHZXZpMUw0TWdYSDdzQVItUFRmNmxhT1BoWHZVQWExbkNnSXl5dUQyTEk5SGdkOG5iM1dybnQwR0tIenFsbUJRV0dYaG40S1gtQ2FyZ3pUNmhTQmpBTFNHWEtVbmttODZUa0VxaS55aE04dzVGc3hnaXloYng1NTNXZHd1Tnc3a3NWNzhHWTJzWkhqTVBnNXNVIiwic3ViIjoiMjMifQ.lJVGoqJwoxpsBWKulq38AN7RllHDLXXxI8txeysqRCotaVsvKKdVcppgtV3FjV94AZMUp0PtAMaZDoeFfj0bTg"
    def genBasicAuth(user, password):
        baBytes= (base64.b64encode("{}:{}".format(user, password).encode())).decode()
        basicAuth = "Basic {}".format(baBytes)
        return basicAuth
    ba = genBasicAuth("sas", "password")
    # idType, idVal, token, basicAuth, endpoint, method
    ret = authenticateAndAuthorise("profile", "23", token, ba, "optouts", "POST")
    print(ret)
