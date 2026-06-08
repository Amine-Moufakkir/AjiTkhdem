from typing import Any, Mapping
import re
import unicodedata
from datetime import datetime
from dateutil.parser import parse as parse_date, ParserError
import geonamescache

URL_RE = re.compile(
    r'^(https?://|www\.)[^\s]+$', re.IGNORECASE
)
TECH_KEY_RE = re.compile(r'\b(ref|id|uuid|uid|hash)\b', re.IGNORECASE)


class NormalizationService:
    def __init__(self):
        self.gc = geonamescache.GeonamesCache()
        # prepare lookup maps (lowercased)
        self.countries = {
            v['name'].lower(): v for k, v in self.gc.get_countries().items()
        }
        # city -> (name, countrycode)
        self.cities = {}
        for k, v in self.gc.get_cities().items():
            name = v.get('name', '').lower()
            if name:
                # keep first occurrence; for collisions later logic can be extended
                if name not in self.cities:
                    self.cities[name] = v

    def normalize(self, offer: Mapping[str, Any]) :
        """
        Normalize an offer dict in-place style but return a new dict.
        Rules:
         - preserve structure and unknown fields
         - do not modify protected keys (job_ref, *id*, *ref*, *uuid*, *hash*)
         - do not modify URLs
         - normalize textual fields: strip, collapse spaces, lowercase, unicode normalize
         - detect dates and convert to ISO8601
         - normalize locations: "city, country" when possible
        """
        return self._normalize_value(offer, key_context=None)

    def _normalize_value(self, value: Any, key_context: None | str = None) -> Any:
        
        if value is None:
            return None
        if isinstance(value, Mapping):
            out = {}
            for k, v in value.items():
                # keep keys identical
                if self._is_protected_key(k):
                    out[k] = v
                else:
                    out[k] = self._normalize_value(v, key_context=k)
            return out
        if isinstance(value, list):
            return [self._normalize_value(v, key_context=key_context) for v in value]
        if isinstance(value, str):
            # Do not change urls
            if URL_RE.match(value.strip()):
                return value
            # Dates
            iso = self._try_parse_date(value)
            if iso is not None:
                return iso
            # Location special-case when key indicates location
            if key_context and key_context.lower() in ('location', 'lieu', 'city', 'ville', 'address'):
                loc = self._normalize_location(value)
                if loc:
                    return loc
            # Generic text normalization
            return self._clean_text(value)
        # other primitive types remain unchanged
        return value

    def _is_protected_key(self, key: str) -> bool:
        
        if not isinstance(key, str):
            return False
        # explicit job_ref protection
        if key == 'job_ref':
            return True
        # match id/ref/uuid/hash anywhere in key
        return bool(TECH_KEY_RE.search(key))

    def _clean_text(self, s: str) -> str:
        # Unicode normalize
        s = unicodedata.normalize('NFKC', s)
        # remove control chars
        s = re.sub(r'[\x00-\x1f\x7f]+', ' ', s)
        # collapse whitespace
        s = re.sub(r'\s+', ' ', s).strip()
        # lowercase
        s = s.lower()
        return s

    def _try_parse_date(self, s: str) -> str | None:
        # quick heuristic: must contain a digit
        if not re.search(r'\d', s):
            return None
        try:
            dt = parse_date(s, fuzzy=True)
            # sanity check year
            if 1900 <= dt.year <= 2100:
                # return ISO 8601 (date or datetime)
                if dt.time() == datetime.min.time():
                    return dt.date().isoformat()
                return dt.isoformat()
        except (ParserError, ValueError):
            return None
        return None

    def _normalize_location(self, s: str) -> str | None:
        
        if not s or not isinstance(s, str):
            return None
        raw = s.strip()
        # remove extra whitespace and lowercase for matching
        l = re.sub(r'\s+', ' ', raw).strip().lower()
        # if already in "city, country" form, normalize components
        if ',' in l:
            parts = [p.strip() for p in l.split(',') if p.strip()]
            if len(parts) >= 2:
                city, country = parts[0], parts[-1]
                country_name = self._match_country(country) or country
                city_name = self._title_case(parts[0])
                return f"{city_name}, {country_name}"
        # direct country match
        country = self._match_country(l)
        if country:
            return country
        # direct city match
        city_entry = self.cities.get(l)
        if city_entry:
            country_code = city_entry.get('countrycode', '').upper()
            country_info = self.gc.get_countries().get(country_code)
            country_name = country_info.get('name') if country_info else country_code
            city_name = self._title_case(city_entry.get('name', ''))
            return f"{city_name}, {country_name}"
        # fallback: return cleaned text (title-cased)
        return self._title_case(raw)

    def _match_country(self, s: str) -> str | None:
        
        if not s:
            return None
        s_l = s.lower()
        # try direct country name
        c = self.countries.get(s_l)
        if c:
            return c.get('name')
        # try country code (alpha2 / alpha3)
        for k, v in self.gc.get_countries().items():
            if k.lower() == s_l or v.get('iso3', '').lower() == s_l:
                return v.get('name')
        return None

    def _title_case(self, s: str) -> str:
        # simple title-case but preserve common acronyms (basic)
        return ' '.join(part.capitalize() for part in s.split())