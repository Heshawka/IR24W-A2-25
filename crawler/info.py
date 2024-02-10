class Info:
    tokens = {}
    scraped_urls = set()
    unique_urls = set()
    seen_urls = set()
    blacklisted_urls = set()
    longest_url = ["", 0]  # first elem is the url, second is num of words


    def __init__(self):
        self.tokens = {}
        self.scraped_urls = set()
        self.unique_urls = set()
        self.seen_urls = set()
        self.blacklisted_urls = set()
        self.longest_url = ["", 0] #first elem is the url, second is num of words
