import asyncio
import logging
import sys
import os

# Ajout du chemin src au PYTHONPATH pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kafka_client.KafkaClient import Kafka
from core.Route import Route
from config.db import AsyncSessionLocal

from fastapi import FastAPI
import uvicorn
from api.routes import router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Main")

app = FastAPI(title="Job Normalization & API Service")
app.include_router(router)

async def run_kafka_consumer():
    """
    Tâche asynchrone pour consommer les messages Kafka.
    """
    logger.info("Démarrage du consommateur Kafka...")
    
    TOPIC_INPUT = "normalisation"
    TOPIC_OUTPUT = "normalized_jobs"
    BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    kafka_service = Kafka(
        topic_output=TOPIC_OUTPUT,
        topics_inputs=[TOPIC_INPUT],
        bootstrap_servers=BOOTSTRAP_SERVERS
    )

    try:
        kafka_service.connect()
    except Exception as e:
        logger.error(f"Impossible de se connecter à Kafka : {e}")
        return

    logger.info(f"Consommateur prêt. Écoute du topic : {TOPIC_INPUT}")

    try:
        # On utilise loop.run_in_executor car listen() est synchrone et bloquant
        loop = asyncio.get_event_loop()
        
        def consume():
            for message in kafka_service.listen():
                data = message["data"]
                topic = message["topic"]
                headers = message["headers"]
                
                # On planifie le traitement asynchrone pour chaque message
                asyncio.run_coroutine_threadsafe(
                    process_message(data, topic, headers), 
                    loop
                )

        await loop.run_in_executor(None, consume)

    except Exception as e:
        logger.error(f"Erreur dans le consommateur Kafka : {e}")
    finally:
        kafka_service.close()

async def process_message(data, topic, headers):
    """Traite un message individuel de manière asynchrone."""
    async with AsyncSessionLocal() as session:
        route = Route(session)
        try:
            await route.normalise_pipeline(data)
            await session.commit()
            logger.info("Message traité et persisté avec succès.")
        except Exception as e:
            await session.rollback()
            logger.error(f"Erreur de traitement : {e}")
            # Note: Kafka handle_process_failure pourrait nécessiter d'être asynchrone 
            # ou appelé via executor si bloquant.

async def main():
    """
    Point d'entrée principal lançant l'API et le consommateur Kafka.
    """
    logger.info("Lancement du service hybride (API + Kafka)...")
    
    # Configuration du serveur API
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # Exécution simultanée
    await asyncio.gather(
        server.serve(),
        run_kafka_consumer()
    )

if __name__ == "__main__":
    # Lancement de la boucle d'événements asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
