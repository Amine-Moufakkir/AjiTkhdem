from fastapi import FastAPI
import time
# pattern: from src.folder_name.file_name import ClassName

from src.orchestrator.orchestrator import Orchestrator
from src.scheduler.scheduler import Scheduler 

app = FastAPI(title="AjiTkhdem - IngestionService")

if __name__ == "__main__":
    time.sleep(10)
    # Target sites to scrape
    targets = [
        {"site": "rekrute", "url": "https://www.rekrute.com/offres.html"}
    ]

    orchestrateur = Orchestrator()
    
    # Pass the lists to the Scheduler
    scheduler = Scheduler(
        orchestrator=orchestrateur
    )

    # Run them one by one
    for target in targets:
        scheduler.schedule(site_name=target["site"], url=target["url"])