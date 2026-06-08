import asyncio
import logging
import sys
import os

# Ajout du chemin src au PYTHONPATH pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kafka.Kafka import Kafka
from core.Route import Route
from config.db import AsyncSessionLocal

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Main")



async def main():
    """
    Fonction principale du service de normalisation.
    """
    logger.info("Démarrage du service de normalisation...")

    # Configuration Kafka
    # Ces valeurs pourraient être extraites des variables d'environnement
    TOPIC_INPUT = "normalisation"
    TOPIC_OUTPUT = "normalized_jobs"
    BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

    # Instanciation de Kafka
    kafka_service = Kafka(
        topic_output=TOPIC_OUTPUT,
        topics_inputs=[TOPIC_INPUT],
        bootstrap_servers=BOOTSTRAP_SERVERS
    )

    try:
        # Connexion au broker
        kafka_service.connect()
    except Exception as e:
        logger.error(f"Impossible de se connecter à Kafka : {e}")
        return

    logger.info(f"Service prêt. Écoute du topic : {TOPIC_INPUT}")

    try:
        # Kafka.listen() est un générateur synchrone
        # On boucle dessus pour traiter les messages un par un
        for message in kafka_service.listen():
            data = message["data"]
            topic = message["topic"]
            headers = message["headers"]

            logger.info(f"Message reçu du topic : {topic}")

            #! a Supprimer durant la production 
            print ("Le data est : ", data)

            # Création d'une session de base de données pour chaque message
            async with AsyncSessionLocal() as session:
                route = Route(session)
                try:
                    # Exécution du pipeline de normalisation
                    # normalise_pipeline gère la normalisation, l'extraction et l'insertion
                    await route.normalise_pipeline(data)
                    
                    # Validation des changements en base de données
                    await session.commit()
                    logger.info("Pipeline exécuté avec succès et données persistées.")

                    # Envoi du succès vers le topic de sortie (si nécessaire)
                    # Ici on renvoie les données originales ou on pourrait renvoyer le résultat
                   

                except Exception as e:
                    # En cas d'erreur, on annule les changements en base
                    await session.rollback()
                    logger.error(f"Erreur lors du traitement du message : {e}")
                    
                    # Gestion de l'échec via Kafka (retry ou DLQ)
                    kafka_service.handle_process_failure(topic, data, headers, e)
                
                finally:
                    # La session est fermée automatiquement par le 'async with'
                    pass

    except KeyboardInterrupt:
        logger.info("Arrêt du service demandé par l'utilisateur.")
    except Exception as e:
        logger.error(f"Erreur fatale du service : {e}")
    finally:
        kafka_service.close()
        logger.info("Service arrêté proprement.")

if __name__ == "__main__":
    # Lancement de la boucle d'événements asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
