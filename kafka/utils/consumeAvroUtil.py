from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


# avroProducer = AvroProducer({
#     'bootstrap.servers': 'localhost:9092',
#     'schema.registry.url': 'http://localhost:8081'
#     }, default_key_schema=key_schema, default_value_schema=value_schema)

c = AvroConsumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'groupid',
    'schema.registry.url': 'http://localhost:8081',
    'auto.offset.reset': 'earliest'})

c.subscribe(['test-topic-1'])

while True:
    try:
        msg = c.poll(10)
        print("poll returned {}".format(msg))

    except SerializerError as e:
        print("Message deserialization failed for {}: {}".format(msg, e))
        break

    if msg is None:
        continue

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        continue

    print(msg.value())

c.close()