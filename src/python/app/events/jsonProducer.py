from confluent_kafka import Producer
import json

producer = None

value = {"email": "a@a.com", "firstName": "David", "profileID": "23416" }
key = {"customerID": "23416"}


def createAuditEventForCreate(docID, doc, ptp):

    # TODO add ptp validation
    doc = {
        "docID" : docID,
        "provider" : str(ptp[0]).split('.')[1],
        "territory": str(ptp[1]).split('.')[1],
        "proposition": str(ptp[2]).split('.')[1],
        "type" : "CREATE",
        "value": doc
    }

    userOrHHID = ".".join(docID.split('.')[0:2])
    docJS = json.dumps(doc)
    producer.produce('user_store_updates', key=userOrHHID, value=docJS)
    # producer.flush()

def createAuditEventForUpdate(docID, newDoc, oldDoc, ptp):

    doc = {
        "docID": docID,
        "provider" : str(ptp[0]).split('.')[1],
        "territory": str(ptp[1]).split('.')[1],
        "proposition": str(ptp[2]).split('.')[1],
        "type" : "UPDATE",
        "value": newDoc,
        "oldValue" : oldDoc
    }
    userOrHHID = ".".join(docID.split('.')[0:2])
    docJS = json.dumps(doc)
    producer.produce('user_store_updates', key=userOrHHID, value=docJS)
    # producer.flush()


def createAuditEventForDelete(docID, ptp):

    doc = {
        "docID": docID,
        "provider" : str(ptp[0]).split('.')[1],
        "territory": str(ptp[1]).split('.')[1],
        "proposition": str(ptp[2]).split('.')[1],
        "type" : "DELETE",
    }
    userOrHHID = ".".join(docID.split('.')[0:2])
    docJS = json.dumps(doc)
    producer.produce('user_store_updates', key=userOrHHID, value=docJS)
    # producer.flush()



def initialise():
    global producer
    producer = Producer({'bootstrap.servers': 'localhost:9092'})




