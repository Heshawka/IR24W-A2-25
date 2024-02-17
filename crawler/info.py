from urllib.parse import urlparse
from collections import defaultdict
import re

class Info:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Info, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.tokens = defaultdict(int)
            self.last_page_tokens = []
            self.scraped_urls = set()
            self.unique_urls = set()
            self.seen_urls = set()
            self.blacklisted_urls = set()
            self.longest_url = ["", 0] #first elem is the url, second is num of words
            self.sub_domains = defaultdict(int)
            self.initialized = "True"

    def tokenize(self, url, webtext):
        #creating RE pattern to match to input webtext
        re_pattern = r'[A-Za-z0-9]+'
        tokens_list = []

        #iterate through webtext and find matches
        matches = re.finditer(re_pattern, webtext)
        tokens_list += [match.group().lower() for match in matches]

        #placing tokens in self.tokens
        for token in tokens_list:
            self.tokens[token] += 1

        #getting longest url in tokens
        if len(tokens_list) > self.longest_url[1]:
            self.longest_url[0] = url
            self.longest_url[1] = len(tokens_list)

        #returns list of tokens for current url to be used for simhashing
        return tokens_list

    #sorts self.tokens to be printed in order of frequency, removing stopwords, and returns top 50 words
    def sort_tokens_dict(self):

        stop_words = [
            'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
            'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being',
            'below', 'between', 'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't",
            'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during',
            'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have',
            "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', "here's", 'hers',
            'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've",
            'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more',
            'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only',
            'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't",
            'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than',
            'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's",
            'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to',
            'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're",
            "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 'which',
            'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you',
            "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'
        ]

        filtered_tokens = {word: freq for word, freq in self.tokens.items() if word not in stop_words}

        sorted_tokens = dict(sorted(filtered_tokens.items(), key=lambda x: (-x[1], x[0])))

        top_50_tokens = dict(list(sorted_tokens.items())[:50])
        return top_50_tokens

    def print_info(self):
        print("NUMBER OF UNIQUE URLS: ", len(self.unique_urls))

        print("LONGEST PAGE: ", self.longest_url[0], " WITH THESE MANY WORDS: ", self.longest_url[1])

        self.tokens = self.sort_tokens_dict()
        print("50 MOST COMMON WORDS: ")
        for key, val in self.tokens.items():
            print(f"{key} {val}")

        self.sub_domains = dict(sorted(self.sub_domains.items(), key=lambda x: x[0]))
        print("SUBDOMAINS IN ics.uci.edu DOMAIN: ")
        for key, val in self.sub_domains.items():
            print(f"{key} {val}")

