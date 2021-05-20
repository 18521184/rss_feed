import re
import feedparser
# import requests
# import json

import urllib.parse
import urllib.request
from bs4 import BeautifulSoup


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    # cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleanr = re.compile(r"document\.write\('\n?([^']*?)(?:\n\s*)?'\);")
    cleantext = re.sub(cleanr, '', cleantext)
    return cleantext

def main():
    # Test with RSS feed aggregate site
    # (A site listing RSS feeds in different category)
    rss_aggr_url = 'https://tuoitre.vn/rss.htm'
    
    feed_aggr = feedparser.parse(rss_aggr_url)
    html_content_rss_aggr = feed_aggr.feed.summary 

    # Test with particular RSS feed
    rss_feed_url = 'https://tuoitre.vn/rss/tin-moi-nhat.rss'
    feed = feedparser.parse(rss_feed_url)

    # Get a sample article URL
    # Also its title
    url = feed.entries[0].links[0]['href']
    title = feed.entries[0].title
    summary = feed.entries[0].summary  

    # feed.entries[i] contains only title and summary
    print('What are in an article we get from RSS feed:\n', feed.entries[0].keys())

    # Crawl and parse meta data of the article from server
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(url)

    soup = BeautifulSoup(page, "lxml")
    
    # We get the first element in the array because we are sure that 
    # any article on tuoitre.vn only has one div tag with classname "main-content-body"
    # Note that findAll or find_all always return a list 
    raw_content = soup.findAll("div", {"class": "main-content-body"})[0]

    # Nonetheless, raw main content body still have some noise
    # such as div tag used for images or suggesting a related article.
    # Thus, we need to get rid of those by extracting p tag only
    # because p tag contains merely paragraph of the content that we need.
    content = ''.join([cleanhtml(str(p)) for p in raw_content.findAll("p", attrs={"class": None, "style": None})])
    
    # Get content's header (somehow as similar as summary)
    # Note that we can convert bs4.element.XXX to string by str() or call .string attribute
    content_header = cleanhtml(str(raw_content.findAll("h2", {"class": "sapo"})[0]))

    print("################## Title:")
    print(title)

    print("################## Content:")
    print(content_header + " " +content)

    print("################## Summary:")
    print(cleanhtml(summary))

    print("################## URL:")
    print(url)

if __name__ == '__main__':
    main()