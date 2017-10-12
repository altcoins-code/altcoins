import sys
import time
import traceback
import os

from mongo import MongoDB
from scraper import Scraper
from static_site import update_static_page

SCRAPE_FREQ = 20  # minutes
NPAGE = 3 # number of altcoin pages to scrape

def scraper_loop():
    db = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017)
    # db = MongoDB(host='localhost', port=27017)  # local flag

    s = Scraper()
    print("Starting scraper...")
    while True:
        try:
            s.pull(n_pages=NPAGE) # number of altcound pages to scrape)
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
