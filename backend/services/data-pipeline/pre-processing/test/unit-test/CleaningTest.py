import re
import os
import sys

# Ajouter le chemin src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.Cleaner import Cleaner


def test_clean_html():
    """Test 1 : Prendre le contenu de page.html et le nettoyer"""
    
    # Vérifier si le fichier test.html existe dans le même dossier
    test_file = os.path.join(os.path.dirname(__file__), 'test.html')
    if not os.path.exists(test_file):
        print(f"✗ Erreur : Le fichier {test_file} n'existe pas !")
        return
    
    # Lire le fichier test.html
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ Fichier {test_file} lu avec succès")
    
    # Nettoyer le contenu
    cleaner = Cleaner()
    cleaned_content = cleaner.clean(content)
    
    # Sauvegarder le résultat dans clean1.html dans le même dossier
    output_file = os.path.join(os.path.dirname(__file__), 'clean1.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✓ Nettoyage effectué et sauvegardé dans {output_file}")


def test_clean_rekrute_file():
    """Test 2 : Prendre le contenu de test_rekrute.html et le nettoyer"""
    
    # Vérifier si le fichier test_rekrute.html existe
    test_file = os.path.join(os.path.dirname(__file__), 'test_rekrute.html')
    if not os.path.exists(test_file):
        print(f"✗ Erreur : Le fichier {test_file} n'existe pas !")
        return
    
    # Lire le fichier
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ Fichier {test_file} lu avec succès")
    
    # Nettoyer le contenu
    cleaner = Cleaner()
    cleaned_content = cleaner.clean(content)
    
    # Sauvegarder le résultat
    output_file = os.path.join(os.path.dirname(__file__), 'clean2.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✓ Nettoyage effectué et sauvegardé dans {output_file}")


def main():
    """Fonction principale pour exécuter les deux tests"""
    
    print("=" * 60)
    print("TEST 1 : Nettoyage de test.html → clean1.html")
    print("=" * 60)
    test_clean_html()
    
    print("\n" + "=" * 60)
    print("TEST 2 : Nettoyage de test_rekrute.html → clean2.html")
    print("=" * 60)
    test_clean_rekrute_file()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES FICHIERS :")
    print("=" * 60)
    
    base_dir = os.path.dirname(__file__)
    fichiers = ['test.html', 'clean1.html', 'test_rekrute.html', 'clean2.html']
    for nom in fichiers:
        chemin = os.path.join(base_dir, nom)
        if os.path.exists(chemin):
            with open(chemin, 'r', encoding='utf-8') as f:
                taille = len(f.read())
            print(f"✓ {nom} ({taille} caractères)")
        else:
            print(f"✗ {nom} (non trouvé)")


if __name__ == "__main__":
    main()
