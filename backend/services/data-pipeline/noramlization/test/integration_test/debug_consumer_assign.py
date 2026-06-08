import json
from kafka import KafkaConsumer, TopicPartition

consumer = KafkaConsumer(
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')) if v else None
)
tp = TopicPartition('normalisation', 0)
consumer.assign([tp])
consumer.seek_to_beginning(tp)

print("Fetching messages using assignment...")
records = consumer.poll(timeout_ms=5000)
for tp, msgs in records.items():
    for msg in msgs:
        print(f"Assign Received: {msg.value}")
