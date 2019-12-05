from confluent_kafka.avro import Consumer




c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'groupid',
    'auto.offset.reset': 'earliest'})

c.subscribe(['user_store_updates'])

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