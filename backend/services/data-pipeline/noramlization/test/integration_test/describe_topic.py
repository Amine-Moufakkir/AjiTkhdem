from kafka import KafkaAdminClient
client = KafkaAdminClient(bootstrap_servers='localhost:9092')
metadata = client.describe_topics(['normalisation'])
print(metadata)
