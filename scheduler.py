import schedule
import time
from datetime import datetime

from crawl import initialize, get_data_to_db

def call_crawler():
    print("Crawler called at:", datetime.datetime.now())
    get_data_to_db()

def scheduling():
    # loop every 2 hours
    schedule.every(2).hours.do(call_crawler)

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    initialize()
    scheduling()