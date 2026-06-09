from dataclasses import dataclass
from typing import Optional
import random


@dataclass
class ScrapingContext:
    user_agent: str
    proxy: dict
    viewport: dict
    locale: str
    timezone_id: str
    min_delay: float
    max_delay: float


class ContextGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    PROXIES = [
        {"http": "http://192.168.1.1:8080", "https": "http://192.168.1.1:8080"},
        {"http": "http://10.0.0.5:8080", "https": "http://10.0.0.5:8080"},
    ]

    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1280, "height": 800},
    ]

    LOCALES = ["en-US", "en-GB", "fr-FR", "fr-CA"]
    TIMEZONES = ["America/New_York", "Europe/London", "Europe/Paris", "Asia/Casablanca"]

    def __init__(
        self,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay

    def generate(self) -> ScrapingContext:
        return ScrapingContext(
            user_agent=random.choice(self.USER_AGENTS),
            proxy=random.choice(self.PROXIES),
            viewport=random.choice(self.VIEWPORTS),
            locale=random.choice(self.LOCALES),
            timezone_id=random.choice(self.TIMEZONES),
            min_delay=self.min_delay,
            max_delay=self.max_delay,
        )