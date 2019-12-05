from controller import pathMatcher
import uuid
from controller import pathTransforms
from persistance import datastore
import logging
logger = logging.getLogger("applogger")


class UpdateForbiddenException(Exception):
    pass

class CreateForbiddenException(Exception):
    pass

class DeleteForbiddenException(Exception):
    pass



class RouterUtils:

    @staticmethod
    def addID(nodeList):
        """Should only be a single item requiring an ID as require outer scope to exist already"""
        for item in nodeList:
            if item.pathVal == "<id>":
                newID = str(uuid.uuid4())
                item.pathVal = newID


def processPath(urlPath):
    """
    Returns the matching list against the path, the normalised list and the outer list
    Normalised one just has the actual resource added on, e.g. /persona is a resouce /persona/<id>/core
    Outer one is the normalised resource one level up in the hierarchy that must exist before this one can be created
        e.g. can't post to /profile/id/persona if /profile/id doesnt exist

    """
    urlList = urlPath.split("/")
    logger.debug(urlList)

    matchNodeList = pathMatcher.findMatch(urlList)
    if matchNodeList:
        normalisedList = pathTransforms.normaliseListEnd(matchNodeList.copy())
        lastNode = matchNodeList[-1]

        nonNormOuterList = pathTransforms.getOuterPathList(normalisedList)
        outerPathList = pathTransforms.normaliseListEnd(nonNormOuterList)

        return (matchNodeList, normalisedList, outerPathList)
    else:
        raise Exception("Unknown route")


async def checkIfExistsAlready(fullNodeList, ptp):
    if len(fullNodeList) == 0: return True
    r = await datastore.exists(fullNodeList, ptp)
    return r

def isMultiDoc(matchNodeList, normNodeList):
    lastNodeF = matchNodeList[-1]
    if lastNodeF.isIdRoot and len(normNodeList) > 3:
        return True
    else:
        return False
        return r


async def getForDelete(matchNodeList):
    r = await processMultiGet(matchNodeList, [])
    return r

async def postAllowed(matchNodeList, normalisedList, outerPathList, ptp):
    """
    Can POST to /optouts - error if already there
    Can POST to /personas - generates new ID
    Can POST to /personas/<id>/optouts if persona exists
    Can't POST to /personas/<id>
    If there are any <ids> in the path preceding the path the POST will initially do a GET to check these are present
    So Can't POST to /personas/<id>/core as previous must exist already and is created by POSTing to /personas
    A POST should include data for the default type under it, e.g. persona co

    Note enforcement of no updates just creates is done by trying to create and failing
    """

    lastMNode = matchNodeList[-1]
    if lastMNode.isIdRoot == True and not lastMNode.postEndpoint:
        raise CreateForbiddenException()

    # Can't POST to /persona/<id>, the /persona makes something at the id
    if lastMNode.isIdNode():
        raise CreateForbiddenException()

    r = await checkIfExistsAlready(outerPathList, ptp)
    if not r:
        return False

    return True


async def putAllowed(matchNodeList, normalisedList, outerPathList, ptp):
    """
    TODO can't PUT to /persona/id if putCreation=False although may be just enforced by having no resource at that

    * check if the resource exists - if it does, then we can just udpate it
    * otherwise we can update if:
        * it is added to put allowed ID node
            i.e. /profile/45/device/34543543
        * or the outer resource exists
            e.g. /profile/45/device/34543543/optouts when /profile/45/device/34543543/core exists
            e.g. /profile/45/persona/23/optouts when /profile/45/persona/23/core exists

    """

    # check if the resource exists - if it does, then we can just udpate it
    r = await checkIfExistsAlready(normalisedList, ptp)
    if r:
        return True

    # otherwise we at least need the outer resource to exist so we can create something new
    r = await checkIfExistsAlready(outerPathList, ptp)
    if not r:
        raise UpdateForbiddenException()

    # finally check we can create a new node, so either default or idnode, idroot not allowed
    if matchNodeList[-1].isIdNode or matchNodeList[-1].isDefault:
        return True
    else:
        raise UpdateForbiddenException()


async def deleteAllowed(matchNodeList, normalisedList, outerPathList, ptp):
    """
    Delete must specify a resource ID, can't do delete to /persona but can to /persona/34
    which will find all data under that and then delete
    Can't delete core docs - should delete at the outer level, i.e. persona/34 is ok not persona/34/core
    but persona/34/optouts is ok
    """

    if matchNodeList[-1].isIdRoot:
        raise DeleteForbiddenException()

    if matchNodeList[-1].isDefault:
        raise DeleteForbiddenException()

    # check if the resource exists - if it doesnt, then we can't delete it. note we look at the normalised list
    # to check an actual resource in case this is an id node
    r = await checkIfExistsAlready(normalisedList, ptp)
    if r:
        return True
    else:
        raise UpdateForbiddenException()




def initialise():
    pass

if __name__ == "__main__":
    pass




# async def processGet(matchNodeList, normNodeList):
#     """
#     Works out if the last node is an idroot or not and then calls processSingle or processMulti
#     """
#     # fullNodeList = normaliseNodeList(idType, idVal, matchNodeList)
#     lastNodeF = matchNodeList[-1]
#     if lastNodeF.isIdRoot and len(normNodeList) > 3:
#         r = await processMultiGet(matchNodeList, normNodeList)
#         return r
#     else:
#         r = await processSingleGet(matchNodeList, normNodeList)
#         return r
#
# async def processMultiGet(matchNodeList, normNodeList):
#     """
#     The aim of this method is to produce an unambiguous nodelist
#     Need to add on the root and if the doc is missing add the
#     default doc
#     i.e. /persona/34343 goes to /profile/33/persona/34343/core
#     """
#     r = await datastore.getAll(matchNodeList)
#     return r
#
#
# async def processSingleGet(matchNodeList, normNodeList):
#     """
#     The aim of this method is to produce an unambiguous nodelist
#     Need to add on the root and if the doc is missing add the
#     default doc
#     i.e. /persona/34343 goes to /profile/33/persona/34343/core
#     """
#
#     r = await datastore.get(normNodeList)
#     return r
