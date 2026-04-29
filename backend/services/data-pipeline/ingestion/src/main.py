import time
from src.orchestrator.orchestrator import Orchestrator
from src.scheduler.scheduler import Scheduler 

if __name__ == "__main__":
    time.sleep(10)
    # ToAdd: Add it In .env
    targets = [
        {"site": "rekrute", "url": "https://www.rekrute.com/offres.html"}
    ]

    orchestrateur = Orchestrator()
    
    scheduler = Scheduler(
        orchestrator=orchestrateur
    )

    for target in targets:
        scheduler.schedule(site_name=target["site"], url=target["url"])