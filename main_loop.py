import traceback

import sys
import time

from scraper import Scraper

SCRAPE_FREQ = 20  # minutes

if __name__ == "__main__":

    s = Scraper()
    print("Starting scraper...")
    while True:
        # print("{}: Starting scrape cycle".format(time.ctime()))
        try:
            s.pull()
        except KeyboardInterrupt:
            print("Exiting....")
            sys.exit(1)
        except Exception as exc:
            print("Error with the scraping:", sys.exc_info()[0])
            traceback.print_exc()
        else:
            print("{}: Successfully finished scraping".format(s.timestamp))
        time.sleep(SCRAPE_FREQ * 60)
