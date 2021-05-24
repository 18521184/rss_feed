import re
import requests
import unicodedata

import feedparser
import urllib.parse

from bs4 import BeautifulSoup as bs4

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

# Ref: https://stackoverflow.com/questions/16467479/normalizing-unicode
# output: text after unicode, normalizing 
def normalize(text):
    text = text.lower()
    text = unicodedata.normalize('NFKC', text)
    text = text.replace('\n', ' ')

    return text

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
            if t:
                if "rss" in t or "xml" in t:
                    href = f.get("href",None)
                    if href:
                        feeds.append(href)
    
    # ...
    parsed_url = urllib.parse.urlparse(url)
    base = parsed_url.scheme + "://" + parsed_url.hostname
    atags = html.findAll("a")
    for a in atags:
        href = a.get("href",None)
        if href:
            
            if ("xml" in href or "rss" in href or "feed" in href):
                if ("https" in href or "http" in href):
                    feeds.append(href)
                else:    
                    feeds.append(base+href)

    return feeds