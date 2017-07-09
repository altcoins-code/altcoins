import sys
import time
import traceback
import os

from db import MongoDB
from scraper import Scraper
from static_site import update_static_page

SCRAPE_FREQ = 20  # minutes


def scraper_loop():
    db = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017)
    # db = MongoDB(host='localhost', port=27017)  # debug

    s = Scraper()
    print("Starting scraper...")
    while True:
        try:
            s.pull()
            db.update(s)
            update_static_page()

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
