import os
import pytest
from core.Cleaner import Cleaner


def test_clean_html():
    """Test 1 : Prendre le contenu de page.html et le nettoyer"""
    
    # Vérifier si le fichier test.html existe dans le même dossier
    test_file = os.path.join(os.path.dirname(__file__), 'test.html')
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    
    # Lire le fichier test.html
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Nettoyer le contenu
    cleaner = Cleaner()
    cleaned_content = cleaner.clean(content)
    
    # Sauvegarder le résultat dans clean1.html dans le même dossier
    output_file = os.path.join(os.path.dirname(__file__), 'clean1.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    assert os.path.exists(output_file), "Output file should be created"
    assert len(cleaned_content) > 0, "Cleaned content should not be empty"


def test_clean_rekrute_file():
    """Test 2 : Prendre le contenu de test_rekrute.html et le nettoyer"""
    
    # Vérifier si le fichier test_rekrute.html existe
    test_file = os.path.join(os.path.dirname(__file__), 'test_rekrute.html')
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    
    # Lire le fichier
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Nettoyer le contenu
    cleaner = Cleaner()
    cleaned_content = cleaner.clean(content)
    
    # Sauvegarder le résultat
    output_file = os.path.join(os.path.dirname(__file__), 'clean2.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    assert os.path.exists(output_file), "Output file should be created"
    assert len(cleaned_content) > 0, "Cleaned content should not be empty"
