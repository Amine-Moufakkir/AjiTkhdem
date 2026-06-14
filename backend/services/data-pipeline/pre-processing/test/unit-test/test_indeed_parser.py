import os
import json
import pytest
from unittest.mock import MagicMock
from services.IndeedParser import IndeedParser
from core.Cleaner import Cleaner
from dto.DataProcessingDTO import DataProcessingDTO
from core.HashPatternGenerator import HashPatternGenerator


def test_indeed_parser_extraction():
    """Test extraction Indeed Parser"""
    # Chemin du fichier HTML de test
    test_file = os.path.join(os.path.dirname(__file__), 'test.html')
    
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    
    # Lire le fichier HTML brut
    with open(test_file, 'r', encoding='utf-8') as f:
        html_brut = f.read()
    
    # Étape 1: Nettoyage
    cleaner = Cleaner()
    html_clean = DataProcessingDTO(
        html=cleaner.clean(html_brut), 
        url="https://ma.indeed.com/?r=us&vjk=0a5d0000df3de9f4"
    )
    assert len(html_clean.html) > 0, "Cleaned HTML should not be empty"
    
    # Étape 2: Extraction
    mock_db = MagicMock()
    hash_gen = HashPatternGenerator()
    parser = IndeedParser(hash_gen, mock_db)
    extracted_dto = parser.extract(html_clean)
    
    # Étape 3: Verify
    assert extracted_dto is not None, "Extraction should return a DTO"
    donnees = extracted_dto.to_dict()
    assert isinstance(donnees, dict), "Result should be a dictionary"
