from abc import ABC, abstractmethod
import redis
from confluent_kafka import Producer
from bs4 import BeautifulSoup
import logging
from typing import List
import random
import json

from src.utility import get_request

class AbstractScrapper(ABC):
    #ToAdd: Add to .env
    proxies = [
        {"http": "http://192.168.1.1:8080", "https": "http://192.168.1.1:8080"},
        {"http": "http://10.0.0.5:8080", "https": "http://10.0.0.5:8080"}
    ]
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
    ]

    def get_random_proxy(self) -> dict:
        return random.choice(self.proxies)

    def get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)

    @abstractmethod
    def scrape(self):
        pass
