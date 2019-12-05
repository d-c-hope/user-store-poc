from jwcrypto import jwk, jwe, jws, jwt
from jwcrypto.common import json_encode, json_decode
import json
from utils import paths
import sys


def loadCertKey():
    with open(paths.configPath + "/token_certificate.pem", "rb") as certfile:
        contents = certfile.read()

        publicKey = jwk.JWK.from_pem(contents)

    return publicKey


def loadEncryptKey():
    with open(paths.configPath + "/sym_encrypt_key", "r") as keyfile:
        key = jwk.JWK.from_json(keyfile.read())
        return key





def decrypt(data, key):
    E = jwe.JWE()
    E.deserialize(data, key)
    decrypted_payload = E.payload
    return decrypted_payload




def validateAndGetTokenWithKeys(token, publicKey, encryptKey):
    jwstoken = jwt.JWT(jwt=token, key=publicKey)
    token.count(".")
    # jwstoken.deserialize(key=publicKey)
    claims = json_decode(jwstoken.claims)
    encrypted_section = decrypt(claims["extra"], encryptKey)
    claims["extra"] = json_decode(encrypted_section)

    return claims


encryptKey=None
publicKey=None

def validateAndGetToken(token):
    global encryptKey, publicKey
    return validateAndGetTokenWithKeys(token, publicKey, encryptKey)

def loadKeys():
    global encryptKey, publicKey
    encryptKey = loadEncryptKey()
    # global publicKey
    publicKey = loadCertKey()


if __name__ == "__main__":


    paths.configPath = sys.path[0] + '/../config'
    loadKeys()

    # token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImliUzAyYzJPdkZMQWMwSVdoQnB5MjdrOWZ6YlhJejRmaEpOd3lkLWNVa2MifQ.eyJzdWIiOiIyMyJ9.ajhP_lXq-blxZZeRerUX4RuLxUaUJERlouRCqboyVFEMH8rjGGyqyeMcw2La9UHvfI84K98lghb6t7bP9TjpgQ"
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImliUzAyYzJPdkZMQWMwSVdoQnB5MjdrOWZ6YlhJejRmaEpOd3lkLWNVa2MifQ.eyJleHRyYSI6ImV5SmhiR2NpT2lKQk1qVTJTMWNpTENKbGJtTWlPaUpCTWpVMlEwSkRMVWhUTlRFeUluMC5GRl9KMndHQjlUMmhGem5aUVJjZ1VDeENrSWFTTS0ycVR3eTE0LWFZdFlTSkNEcEFob2gtYTVmMjE5WW1pYkI2TWV2U3p3RlVpb3J2VFpDVTlMbVRNdjZXOGhYcXZoanQuNy04N25TOGF4NHFyM2llUW82aTJYdy5YUVgtcGJlNkFHaUVSSTBtVlBwQUJoQjZWOUJmMnc4eVFwcm9Cam9LejFJLkxBNXpCYmUwdGVJLXMtQ0FqR01LTUhpdUlWaUR3Q0I5MmF6X2tKLW81YmMiLCJzdWIiOiIyMyJ9.rM8vTu73SQjd_9Z42yqEEMQkJjqtAfgipKFuO351scu-QOLI3JAkLSDhW7bnLU1ZhQwt4y2PV53qpG9P1Xh56w"
    validateAndGetTokenWithKeys(token, publicKey, encryptKey)
