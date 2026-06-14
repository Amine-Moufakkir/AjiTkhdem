# Resultat du Test - Prompt 2

```
============================= test session starts ==============================
platform linux -- Python 3.14.5, pytest-9.1.0, pluggy-1.6.0
rootdir: /home/oss/Projects/Presistent/ProjectEnovation/AjiTkhdem/backend/services/data-pipeline/ingestion
plugins: anyio-4.13.0, base-url-2.1.0, asyncio-1.4.0, playwright-0.8.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 2 items

test/test_rekrute_scraper.py .                                           [ 50%]
test/test_indeed_scraper.py .                                            [100%]

=============================== warnings summary ===============================
test/test_indeed_scraper.py: 17 warnings
  /home/oss/Projects/Presistent/ProjectEnovation/AjiTkhdem/backend/services/data-pipeline/ingestion/src/scrapper/IndeedScraper.py:108: DeprecationWarning: 'asyncio.iscoroutinefunction' is deprecated and slated for removal in Python 3.16; use inspect.iscoroutinefunction() instead
    if asyncio.iscoroutinefunction(callback):

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 2 passed, 17 warnings in 95.06s (0:01:35) ===================
```
