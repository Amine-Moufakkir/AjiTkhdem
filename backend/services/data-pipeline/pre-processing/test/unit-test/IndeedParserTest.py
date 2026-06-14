import sys
import os
import json
from unittest.mock import MagicMock

# Ajouter le chemin src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.IndeedParser import IndeedParser
from core.Cleaner import Cleaner
from dto.DataProcessingDTO import DataProcessingDTO
from core.HashPatternGenerator import HashPatternGenerator


def main():
    # Chemin du fichier HTML de test
    test_file = os.path.join(os.path.dirname(__file__), 'test.html')
    
    if not os.path.exists(test_file):
        print(f"❌ Erreur: Fichier {test_file} non trouvé")
        sys.exit(1)
    
    # Lire le fichier HTML brut
    with open(test_file, 'r', encoding='utf-8') as f:
        html_brut = f.read()
    
    print("=" * 80)
    print("TEST EXTRACTION INDEED PARSER")
    print("=" * 80)
    
    # Étape 1: Nettoyage
    print("\n📋 Étape 1: Nettoyage du HTML...")
    cleaner = Cleaner()
    html_clean = DataProcessingDTO(
        html=cleaner.clean(html_brut), 
        url="https://ma.indeed.com/?r=us&vjk=0a5d0000df3de9f4"
    )
    print(f"✓ HTML nettoyé ({len(html_clean.html)} caractères)")
    
    # Étape 2: Extraction
    print("\n📋 Étape 2: Extraction des données...")
    mock_db = MagicMock()
    hash_gen = HashPatternGenerator()
    parser = IndeedParser(hash_gen, mock_db)
    extracted_dto = parser.extract(html_clean)
    print("✓ Extraction terminée")
    
    # Étape 3: Affichage
    print("\n📋 Résultats de l'extraction:")
    print("-" * 80)
    # Convertir le DTO en dict pour l'affichage JSON
    donnees = extracted_dto.to_dict()
    print(json.dumps(donnees, ensure_ascii=False, indent=2, default=str))
    print("-" * 80)
    
    print("\n✅ Test terminé avec succès")


if __name__ == "__main__":
    main()
