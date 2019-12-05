import sys
import pickle
sys.path.append(sys.path[0] + "/..")

import createToken as createTokenTools


# Handle the outer payload
payload = {
    'iss': 'https://sky.com',
    'sub': '23',
    'type' : 'profile',
    'jti': "aaaabbbb",
    'extra': None
}

extra = {
    "email":"name@gmail.com",
    "scopes":["profile", "persona", "core", "optouts", "device", "household, "],
    "otherIDs" : {
        "household": 456
    }
}

def createToken(i):
    payload['sub'] = "{}".format(i)
    return createTokenTools.createToken(payload, extra)


tokens = [(createToken(i)) for i in range(2000)]
with open("tokens", 'wb') as f:
    pickle.dump(tokens, f)
