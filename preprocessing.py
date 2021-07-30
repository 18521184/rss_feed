import re
from urllib import request
import requests
import unicodedata
import feedparser
import urllib.parse

from bs4 import BeautifulSoup as bs4

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def cleanhtml(raw_html):
    # cleanr = re.compile('<.*?>')
    # Filter HTML tag
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    # Filter document.write()
    cleanr = re.compile(r"document\.write\('\n?([^']*?)(?:\n\s*)?'\);")
    cleantext = re.sub(cleanr, '', cleantext)
    return cleantext

def is_relevant(text):
    # Describe list of keywords indicating the text is relevant
    keywords = ['covid', 'corona', 'sars', 'cov-']
    # And more ['cách ly', 'đại dịch', 'dịch bệnh', 'dịch']
    text = text.lower()
    for word in keywords:
        if word in text:
            return True

    return False

# Check if an RSS feed is crawlable
# some sites might be not likely available to crawl hence causing error 
def is_crawlable(url):
    try:
        if requests.get(url, timeout=3.0):
            return True
    except Exception:
        return False
    return True

# Ref: https://stackoverflow.com/questions/16467479/normalizing-unicode
# output: text after unicode, normalizing 
def normalize(text):
    # text = text.lower()
    text = unicodedata.normalize('NFKC', text)
    text = text.replace('\n', ' ')

    return text

# # Remove duplicates and validate RSS feed URL from find_feeds
# def validate_feeds(feeds, url):
#     results = set()
#     for feed in feeds:
#         if feed != url and len(url) < len(feed):
#             results.add(feed)
#     return list(results)

# Get all RSS feed URL from RSS aggregator site
def find_feeds(url):
    feeds = []

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(url)
    html = bs4(page, "lxml")
    feed_urls = html.findAll("link", rel="alternate")
    # ...
    if len(feed_urls) > 1:
        for f in feed_urls:
            t = f.get("type",None)
            if t and (("rss" in t) or ("xml" in t)):
                href = f.get("href",None)
                if href and is_crawlable(href):
                    feeds.append(href)

    # ...
    parsed_url = urllib.parse.urlparse(url)
    base = parsed_url.scheme + "://" + parsed_url.hostname
    atags = html.findAll("a")
    for a in atags:
        href = a.get("href",None)
        if href and ("xml" in href or "rss" in href or "feed" in href):
            if ("https" in href or "http" in href) and is_crawlable(href):
                feeds.append(href)
            else:
                feeds.append(base+href)
    
    # Remove duplicate
    feeds = list(set(feeds))

    return feeds

# Reference
# feedparser with timeout: https://stackoverflow.com/a/39330232