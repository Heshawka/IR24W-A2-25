from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger
import scraper
import time
from urllib.parse import urlparse


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        #initializing a dict with domains and the time they're accessed
        domain_access_times = {}
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            #getting domain
            url_split = urlparse(tbd_url).netloc.split('.')
            domain = '.'.join(url_split[-3:])
            print("IN THIS DOMAIN: " + domain)

            #sleeps for .5 secs if domain has been seen in last half second
            if domain in domain_access_times and (time.time() - domain_access_times[domain] < .5):
                print("!!!WE ARE SLEEPING!!!")
                time.sleep(.5)

            #store url in domain_access_times dict
            domain_access_times[domain] = time.time()

            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
