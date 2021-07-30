# -*- coding: utf-8 -*-
import re, json
import feedparser
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from hashlib import md5

from os import path

from dbconnector import add
from preprocessing import is_relevant, cleanhtml, find_feeds, normalize

# 
def get_content(url):
    content = ''
    try:
        # Crawl and parse meta data of the article from server
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        page = opener.open(url)

        soup = BeautifulSoup(page, "lxml")

        if 'tuoitre.vn' in url:
            # We get the first element in the array because we are sure that 
            # any article on tuoitre.vn only has one div tag with classname "main-content-body"
            # Note that find_all or find_all always return a list 
            raw = soup.find_all("div", {"id": "main-detail-body"})[0]

            # Nonetheless, raw main content body still have some noise
            # such as div tag used for images or suggesting a related article.
            # Thus, we need to get rid of those by extracting p tag only
            # because p tag contains merely paragraph of the content that we need.
            # paras = raw.find_all("p", attrs={"class": None, "style": None})
            paras = raw.findChildren("p", attrs={"style": None}, recursive=False)

            content = ''.join([str(p) for p in paras])

        elif 'vnexpress' in url:
            raw = soup.find_all('article', attrs={"class": "fck_detail"})[0]
            paras = raw.find_all('p', attrs={'class': "Normal", 'style': None, 'id': None})

            content = ' '.join([str(p) for p in paras])

        elif 'thanhnien.vn' in url:
            raw = soup.find_all("div", {"id": "abody"})[0]
            divs = raw.find_all("div", attrs={"class": None, "id": None, "style": None})
                
            new_divs = []
            for div in divs:
                s = str(div)
                if '<table ' not in s and 'Ảnh: ' not in s:
                    new_divs.append(s)

            content = ''.join(new_divs)

        elif 'nld.com.vn' in url:
            raw = soup.find_all("div", {"class": "content-news-detail old-news"})[0]
            content = ''.join([str(p) for p in raw.find_all("p", attrs={"class": None, "style": None})])
            
        elif 'vietnamnet.vn' in url:
            raw_list = soup.find_all("div", {"id": "ArticleContent"})
            if len(raw_list) <= 0:
                raw_list = soup.find_all("div", {"id": "Magazine-Acticle"})[0]

            raw = raw_list[0]
            paras = raw.find_all("p", attrs={"class": None, "style": None})
            if (len(paras) == 0):
                paras = raw.find_all("p", attrs={"class": "t-j", "style": None})
            
            new_paras = []
            for i in range(len(paras)-1):
                if len(paras[i].find_all("iframe")) > 0:
                    continue
                new_paras.append(str(paras[i]))
            content = ' '.join(new_paras)
            
        elif 'moh.gov.vn' in url:
            raw = soup.findAll("div", {"id": "content-detail"})
            # If the main body content with id called "content-detail" available
            if len(raw) > 0:
                raw = raw[0]
            # Otherwise, we have run into other case in which the main body content has class
            # named "journal-content-article"
            else:
                raw = soup.findAll("div", {"class": "journal-content-article"})[0]
                 
            # get list of p elements without any attributes or img element as a child element
            # ref: https://stackoverflow.com/a/34111473
            # use encode_contents in bs4 for UTF-8 encoded bytestring
            # ref: https://stackoverflow.com/a/18602241
            p_tags = raw.find_all(lambda tag: tag.name == 'p' and (not tag.attrs) and (not "<img" in str(tag.encode_contents)))

            # Concatenate into a document except the two last p elements which contain source and author of the news 
            content = ''.join([str(p) for p in p_tags[:-2]])

        # elif 'baochinhphu.vn' in url:
        #     try:
        #         raw = soup.findAll("div", {"class": "article-body cmscontents"})[0]
        #     except Exception as err:
        #         print(url)
        #         return content
        #     #summary : phan chu in dam o dau moi bai
        #     content = ''.join([cleanhtml(str(raw.findAll("div", {"class": "summary"})[0]))])
    
        #     #content:
        #     paras = raw.findAll("p", recursive=False)
        #     for i in range(len(paras)-1):
        #         content += ''.join([cleanhtml(str(paras[i]))])
        #     #content += ''.join([cleanhtml(str(p)) for p in raw.findAll("p", recursive=False)])

    except Exception as err:
        write_log(url, err)
        return content

    # Filter out html tags and unwanted encoding characters
    content = cleanhtml(content)
    content = normalize(content)

    return content

def write_log(url, err):
    with open('debug.txt', 'a+') as f:
        f.write(str(url) + '\n' + str(err) + '\n')

# Get unicity by MD5 hash
def get_digest(url):
    return str(md5(str(url).encode()).hexdigest())

def crawl(url):
    data = {
        "rss_url": url,
        "articles": []
    }

    # Get all available news on the RSS feed
    feed = feedparser.parse(url)

    for i in range(len(feed.entries)):
        # Get a sample article URL
        # Also its title
        url = feed.entries[i].links[0]['href']
        title = normalize(cleanhtml(feed.entries[i].title))
        summary = normalize(cleanhtml(feed.entries[i].summary))

        content = get_content(url)

        # Check if the content is attainable
        # Also check if the article is relevant to COVID-19
        # If we use summary and title, it would be faster and less resource consumption
        # Nonetheless, the summary is not very reliable.
        if len(content) == 0 or (len(content) != 0 and is_relevant(title)==False and is_relevant(content)==False):
            # If none match, continue to another aritcle
            continue

        # # Get content's header (somehow as similar as summary)
        # # Note that we can convert bs4.element.XXX to string by str() or call .string attribute
        # # summary field is also content header
        # content_header = cleanhtml(str(raw_content.find_all("h2", {"class": "sapo"})[0]))

        # Get id and date of the article
        hash = get_digest(url)
        date = feed.entries[i].published

        data['articles'].append({
            "hash": hash,
            "summary": summary,
            "title": title,
            "content": content,
            "url": url,
            "publish_date": date
        })

    if len(data['articles']) > 0:
        return data
    else:
        return None

def get_data_to_csv():
    feeds_url = None
    # Import list of RSS feeds 
    with open('feeds_url.txt', 'r') as f:
        feeds_url = f.read().split('\n')
    
    data = None
    with open('crawl_results.csv', 'a+') as f:
        f.write('\n')
        for i in range(len(feeds_url)):
            print("Crawling from {}".format(feeds_url[i]))     # ??
            data = crawl(feeds_url[i])
            if data:
                # Count number of articles in this RSS feed
                n_articles = len(data['articles'])
                
                # Convert and import articles as CSV entries into CSV file 
                for j in range(n_articles):
                    entry = ','.join([
                        data['articles'][j]['hash'],
                        data['articles'][j]['summary'],
                        data['articles'][j]['title'],
                        data['articles'][j]['content'],
                        data['articles'][j]['url'],         # Article URL
                        feeds_url[i],                       # RSS feed URL
                        data['articles'][j]['publish_date']
                    ])

                    if j != n_articles - 1:
                        entry = entry + '\n'

                    f.write(entry)

# MySQL included
def get_data_to_db(db):
    feeds_url = None
    # Import list of RSS feeds 
    with open('feeds_url.txt', 'r') as f:
        feeds_url = f.read().split('\n')
    
    data = None
    for i in range(len(feeds_url)):
        print("Crawling from {}".format(feeds_url[i]))
        data = crawl(feeds_url[i])
        if data:
            # Count number of articles in this RSS feed
            n_articles = len(data['articles'])
            add(db, data, feeds_url[i])        

# Check if an RSS feed is crawlable
# some sites might be not likely available to crawl hence causing error 
def is_crawlable(url):
    try:
        feed = feedparser.parse(url)
    except Exception:
        return False
    return True

def get_feeds_url():
    # List of sites to be ignored due to not containing usable information
    blacklist = [
        'video'
    ]
    # Aggregate all RSS feeds URL from RSS aggregator site
    rss_aggr_urls = [
        # 'https://tuoitre.vn/rss.htm',
        # 'https://vnexpress.net/rss',
        # 'https://thanhnien.vn/rss.html',
        # 'http://vietnamnet.vn/vn/rss/',
        # 'https://nld.com.vn/rss.htm',
        # 'https://ncov.moh.gov.vn/web/guest/rss',
        'https://baochinhphu.vn/Rss/'
    ]
    with open('feeds_url.txt', 'a+') as f:
        for url in rss_aggr_urls:
            feeds_url = find_feeds(url)
            new_feeds_url = []

            n_feeds = len(feeds_url)
            # Validate each RSS feed uRL
            for i in range(n_feeds):
                flag = True     # For decision to add linebreak
                # Check if URL containing word in blacklist
                for word in blacklist:
                    if word in feeds_url[i]:
                        flag = False
                        break
                
                # Skip pages if 
                if not is_crawlable(feeds_url[i]):
                    continue

                # Stop adding line break at the last element 
                if flag:
                    if i != n_feeds-1:
                        new_feeds_url.append(feeds_url[i] + '\n')
                    else:
                        new_feeds_url.append(feeds_url[i])

            f.writelines(new_feeds_url)

def initialize():
    if not path.exists("crawl_results.csv"):
        # Create a results file with headers
        data_headers = [
            "hash",
            "summary",
            "title",
            "content",
            "article_url",
            "feed_url",
            "publish_date"
        ]
        with open('crawl_results.csv', 'a+') as f:
            f.write(','.join(data_headers))
    
    if not path.exists("feeds_url.txt"):
        # Export RSS feeds' URL to file
        get_feeds_url()

if __name__ == '__main__':
    initialize()
    get_data_to_csv()
    # get_data_to_db()


# Key extracting
## source
# // feed.feed.docs for overall
# // feed.entries[idx].link(s) for detail
# // feed.entries[idx].title_detail.base for RSS source hyperlink
## date // feed.feed.published
## unicity // feed.entries[0].id
## Can I get more than 30 article per RSS feed request? (Can not)
## How do I get all RSS feed via an RSS aggregator site? (find_feed)

# Stucture of the JSON dataset
# [{
#     "site": "",
#     "feeds": [
#         {
#             "rss_url": "",
#             "articles": [{
#                 "hash": "",
#                 "summary": "",
#                 "title": "",
#                 "content": "",
#                 "url": "",
#                 "publish_date": "",
#             }]
#         }
#     ]
# }]

# Structure of an article
# "rss_url": "",
# "articles": [{
#     "hash": "",
#     "summary": "",
#     "title": "",
#     "content": "",
#     "url": "",
#     "publish_date": "",