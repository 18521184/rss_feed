#!/usr/local/bin/python3.3
from os import O_APPEND
from sys import hexversion
from bs4 import BeautifulSoup as bs4
from feedparser.api import parse
import requests
import feedparser
import urllib.parse

from requests.models import parse_url

def findfeed(site):

    result = []
    possible_feeds = []

    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(site)
    html = bs4(page, "lxml")

    # raw = requests.get(site).text
    # html = bs4(raw,"lxml")
    feed_urls = html.findAll("link", rel="alternate")
    if len(feed_urls) > 1:
        for f in feed_urls:
            t = f.get("type",None)
            if t:
                if "rss" in t or "xml" in t:
                    href = f.get("href",None)
                    if href:
                        possible_feeds.append(href)
    parsed_url = urllib.parse.urlparse(site)
    base = parsed_url.scheme+"://"+parsed_url.hostname
    atags = html.findAll("a")
    for a in atags:
        href = a.get("href",None)
        if href:
            
            if ("xml" in href or "rss" in href or "feed" in href):
                if ("https" in href or "http" in href):
                    possible_feeds.append(href)
                else:    
                    possible_feeds.append(base+href)
    print(possible_feeds)
    return possible_feeds
    # for url in list(set(possible_feeds)):
    #     f = feedparser.parse(url)
    #     if len(f.entries) > 0:
    #         if url not in result:
    #             result.append(url)
    # return result
findfeed('https://thanhnien.vn/rss.html')