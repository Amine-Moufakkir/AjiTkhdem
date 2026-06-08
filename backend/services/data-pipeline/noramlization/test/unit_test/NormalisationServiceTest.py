
from src.services.NormalisationService import NormalizationService

# Initialize the service
service = NormalizationService()

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

# Display results
print("=== ORIGINAL OFFER ===")
for key, value in mock_offer.items():
    print(f"{key}: {value}")

print("\n=== NORMALIZED OFFER ===")
for key, value in normalized.items():
    print(f"{key}: {value}")

print("\n=== DIFFERENCES ===")
for key in mock_offer.keys():
    if mock_offer[key] != normalized[key]:
        print(f"{key}:")
        print(f"  Before: {mock_offer[key]}")
        print(f"  After:  {normalized[key]}")