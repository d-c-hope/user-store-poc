import aiohttp
import asyncio
from jwcrypto import jwk, jwe, jws, jwt
from jwcrypto.common import json_encode, json_decode
import json



def loadCertKeys():
    with open("token_key/cert_key.pem", "rb") as keyfile:
        contents = keyfile.read()
        print(contents)
        privateKey = jwk.JWK.from_pem(contents)
    with open("token_key/sign_certificate.pem", "rb") as certfile:
        contents = certfile.read()
        print(contents)
        publicKey = jwk.JWK.from_pem(contents)

    return privateKey, publicKey


def makeJWT(payload, privateKey, publicKey):
    print(type(payload))
    token = jwt.JWT(header={"alg": "RS256", "kid": publicKey.thumbprint()},
                    claims=payload)
    # token = jwt.JWT(header={"alg": "RS256"},
    #                 claims=payload)

    # privateKey = jwk.JWK(generate='oct', size=256)
    # privateKey = jwk.JWK.generate(kty='RSA', size=256)
    print(privateKey)
    token.make_signed_token(privateKey)
    signed = token.serialize()

    return signed


def loadEncryptKey():
    with open("token_key/sym_encrypt_key", "r") as keyfile:
        key = jwk.JWK.from_json(keyfile.read())
        return key


def symEncrypt(payload, encryptKey):
    # sym_key = jwk.JWK.generate(kty='oct', size=256)
    sym = {"alg": "A256KW", "enc": "A256CBC-HS512"}

    stringPayload = json.dumps(payload)
    E = jwe.JWE(stringPayload.encode('utf-8'), json_encode(sym))
    E.add_recipient(encryptKey)
    encrypted_token = E.serialize(compact=True)
    return encrypted_token

# b'-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDR3QL6gAZS8EVF\nRnteqxemF/1SMR0qRJF3DkgSRpmA7oBkmenC48UEzfhsA8iGPIGajG55gD97G0kV\nVGu4vecTPssnDjlDmvojFuqWSiYoYzcjWjwGHVv6Gz29lLW9jhJAcXIwa2TtP9ns\nwHctgSSzgK+uthmITj+0Rds5YosAEqogB+X1XfhmTJmg4LhHlxuV4wbfM5DFcks2\nZFW8Yvb1CqEAZOA4GqmqFkKFFMU0+szO9hCCIQRjPq9Chu51J+h4dkbTZ1oZ4m72\nvwMc33YyN9jINvJpDPyK6hG3usZlZ4OZ8pc9/APWfaLvhF2XRJYUbjATKbzOxyhB\n4qC8PV0JAgMBAAECggEAIgvA1/K9E+d21W5BxXHsPD3YEuV03c6R6saeWpipfoky\nux9dFQjuhYEEtEFI3r4iKHhv07ZCli4vBQ7VCvuD6VNekc906srRma+2DvuohRTT\ndSDGbBeHPGP++CqP8ViDDYFaDRDfJr4dFJOEwhUZZyWRWr6gFcTcANr0XbLm6fPS\nAGosJTpIUXRkEVOksLM4T+RZH/j/mT1mwWpuTglSOH/VzE6UL4N6ZWQMdtaVvj5F\nT4qoLKMrB2Dfv/p7/SZ3y1wpOaPwFs7/I+wEROtKz5maDF83gF2w1bvayATES8Vh\nBcGCEGMXSWF9+++OpsUpPgPxchDQ5ZQ2GnK8HeCKoQKBgQDpd4s5dD2iPPjuweFD\n8xdcY3DxZ6ocMLgcQ3tnQ2WIXikOvL6mrdBwnzbrsbWk2q4U+p6CEonVAifiein4\nR6nYG4aQgDCPUX6gJnTvx5ySExPsfkQo6aJ6etLOaKyHfd0d3aPrLB1YBVuivKJW\n4PY9dJx6YysV4DN2czMTqjjGzwKBgQDmHkYNBkTNTpU4UETY+Appye4cTCUbiKoA\nv0HudhwNp5cQ6ZZq5fzvDZtMKWbp6nrc3cgOjJi771iBo1M8HBjQ8e8GIAs3jOP0\nHODlqHx+Jx/WkicWjuTL8uQ0YiLyCKHISN0G8ZO/W2toFgxXdnR8YFIC+nyO5G/4\nVzzHznyUpwKBgQCnCEgriuattEHFUCECpGEKUHr1u90Q3ipazkzzzFxP/E4TpSYh\nyile6go5BqOWln4FtGjDVtAV/bzbY9uzLlJtswPLTmtvnjaiDeGLy5xRRiTzBkNt\nofoE9urrkigdqAcS3wfvsVgtKWguPhdHYRvLTCrHxTuGIymujSz13MtSMQKBgQDJ\nBhtF13sVKxfZ+O0b6RsXrSpQGAi2k92HB40uJol9ODEUuioHumAJ6QYIM4bOw2KP\nPUM9yn7GdmEH5siYkybuqNqYrDeAUJj2MKAan+QZRE5g4I46+5tNuyK1zCEg9H93\n+obzQOhD2zXp2JDxeu5plK8wIOfc4BwcgwD6vxw/swKBgQDCRJNW6KO0xt1vdjrP\neYxO4BU68/HpONIB/yThpC5ZC51RIN6QU16blawoUhc7qDq+KTTMQ/T+YKOxMowc\n/iV8CMDH+nixEXspd3bvrUDKefyLB9MIultc4FutBpIg6uAnn7HtQzCv3A2eqPj0\nXK+ekXNT1JZxA7kLPY1/kxcU3g==\n-----END PRIVATE KEY-----\n'


def createTokenWithKeys(clearPayload, payloadToEncrypt, privateKey, publicKey, encryptKey):

    encrypted_section = symEncrypt(payloadToEncrypt, encryptKey)

    # Handle the outer payload
    clearPayload["extra"] = encrypted_section
    print("Payload {}".format(clearPayload))
    signed = makeJWT(clearPayload, privateKey, publicKey)
    return signed


encryptKey = loadEncryptKey()
privateKey, publicKey = loadCertKeys()


def createToken(clearPayload, payloadToEncrypt):
    global privateKey, publicKey, encryptKey
    return createTokenWithKeys(clearPayload, payloadToEncrypt, privateKey, publicKey, encryptKey)


if __name__ == "__main__":

    token = createTokenWithKeys({"sub":"23", 'jti': "aaaabbbb", "type": "profile",
                                 "otherIDs": {"household": "456"}, 'ppt': {
                                                "prov": "SKY","ter": "GB","prop": "SKYGO"}
                                 },
                                {
                                    "email":"name@gmail.com",
                                    "scopes":["profile", "persona", "core",
                                               "optouts", "device", "household", "hhcore"],
                                    "otherIDs": {
                                                   "household": 456
                                               }
                                },
                                privateKey, publicKey, encryptKey)
    print(token)
    hhtoken = createTokenWithKeys({"sub":"2367", 'jti': "123abc", "type": "household",
                                 'ppt': {
                                                "prov": "SKY","ter": "GB","prop": "SKYGO"}
                                 },
                                {
                                    "email":"name@gmail.com",
                                    "scopes":["profile", "persona", "core",
                                               "optouts", "device", "household", "hhcore"],
                                    "otherIDs": {}
                                },
                                privateKey, publicKey, encryptKey)
    print(hhtoken)





