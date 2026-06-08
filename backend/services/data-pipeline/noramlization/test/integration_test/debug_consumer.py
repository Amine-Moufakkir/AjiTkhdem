import json
import uuid
from kafka import KafkaConsumer, KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))
producer.send('normalisation', value={"test": "hello"})
producer.flush()

consumer = KafkaConsumer(
    'normalisation',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    consumer_timeout_ms=5000,
    group_id=str(uuid.uuid4())
)

print("Starting consumer loop...")
for msg in consumer:
    print(f"Received: {msg.value}")
