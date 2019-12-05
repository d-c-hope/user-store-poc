from confluent_kafka import Producer

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


value_schema_str = """
{
   "namespace": "cch.userstore.event",
   "name": "value",
   "type": "record",
   "fields" : [
     {
       "name" : "email",
       "type" : "string"
     },
     {
       "name" : "firstName",
       "type" : "string"
     },
     {
       "name" : "profileID",
       "type" : "string"
     },
   ]
}
"""

key_schema_str = """
{
   "namespace": "cch.userstore.event",
   "name": "key",
   "type": "record",
   "fields" : [
     {
       "name" : "profileID",
       "type" : "string"
     }
   ]
}
"""

value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)
value = {"email": "a@a.com", "firstName": "David", "profileID": "23416" }
key = {"customerID": "23416"}

avroProducer = AvroProducer({
    'bootstrap.servers': 'localhost:9092',
    'schema.registry.url': 'http://localhost:8081'
    }, default_key_schema=key_schema, default_value_schema=value_schema)

for i in range(2):
    print("adding event")
    avroProducer.produce(topic='test-userstore-topic-1', value=value, key=key)
avroProducer.flush()