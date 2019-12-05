from config.tenancies import validTerritories, validProviders, validPropositions
from config.tenancies import mProv, mProp, mTer

class InvalidPTP(Exception):
    pass

def checkTenancy(headers):

    if not "Provider" in headers:
        raise InvalidPTP()
    elif not headers["Provider"] in validProviders:
        raise InvalidPTP()

    if not "Territory" in headers:
        raise InvalidPTP()
    elif not headers["Territory"] in validTerritories:
        raise InvalidPTP()

    # don't enforce proposition, would make sense necessarily on a CRM call for example
    if "Proposition" in headers and not headers["Territory"] in validTerritories:
        raise InvalidPTP()


def mapPTP(headers, names=("Provider", "Territory", "Proposition")):

    prov = mProv["default"]
    ter = mTer["default"]
    prop = mProp["default"]
    if names[0] in headers and headers[names[0]] in mProv:
        prov = mProv[headers[names[0]]]
    if names[1] in headers and headers[names[1]] in mTer:
        ter = mTer[headers[names[1]]]
    if names[2] in headers and headers[names[2]] in mProp:
        prop = mProp[headers[names[2]]]
    return (prov, ter, prop)