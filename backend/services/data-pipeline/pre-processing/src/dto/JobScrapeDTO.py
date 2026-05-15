



class JobScrapeDTO:
    def __init__(self, message : dict ):
        self.url = message["data"].get("url")
        self.html = message["data"].get("html")
        self.parser_type = message["data"].get("parser_type")
        self.topic = message["topic"]