import asyncio
import couchbase.experimental; couchbase.experimental.enable()
from acouchbase.bucket import Bucket
from persistance.tenancySelector import getTenancy


cbDict = {
}

prefixesDict = {
    "sky" : ""
}

async def initialise():
    global cbDict
    cb = Bucket('couchbase://localhost/testbucket', username='testuser', password='password')
    await cb.connect()
    cbDict["sky"] = cb
    return True

async def getData(docID, ptp):
    try:
        tenancy = getTenancy(ptp)
        docID = prefixesDict[tenancy] + docID
        r = await cbDict[tenancy].get(docID)
        return r.value
    except Exception as e:
        return None

async def insert(docID, doc, ptp):
    tenancy = getTenancy(ptp)
    docID = prefixesDict[tenancy] + docID
    return await cbDict[tenancy].insert(docID, doc)

async def upsert(docID, doc, ptp):
    tenancy = getTenancy(ptp)
    docID = prefixesDict[tenancy] + docID
    return await cbDict[tenancy].upsert(docID, doc)

async def delete(docID, ptp):
    tenancy = getTenancy(ptp)
    docID = prefixesDict[tenancy] + docID
    return await cbDict[tenancy].delete(docID)



if __name__ == "__main__":
    async def do_test():
        await setData("test1234", {"name": "david"})
        return await getData("test1234")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getConnection())
    rv = loop.run_until_complete(do_test())
    print(rv.value)