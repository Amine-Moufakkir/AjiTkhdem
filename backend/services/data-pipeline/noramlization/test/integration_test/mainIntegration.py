import asyncio
import os
import sys
import time
from unittest.mock import MagicMock

# Ajuster le PYTHONPATH pour inclure src
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from kafka.Kafka import Kafka
import src.kafka.Kafka as kafka_module
from config.db import AsyncSessionLocal, engine
from models.base import Base, Job, Entreprise
from main import main
from sqlalchemy import select

class MockBroker:
    def __init__(self):
        self.messages = []

    def send(self, message, topic):
        print(f"[MockBroker] Sending message to topic {topic}")
        self.messages.append({
            "topic": topic,
            "data": message,
            "headers": []
        })

# Instanciation globale du broker pour le mock
mock_broker = MockBroker()

class MockKafka:
    def __init__(self, topic_output, topics_inputs, bootstrap_servers='kafka:9092'):
        self.topic_output = topic_output
        self.topics_inputs = topics_inputs
        self.bootstrap_servers = bootstrap_servers
        self.producer = MagicMock()
        self.consumer = MagicMock()

    def connect(self):
        print("[MockKafka] Connected to mock broker")

    def listen(self):
        print("[MockKafka] Listening for messages...")
        for message in mock_broker.messages:
            yield message
        print("[MockKafka] No more messages in mock broker.")

    def handle_process_failure(self, topic, data, headers, exception):
        print(f"[MockKafka] Handling failure for {topic}: {exception}")

    def close(self):
        print("[MockKafka] Closing connection")

# Monkeypatching the Kafka class in the module
kafka_module.Kafka = MockKafka

async def run_test():
    print("=== Démarrage du test d'intégration ===")

    # 1. Nettoyage et initialisation de la base de données (si nécessaire)
    # Pour ce test, on suppose que la DB est prête ou on peut créer les tables
    async with engine.begin() as conn:
        # Optionnel : Recréer les tables pour un test propre
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 2. Préparation du message de test
    test_data = {
        "job_title": "Software Engineer",
        "company_name": "Antigravity AI",
        "description": "We are looking for an AI agent expert.",
        "location": "San Francisco",
        "job_type": "Full-time",
        "salary": 150000,
        "source": "LinkedIn",
        "apply_url": "https://example.com/apply"
    }
    
    # 3. Utilisation du MockBroker pour envoyer le message
    mock_broker.send(test_data, "normalisation")

    # 4. Attente de 2 secondes
    print("Attente de 2 secondes...")
    await asyncio.sleep(2)

    # 5. Appel de la méthode main pour traiter le message
    # Comme on a mocké Kafka.listen(), main() s'arrêtera quand les messages seront consommés
    print("Appel de la méthode main()...")
    try:
        # On utilise asyncio.wait_for pour éviter un blocage infini si main() ne s'arrête pas
        await asyncio.wait_for(main(), timeout=10)
    except asyncio.TimeoutError:
        print("Fin du traitement (timeout atteint).")
    except Exception as e:
        print(f"Erreur durant l'exécution de main() : {e}")

    # 6. Vérification de la base de données
    print("Vérification de la base de données...")
    async with AsyncSessionLocal() as session:
        # Vérifier si l'entreprise a été créée
        result_ent = await session.execute(select(Entreprise).where(Entreprise.name == "Antigravity AI"))
        entreprise = result_ent.scalar_one_or_none()
        
        if entreprise:
            print(f"✓ Entreprise trouvée : {entreprise.name}")
        else:
            print("✗ Entreprise non trouvée.")
            return False

        # Vérifier si le job a été créé
        result_job = await session.execute(select(Job).where(Job.entreprise_id == entreprise.id))
        job = result_job.scalar_one_or_none()
        
        if job:
            print(f"✓ Job trouvé pour l'entreprise {entreprise.name}")
            print(f"  Description : {job.description[:30]}...")
            print(f"  Salaire : {job.salaire}")
        else:
            print("✗ Job non trouvé.")
            return False

    print("=== Test d'intégration réussi ! ===")
    return True

if __name__ == "__main__":
    success = asyncio.run(run_test())
    if not success:
        sys.exit(1)
