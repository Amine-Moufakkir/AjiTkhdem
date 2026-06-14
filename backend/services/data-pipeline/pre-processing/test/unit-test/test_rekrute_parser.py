import os
import json
import pytest
from unittest.mock import MagicMock
from services.RekruteParser import RekruteParser
from core.Cleaner import Cleaner
from dto.DataProcessingDTO import DataProcessingDTO
from core.HashPatternGenerator import HashPatternGenerator


def test_rekrute_parser_extraction():
    """Test extraction Rekrute Parser"""
    # Chemin du fichier HTML de test
    test_file = os.path.join(os.path.dirname(__file__), 'test_rekrute.html')
    
    if not os.path.exists(test_file):
        pytest.skip(f"Test file {test_file} not found")
    
    # Lire le fichier HTML brut
    with open(test_file, 'r', encoding='utf-8') as f:
        html_brut = f.read()
    
    # Étape 1: Nettoyage
    cleaner = Cleaner()
    test_url = "https://www.rekrute.com/offre-emploi-ingenieur-devops-senior-fh-recrutement-sofrecom-maroc-rabat-182541.html"
    
    html_clean = DataProcessingDTO(
        html=cleaner.clean(html_brut), 
        url=test_url
    )
    assert len(html_clean.html) > 0, "Cleaned HTML should not be empty"
    
    # Étape 2: Extraction
    mock_hash_gen = HashPatternGenerator()
    mock_db = MagicMock()
    
    parser = RekruteParser(mock_hash_gen, mock_db)
    extracted_dto = parser.extract(html_clean)
    
    # Étape 3: Verify
    assert extracted_dto is not None, "Extraction should return a DTO"
    donnees = extracted_dto.to_dict()
    assert isinstance(donnees, dict), "Result should be a dictionary"
