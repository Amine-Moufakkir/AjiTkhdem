import asyncio
import os
from dotenv import load_dotenv

from config.MongoConnection import MongoConnection
from kafka_utils.kafka import Kafka
from services.ParserFactory import ParserFactory
from core.Route import Route
from models.db import MongoDB


load_dotenv()


async def main():
    """
    Fonction principale qui initialise toutes les dépendances
    et lance la Route pour traiter les messages Kafka.
    """
    
    # ============================================================
    # 1. INITIALISER MONGODB
    # ============================================================
    try:
        print("📦 Initialisation de MongoDB...")
        mongo_connection = MongoConnection()
        await mongo_connection.connect()
        
        db = MongoDB(mongo_connection, collection_name="raw_data")
        print("✅ MongoDB initialisé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation MongoDB : {e}")
        return
    
    
    # ============================================================
    # 2. INITIALISER PARSER FACTORY
    # ============================================================
    try:
        print("\n🏭 Initialisation de la ParserFactory...")
        parser_factory = ParserFactory(db)
        print("✅ ParserFactory initialisée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation ParserFactory : {e}")
        await mongo_connection.close()
        return
    
    
    # ============================================================
    # 3. INITIALISER KAFKA
    # ============================================================
    try:
        print("\n📡 Initialisation de Kafka...")
        
        # Récupérer les variables d'environnement
        kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        input_topics = os.getenv("KAFKA_INPUT_TOPICS", "raw_jobs").split(",")
        output_topic = os.getenv("KAFKA_OUTPUT_TOPIC", "processed_jobs")
        max_retries = int(os.getenv("KAFKA_MAX_RETRIES", "5"))
        
        kafka = Kafka(
            topic_output=output_topic,
            topics_inputs=input_topics,
            bootstrap_servers=kafka_bootstrap,
            max_retries=max_retries
        )
        
        kafka.connect()
        print("✅ Kafka initialisé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation Kafka : {e}")
        await mongo_connection.close()
        return
    
    
    # ============================================================
    # 4. CRÉER LA ROUTE
    # ============================================================
    try:
        print("\n🛣️ Création de la Route...")
        route = Route(
            kafka=kafka,
            parser_factory=parser_factory,
            output_topic=output_topic
        )
        print("✅ Route créée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la Route : {e}")
        await mongo_connection.close()
        kafka.close()
        return
    
    
    # ============================================================
    # 5. LANCER LA ROUTE
    # ============================================================
    try:
        print("\n🚀 Démarrage du pipeline de traitement...")
        print("=" * 60)
        
        # Utiliser le premier topic d'entrée
        input_topic = input_topics[0] if input_topics else "raw_jobs"
        
        await route.main(input_topic=input_topic)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du pipeline")
    except Exception as e:
        print(f"\n❌ Erreur critique : {e}")
    finally:
        print("\n🧹 Nettoyage des ressources...")
        kafka.close()
        await mongo_connection.close()
        print("✅ Ressources fermées")


if __name__ == "__main__":
    asyncio.run(main())
