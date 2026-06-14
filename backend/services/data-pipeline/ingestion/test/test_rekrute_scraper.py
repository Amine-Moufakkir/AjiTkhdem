import pytest
import redis
from unittest.mock import MagicMock
from scrapper.RekruteScrapper import RekruteScrapper
from orchestrator.context import ContextGenerator

def test_rekrute_scraper_scrape():
    # Setup
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Clear Redis as requested
    redis_client.flushdb()
    
    # Mock Kafka Producer
    mock_producer = MagicMock()
    
    context_gen = ContextGenerator()
    context = context_gen.generate()
    
    base_url = "https://www.rekrute.com/offres.html"
    
    scraper = RekruteScrapper(
        redis_client=redis_client,
        kafka_producer=mock_producer,
        base_url=base_url,
        context=context,
        use_proxy=False
    )
    
    # Execute
    # RekruteScrapper.scrape() is synchronous and returns None
    # but the prompt says "verifier si le retourne et None ou non"
    # Wait, RekruteScrapper.scrape() doesn't return anything (None).
    # Let me check the code again.
    
    scraper.scrape()
    
    # Verification: Check if some keys were added to Redis
    # or if the producer was called.
    # We can't easily verify the return if it's always None.
    # However, I'll follow the prompt's logic if possible.
    # The prompt says: "verifier si le retourne et None ou non"
    
    # Let's check if we have any "rekrut:seen:*" keys in Redis
    keys = redis_client.keys("rekrut:seen:*")
    assert len(keys) > 0
    assert mock_producer.produce.called
