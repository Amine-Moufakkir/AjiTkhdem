

import hashlib




class HashGenerator:
    """S'occupe uniquement de la génération d'empreintes numériques."""
    def generate(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()
