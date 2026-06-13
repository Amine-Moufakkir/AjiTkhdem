
from scrapper.scrapper import AbstractScrapper


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

class RekruteScrapper(AbstractScrapper):
    MAX_PAGES = 2 #ToChange: changin in production

    def __init__(self, redis_client: redis.Redis, kafka_producer: Producer, base_url: str, context: Optional[ScrapingContext] = None, use_proxy: bool = True, useProxy: bool | None = None):
        super().__init__(context=context, use_proxy=use_proxy, useProxy=useProxy)
        self.redis = redis_client
        self.producer = kafka_producer
        self.base_url = base_url
        #ToAdd: Add to .env
        self.topic = "raw_jobs"
        self.CACHE_TTL = 48 * 60 * 60 

    def _extract_job_links(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'html.parser')
        #ToAdd: Add to .env
        links = [a['href'] for a in soup.select('a.titreJob')] #TODO: Use rekrut CSS specifier
        return [f"https://www.rekrute.com{link}" for link in links] #Use rekrute link

    def scrape(self) -> None:
        # Initialize the Pagination Sequence
        for page in range(1, self.MAX_PAGES + 1):
            page_url = f"{self.base_url}?s=3&p={page}&o=1"
            
            # SRetrieve and Extract the Search Page
            current_proxy = self.context.proxy if self.use_proxy and self.context else None
            current_ua = self.context.user_agent if self.context else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            
            search_html = get_request(
                url=page_url, 
                proxy=current_proxy, 
                user_agent=current_ua
            )
            if not search_html:
                logging.warning(f"Failed to fetch page {page}. Skipping.")
                continue
            #ToRemove: For Dev Mode
            print(f"Page HTML fetched SUCCEFULLY {page}")
            job_links = self._extract_job_links(search_html)

            #Check for Empty Page
            if not job_links:
                print(f"No jobs found on page {page}. Stopping scraping run.")
                break

            #If All Jobs are Cachecd
            already_seen_count = 0
            for link in job_links:
                if self.redis.exists(f"rekrut:seen:{link}"):
                    already_seen_count += 1
            
            if already_seen_count == len(job_links):
                #ToRemove: For Dev Mode
                print(f"All {len(job_links)} jobs on page {page} are already cached. Caught up to history. Stopping.")
                break

            #Upload Jobs
            for link in job_links:
                #Skiping Cacked Jobs
                if self.redis.exists(f"rekrut:seen:{link}"):
                    continue

                #Fetch New Jobs
                #ToRemove: For Dev Mode
                print(f"Fetching new job: {link}")
                job_html = get_request(
                    url=link, 
                    proxy=current_proxy, 
                    user_agent=current_ua
                )
                if not job_html:
                    #ToRemove: For Dev Mode
                    logging.warning(f"Failed to fetch job HTML {link}. Skipping.")
                    continue
                #ToRemove: For Dev Mode
                print(f"Job HTML Ftech SECSSFULLY {link}")

                #Adding to Kafka queue and Redis cache
                try:
                    #Push to Kafka queue
                    payload = json.dumps({"source": "rekrut", "url": link, "html": job_html})
                    self.producer.produce(self.topic, key=link, value=payload)
                    #ToRemove: For Dev Mode
                    print(f"Adding Job to Kafka: {link}")
                    
                    #Push to Redis cache
                    self.redis.setex(f"rekrut:seen:{link}", self.CACHE_TTL, "1")
                    #ToRemove: For Dev Mode
                    print(f"Adding Job Link to Redis: {link}")
                    
                except Exception as e:
                    logging.error(f"Failed to process {link} to Kafka/Redis: {e}")

            #Flush Kafka Memory
            self.producer.flush()
        #ToRemove: For Dev Mode
        print("Scraping run completed successfully.")