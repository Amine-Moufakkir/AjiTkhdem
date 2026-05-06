import json
from kafka import KafkaConsumer, KafkaProducer

class Kafka:
    def __init__(self, bootstrap_servers='kafka:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumer = None

    def connect(self):
        """Initialise la connexion au broker Kafka."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print(f"Connecté au broker Kafka sur {self.bootstrap_servers}")
        except Exception as e:
            print(f"Erreur de connexion Kafka : {e}")

    def listen(self, topics):
        """
        Ecoute un ou plusieurs topics et retourne un dictionnaire 
        contenant le nom du topic et la donnée.
        """
        # Configuration du consommateur pour accepter une liste de topics
        self.consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='pre-processing-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        # S'abonner aux topics (peut être une liste comme ['topic1', 'topic2'])
        if isinstance(topics, str):
            topics = [topics]
        
        self.consumer.subscribe(topics)
        print(f"Ecoute activée sur : {topics}")

        for message in self.consumer:
            # On retourne un dictionnaire avec le topic source et la data
            yield {
                "topic": message.topic,
                "data": message.value
            }




    def send(self, topic, data, category):
        """Prend des données avec une catégorie et les met en file Kafka."""
        if self.producer is None:
            self.connect()
            
        payload = {
            "category": category,
            "data": data
        }
        
        try:
            self.producer.send(topic, value=payload)
            self.producer.flush()
        except Exception as e:
            print(f"Erreur lors de l'envoi du message : {e}")
