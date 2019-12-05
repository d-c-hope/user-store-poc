from pampy import match, _
from config.tenancies import Proposition, Provider, Territory, patternsAndActions


class NoTenancyMatchException(Exception):
    pass

# Pattern matcher doesn't yet support enums, will soon
def enumToStr(ptp):
    return map(lambda x : str(x), ptp)

def getTenancy(ptp):
    try:
        r = match(enumToStr(ptp), *patternsAndActions)
        return r
    except:
        raise NoTenancyMatchException



if __name__ == "__main__":

    getTenancy((Provider.SKY, Territory.GB, Proposition.UNKNOWN))

    # input = (10,2,3)
    # pattern1 = (1, _, _)
    # action1 = lambda x, y: print("matches 1")
    # pattern2 = (10, _, _)
    # action2 = lambda x, y: print("matches 10")
    # match(input,
    #         pattern1, action1,
    #         pattern2, action2)
    #
    # inputb = enumToStr((Provider.SKY, Territory.GB, Proposition.UNKNOWN))

    # pattern1b = (str(Provider.SKY), _, _)
    # action1b = lambda x, y: print("matches Sky")
    # pattern2b = (str(Provider.NOWTV), _, _)
    # action2b = lambda x, y: print("matches NowTV")
    #
    # match(inputb,
    #       pattern1b, action1b,
    #       pattern2b, action2b)

    # getTenancyOptions((Provider.SKY, None, Proposition.UNKNOWN))