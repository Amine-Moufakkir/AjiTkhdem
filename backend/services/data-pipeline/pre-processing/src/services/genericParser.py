
from abc import ABC, abstractmethod

from core.HashGenerator import HashGenerator
from core.Cleaner import Cleaner

# --- Classes définies à l'extérieur (Ailleurs) ---


class GenericParser(ABC):
    def __init__(self):
        # On instancie les classes définies ailleurs
        self.cleaner = Cleaner()
        self.hash_generator = HashGenerator()



    def __extract(self, raw_data: str) -> str:
        """Méthode privée d'extraction."""
        # Logique simulée : on pourrait imaginer une extraction de JSON ou RegEx ici
        return raw_data

    def pipeline(self, data: str):
        """Méthode publique : le chef d'orchestre."""
        # 1. Extraction (Privée)
        extracted = self.__extract(data)
        
        # 2. Nettoyage
        cleaned = self.cleaner.clean(extracted)
        
        # 3. Hachage
        data_id = self.hash_generator.generate(cleaned)
        
        # 4. Traitement final (Abstrait)
        # return self.process(data_id, cleaned)




#     @abstractmethod
#     def process(self, data_id: str, data: str):
#         """À implémenter dans les classes filles (ex: KafkaPublisher)."""
#         pass

# # --- Implémentation concrète ---

# class KafkaParser(GenericParser):
#     def process(self, data_id: str, data: str):
#         print(f"DEBUG: Envoi vers Kafka...")
#         print(f"ID: {data_id} | Payload: {data}")

# # Test
# if __name__ == "__main__":
#     p = KafkaParser()
#     p.pipeline("   donnée brute de kafka   ")