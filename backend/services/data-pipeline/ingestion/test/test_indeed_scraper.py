import pytest
import asyncio
import redis
import os
from scrapper.IndeedScraper import IndeedScraper
from orchestrator.orchestrator import IndeedRedisWrapper
from orchestrator.context import ContextGenerator

@pytest.mark.asyncio
async def test_indeed_scraper_scrape():
    # Setup
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Clear Redis as requested
    redis_client.flushdb()
    
    redis_service = IndeedRedisWrapper(redis_client)
    context_gen = ContextGenerator()
    context = context_gen.generate()
    
    scraper = IndeedScraper(
        redis_service=redis_service,
        headless=True,
        min_delay=1.0,
        max_delay=2.0,
        context=context,
        use_proxy=False # Disable proxy for testing unless required
    )
    
    search_url = "https://ma.indeed.com/jobs?q=developpeur&l=Casablanca"
    
    # Execute
    result = await scraper.scrape(search_url)
    
    # Verify
    assert result is not None
    assert "id_jobs" in result
    assert "html_jobs" in result
    assert isinstance(result["id_jobs"], list)
    assert isinstance(result["html_jobs"], list)
    
    # If jobs were found, they should be in Redis now
    if result["id_jobs"]:
        for job_id in result["id_jobs"]:
            assert redis_client.exists(f"indeed:seen:{job_id}")
