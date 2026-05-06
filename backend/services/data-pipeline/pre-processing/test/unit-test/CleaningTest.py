import re
import os

from src.core.Cleaner import Cleaner


def test_clean_html():
    """Test 1 : Prendre le contenu de page.html et le nettoyer"""
    
    # Vérifier si le fichier page.html existe
    if not os.path.exists('./test/test.html'):
        print("✗ Erreur : Le fichier page.html n'existe pas !")
        return
    
    # Lire le fichier page.html
    with open('./test/test.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("✓ Fichier page.html lu avec succès")
    
    # Nettoyer le contenu
    cleaner = Cleaner()
    cleaned_content = cleaner.clean(content)
    
    # Sauvegarder le résultat dans clean1.html
    output_file = './test/clean1.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✓ Nettoyage effectué et sauvegardé dans {output_file}")
    print("\nContenu nettoyé :")
    print("-" * 50)
    print(cleaned_content)
    print("-" * 50)


def test_clean_external_file():
    """Test 2 : Prendre le contenu de test.html et le nettoyer"""
    
    # Vérifier si le fichier test.html existe
    if not os.path.exists('./test/unit-test/test.html'):
        print("✗ Erreur : Le fichier test.html n'existe pas !")
        return
    
    # Lire le fichier test.html
    with open('./test/unit-test/test.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("✓ Fichier test.html lu avec succès")
    
    # Nettoyer le contenu
    cleaner = Cleaner()
    cleaned_content = cleaner.clean(content)
    
    # Sauvegarder le résultat dans clean2.html
    output_file = './test/unit-test/clean2.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✓ Nettoyage effectué et sauvegardé dans {output_file}")
    print("\nContenu original de test.html :")
    print("-" * 50)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("\nContenu nettoyé :")
    print("-" * 50)
    print(cleaned_content[:500] + "..." if len(cleaned_content) > 500 else cleaned_content)
    print("-" * 50)


def main():
    """Fonction principale pour exécuter les deux tests"""
    
    print("=" * 60)
    print("TEST 1 : Nettoyage de page.html → clean1.html")
    print("=" * 60)
    test_clean_html()
    
    print("\n" + "=" * 60)
    print("TEST 2 : Nettoyage de test.html → clean2.html")
    print("=" * 60)
    test_clean_external_file()
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES FICHIERS :")
    print("=" * 60)
    
    fichiers = ['page.html', 'clean1.html', 'test.html', 'clean2.html']
    for fichier in fichiers:
        if os.path.exists(fichier):
            with open(fichier, 'r', encoding='utf-8') as f:
                taille = len(f.read())
            print(f"✓ {fichier} ({taille} caractères)")
        else:
            print(f"✗ {fichier} (non trouvé - doit être créé manuellement)")


if __name__ == "__main__":
    main()