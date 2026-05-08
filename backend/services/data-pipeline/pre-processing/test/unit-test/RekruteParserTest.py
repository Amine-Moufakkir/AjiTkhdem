import sys
import os
import json
from unittest.mock import MagicMock

# Ajouter le chemin src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.RekruteParser import RekruteParser
from core.Cleaner import Cleaner

# Note: Depending on your exact architecture, if RekruteParser requires 
# HashPatternGenerator and MongoDB in its constructor, you can import them 
# and pass them here, or use mock objects if you strictly want to test offline.
# Example: parser = RekruteParser(mock_hash_gen, mock_db) 
# Here we assume it instantiates just like IndeedParser()

def main():
    # Chemin du fichier HTML de test
    test_file = os.path.join(os.path.dirname(__file__), 'test_rekrute.html')
    
    if not os.path.exists(test_file):
        print(f"❌ Erreur: Fichier {test_file} non trouvé.")
        print("Assurez-vous d'avoir sauvegardé le code source de l'offre dans ce fichier.")
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
    
    # On utilise l'URL exacte de test pour vérifier l'extraction du Regex (job_ref)
    # On utilise l'URL exacte de test pour vérifier l'extraction du Regex (job_ref)
    test_url = "https://www.rekrute.com/offre-emploi-ingenieur-devops-senior-fh-recrutement-sofrecom-maroc-rabat-182541.html"
    
    html_clean = {
        "html": cleaner.clean(html_brut), 
        "url": test_url
    }
    
    print(f"✓ HTML nettoyé ({len(html_clean['html'])} caractères)")
    
    # Étape 2: Extraction
    print("\n📋 Étape 2: Extraction des données...")
    try:
        # Instanciation du parser (ajoutez les arguments ici si votre architecture l'exige)
        mock_hash_gen = MagicMock()
        mock_db = MagicMock()
        
        # Pass the fake objects into the constructor
        parser = RekruteParser(mock_hash_gen, mock_db)
        donnees = parser.extract(html_clean)
        print("✓ Extraction terminée")
        
        # Étape 3: Affichage
        print("\n📋 Résultats de l'extraction:")
        print("-" * 80)
        print(json.dumps(donnees, ensure_ascii=False, indent=2))
        print("-" * 80)
        
        print("\n✅ Test terminé avec succès")
        
    except Exception as e:
        print(f"\n❌ Erreur pendant l'extraction : {e}")

if __name__ == "__main__":
    main()