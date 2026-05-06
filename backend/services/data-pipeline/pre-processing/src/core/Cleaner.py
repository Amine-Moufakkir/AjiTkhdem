import re


class Cleaner:
    """S'occupe  du suppression des balises html unitul . Il est concus pour etre utilisé par n'importe parser."""

    def clean(self, data: str) -> str:
        if not data:
            return ""

        # Supprimer les balises script
        data = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer les balises style
        data = re.sub(r'<style[^>]*>.*?</style>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer les balises noscript
        data = re.sub(r'<noscript[^>]*>.*?</noscript>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer les commentaires HTML
        data = re.sub(r'<!--.*?-->', '', data, flags=re.DOTALL)

        # ========== NOUVEAU : Supprimer les balises SVG ==========
        data = re.sub(r'<svg[^>]*>.*?</svg>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # ========== NOUVEAU : Supprimer les balises path (dans SVG ou standalone) ==========
        data = re.sub(r'<path[^>]*>.*?</path>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # ========== NOUVEAU : Supprimer les balises meta ==========
        data = re.sub(r'<meta[^>]*>', '', data, flags=re.IGNORECASE)

        # ========== NOUVEAU : Supprimer les balises viewport (meta viewport) ==========
        data = re.sub(r'<meta[^>]*name=["\']viewport["\'][^>]*>', '', data, flags=re.IGNORECASE)

        # ========== NOUVEAU : Supprimer les balises format-detection ==========
        data = re.sub(r'<meta[^>]*name=["\']format-detection["\'][^>]*>', '', data, flags=re.IGNORECASE)

        # ========== NOUVEAU : Supprimer les balises referrer ==========
        data = re.sub(r'<meta[^>]*name=["\']referrer["\'][^>]*>', '', data, flags=re.IGNORECASE)

        # ========== NOUVEAU : Supprimer favicon (toutes les formes) ==========
        # Link rel="icon" ou rel="shortcut icon"
        data = re.sub(r'<link[^>]*rel=["\'].*icon.*["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # Meta msapplication-TileImage
        data = re.sub(r'<meta[^>]*name=["\']msapplication-TileImage["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # Apple touch icon
        data = re.sub(r'<link[^>]*rel=["\']apple-touch-icon[^"\']*["\'][^>]*>', '', data, flags=re.IGNORECASE)

        # ========== NOUVEAU : Supprimer les layout hints ==========
        # Balises meta avec charset (layout hint)
        data = re.sub(r'<meta[^>]*charset=[^>]*>', '', data, flags=re.IGNORECASE)
        # Meta http-equiv (X-UA-Compatible, content-type, etc.)
        data = re.sub(r'<meta[^>]*http-equiv=[^>]*>', '', data, flags=re.IGNORECASE)
        # Meta theme-color (layout hint)
        data = re.sub(r'<meta[^>]*name=["\']theme-color["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # Meta color-scheme
        data = re.sub(r'<meta[^>]*name=["\']color-scheme["\'][^>]*>', '', data, flags=re.IGNORECASE)

        # ========== NOUVEAU : Supprimer les tracking headers invisibles ==========
        # Open Graph meta (tracking)
        data = re.sub(r'<meta[^>]*property=["\']og:[^"\']*["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # Twitter Card meta (tracking)
        data = re.sub(r'<meta[^>]*name=["\']twitter:[^"\']*["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # Facebook meta
        data = re.sub(r'<meta[^>]*property=["\']fb:[^"\']*["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # Canonical URL (SEO tracking)
        data = re.sub(r'<link[^>]*rel=["\']canonical["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # DNS prefetch (tracking)
        data = re.sub(r'<link[^>]*rel=["\']dns-prefetch["\'][^>]*>', '', data, flags=re.IGNORECASE)
        # Preconnect (tracking)
        data = re.sub(r'<link[^>]*rel=["\']preconnect["\'][^>]*>', '', data, flags=re.IGNORECASE)

        # Supprimer les éléments UI communs (header, footer, nav, sidebar, breadcrumb)
        data = re.sub(r'<(header|footer|nav|aside|\.navbar|\.sidebar|\.breadcrumb)[^>]*>.*?</\1>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer les popups, modals, banners cookies
        data = re.sub(r'<(div|section)[^>]*class=["\']*(modal|popup|cookie-banner|cookie-consent)[^"\']*["\'][^>]*>.*?</\1>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer les balises ad-related
        data = re.sub(r'<(div|section)[^>]*class=["\']*(ad|advertisement|ads)[^"\']*["\'][^>]*>.*?</\1>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer Google Tag Manager, Facebook Pixel et tracking
        data = re.sub(r'<img[^>]*pixel[^>]*>', '', data, flags=re.IGNORECASE)
        data = re.sub(r'<iframe[^>]*(gtag|facebook|analytics)[^>]*>.*?</iframe>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer les inputs cachés et data-* attributes inutiles
        data = re.sub(r'<input[^>]*type=["\']?hidden["\']?[^>]*>', '', data, flags=re.IGNORECASE)

        # Supprimer les éléments avec display:none, skeleton loaders et lazy-loading placeholders
        data = re.sub(r'<[^>]*style=["\'].*?display\s*:\s*none[^"\']*["\'][^>]*>.*?</[^>]*>', '', data, flags=re.DOTALL | re.IGNORECASE)
        data = re.sub(r'<(div|span)[^>]*class=["\']*(skeleton|loader|placeholder-loader)[^"\']*["\'][^>]*>.*?</\1>', '', data, flags=re.DOTALL | re.IGNORECASE)

        # Supprimer les nœuds DOM dupliqués (éléments avec id ou class contenant "duplicate", "clone")
        data = re.sub(r'<[^>]*(id|class)=["\']*(duplicate|clone)[^"\']*["\'][^>]*>.*?</[^>]*>', '', data, flags=re.DOTALL | re.IGNORECASE)

        return data.strip()
    






"""
DOCUMENTATION DU CLEANER HTML
=============================

Cette classe nettoie le HTML en supprimant les éléments non pertinents 
pour l'extraction de contenu textuel métier.

CATÉGORIES D'ÉLÉMENTS SUPPRIMÉS
--------------------------------

A. SCRIPTS ET STYLES (Exécution et mise en forme)
    • <script> : JavaScript exécutable (tracking, animations, logique)
    • <style> : CSS embarqué (règles de mise en forme)
    • <noscript> : Contenu alternatif si JS désactivé
    • <!-- --> : Commentaires HTML (notes développeur, code commenté)

B. MÉDIAS ET GRAPHIQUES (Contenu visuel non textuel)
    • <svg> : Graphiques vectoriels (icônes, logos, illustrations)
    • <path> : Tracés SVG (chemins graphiques)
    • <img src="pixel"> : Pixels de tracking 1x1 (analytics, email tracking)

C. MÉTADONNÉES (Informations techniques navigateur)
    1. Configuration viewport :
       • <meta name="viewport"> : Adaptation mobile/desktop
         Utile pour reproduire conditions navigateur
         Debug scraping mobile vs desktop
    
    2. Détection automatique :
       • <meta name="format-detection"> : Désactive détection auto 
         (téléphone, adresse, date)
    
    3. Politique de sécurité :
       • <meta name="referrer"> : Contrôle envoi en-tête Referer HTTP

D. FAVICONS (Icônes de site)
    • <link rel="icon"> : Favicon standard
    • <link rel="shortcut icon"> : Favicon legacy IE
    • <link rel="apple-touch-icon"> : Icône iOS (iPhone, iPad)
    • <meta name="msapplication-TileImage"> : Tuile Windows 8/10
    → Totalement inutiles pour le contenu textuel métier

E. LAYOUT HINTS (Indices de rendu navigateur)
    • <meta charset=""> : Encodage caractères (UTF-8, ISO, etc.)
    • <meta http-equiv=""> : Équivalents en-têtes HTTP 
      (X-UA-Compatible, Content-Type, refresh, etc.)
    • <meta name="theme-color"> : Couleur barre navigateur mobile
    • <meta name="color-scheme"> : Mode clair/sombre forcé
    → Pertinent uniquement pour le rendu, pas pour le contenu

F. TRACKING HEADERS INVISIBLES (Pistage utilisateur)
    1. Réseaux sociaux :
       • <meta property="og:*"> : Open Graph (Facebook, LinkedIn)
       • <meta name="twitter:*"> : Twitter Cards
       • <meta property="fb:*"> : Facebook App ID, pages
    
    2. SEO et optimisation :
       • <link rel="canonical"> : URL canonique (évite duplicate content)
       • <link rel="dns-prefetch"> : Pré-résolution DNS (accélère chargement)
       • <link rel="preconnect"> : Pré-connexion serveurs externes
    → Tracking invisible, sert au marketing et analytics

G. ÉLÉMENTS UI NON CONTENU (Interface utilisateur)
    1. Structure du site :
       • <header> : En-tête (logo, titre site, navigation principale)
       • <footer> : Pied de page (copyright, liens légaux, contact)
       • <nav> : Menu navigation
       • <aside> : Barre latérale (widgets, liens connexes)
    
    2. Éléments flottants :
       • class="modal" : Fenêtres modales (login, promo)
       • class="popup" : Popups (newsletter, sortie, bienvenue)
       • class="cookie-banner" : Bannière consentement cookies
       • class="cookie-consent" : Variante consentement cookies
    
    3. Publicités :
       • class="ad" : Bloc publicitaire
       • class="advertisement" : Variante publicité
       • class="ads" : Groupe de publicités

H. TRACKING IFRAMES ET PIXELS (Analytics tiers)
    • <iframe> avec "gtag" : Google Tag Manager
    • <iframe> avec "facebook" : Facebook Pixel iframe
    • <iframe> avec "analytics" : Analytics divers
    → Scripts de tracking chargés depuis domaines tiers

I. INPUTS CACHÉS (Données de formulaire)
    • <input type="hidden"> : CSRF tokens, IDs session, données form
    → Valeurs techniques sans intérêt pour le contenu

J. CONTENU MASQUÉ (Display none et chargement)
    1. Éléments invisibles :
       • style="display:none" : Contenu masqué (onglets, tooltips, etc.)
    
    2. États de chargement :
       • class="skeleton" : Animation chargement (placeholder gris)
       • class="loader" : Spinner chargement
       • class="placeholder-loader" : Variante placeholder
    → Contenu temporaire ou masqué pour l'utilisateur

K. CONTENU DUPLIQUÉ (Redondances DOM)
    • id="duplicate" : Éléments marqués comme doublons
    • id="clone" : Éléments clonés (responsive, A/B testing)
    • class="duplicate" : Variante classe doublon
    • class="clone" : Variante classe clone
    → Versions alternatives du même contenu

POURQUOI CE NETTOYAGE ?
-----------------------
✅ Contenu métier pur : Ne garde que le texte utile
✅ Debug simplifié : Reproduit conditions navigateur mobile/desktop
✅ Pipeline optimisé : Moins de bruit = meilleure extraction
✅ Performance : Données plus légères à traiter
✅ Confidentialité : Supprime trackers et pixels espions

EXEMPLE D'UTILISATION :
-----------------------
cleaner = Cleaner()
html_clean = cleaner.clean(html_brut)
# html_clean contient uniquement le contenu textuel pertinent
"""