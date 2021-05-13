# import urllib2 python2
import urllib.request
from bs4 import BeautifulSoup

website_list = ['https://vnexpress.net', 'https://tuoitre.vn', 'https://thanhnien.vn', 'https://dantri.com.vn', 'https://vietnamnet.vn']

def crawl_html(website):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    page = opener.open(website)
    soup = BeautifulSoup(page, "lxml")
    div = soup.find_all('a')

    # items = soup.findAll('title=')
    # print(items)
    f = open("thanhien.html", "w", encoding='utf-8')
    f.write(str(div))
    f.close()

def main():
    crawl_html('https://thanhnien.vn/giai-tri/tran-thanh-treo-thuong-cho-cau-be-khuyet-tat-da-moi-qua-bong-nhan-5-trieu-dong-1382282.html')

if __name__ == "__main__":
    main()