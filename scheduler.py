import schedule
import time
from datetime import datetime

from crawl import initialize, get_data_to_db
from dbconnector import create_db_engine

def call_crawler(engine):
    print("Crawler called at:", datetime.now())
    # Create new session for database connector from the engine
    db = engine.connect()
    # Crawl data from RSS feeds and upload those to the database
    get_data_to_db(db)
    # Close connection of the db connector
    db.close()

def scheduling(engine):
    # loop every 2 hours
    schedule.every(2).hours.do(lambda: call_crawler(engine))

    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    initialize()
    engine = create_db_engine()
    scheduling(engine)