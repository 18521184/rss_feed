import schedule
import time
from datetime import datetime

def my_code():
    print(datetime.time(datetime.now()))

def main():
    # loop every 10 seconds
    schedule.every(10).seconds.do(my_code)

    # loop every 6 hours
    # schedule.every(6).hour.do(my_code)

    # loop everyday at 6 am
    # schedule.every().day.at("6:00").do(my_code)
    while 1:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()