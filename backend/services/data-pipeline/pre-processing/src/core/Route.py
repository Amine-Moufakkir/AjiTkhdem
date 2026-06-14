from config.MongoConnection import MongoConnection
from dto.DataProcessingDTO import DataProcessingDTO
from dto.JobScrapeDTO import JobScrapeDTO
from kafka_utils.kafka import Kafka
from services.ParserFactory import ParserFactory
import asyncio
import json


class Route:
    
    def __init__(self, kafka: Kafka, parser_factory: ParserFactory, output_topic: str ):
        """
        Initialise la Route avec les dépendances nécessaires.
        
        Args:
            kafka: Instance Kafka pour consommer et produire les messages
            parser_factory: Factory pour créer les parsers appropriés
            output_topic: Topic Kafka où envoyer les résultats traités
        """
        self.kafka = kafka
        self.parser_factory = parser_factory
       
        
        
    async def main(self, input_topic: str):
        """
        Fonction principale qui écoute un topic Kafka, traite les données 
        avec le scrapper et envoie les résultats.
        
        JobScrapeDTO(kafka[pre-processing service]) -> DataProcessingDTO(pipline) -> JobCleanedDTO(kafka[normalization_service])
        Args:
            input_topic: Topic Kafka à écouter
        """
        try:
            
            print("🔍 Test de connexion Kafka et MongoDB en cours...")

            await self.test_kafka_connection()
            if self.parser_factory is None:
                raise ValueError("ParserFactory manquant")
            connection = self.parser_factory.getMongoDb().getMongoConnection()
            await self.test_mongodb_connection(connection)


            print(f"🚀 Démarrage de la Route - Écoute du topic: {input_topic}")
            self.kafka.connect()
                
            for message in self.kafka.listen():
                try:
                    jobScrapeDTO = JobScrapeDTO(message)
                    
                    print(f"📨 Message reçu du topic '{jobScrapeDTO.topic}'")
                    
                    # Récupérer le type de parser depuis les données ou headers
                    
                    if jobScrapeDTO.parser_type  is None:
                        raise ValueError("Type de parser manquant dans les données")
                    
                    
                    if jobScrapeDTO.html is None:
                        raise ValueError("HTML manquant dans les données")
                    
                    
                    # Construire le parser avec la factory
                    parser = self.parser_factory.build_parser(jobScrapeDTO.parser_type)
                    
                    # Traiter les données avec le scrapper
                    print(f"⚙️ Traitement avec le parser: {jobScrapeDTO.parser_type}")

                    dataProcessingDTo = DataProcessingDTO(jobScrapeDTO.html, jobScrapeDTO.url)
                    
                    result = await parser.pipeline(dataProcessingDTo)
                    
                    if result:
                        
                        self.kafka.send_on_succes( result.to_dict(), [])
                        
                    else:
                        print(f"⚠️ Aucun résultat à envoyer (doublon détecté)")



                        
                except ValueError as e:
                    print(f"❌ Erreur - Type de parser invalide: {e}")
                    #! Doit etre journaliser
                    self.kafka.handle_process_failure(message["topic"], message["data"], message["headers"], e)
                    
                    #! Doit etre journaliser 
                    
                except RuntimeError as e:
                    print(f"❌ Erreur runtime lors du traitement: {e}")
                    #! Doit etre journaliser
                    self.kafka.handle_process_failure(message["topic"], message["data"], message["headers"], e)

                    
                except Exception as e:
                    print(f"❌ Erreur inattendue lors du traitement: {e}")
                    #! Doit etre journaliser
                    self.kafka.handle_process_failure(message["topic"], message["data"], message["headers"], e)



        
                    
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"❌ Erreur critique dans la Route: {e}")
        finally:
            self.kafka.close()
            print("🔌 Connexion Kafka fermée")
        
         
    async def test_kafka_connection(self) -> bool:
        """
        Teste la connexion au broker Kafka.
        
        Returns:
            True si la connexion est réussie, False sinon
        """
        try:
            print("🔍 Test de connexion Kafka en cours...")
            self.kafka.connect()
            
            # Essayer d'envoyer un message de test
            test_message = {"test": "connection", "timestamp": str(__import__('datetime').datetime.now())}
            future = self.kafka.send_on_succes(test_message, [])
            
            # Attendre la confirmation
            record_metadata = future.get(timeout=10)
            
            print(f"✅ Connexion Kafka réussie !")
            print(f"   Topic: {record_metadata.topic}")
            print(f"   Partition: {record_metadata.partition}")
            print(f"   Offset: {record_metadata.offset}")
            
            self.kafka.close()
            return True
            
        except Exception as e:
            raise Exception(f"❌ Erreur lors du test de connexion Kafka: {e}") 
    
    async def test_mongodb_connection(self, mongo_connection) -> bool:
        """
        Teste la connexion à MongoDB.
        
        Args:
            mongo_connection: Instance de MongoConnection à tester
            
        Returns:
            True si la connexion est réussie, False sinon
        """
        try:
            print("🔍 Test de connexion MongoDB en cours...")
            
            # Établir la connexion
            await mongo_connection.connect()
            
            # Essayer d'accéder à une collection de test
            test_collection = mongo_connection.get_collection("test_connection")
            
            # Insérer un document de test
            test_doc = {
                "test": "connection",
                "timestamp": __import__('datetime').datetime.now()
            }
            result = await test_collection.insert_one(test_doc)
            
            print(f"✅ Connexion MongoDB réussie !")
            print(f"   Document inséré avec l'ID: {result.inserted_id}")
            
            # Vérifier que le document a bien été inséré
            found_doc = await test_collection.find_one({"_id": result.inserted_id})
            if found_doc:
                print(f"   Document récupéré avec succès")
            
            # Nettoyer le document de test
            await test_collection.delete_one({"_id": result.inserted_id})
            print(f"   Document de test supprimé")
            
            # Fermer la connexion
            await mongo_connection.close()
            
            return True
            
        except Exception as e:
            raise Exception(f"❌ Erreur lors du test de connexion MongoDB: {e}")
            


