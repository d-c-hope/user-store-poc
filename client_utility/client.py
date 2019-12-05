import aiohttp
import asyncio
import createToken as createTokenTools




# Handle the outer payload
payload1 = {
    'iss': 'https://sky.com',
    'sub': '23',
    'type' : 'profile',
    'jti' : "aaaabbbb",
    'ppt': {
        "prov": "SKY",
        "ter": "GB",
        "prop": "SKYGO"
    },
    'extra': None
}

extra1 = {
    "email":"name@gmail.com",
    "scopes":["profile", "persona", "core", "optouts", "device", "hhcore"],
    "otherIDs" : {
        "household": "456"
    }
}

def createToken1():
    return createTokenTools.createToken(payload1, extra1)

payloadHH1 = {
    'iss': 'https://sky.com',
    'sub': '2367',
    'type' : 'household',
    'jti' : "34a32h43b24296da2",
    'ppt': {
        "prov": "SKY",
        "ter": "GB",
        "prop": "SKYGO"
    },
    'extra': None
}

extraHH1 = {
    "email":"name@gmail.com",
    "scopes":["persona", "core", "optouts", "device", "hhcore"],
    "otherIDs" : {
    }
}
def createTokenHH1():
    return createTokenTools.createToken(payloadHH1, extraHH1)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    token = createToken1()
    hhtoken = createTokenHH1()

    async def doRequest(method, endpoint, data, basicAuth, headers):

        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(basicAuth[0], basicAuth[1])) as session:
            if method == "get":
                r = await session.get(endpoint, headers = headers)
            elif method == "post":
                r = await session.post(endpoint, json=data, headers=headers)
            elif method == "put":
                r = await session.put(endpoint, json=data, headers = headers)
            elif method == "delete":
                r = await  session.delete(endpoint, headers=headers)
            statuscode = r.status
            print(statuscode)
            if statuscode in (200, 201, 202, 203, 204):
                try:
                    json = await r.json()
                    print(json)
                    return json
                except:
                    print("Couldn't decode json")
            else:
                raise Exception()

    async def doGQLRequest(endpoint, data, basicAuth, headers):

        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(basicAuth[0], basicAuth[1])) as session:

            r = await session.post(endpoint, data=data, headers=headers)
            statuscode = r.status
            print(statuscode)
            try:
                if statuscode in (200, 201,202,203,204):
                    json = await r.json()
                    # print(json)
                    return json
            except:
                print("Couldn't decode json")

    def runTest(method, endpoint, data, basicAuth, headers, message = ""):

        try:
            result = loop.run_until_complete(doRequest(method, endpoint, data, basicAuth, headers))
            print("result was {}".format(result))
            return result
        except Exception as e:
            print("{} {}".format(message, e))

    def runTestGQL(endpoint, data, basicAuth, headers, message = ""):

        try:
            result = loop.run_until_complete(doGQLRequest(endpoint, data, basicAuth, headers))
            print("result was {}".format(result))
            return result
        except Exception as e:
            print("{} {}".format(message, e))


    def getPersonaID(result):
        personaIds = list(result.keys())
        personaId = personaIds[0].split(".")[-1]
        print("Perona ID is {}".format(personaId))
        return personaId

    endpoint = "http://localhost:8000"
    headers = {'x-token': token, 'Provider': 'SKY', 'Territory': 'GB',
               }
    headersHH = {'x-token': hhtoken, 'Provider': 'SKY', 'Territory': 'GB',
               }
    headersNoToken = {'Provider': 'SKY', 'Territory': 'GB',
                 }

    ex1 = lambda: runTest("post", "{}/profile".format(endpoint), {"email": "david"},
                          ("sas", "password"), headers, "Create profile failed")

    ex1bNoTok = lambda: runTest("put", "{}/profile/23/device/3456".format(endpoint), {'deviceName': "device x"},
                          ("sas_privileged", "password"), headersNoToken, "Put with no token, priv user failed")
    ex2 = lambda: runTest("get", "{}/profile".format(endpoint), None,
                          ("sas", "password"), headers, "Get profile failed")
    ex3 = lambda: runTest("get", "{}/profile/24/optouts".format(endpoint), {"email": "david"},
                          ("sas", "password"), headers, "Attempt to use wrong profile ID failed as expected")
    ex4 = lambda: runTest("post", "{}/profile/23/optouts".format(endpoint), {"marketing": True, "pushNotifications": True},
                          ("sas", "password"), headers, "Create opt-outs failed")
    ex5 = lambda: runTest("post", "{}/profile/23/optouts".format(endpoint),
                          {"marketing": True, "pushNotifications": True},
                          ("sas", "password"), headers, "Create opt-outs failed as expected")
    ex6 = lambda: runTest("post", "{}/profile/23/persona".format(endpoint), {"displayName":"david"},
                          ("sas", "password"), headers, "Create persona failed")
    ex6b = lambda: runTest("get", "{}/profile/23/persona".format(endpoint), None,
                          ("sas", "password"), headers, "Get persona failed")
    ex7 = lambda pID: runTest("put", "{}/profile/23/persona/{}".format(endpoint, pID), {"displayName":"mark"},
                          ("sas", "password"), headers, "Update core persona failed")
    ex8 = lambda: runTest("get", "{}/profile/23/persona".format(endpoint), None,
                          ("sas", "password"), headers, "Get persona failed")
    ex9a = lambda: runTest("put", "{}/profile/23/device/56".format(endpoint),
                           {'deviceName': "device one"},
                          ("sas", "password"), headers, "Add device failed")
    ex9b = lambda: runTest("put", "{}/profile/23/device/86".format(endpoint),
                           {'deviceName': "device one"},
                           ("sas", "password"), headers, "Add device failed")
    ex9c = lambda: runTest("put", "{}/profile/23/device/86/settings".format(endpoint),
                           {'volume': 23},
                          ("sas", "password"), headers, "Update device failed")
    ex9d = lambda: runTest("post", "{}/profile/23/device/86/settings/video".format(endpoint),
                           {'ratio': "16/9"},
                          ("sas", "password"), headers, "Add device settings failed")
    ex9e = lambda: runTest("put", "{}/profile/23/device/86/settings/video".format(endpoint),
                           {'ratio': "4/3"},
                           ("sas", "password"), headers, "Update device failed")
    ex10 = lambda: runTest("get", "{}/profile/23/device".format(endpoint), None,
                           ("sas", "password"), headers, "Get devices failed")
    ex11 = lambda: runTest("delete", "{}/profile/23/device/56".format(endpoint), None,
                           ("sas", "password"), headers, "Delete device failed")
    ex12 = lambda: runTest("delete", "{}/profile/23/device/86/settings".format(endpoint), None,
                           ("sas", "password"), headers, "Delete device settings failed")
    ex13 = lambda: runTest("delete", "{}/profile/23/device/86/settings".format(endpoint), None,
                           ("nowTVCRM", "password"), headers, "Failed as expected due to no agent header")

    ex14HH = lambda: runTest("post", "{}/household".format(endpoint), {"email": "david"},
                          ("sas", "password"), headers, "Create profile failed")
    ex14HHTok = lambda: runTest("post", "{}/household".format(endpoint), {"email": "david"},
                             ("sas", "password"), headersHH, "Create profile failed")
    ex15Rev = lambda: runTest("put", "{}/revokelist".format(endpoint), {'revokedTokens': ['aaaabbbb']},
                             ("id_priv", "password"), headers, "Revoke tokens failed")
    ex15Revb = lambda: runTest("put", "{}/revokelist".format(endpoint), {'revokedTokens': []},
                              ("id_priv", "password"), headers, "Revoke tokens failed")
    ex1()
    ex1bNoTok()
    ex2()
    ex3()
    ex4()
    ex5()
    ex6()
    res = ex6b()
    pID = getPersonaID(res)
    ex7(pID)
    ex8()
    ex9a()
    ex9b()
    ex9c()
    ex9d()
    ex9e()
    ex10()
    ex11()
    ex12()
    ex13()
    ex14HH()
    ex14HHTok()
    # ex15Rev()
    # ex15Revb()

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

    exgql1 = lambda: runTestGQL("{}/graphql".format(endpoint), queryString,
                           ("sas", "password"), headers, "Graph QL fetch failed")
    # exgql1()
