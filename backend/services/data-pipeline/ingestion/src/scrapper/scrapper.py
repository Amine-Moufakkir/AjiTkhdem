from abc import ABC, abstractmethod
import redis
from confluent_kafka import Producer
from bs4 import BeautifulSoup
import logging
from typing import List, Optional
import random
import json

from utility import get_request
from orchestrator.context import ScrapingContext

class AbstractScrapper(ABC):
    def __init__(self, context: Optional[ScrapingContext] = None):
        self._context = context

    @property
    def context(self) -> Optional[ScrapingContext]:
        return self._context

    @context.setter
    def context(self, value: ScrapingContext):
        
        self._context = value

    @abstractmethod
    def scrape(self):
        pass
