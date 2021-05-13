import feedparser

python_wiki_rss_url = "https://thanhnien.vn/giai-tri/tran-thanh-treo-thuong-cho-cau-be-khuyet-tat-da-moi-qua-bong-nhan-5-trieu-dong-1382282.html"

feed = feedparser.parse(python_wiki_rss_url)

# print(feed)
f = open("out.rss", "w", encoding='utf-8')
f.write(str(feed))
f.close()