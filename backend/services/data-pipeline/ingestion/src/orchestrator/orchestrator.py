from src.scrapper.scrapper import AbstractScrapper
from src.scrapper.scrapper import RekruteScrapper
import redis
from confluent_kafka import Producer
class Orchestrator:
    def __init__(self):
        #Redis Client Initiate
        self.redis_client = redis.Redis(
            host='redis', 
            port=6379, 
            db=0,
            decode_responses=True
        )

        #Kafka Producer Initiate
        kafka_conf = {
            'bootstrap.servers': 'kafka:9092',
            'client.id': 'ingestion-service',
            # Automatically retry if the broker isn't ready yet
            'reconnect.backoff.ms': 1000,
            'reconnect.backoff.max.ms': 10000,
        }
        self.kafka_producer = Producer(kafka_conf)

    def create_scraper(self, site_name: str, url: str) -> AbstractScrapper:        
        name = site_name.lower()
        #ToAdd: Add to .env
        if name == "rekrute":
            return RekruteScrapper(
                redis_client=self.redis_client,
                kafka_producer=self.kafka_producer,
                base_url=url
            )
        # To add other scrapers later, just add more conditions here
        else:
            raise ValueError(f"Le scraper pour le site '{site_name}' n'existe pas.")