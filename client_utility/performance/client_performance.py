import aiohttp
import asyncio
import time
import sys
import pickle
sys.path.append(sys.path[0] + "/..")

import createToken as createTokenTools

# Handle the outer payload
payload1 = {
    'iss': 'https://sky.com',
    'sub': '23',
    'type' : 'profile',
    'extra': None
}

extra1 = {
    "email":"name@gmail.com",
    "scopes":["profile", "persona", "core", "optouts", "device", "household, "],
    "otherIDs" : {
        "household": 456
    }
}

def createToken1():
    return createTokenTools.createToken(payload1, extra1)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    token = createToken1()


    async def doRequest(method, endpoint, data, basicAuth, token, headers):
        headersLocal = headers.copy()
        headersLocal['x-token'] = token
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(basicAuth[0], basicAuth[1])) as session:
            if method == "get":
                r = await session.get(endpoint, headers = headersLocal)
            elif method == "post":
                r = await session.post(endpoint, json=data, headers=headersLocal)
            elif method == "put":
                r = await session.put(endpoint, json=data, headers = headersLocal)
            elif method == "delete":
                r = await  session.delete(endpoint, headers=headersLocal)
            statuscode = r.status

            try:
                if statuscode in (200, 201,202,203,204):
                    json = await r.json()
                    return json
            except:
                print("Couldn't decode json")


    endpoint = "http://localhost:8000"
    headers = {'x-token': None, 'Provider': 'SKY', 'Territory': 'GB',
               }

    tokens = []
    with open("tokens", 'rb') as f:
        tokens = pickle.load(f)


    tS = time.time()
    async def runAllGET():
        for i in range(10):
            tests = [doRequest("get", "{}/profile".format(endpoint), None,
                              ("sas", "password"), tokens[j], headers) for j in range(200)]
            await asyncio.gather(
                *tests
            )

    async def runAllPOST(n, m):
        for i in range(n):
            tests = [doRequest("post", "{}/profile".format(endpoint), {"email": "david"},
                              ("sas", "password"), tokens[j], headers) for j in range(m)]
            await asyncio.gather(
                *tests
            )

    asyncio.run(runAllPOST(10, 200))
    tE = time.time()
    print(tE - tS)

