import json
import time
from kafka import KafkaConsumer, KafkaProducer
import uuid
import re
from datetime import datetime, timedelta

class Kafka:
    def __init__(self, topic_output,topics_inputs:list  ,  bootstrap_servers='kafka:9092', max_retries=5, base_delay=1, max_delay=60):
        """
        Args:
            bootstrap_servers: Adresse du broker Kafka
            max_retries: Nombre maximum de tentatives
            base_delay: Délai initial en secondes (exponentiel : base_delay * 2^attempt)
            max_delay: Délai maximum en secondes
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.consumer = None
        
        # Configuration du retry
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.topic_output = topic_output

        self.topics_inputs = []
        for topic in topics_inputs:
            self.topics_inputs.append(topic) # Topic principal
            for i in range(1, max_retries + 1):
                self.topics_inputs.append(f"{topic}_retry_{i}") # Tous les topics de retry
       

    def connect(self):
        """Initialise la connexion au broker Kafka avec configuration retry."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                # Configuration retry native Kafka
                retries=5,
                retry_backoff_ms=1000,
                max_in_flight_requests_per_connection=1,
                acks='all',
                # Timeout
                request_timeout_ms=30000,
                max_block_ms=60000
            )
            print(f"✓ Connecté au broker Kafka sur {self.bootstrap_servers}")
        except Exception as e:
            print(f"✗ Erreur de connexion Kafka : {e}")
            raise

    def _calculate_backoff(self, attempt: int) :
        """Calcule le délai exponentiel : 1s, 2s, 4s, 8s..."""
        delai_secondes = self.base_delay * (2 ** attempt)
        upcoming_date = datetime.now() + timedelta(seconds=delai_secondes)

        
        return upcoming_date.timestamp() # Retourne un float (ex: 1715806791.5)

    
    def generate_unique_id(self) -> str:
        
        return str(uuid.uuid4())
    

    def handle_process_failure(self, topic: str, payload: dict, headers: list, exception: Exception):
        """
        Gère l'échec global du traitement et décide du re-routage.
        """
        # Extraire ou initialiser le compteur de tentatives depuis les headers
        retry_count = 0
        header_dict = {h[0]: h[1] for h in headers} if headers else {}
        
        if b'retry_count' in header_dict:
            retry_count = int(header_dict[b'retry_count'].decode('utf-8'))
 

        if retry_count < self.max_retries:
            new_retry_count = retry_count + 1
            topic = f"{topic}_retry_{new_retry_count}"

            
            
            
            unlock_date  = self._calculate_backoff(new_retry_count)
            

         
            print(f"⚠️ Échec du traitement : {exception}")
            print(f"🔄 Tentative {new_retry_count}/{self.max_retries}. "
                  f"Republique dans {unlock_date}s...")

            
            # Préparation des nouveaux headers
            new_headers = [
                ('retry_count', str(new_retry_count).encode('utf-8')),
                ('last_error', str(exception).encode('utf-8')) , 
                ('unlock_date', str(unlock_date).encode('utf-8'))
            ]

            if  self.producer is None : 
                raise Exception("Le producteur n'a pas encore été initialisé.")

            try:
                
                self.producer.send(
                    topic=topic,
                    value=payload,
                    headers=new_headers
                )
                self.producer.flush()

                
                return True
            except Exception as e:
                print(f"❌ Impossible de republier pour retry : {e}")
        else:
            print(f"🚫 Max retries atteint ({self.max_retries}). Envoi vers DLQ.")
            self._send_to_dlq(topic, payload, headers, exception)
        
        return False

    def _send_to_dlq(self, original_topic, payload, headers, exception):
        
        dlq_topic = f"{original_topic}.dlq"
        # Logique d'envoi vers la Dead Letter Queue pour analyse manuelle

        if self.producer is None : 
            raise Exception("Le producteur n'a pas encore été initialisé.")
        
        self.producer.send(topic=dlq_topic, value=payload, headers=headers)
        self.producer.flush()


    def send_on_succes(self, payload, headers):

        if self.producer is None : 
            raise Exception("Le producteur n'a pas encore été initialisé.")
    
        
        future = self.producer.send(topic=self.topic_output, value=payload, headers=headers)
        self.producer.flush()
        return future



    def close(self):
        """Ferme le producteur et le consommateur."""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            print("✓ Producteur Kafka fermé.")
        if self.consumer:
            self.consumer.close()
            print("✓ Consommateur Kafka fermé.")


    def listen(self):
        """
        Ecoute les topics et extrait les métadonnées de retry si présentes.
        """
        self.consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='normalisation-group',
            # On décode le JSON ici pour la 'value'
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        self.consumer.subscribe(self.topics_inputs)

        for message in self.consumer:
            topic = message.topic
            pattern = r"^(.+)_retry_(\d+)$"
            match = re.match(pattern, topic)
            
            header_dict = {}
            if match:
                raw_headers = message.headers if message.headers else []
                header_dict = {k.decode('utf-8'): v.decode('utf-8') for k, v in raw_headers}

                # Gestion de la date de déblocage pour les retries
                unlock_date_raw = header_dict.get('unlock_date')
                if unlock_date_raw:
                    unlock_timestamp = float(unlock_date_raw)
                    unlock_date = datetime.fromtimestamp(unlock_timestamp)
                    if unlock_date > datetime.now():
                        # Pas encore prêt : on republie et on attend un peu
                        if self.producer is None:
                            raise Exception("Le producteur n'a pas encore été initialisé.")
                        self.producer.send(topic=topic, value=message.value, headers=message.headers)
                        self.producer.flush()
                        time.sleep(1)
                        continue

            # On renvoie tout dans le dictionnaire pour que le pipeline y ait accès
            yield {
                "topic": message.topic,
                "data": message.value,
                "headers": message.headers
            }

   


