import aiohttp
import asyncio
from jwcrypto import jwk, jwe, jws, jwt
from jwcrypto.common import json_encode, json_decode
import json



def loadCertKey():
    # with open("token_key/wrong_certificate.pem", "rb") as certfile:
    with open("token_key/sign_certificate.pem", "rb") as certfile:
        contents = certfile.read()
        print(contents)
        publicKey = jwk.JWK.from_pem(contents)

    return publicKey


def loadEncryptKey():
    with open("token_key/sym_encrypt_key", "r") as keyfile:
        key = jwk.JWK.from_json(keyfile.read())
        return key


def verifyAndGetHouseholds(token, verify_key, decrypt_key):
    # Verify the complete token
    # jwstoken = jws.JWS()
    jwstoken = jws.JWT(jwt=token)
    jwstoken.deserialize(signed)

    # jwstoken.verify(outer_key)
    jwstoken.verify(verify_key)
    recPayload = jwstoken.payload
    recPayloadD = json.loads(recPayload)

    # pull out households and then decrypt
    recHouseholdsE = recPayloadD['households']
    # Decrypting the innter payload
    E = jwe.JWE()
    E.deserialize(recHouseholdsE, key=decrypt_key)
    decrypted_payload = E.payload
    return decrypted_payload


def decrypt(data, key):
    E = jwe.JWE()
    E.deserialize(data, key)
    decrypted_payload = E.payload
    return decrypted_payload


def validateAndGetToken(token, publicKey, encryptKey):

    jwstoken = jwt.JWT(jwt=token, key=publicKey)
    token.count(".")
    # jwstoken.deserialize(key=publicKey)
    claims = json_decode(jwstoken.claims)
    print(claims)
    encrypted_section = decrypt(claims["extra"], encryptKey)
    print(json_decode(encrypted_section))
    claims["extra"] = json_decode(encrypted_section)
    print(claims)
    return claims


encryptKey = loadEncryptKey()
publicKey = loadCertKey()



if __name__ == "__main__":

    # token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImliUzAyYzJPdkZMQWMwSVdoQnB5MjdrOWZ6YlhJejRmaEpOd3lkLWNVa2MifQ.eyJzdWIiOiIyMyJ9.ajhP_lXq-blxZZeRerUX4RuLxUaUJERlouRCqboyVFEMH8rjGGyqyeMcw2La9UHvfI84K98lghb6t7bP9TjpgQ"
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImliUzAyYzJPdkZMQWMwSVdoQnB5MjdrOWZ6YlhJejRmaEpOd3lkLWNVa2MifQ.eyJleHRyYSI6ImV5SmhiR2NpT2lKQk1qVTJTMWNpTENKbGJtTWlPaUpCTWpVMlEwSkRMVWhUTlRFeUluMC5GRl9KMndHQjlUMmhGem5aUVJjZ1VDeENrSWFTTS0ycVR3eTE0LWFZdFlTSkNEcEFob2gtYTVmMjE5WW1pYkI2TWV2U3p3RlVpb3J2VFpDVTlMbVRNdjZXOGhYcXZoanQuNy04N25TOGF4NHFyM2llUW82aTJYdy5YUVgtcGJlNkFHaUVSSTBtVlBwQUJoQjZWOUJmMnc4eVFwcm9Cam9LejFJLkxBNXpCYmUwdGVJLXMtQ0FqR01LTUhpdUlWaUR3Q0I5MmF6X2tKLW81YmMiLCJzdWIiOiIyMyJ9.rM8vTu73SQjd_9Z42yqEEMQkJjqtAfgipKFuO351scu-QOLI3JAkLSDhW7bnLU1ZhQwt4y2PV53qpG9P1Xh56w"
    validateAndGetToken(token, publicKey, encryptKey)






