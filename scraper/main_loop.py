import os
import sys
import time
import traceback

from db import MongoDB
from scraper import Scraper

SCRAPE_FREQ = 20  # minutes


def scraper_loop():
    db = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017)

    s = Scraper()
    print("Starting scraper...")
    while True:
        try:
            s.pull()
            db.update(s)

        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print("{}: Successfully finished scraping".format(s.timestamp))
        time.sleep(SCRAPE_FREQ * 60)


if __name__ == "__main__":
    scraper_loop()
