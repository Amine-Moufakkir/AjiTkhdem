from bs4 import BeautifulSoup

from core.HashGenerator import HashGenerator
from core.HashPatternGenerator import HashPatternGenerator
from models.db import MongoDB
from .genericParser import GenericParser
import re
from urllib.parse import urlparse, parse_qs

class IndeedParser(GenericParser):
    """Parser pour les offres d'emploi Indeed."""

    def __init__(self , hash_generator: HashPatternGenerator , db: MongoDB):
        hash_generator.setPattern("site-job_title-job_ref-company_location-job_type-job_description")
        super().__init__(hash_generator , db)

    def extract(self, cleaned_html: dict) -> dict:
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
        soup = BeautifulSoup(cleaned_html["html"], 'lxml')
        
        return {
            'site': "Indeed",
            'job_title': self._extract_job_title(soup),
            'job_ref': self._extract_vjk_from_url(cleaned_html["url"]),
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
        job_container = soup.find('span', class_='js-match-insights-provider-18uwqyc e1wnkr790')
        if job_container and job_container.get('id'):
            return job_container.get('id')
        
        return None
    
    

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

    def _extract_company(self, soup: BeautifulSoup):
      """Extrait les infos de l'entreprise depuis le HTML Indeed."""
      
      company_name = None
      company_ref = None
      
      # ============================================================
      # ÉTAPE 1: Trouver le lien de l'entreprise
      # ============================================================
      
      # Cherche le lien dans le span css-qcqa6h (format actuel Indeed)
      company_link = None
      company_span = soup.find('span', class_='css-qcqa6h')
      if company_span:
          company_link = company_span.find('a', href=re.compile(r'/cmp/'))
      
      # Fallback: Cherche n'importe quel lien avec /cmp/ dans le href
      if not company_link:
          company_link = soup.find('a', href=re.compile(r'/cmp/'))
      
      # ============================================================
      # ÉTAPE 2: Extraire le NOM
      # ============================================================
      
      if company_link:
          # Méthode 1: Texte du lien
          company_name = self._clean_text(company_link.get_text())
          
          # Méthode 2: aria-label (si texte vide)
          if not company_name:
              aria_label = str(company_link.get('aria-label', ''))
              if aria_label:
                  # Extrait "GIDE" de "GIDE (opens in a new tab)"
                  match = re.search(r'^(.+?)\s*\(', aria_label)
                  if match:
                      company_name = self._clean_text(match.group(1))
      
      # Fallback si aucun lien trouvé
      if not company_name:
          company_elem = soup.find('div', attrs={'data-testid': 'inlineTitle-companyName'})
          if company_elem:
              company_name = self._clean_text(company_elem.get_text())
      
      # ============================================================
      # ÉTAPE 3: Extraire la RÉFÉRENCE (campaignid)
      # ============================================================
      
      if company_link:
          href = str(company_link.get('href', ''))
          
          # Extraire UNIQUEMENT le campaignid comme référence
          campaignid_match = re.search(r'campaignid=([^&]+)', href)
          if campaignid_match:
              company_ref = campaignid_match.group(1)
      
      # ============================================================
      # CONSTRUCTION DU RÉSULTAT
      # ============================================================
      
      return {
          'name': company_name,
          'ref': company_ref,
      }

    def _extract_job_type(self, soup: BeautifulSoup):
    
        job_type_elem = soup.find('span', attrs={
        'data-testid': re.compile('jobType', re.IGNORECASE)
         })
        if job_type_elem:
            return self._clean_text(job_type_elem.get_text())

        # Méthode 2: Chercher la classe spécifique Indeed
        job_type_elem = soup.find('span', class_=re.compile(r'js-match-insights-provider'))
        if job_type_elem:
            return self._clean_text(job_type_elem.get_text())

        # Méthode 3: Chercher dans la section metadata footer
        metadata = soup.find('div', class_='jobsearch-JobMetadataFooter')
        if metadata:
            type_span = metadata.find('span')
            if type_span:
                return self._clean_text(type_span.get_text())

        # Méthode 4: Chercher tout span avec texte de type contrat connu
        contrats_types = ['permanent', 'temporary', 'contract', 'full-time', 
                         'part-time', 'cdi', 'cdd', 'freelance', 'stage', 'internship']

        all_spans = soup.find_all('span')
        for span in all_spans:
            text = self._clean_text(span.get_text())
            if text and text.lower() in contrats_types:
                return text

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

    def _extract_vjk_from_url( self , url: str) :
        """
        Extrait l'identifiant vjk d'une URL Indeed.
        
        L'identifiant vjk est toujours présent dans les URLs Indeed sous
        différentes formes :
        - Paramètre GET: ?vjk=0a5d0000df3de9f4
        - Dans le chemin: /0a5d0000df3de9f4
        - Fragment: #vjk=0a5d0000df3de9f4
        
        Args:
            url: URL Indeed complète
            
        Returns:
            Identifiant vjk ou None si non trouvé
            
        Examples:
            >>> extract_vjk_from_url('https://ma.indeed.com/?r=us&vjk=0a5d0000df3de9f4')
            '0a5d0000df3de9f4'
            
            >>> extract_vjk_from_url('https://ma.indeed.com/viewjob?vjk=0a5d0000df3de9f4')
            '0a5d0000df3de9f4'
            
            >>> extract_vjk_from_url('https://ma.indeed.com/job/0a5d0000df3de9f4')
            '0a5d0000df3de9f4'
        """
        if not url:
            return None
        
        # Méthode 1: Chercher vjk comme paramètre GET (?vjk=... ou &vjk=...)
        vjk_pattern = r'[?&]vjk=([a-f0-9]+)'
        match = re.search(vjk_pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Méthode 2: Utiliser urllib pour parser les paramètres
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'vjk' in params:
                return params['vjk'][0]
        except:
            pass
        
        # Méthode 3: Chercher vjk dans le chemin (format /job/IDENTIFIANT)
        path_pattern = r'/job/([a-f0-9]+)'
        match = re.search(path_pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Méthode 4: Chercher vjk après un slash tout seul
        vjk_in_path = r'/([a-f0-9]{16,})'
        match = re.search(vjk_in_path, url, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Méthode 5: Chercher vjk dans le fragment (#vjk=...)
        fragment_pattern = r'vjk=([a-f0-9]+)'
        match = re.search(fragment_pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    