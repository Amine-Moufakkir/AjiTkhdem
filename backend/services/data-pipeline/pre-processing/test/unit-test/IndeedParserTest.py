import sys
import os
import json

# Ajouter le chemin src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from services.IndeedParser import IndeedParser
from core.Cleaner import Cleaner


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
    html_clean = {
                "html":cleaner.clean(html_brut) , 
                "url":"https://ma.indeed.com/?r=us&vjk=0a5d0000df3de9f4"
                  }
    print(f"✓ HTML nettoyé ({len(html_clean)} caractères)")
    
    # Étape 2: Extraction
    print("\n📋 Étape 2: Extraction des données...")
    parser = IndeedParser()
    donnees = parser.extract(html_clean)
    print("✓ Extraction terminée")
    
    # Étape 3: Affichage
    print("\n📋 Résultats de l'extraction:")
    print("-" * 80)
    print(json.dumps(donnees, ensure_ascii=False, indent=2))
    print("-" * 80)
    
    print("\n✅ Test terminé avec succès")


if __name__ == "__main__":
    main()
