import pytest
from services.NormalisationService import NormalizationService

@pytest.fixture
def service():
    return NormalizationService()

def test_normalization_service(service):
    # Mock job offer data
    mock_offer = {
        'site': "Indeed",
        'job_title': "Senior   Python  Developer",
        'job_ref': "REF-12345-XYZ",
        'company': "Tech  Corp   Inc.",
        'location': "PARIS",
        'job_type': "Full-Time",
        'job_description': "We are looking for a talented developer.   Join us!",
        'posted_date': "2026-05-15",
        'url': "https://www.indeed.com/jobs?q=python",
        'salary_id': "SALARY_001"
    }

    # Normalize the offer
    normalized = service.normalize(mock_offer)

    # Assertions
    assert normalized['site'] == "indeed"
    assert normalized['job_title'] == "senior python developer"
    assert normalized['company'] == "tech corp inc."
    assert normalized['location'] == "Paris, France"
    assert normalized['job_type'] == "full-time"
    assert "talented developer" in normalized['job_description']
    # Check that extra spaces are removed
    assert "  " not in normalized['job_title']
    assert "  " not in normalized['company']
