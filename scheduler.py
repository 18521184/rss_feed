import schedule
import time
from datetime import datetime

from crawl import initialize, get_data_to_db
from dbconnector import get_db_session

def call_crawler(db):
    print("Crawler called at:", datetime.now())
    get_data_to_db(db)

def scheduling(db):
    # loop every 2 hours
    schedule.every(2).hours.do(lambda: call_crawler(db))

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    initialize()
    db = get_db_session()
    scheduling(db)