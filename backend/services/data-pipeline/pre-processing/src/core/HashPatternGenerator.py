import hashlib

from core.HashGenerator import HashGenerator




class HashPatternGenerator(HashGenerator):
    """
    Génère un hash à partir d'un pattern d'attributs.
    
    Le pattern définit l'ordre des attributs à extraire et hacher.
    Exemple: pattern = "company_ref-job_ref-site"
    """
    
    def __init__(self, pattern: str = ''):
        """
        Args:
            pattern: Chaîne définissant les attributs séparés par '-'
                     Exemple: "company_ref-job_ref-site"
        """
        self.pattern = pattern
        # Liste des noms d'attributs dans l'ordre
        self.attributes = pattern.split('-')
    
  
      
    def setPattern(self, pattern: str):
        self.pattern = pattern
        self.attributes = pattern.split('-')
    def generate(self, data: dict) -> str:
        """
        Génère un hash selon le pattern.
        
        Args:
            data: Dictionnaire contenant les valeurs des attributs
                  Exemple: {'company_ref': 'mobvjcmp', 'job_ref': 'abc123', 'site': 'indeed'}
        
        Returns:
            Hash SHA256 des valeurs concaténées selon le pattern
        """
        # Extraire les valeurs dans l'ordre du pattern
        values = []
        for attr in self.attributes:
            value = data.get(attr, '')
            values.append(str(value))
        
        # Concaténer avec '-' comme dans le pattern
        combined = '-'.join(values)
        
        # Générer le hash
        return hashlib.sha256(combined.encode()).hexdigest()