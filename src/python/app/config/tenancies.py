from enum import Enum
from pampy import match, _


class Provider(Enum):
    SKY = 1
    NOWTV = 2
    UNKNOWN = 100


class Territory(Enum):
    GB = 1
    UNKNOWN = 100

class Proposition(Enum):
    SKYGO = 1
    UNKNOWN=100


validProviders = ("SKY", "NOWTV")
validTerritories = ("GB")
validPropositions = ("SKYGO", "NOWTV")

mProv = {
    "SKY": Provider.SKY,
    "default": Provider.UNKNOWN
}
mTer = {
    "GB": Territory.GB,
    "default": Territory.UNKNOWN
}
mProp = {
    "SKYGO": Proposition.SKYGO,
    "default": Proposition.UNKNOWN
}

patternsAndActions = (
    (str(Provider.SKY), _, _), lambda x, y: "sky",
    (str(Provider.NOWTV), _, _), lambda x, y: "international"
)