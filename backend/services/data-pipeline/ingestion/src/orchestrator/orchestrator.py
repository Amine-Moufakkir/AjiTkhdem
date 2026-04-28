from src.scrapper.scrapper import AbstractScrapper
from src.scrapper.scrapper import RekruteScrapper
import redis
from confluent_kafka import Producer
class Orchestrator:
    def __init__(self):
        kafka_conf = {'bootstrap.servers': 'localhost:9092'}

        self.redis_client = redis.Redis(
            host='localhost', 
            port=6379, 
            db=0,
            decode_responses=True
        )
        self.kafka_producer = Producer(kafka_conf)

    def create_scraper(self, site_name: str, url: str) -> AbstractScrapper:        
        name = site_name.lower()
        
        if name == "rekrute":
            return RekruteScrapper(
                redis_client=self.redis_client,
                kafka_producer=self.kafka_producer,
                base_url=url
            )
        # To add other scrapers later, just add more conditions here
        else:
            raise ValueError(f"Le scraper pour le site '{site_name}' n'existe pas.")