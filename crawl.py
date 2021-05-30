import re, json, feedparser
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from hashlib import md5

import os.path
from os import path

from dbconnector import establish, add
from preprocessing import is_relevant, cleanhtml, find_feeds, normalize

# 
def get_content(url):
    # Crawl and parse meta data of the article from server
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(url)

    soup = BeautifulSoup(page, "lxml")
    content = ''

    try:
        if 'tuoitre.vn' in url:
            # We get the first element in the array because we are sure that 
            # any article on tuoitre.vn only has one div tag with classname "main-content-body"
            # Note that findAll or find_all always return a list 
            raw = soup.findAll("div", {"id": "main-detail-body"})[0]

            # Nonetheless, raw main content body still have some noise
            # such as div tag used for images or suggesting a related article.
            # Thus, we need to get rid of those by extracting p tag only
            # because p tag contains merely paragraph of the content that we need.
            # paras = raw.findAll("p", attrs={"class": None, "style": None})
            paras = raw.findChildren("p", attrs={"style": None}, recursive=False)

            content = ''.join([cleanhtml(str(p)) for p in paras])

        elif 'vnexpress' in url:
            raw = soup.find_all('article', attrs={"class": "fck_detail"})[0]
            paras = raw.find_all('p', attrs={'class': "Normal", 'style': None, 'id': None})

            content = ' '.join([cleanhtml(str(p)) for p in paras])

        elif 'thanhnien.vn' in url:
            raw = soup.findAll("div", {"id": "abody"})[0]
            divs = raw.findAll("div", attrs={"class": None, "id": None, "style": None})
                
            new_divs = []
            for div in divs:
                s = str(div)
                if '<table ' not in s and 'Ảnh: ' not in s:
                    new_divs.append(cleanhtml(s))

            content = ''.join(new_divs)

        elif 'nld.com.vn' in url:
            raw = soup.findAll("div", {"class": "content-news-detail old-news"})[0]
            content = ''.join([cleanhtml(str(p)) for p in raw.findAll("p", attrs={"class": None, "style": None})])
            
        elif 'vietnamnet.vn' in url:
            raw_list = soup.findAll("div", {"id": "ArticleContent"})
            if len(raw_list) <= 0:
                raw_list = soup.findAll("div", {"id": "Magazine-Acticle"})[0]

            raw = raw_list[0]
            paras = raw.findAll("p", attrs={"class": None, "style": None})
            if (len(paras) == 0):
                paras = raw.findAll("p", attrs={"class": "t-j", "style": None})
            
            new_paras = []
            for i in range(len(paras)-1):
                if len(paras[i].findAll("iframe")) >0:
                    continue
                new_paras.append(cleanhtml(str(paras[i])))
            content = ' '.join(new_paras)

    except Exception as err:
        print('Error at:',url)
        print('Error details:', err)
        write_log(url, err)
        return content

    content = normalize(content)

    return content

def write_log(url, err):
    with open('debug.txt', 'a+') as f:
        f.write(str(url) + '\n' + str(err) + '\n')

# Get unicity by MD5 hash
def get_id(url):
    return md5(str(url).encode()).hexdigest()

def crawl(url):
    data = {
        "rss_url": url,
        "articles": []
    }

    # Test with particular RSS feed
    feed = feedparser.parse(url)

    for i in range(len(feed.entries)):
        # Get a sample article URL
        # Also its title
        url = feed.entries[i].links[0]['href']
        title = feed.entries[i].title
        summary = cleanhtml(feed.entries[i].summary)  

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
        # content_header = cleanhtml(str(raw_content.findAll("h2", {"class": "sapo"})[0]))

        # Get id and date of the article
        id = get_id(url)
        date = feed.entries[i].published

        data['articles'].append({
            "id": id,
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
    
    # cnt = 0
    data = None
    with open('crawl_results.csv', 'a+') as f:
        f.write('\n')
        for i in range(len(feeds_url)):
            data = crawl(feeds_url[i])
            if data:
                # Count number of articles in this RSS feed
                n_articles = len(data['articles'])
                
                # Convert and import articles as CSV entries into CSV file 
                for j in range(n_articles):
                    entry = ','.join([
                        data['articles'][j]['id'],
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
                    
                print('Successfully crawl {} articles from {}'.format(n_articles, feeds_url[i]))

# MySQL included
def get_data_to_db():
    db = establish()

    feeds_url = None
    # Import list of RSS feeds 
    with open('feeds_url.txt', 'r') as f:
        feeds_url = f.read().split('\n')
    
    data = None
    for i in range(len(feeds_url)):
        data = crawl(feeds_url[i])
        if data:
            # Count number of articles in this RSS feed
            n_articles = len(data['articles'])
            add(db, data, feeds_url[i])        
            print('Successfully added {} articles from {} to database'.format(n_articles, feeds_url[i]))

def get_feeds_url():
    # List of sites to be ignored due to not containing usable information
    blacklist = [
        'video'
    ]
    # Aggregate all RSS feeds URL from RSS aggregator site
    rss_aggr_urls = [
        'https://tuoitre.vn/rss.htm',
        'https://vnexpress.net/rss',
        'https://thanhnien.vn/rss.html',
        'http://vietnamnet.vn/vn/rss/',
        'https://nld.com.vn/rss.htm'
    ]
    with open('feeds_url.txt', 'a+') as f:
        for url in rss_aggr_urls:
            feeds_url = find_feeds(url)
            new_feeds_url = []

            n_feeds = len(feeds_url)
            # Validate each RSS feed uRL
            for i in range(n_feeds):
                flag = True
                # Check if URL containing word in blacklist
                for word in blacklist:
                    if word in feeds_url[i]:
                        flag = False
                        break 
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
            "id",
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
    # get_data_to_csv()
    get_data_to_db()


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
#                 "id": "",
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
#     "id": "",
#     "summary": "",
#     "title": "",
#     "content": "",
#     "url": "",
#     "publish_date": "",