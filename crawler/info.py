class Info:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Info, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.tokens = {}
            self.scraped_urls = set()
            self.unique_urls = set()
            self.seen_urls = set()
            self.blacklisted_urls = set()
            self.longest_url = ["", 0] #first elem is the url, second is num of words
            self.initialized = "True"
