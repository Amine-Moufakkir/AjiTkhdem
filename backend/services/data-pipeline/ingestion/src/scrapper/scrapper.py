from abc import ABC, abstractmethod
class AbstractScraper(ABC):
    def __init__(self, url, user_agents, proxy_ips):
        self.url = url
        self.user_agents = user_agents
        self.proxy_ips = proxy_ips

    @abstractmethod
    def scrape(self):
        pass
