from bs4 import BeautifulSoup
from .genericParser import GenericParser
import re

class IndeedParser(GenericParser):
    """Parser pour les offres d'emploi Indeed."""

    def extract(self, cleaned_html: str) -> dict:
        """
        Extrait les informations d'une offre d'emploi Indeed depuis le HTML nettoyé.
        
        Args:
            cleaned_html: Chaîne HTML nettoyée (sans scripts, styles, etc.)
        
        Returns:
            Dictionnaire contenant les champs extraits:
            - job_title: Titre du poste
            - job_ref: Référence/ID de l'offre
            - company: {name, ref}
            - location: Localisation du poste
            - job_type: Type de contrat
            - job_description: Description complète
        """
        soup = BeautifulSoup(cleaned_html, 'lxml')
        
        return {
            'job_title': self._extract_job_title(soup),
            'job_ref': self._extract_job_ref(soup),
            'company': self._extract_company(soup),
            'location': self._extract_location(soup),
            'job_type': self._extract_job_type(soup),
            'job_description': self._extract_job_description(soup),
        }

    def _extract_job_title(self, soup: BeautifulSoup) :
        """Extrait le titre du poste."""
        # Cherche h1 ou h2 avec classe de titre
        title_elem = soup.find('h1', class_='jobsearch-JobComponent-title')
        if not title_elem:
            title_elem = soup.find('h1')
        
        if title_elem:
            return self._clean_text(title_elem.get_text())
        return None

    def _extract_job_ref(self, soup: BeautifulSoup) :
        """Extrait la référence/ID de l'offre depuis l'URL ou attribut HTML."""
        # Cherche un attribut data-job-id ou similaire
        job_elem = soup.find(attrs={'data-job-id': True})
        if job_elem:
            return job_elem.get('data-job-id')
        
        # Alternative: chercher dans les attributs id
        job_container = soup.find('div', class_='jobsearch-JobComponent')
        if job_container and job_container.get('id'):
            return job_container.get('id')
        
        return None

    def _extract_company(self, soup: BeautifulSoup) -> dict:
        """Extrait les infos de l'entreprise."""
        company_name = None
        company_ref = None
        
        # Cherche le nom de l'entreprise
        company_elem = soup.find('span', class_='css-1saizt3')
        if not company_elem:
            company_elem = soup.find('div', attrs={'data-testid': 'inlineTitle-companyName'})
        
        if company_elem:
            company_name = self._clean_text(company_elem.get_text())
        
        # Cherche le lien/ref de l'entreprise
        company_link = company_link = soup.find('a', attrs={
    'data-testid': re.compile('companyLink')
})
        if company_link:
            company_ref = company_link.get('href')
        
        return {
            'name': company_name,
            'ref': company_ref,
        }

    def _extract_location(self, soup: BeautifulSoup) :
        """Extrait la localisation du poste."""
        # Cherche le div avec id jobLocationText
        location_text = soup.find('div', id='jobLocationText')
        if location_text:
            location_span = location_text.find('span')
            if location_span:
                return self._clean_text(location_span.get_text())
        
        # Alternative: utiliser le data-testid
        location_elem = soup.find('div', attrs={'data-testid': 'jobsearch-JobInfoHeader-companyLocation'})
        if location_elem:
            return self._clean_text(location_elem.get_text())
        
        return None

    def _extract_job_type(self, soup: BeautifulSoup) :
        """Extrait le type de contrat."""
        # Cherche les informations de type d'emploi (dans la section metadata)
        job_type_elem = soup.find('span', attrs={
    'data-testid': re.compile('jobType')
})
        if job_type_elem:
            return self._clean_text(job_type_elem.get_text())
        
        # Alternative: chercher dans la description ou métadonnées
        metadata = soup.find('div', class_='jobsearch-JobMetadataFooter')
        if metadata:
            type_span = metadata.find('span')
            if type_span:
                return self._clean_text(type_span.get_text())
        
        return None

    def _extract_job_description(self, soup: BeautifulSoup) :
        """Extrait la description complète du poste."""
        # Cherche le div avec id jobDescriptionText
        desc_elem = soup.find('div', id='jobDescriptionText')
        if desc_elem:
            return self._clean_text(desc_elem.get_text())
        
        # Alternative: utiliser la classe
        desc_elem = soup.find('div', class_='jobsearch-JobComponent-description')
        if desc_elem:
            return self._clean_text(desc_elem.get_text())
        
        return None

    def _clean_text(self, text: str) :
        """Nettoie le texte extrait."""
        if not text:
            return None
        
        # Supprimer espaces inutiles
        text = ' '.join(text.split())
        return text.strip()
