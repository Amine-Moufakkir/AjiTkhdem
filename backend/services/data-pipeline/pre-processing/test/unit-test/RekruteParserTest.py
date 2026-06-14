import sys
import os
import json
from unittest.mock import MagicMock

# Ajouter le chemin src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.RekruteParser import RekruteParser
from core.Cleaner import Cleaner
from dto.DataProcessingDTO import DataProcessingDTO
from core.HashPatternGenerator import HashPatternGenerator

def main():
    # Chemin du fichier HTML de test
    test_file = os.path.join(os.path.dirname(__file__), 'test_rekrute.html')
    
    if not os.path.exists(test_file):
        print(f"❌ Erreur: Fichier {test_file} non trouvé.")
        sys.exit(1)
    
    # Lire le fichier HTML brut
    with open(test_file, 'r', encoding='utf-8') as f:
        html_brut = f.read()
    
    print("=" * 80)
    print("TEST EXTRACTION REKRUTE PARSER")
    print("=" * 80)
    
    # Étape 1: Nettoyage
    print("\n📋 Étape 1: Nettoyage du HTML...")
    cleaner = Cleaner()
    
    test_url = "https://www.rekrute.com/offre-emploi-ingenieur-devops-senior-fh-recrutement-sofrecom-maroc-rabat-182541.html"
    
    html_clean = DataProcessingDTO(
        html=cleaner.clean(html_brut), 
        url=test_url
    )
    
    print(f"✓ HTML nettoyé ({len(html_clean.html)} caractères)")
    
    # Étape 2: Extraction
    print("\n📋 Étape 2: Extraction des données...")
    try:
        mock_hash_gen = HashPatternGenerator()
        mock_db = MagicMock()
        
        parser = RekruteParser(mock_hash_gen, mock_db)
        extracted_dto = parser.extract(html_clean)
        print("✓ Extraction terminée")
        
        # Étape 3: Affichage
        print("\n📋 Résultats de l'extraction:")
        print("-" * 80)
        donnees = extracted_dto.to_dict()
        print(json.dumps(donnees, ensure_ascii=False, indent=2, default=str))
        print("-" * 80)
        
        print("\n✅ Test terminé avec succès")
        
    except Exception as e:
        print(f"\n❌ Erreur pendant l'extraction : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
