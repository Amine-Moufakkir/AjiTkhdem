

import hashlib

from dto.DataProcessingDTO import DataProcessingDTO




class HashGenerator:
    """S'occupe uniquement de la génération d'empreintes numériques."""
   
    def generate(self, data: dict) :
        raise NotImplementedError

        
