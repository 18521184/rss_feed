import schedule
import time
from datetime import datetime

from crawl import initialize, get_data_to_db
from dbconnector import create_connector

def call_crawler(db):
    print("Crawler called at:", datetime.now())
    # Crawl data from RSS feeds and upload those to the database
    get_data_to_db(db)

def scheduling(db):
    # loop every 60 minutes
    schedule.every(60).minutes.do(lambda: call_crawler(db))

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    initialize()
    db = create_connector()
    scheduling(db)