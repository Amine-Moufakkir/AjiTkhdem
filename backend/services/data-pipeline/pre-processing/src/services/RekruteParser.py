import json
import re
from bs4 import BeautifulSoup

from core.HashGenerator import HashGenerator
from core.HashPatternGenerator import HashPatternGenerator
from models.db import MongoDB
from .genericParser import GenericParser

class RekruteParser(GenericParser):
    """Parser résilient pour les offres d'emploi Rekrute."""

    def __init__(self, hash_generator: HashPatternGenerator, db: MongoDB):
        # We use the exact same hash pattern to maintain consistency across the pipeline
        hash_generator.setPattern("site-job_title-job_ref-company_location-job_type-job_description")
        super().__init__(hash_generator, db)

    def extract(self, cleaned_html: dict) -> dict:
        soup = BeautifulSoup(cleaned_html["html"], 'lxml')
        url = cleaned_html.get("url", "")
        
        # 1. Try to load the hidden JSON-LD structured data first
        json_ld = self._extract_json_ld(soup)
        
        return {
            'site': "Rekrute",
            'job_title': self._extract_job_title(soup, json_ld),
            'job_ref': self._extract_job_ref(url),
            'company': self._extract_company(soup, json_ld),
            'location': self._extract_location(soup, json_ld),
            'job_type': self._extract_job_type(soup, json_ld),
            'job_description': self._extract_job_description(soup, json_ld),
        }
        
    def _extract_json_ld(self, soup: BeautifulSoup) -> dict:
        """Extrait les données structurées cachées pour un scraping ultra-fiable."""
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag and script_tag.string:
            try:
                # Remove control characters that could break the JSON parser
                clean_json = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', script_tag.string)
                return json.loads(clean_json)
            except json.JSONDecodeError:
                pass
        return {}

    def _extract_job_title(self, soup: BeautifulSoup, json_ld: dict):
        # Priority 1: JSON-LD
        if json_ld and 'title' in json_ld:
            return self._clean_text(json_ld['title'])
        
        # Priority 2: HTML Parsing
        title_elem = soup.find('h1')
        if title_elem:
            # Slices off the "- Casablanca" that Rekrute often appends to the H1
            raw_title = title_elem.get_text().split('-')[0]
            return self._clean_text(raw_title)
            
        return None

    def _extract_job_ref(self, url: str):
        """Extrait l'ID depuis la fin de l'URL Rekrute."""
        if not url:
            return None
            
        # Regex captures the numbers right before ".html" (e.g., ...-182541.html)
        match = re.search(r'-(\d+)\.html$', url, re.IGNORECASE)
        if match:
            return match.group(1)
            
        return None

    def _extract_company(self, soup: BeautifulSoup, json_ld: dict):
        company_name = None
        company_ref = None
        
        # Priority 1: Name from JSON-LD
        if json_ld and 'hiringOrganization' in json_ld:
            company_name = json_ld['hiringOrganization'].get('name')
            
        # Priority 2: Name from Krunchy/FeelGood Badge Alt text
        if not company_name:
            img_elem = soup.find('img', alt=re.compile(r'Entreprises (Krunchy|Feel Good) - (.+)'))
            if img_elem:
                match = re.search(r'Entreprises (?:Krunchy|Feel Good) - (.+)', img_elem.get('alt', ''))
                if match:
                    company_name = match.group(1)

        # Extract Company ID (ref) from the logo image URL
        logo_img = soup.find('img', src=re.compile(r'/recruiter_id/(\d+)'))
        if logo_img:
            match = re.search(r'/recruiter_id/(\d+)', logo_img.get('src', ''))
            if match:
                company_ref = match.group(1)
                
        return {
            'name': self._clean_text(company_name),
            'ref': company_ref
        }

    def _extract_location(self, soup: BeautifulSoup, json_ld: dict):
        # Priority 1: JSON-LD
        if json_ld and 'jobLocation' in json_ld:
            loc_data = json_ld['jobLocation'].get('address', {})
            locality = loc_data.get('addressLocality')
            if locality:
                return self._clean_text(locality)
                
        # Priority 2: The standard list item with the map-marker icon
        location_elem = soup.find('li', title='Région')
        if location_elem:
            raw_text = location_elem.get_text()
            # Clean up the noise like "1 poste(s) sur" and "- Maroc"
            clean_loc = re.sub(r'\d+\s*poste\(s\) sur', '', raw_text)
            clean_loc = clean_loc.replace('- Maroc', '')
            return self._clean_text(clean_loc)
            
        return None

    def _extract_job_type(self, soup: BeautifulSoup, json_ld: dict):
        # Priority 1: JSON-LD
        if json_ld and 'employmentType' in json_ld:
            return self._clean_text(json_ld['employmentType'])
            
        # Priority 2: Spans containing "Type de contrat"
        type_elem = soup.find('span', class_='tagContrat', title='Type de contrat')
        if type_elem:
            return self._clean_text(type_elem.get_text())
            
        return None

    def _extract_job_description(self, soup: BeautifulSoup, json_ld: dict):
        # Priority 1: JSON-LD usually holds the raw HTML or cleaned text
        if json_ld and 'description' in json_ld:
            desc = self._clean_text(json_ld['description'])
            if desc: return desc
            
        # Priority 2: Iterate through blocks and merge "Poste", "Profil", and "Entreprise"
        description_parts = []
        blocks = soup.find_all('div', class_='col-md-12 blc')
        
        for block in blocks:
            h2 = block.find('h2')
            if h2 and h2.get_text(strip=True) in ['Poste :', 'Profil recherché :', 'Entreprise :']:
                # Extract the title so it's not repeated, then grab the remaining text
                h2_text = h2.get_text(strip=True)
                h2.extract()
                block_text = block.get_text(separator=' ', strip=True)
                description_parts.append(f"{h2_text}\n{block_text}")
                
        if description_parts:
            return self._clean_text('\n\n'.join(description_parts))
            
        return None

    def _clean_text(self, text: str):
        """Enlève les espaces multiples, retours chariot et tabulations excessives."""
        if not text:
            return None
        # Replace multiple spaces/newlines/tabs with a single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()