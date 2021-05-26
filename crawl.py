from calendar import c
import re, json, feedparser

import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

from preprocessing import is_relevant, cleanhtml, find_feeds, normalize

# 
def get_content(url):
    # Crawl and parse meta data of the article from server
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(url)

    soup = BeautifulSoup(page, "lxml")
    content = ''

    if 'tuoitre.vn' in url:
        # We get the first element in the array because we are sure that 
        # any article on tuoitre.vn only has one div tag with classname "main-content-body"
        # Note that findAll or find_all always return a list 
        try:
            raw = soup.findAll("div", {"class": "main-content-body"})[0]
        except Exception as err:
            print(url)
            return content

        # Nonetheless, raw main content body still have some noise
        # such as div tag used for images or suggesting a related article.
        # Thus, we need to get rid of those by extracting p tag only
        # because p tag contains merely paragraph of the content that we need.
        content = ''.join([cleanhtml(str(p)) for p in raw.findAll("p", attrs={"class": None, "style": None})])

    elif 'vnexpress' in url:
        pass
    elif 'thanhnien.vn' in url:
        try:
            raw = soup.findAll("div", {"id": "abody"})[0]
            divs = raw.findAll("div", attrs={"class": None, "id": None, "style": None})
        except Exception as err:
            print(url)
            return content
            
        new_divs = []
        for div in divs:
            s = str(div)
            if '<table ' not in s and 'Ảnh: ' not in s:
                new_divs.append(cleanhtml(s))

        content = ''.join(new_divs)

    elif 'nld.com.vn' in url:
        try:
            raw = soup.findAll("div", {"class": "content-news-detail old-news"})[0]
        except Exception as err:
            print(url)
            return content
        content = ''.join([cleanhtml(str(p)) for p in raw.findAll("p", attrs={"class": None, "style": None})])
    elif 'vietnamnet.vn' in url:
        try:
            raw = soup.findAll("div", {"class": "ArticleContent"})[0]
        except Exception as err:
            try:
                raw = soup.findAll("div", {"class": "Magazine-Acticle"})[0]
            except Exception as err:
                print(url)
                return content
            # return content
        #content = ''.join([cleanhtml(str(p)) for p in raw.findAll("p", attrs={"class": None, "style": None})])
        paras = raw.findAll("p", attrs={"class": None, "style": None})
        if (len(paras)==0):
            paras = raw.findAll("p", attrs={"class": "t-j", "style": None})
        new_paras = []
        for i in range(len(paras)-1):
            if len(paras[i].findAll("iframe")) >0:
                continue
            new_paras.append(cleanhtml(str(paras[i])))
        content = ' '.join(new_paras)
            # content = ''.join([cleanhtml(str(p)) for p in raw.findAll("p", attrs={"class": "t-j", "style": None})])

    content = normalize(content)
    return content

def crawl():
    # # Aggregate all RSS feeds URL from RSS aggregator site
    # rss_aggr_urls = [
    #     'https://tuoitre.vn/rss.htm',
    #     'https://vnexpress.net/rss',
    #     'https://thanhnien.vn/rss.html',
    #     'http://vietnamnet.vn/vn/rss/',
    #     'https://nld.com.vn/rss.htm'
    # ]
    rss_aggr_urls = [
        'https://vietnamnet.vn/vn/rss/'
    ]
    # List of sites to be ignored due to not containing usable information
    blacklist = [
        'thanhnien.vn/video/',
    ]

    for site in rss_aggr_urls:
        feeds_url = find_feeds(site)
        return_data = {
            "site": site,
            "feeds": []
        }
        data = None

        for url in feeds_url:
            # Check if the url is in blacklist
            if url in blacklist:
                continue
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

                # if len(content) != 0 and is_relevant(title)==False and is_relevant(content)==False:
                #     # If none match, continue to another aritcle
                #     continue

                # # Get content's header (somehow as similar as summary)
                # # Note that we can convert bs4.element.XXX to string by str() or call .string attribute
                # # summary field is also content header
                # content_header = cleanhtml(str(raw_content.findAll("h2", {"class": "sapo"})[0]))

                data['articles'].append({
                    "id": feed.entries[i].id,
                    "title": title,
                    # "summary": summary,
                    "content": content
                    # "url": url,
                    # "publish_date": feed.entries[i].published
                })

            return_data['feeds'].append(data)
            if len(data) !=0:
                break
    
    return return_data

def get_data():
    data = []
    data.append(crawl())

    # f = open('crawl_central.txt', 'w+')
    # f.write(json.dumps(data, indent=4, ensure_ascii=False))
    # f.close()

    # print(len(data[0]['feeds'])*len(data[0]['feeds'][0]['articles']))

    # for post in data:
    #     print(post)
    
# get_data()
# print(get_content('https://vietnamnet.vn/vn/thoi-su/thu-tuong-pham-minh-chinh-tiep-tuc-doi-moi-dong-bo-toan-dien-cong-tac-xay-dung-phap-luat-739949.html'))
# print(get_content('https://vietnamnet.vn/vn/giai-tri/nhac/khac-hung-ghen-co-vy-li-lom-khong-sen-sua-hay-khoc-nhu-khac-viet-630053.html'))

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
 