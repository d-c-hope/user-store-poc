import asyncio
import couchbase.experimental; couchbase.experimental.enable()
from acouchbase.bucket import Bucket
cb=None
import persistance.tenancySelector
from persistance import couchbaseWrapper

class AlreadyExistsException(Exception):
    pass

class IndexDocsException(Exception):
    pass

class DataStoreUtils:

    @staticmethod
    def getParentPathList(pathList):
        res_list = [i for i, value in enumerate(pathList) if value.pathString.startswith("<")]
        parentPathList = pathList[0:res_list[-1]+1]
        remainder = pathList[res_list[-1]+1:]
        return (parentPathList, remainder)

    @staticmethod
    async def updateIndexDoc(parentPathList,docName, isUpdate, ptp):
        indexDocName = ".".join([item.pathVal for item in parentPathList[0:2]]) + ".index"
        indexDoc = await couchbaseWrapper.getData(indexDocName, ptp)
        if not indexDoc and not isUpdate:
            indexDoc = {}
        if not docName in indexDoc:
            indexDoc[docName] = True
            await couchbaseWrapper.upsert(indexDocName, indexDoc, ptp)


async def exists(pathList, ptp):
    try:
        doc  = await get(pathList, ptp)
        if doc: return True
        else: return False
    except:
        return False


async def get(pathList, ptp):
    pPathList, remainder = DataStoreUtils.getParentPathList(pathList)
    docName = ".".join([item.pathVal for item in pPathList])
    doc = await couchbaseWrapper.getData(docName, ptp)
    subDoc = doc[remainder[0].pathVal]
    return subDoc


async def getAllSubDocs(pathDotString, ptp):
    """
    Used by the graphql resolver. Bypasses the pathlist logic
    and returns all docs at the path e.g. profile.23
    Cant use with an ID root such as profile.23.persona
    """
    # pPathList, remainder = DataStoreUtils.getParentPathList(pathList)
    # docName = ".".join([item.pathVal for item in pPathList])
    doc = await couchbaseWrapper.getData(pathDotString, ptp)
    return doc
    # subDoc = doc[remainder[0].pathVal]
    # return subDoc


async def getAll(idRootPathList, resourcePathList, ptp):
    """
    Gets all items at pathList conforming to resoucePathList
    e.g. under persona might be 7 docs but if resource path list is persona/<id>/corepersona this will only return
    the corepersona docs say optouts as in persona/<id>/optouts
    """

    # Lookup the different docs under the given profile via the index doc
    indexDocName = ".".join([item.pathVal for item in idRootPathList[0:2]]) + ".index"
    indexDoc = await couchbaseWrapper.getData(indexDocName, ptp)

    r = {}
    pathListString = ".".join([item.pathVal for item in idRootPathList])
    # then find the ones that match the pathliststring. note indexdoc names will match pathlist beause pathlist is
    # always an ID root with IDs directly below, e.g. persona IDs
    for item in indexDoc:
        itemNodes = item.split(".")
        if item.startswith(pathListString) and len(itemNodes) == (len(idRootPathList) +1):
            d = await couchbaseWrapper.getData(item, ptp)
            _, remainder = DataStoreUtils.getParentPathList(resourcePathList)
            defSubDocName = ".".join([item.pathVal for item in remainder])
            if defSubDocName in d:
                r[item] = d[defSubDocName]
    return r

async def getAllGQL(mainPath, resourceNames, ptp):
    """
    Gets all items at mainPath and includes all sub-resources with names in resourceNames
    Both should be of form a.b.c

    """

    asList = mainPath.split(".")

    # Lookup the different docs under the given profile via the index doc
    indexDocName = ".".join(asList[0:2]) + ".index"
    indexDoc = await couchbaseWrapper.getData(indexDocName, ptp)

    # _, remainder = DataStoreUtils.getParentPathList(resourcePathList)

    r = {}
    # pathListString = ".".join([item.pathVal for item in idRootPathList])
    # then find the ones that match the pathliststring. note indexdoc names will match pathlist beause pathlist is
    # always an ID root with IDs directly below, e.g. persona IDs
    for item in indexDoc:
        itemNodes = item.split(".")
        if item.startswith(mainPath) and len(itemNodes) == (len(asList) +1):
            d = await couchbaseWrapper.getData(item, ptp)
            # _, remainder = DataStoreUtils.getParentPathList(resourcePathList)
            # defSubDocName = ".".join([item.pathVal for item in remainder])
            subDocs = {} # should replace this with a filter
            for resource in resourceNames:
                if resource in d:
                    subDocs[resource] = d[resource]
            r[item] = subDocs
    return r


async def create(pathList, doc, ptp):
    """
    Need to store the doc at the path
    Could have a doc for every path and then a separate doc to list which docs exist
    For consistency and to avoid too many small DB docs being written and read (expecially given the
    user will read the profile as a whole often) instead each layer will have docs
    e.g. for /profile/<id>/persona/<id>/device/<id> we shall have a doc for profile/<id>/*,
    a doc for /profile/<id>/persona/<id>/* and a doc for /profile/<id>/persona/<id>/device/<id>/*
    rather than everything in one doc or say a doc for /profile/optouts and one for /profile/core

    So... this needs to do the following things:
    1. work out which doc to insert into, e.g. profile.2 or profile.2.persona.5
    2. check the doc exists
    2b. create it if it doesn't
    3. Add into it
    Note, we already checked before that we had an object in the case of say persona/<id>/optouts
    we checked that persona/<id> existed before here so no need to check
    no ignore:Note that when adding to /persona, this is turned into /persona/<id>/core and would be the first doc
    """
    pPathList, remainder = DataStoreUtils.getParentPathList(pathList)
    docName = ".".join([item.pathVal for item in pPathList])

    getRes = await couchbaseWrapper.getData(docName, ptp)
    containerDoc = {}
    if getRes:
        containerDoc = getRes
    subDocName = ".".join([item.pathVal for item in remainder])
    if subDocName in containerDoc:
        raise AlreadyExistsException("Can't create, already exists")

    containerDoc[subDocName] = doc
    await couchbaseWrapper.upsert(docName, containerDoc, ptp)

    try:
        await DataStoreUtils.updateIndexDoc(pPathList, docName, False, ptp)
    except:
        raise IndexDocsException

    return doc


async def update(pathList, doc, ptp):
    """
    """
    pPathList, remainder = DataStoreUtils.getParentPathList(pathList)
    docName = ".".join([item.pathVal for item in pPathList])

    getRes = await couchbaseWrapper.getData(docName, ptp)
    containerDoc = {}
    if getRes:
        containerDoc = getRes
    subDocName = ".".join([item.pathVal for item in remainder])

    oldDoc = None
    if subDocName in containerDoc:
        oldDoc = containerDoc[subDocName]
    containerDoc[subDocName] = doc
    await couchbaseWrapper.upsert(docName, containerDoc, ptp)

    try:
        await DataStoreUtils.updateIndexDoc(pPathList, docName, True, ptp)
    except:
        raise IndexDocsException

    return oldDoc, doc


async def deleteSingle(pathList, ptp):
    """
    Could be profile/23/persona/45 or profile/23/persona/45/optouts
    Doesn't do idRoots, i.e. not for calling like profile/23/persona

    Must delete resources maching but also under the path
    Note must also remove index doc
    """

    # Lookup the different docs under the given profile via the index doc
    indexDocName = ".".join([item.pathVal for item in pathList[0:2]]) + ".index"
    indexDoc = await couchbaseWrapper.getData(indexDocName, ptp)

    r = {}
    pPathList, remainder = DataStoreUtils.getParentPathList(pathList)
    stringToMatch = ".".join([item.pathVal for item in pPathList])
    def doesMatchOnStart(item):
        # itemNodes = item.split(".")
        if item.startswith(stringToMatch): return True
        else: return False
    def doesMatchExactly(item):
        # itemNodes = item.split(".")
        if item == stringToMatch: return True
        else: return False

    matchesOnStartOrExact = set(filter(doesMatchOnStart, indexDoc.keys()))
    matchesExactly = set(filter(doesMatchExactly, indexDoc.keys()))
    matchesOnStart = matchesOnStartOrExact - matchesExactly

    """
        Examples of matches to /profile/34/persona/4 might be:
        /profile/34/persona/4/core                   /profile/34/persona/4, /core (matches exactly on parent)
        /profile/34/persona/4/optoouts               /profile/34/persona/4, /core (matches exactly on parent)
        /profile/34/persona/4/sports/8/favteam       /profile/34/persona/4/sports/8, /favteam (matches on start on parent)
    """
    # Simpler case as don't need to get doc and look in it
    for item in matchesOnStart:
        await couchbaseWrapper.delete(item, ptp)
        del indexDoc[item]

    for item in matchesExactly: # should only be one
        if len(remainder) == 0:
            await couchbaseWrapper.delete(item, ptp)
            del indexDoc[item]
        else:
            itemDoc = await couchbaseWrapper.getData(item, ptp)
            remString = ".".join([item.pathVal for item in remainder])
            for subItem in list(itemDoc.keys()):
                if subItem.startswith(remString):
            # if remString in itemDoc:

                    del itemDoc[subItem]
            await couchbaseWrapper.upsert(item, itemDoc, ptp)
            if len(itemDoc) == 0:
                del indexDoc[item]

    await couchbaseWrapper.upsert(indexDocName, indexDoc, ptp)



async def initialise():
    await couchbaseWrapper.initialise()


if __name__ == "__main__":
    async def do_test():
        await setData("test1234", {"name": "david"})
        return await getData("test1234")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getConnection())
    rv = loop.run_until_complete(do_test())
    print(rv.value)

