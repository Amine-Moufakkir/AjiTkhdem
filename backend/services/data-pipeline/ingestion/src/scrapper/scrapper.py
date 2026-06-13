from abc import ABC, abstractmethod
from typing import Optional

from orchestrator.context import ScrapingContext


def resolve_use_proxy(use_proxy: bool = True, useProxy: bool | None = None) -> bool:
    return use_proxy if useProxy is None else useProxy


class AbstractScrapper(ABC):
    def __init__(self, context: Optional[ScrapingContext] = None, use_proxy: bool = True, useProxy: bool | None = None):
        self._context = context
        self.use_proxy = resolve_use_proxy(use_proxy=use_proxy, useProxy=useProxy)

    @property
    def context(self) -> Optional[ScrapingContext]:
        return self._context

    @context.setter
    def context(self, value: ScrapingContext):
        
        self._context = value

    @abstractmethod
    def scrape(self):
        pass
