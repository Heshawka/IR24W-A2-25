import re, hashlib
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Comment
from crawler.info import Info as info

#lower bound of 1000 chars for each webpage
lower_text_bound = 1500
upper_text_bound = 200000

#simhash_threshold
simhash_threshold = 5

def scraper(url, resp):

    links = extract_next_links(url, resp)

    if links:
        return [link for link in links if is_valid(link)]
    else:
        return []

def hash_token(token):
    #hash token using MD5 and return binary digest
    return hashlib.md5(token.encode()).digest()

def simhash(tokens_list, hash_size=128):
    v = [0] * hash_size
    for token in tokens_list:
        hashed_token = hash_token(token)
        for i in range(hash_size):
            bit = (hashed_token[i // 8] >> (i % 8)) & 1
            if bit == 1:
                v[i] += 1
            else:
                v[i] -= 1
    fingerprint = 0
    for i in range(hash_size):
        if v[i] > 0:
            fingerprint |= (1 << i)
    return fingerprint

def hamming_distance(hash1, hash2):
    return bin(hash1^hash2).count('1')

def extract_next_links(url, resp):

    # initializing instance of info class to keep track of data (only does this once)
    info_collection = info()
    #initializing empty list for found links
    links = []

    #if page content does not exist, return empty list
    if not resp.raw_response:
        return []

    #getting url without query to compare to info_collection
    parsed = urlparse(url)
    url_without_query = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    #checks for 204 (no-content success), error codes, if url is blacklisted or already scraped -> doesn't scrape this page
    if (resp.status == 204 or resp.status >= 400) or (url in info_collection.scraped_urls) or (url in info_collection.blacklisted_urls) or (url_without_query in info_collection.unique_urls):
        info_collection.blacklisted_urls.add(url)
        return []

    #creating soup object
    soup = BeautifulSoup(resp.raw_response.content, "lxml")

    #extracting all comments
    for tag in soup(text=lambda text: isinstance(text, Comment)):
        tag.extract()

    #removing script and style elements (CSS/JS)
    for element in soup.find_all(['script', 'style']):
        element.extract()

    #getting webtext
    webtext = soup.get_text()
    #replaces whitespace with single space for normalization
    space_delimited_text = re.sub(r'\s+', ' ', webtext)

    #if text is less than 1000 chars, blacklist and return empty list
    if (len(space_delimited_text) < lower_text_bound) or (len(space_delimited_text) > upper_text_bound):
        info_collection.blacklisted_urls.add(url)
        return []

    #tokenizing current url
    tokens_list = info_collection.tokenize(url, webtext)

    #getting links
    link_elems = soup.select("a[href]")

    #simhash current url for comparisons
    url_simhash = simhash(tokens_list)

    #iterating through the links
    for link_elem in link_elems:
        href = link_elem.get("href")
        if href:
            #converting to abs urls
            href = urljoin(url, href)

            #defragmenting url
            href = urlparse(href)
            href = href.scheme + "://" + href.netloc + href.path + href.params + href.query

            #if not seen, place in seen_urls
            if href not in info_collection.seen_urls:
                links.append(href)
                info_collection.seen_urls.add(href)

    #simhashing
    last_page_simhash = simhash(info_collection.last_page_tokens)

    #getting hamming distance
    distance = hamming_distance(url_simhash, last_page_simhash)

    #if similar enough, add current url to blacklist and update last_page_tokens
    if distance <= simhash_threshold:
        info_collection.blacklisted_urls.add(url)
    info_collection.last_page_tokens = tokens_list

    #url has been fully scraped
    info_collection.scraped_urls.add(url)
    return links

def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    # initializing instance of info class to keep track of data (only does this once)
    info_collection = info()

    try:
        parsed = urlparse(url)
        subdomain = parsed.netloc.split('.')

        if parsed.scheme not in set(["http", "https"]):
            return False

        #domain check
        if not re.match(
            r'^(\w*.)(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu)$',
            parsed.netloc):
            return False

        if "pdf" in url:
            return False

        if "#comment" in url or "#comments" in url:
            return False

        if "?share" in url:
            return False

        if subdomain[0] == "ngs":
            return False

        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|bib)$", parsed.path.lower()):
            return False

        #adding urls we actually care about to unique_urls
        url_without_query = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        info_collection.unique_urls.add(url_without_query)

        #add valid url's subdomain to info_collection if it's under ics.uci.edu domain
        if re.match(r'^(\w+.)(ics.uci.edu)$', parsed.netloc):
            info_collection.sub_domains[f"{parsed.scheme}://{parsed.netloc}"] += 1

        return True


    except TypeError:
        print ("TypeError for ", parsed)
        raise
