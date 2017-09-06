import json
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from constants import NUMERIC, ORDER, RAW_COLS


class Scraper:
    def __init__(self):
        self.res = None  # Server response
        self.data = None  # Organized data
        self.timestamp = None
        self.page = 1  # first N pages
        self.images = None

    def pull(self):
        """Pull and format data into datafram"""
        frames = []
        base_url = 'https://www.coingecko.com/en?page='
        n_pages = 3
        for page in range(1, n_pages + 1):
            # gets features for each coin
            # print('Scraping page %d...' % page)
            self.page = page
            self.fetch(base_url + str(page))
            frames.append(self.process())
        self.data = pd.concat(frames)

    def fetch(self, url):
        """Get source"""
        self.res = requests.get(url).text

    def process(self):
        """Process scraped response data"""

        def get_coin_assets(res):
            """Scrapes harder to find stuff like coin icon, week plot and raw btc value"""

            class Coin():
                def __init__(self, coin_tag):
                    self.tag = coin_tag
                    self.info = coin_tag.find("td", {"class": "td-coin"})
                    if self.info:  # coin is probably legit
                        self.key = self.get_coin_key()
                        self.frame = self.get_frame()

                def get_precise_btc(self):
                    raw_btc = self.tag.find("span", {"class": "currency-exchangable"})
                    if raw_btc and raw_btc['data-price-btc']:
                        return float(raw_btc['data-price-btc'])  # high precision

                def get_week_data(self):
                    data_raw = self.tag.find("div", {"class": "coin_portfolio_price_chart_mini_plain"})
                    return json.loads(data_raw.attrs['data-prices'])

                def get_coin_icon(self):
                    _img = str(self.info.find('img'))
                    return _img.replace('<img alt="Loader" class="omni-coin-image" data-img', '<img src')

                def get_coin_key(self):
                    first_nl = self.info.text.strip().index('\n')
                    return self.info.text.strip()[0:first_nl]  # coin key

                def get_frame(self):
                    return {
                        'img': self.get_coin_icon(),
                        'price btc': self.get_precise_btc(),
                        'week data': self.get_week_data()
                    }

                def exists(self):
                    try:
                        _exists = self.key and self.frame
                        return _exists
                    except:
                        return False

            frame = {}
            soup = BeautifulSoup(res, 'html5lib')
            for c in soup.findAll("tr"):
                coin = Coin(c)
                if coin.exists():
                    frame[coin.key] = coin.frame
            return pd.DataFrame(frame).T

        def get_coin_data(coin='bitcoin', cur='usd'):  # DEPRECATED
            """Scrape info from coin specific page"""
            url = 'https://www.coingecko.com/en/price_charts/%s/%s' % (coin, cur)
            res = requests.get(url).text
            df = pd.read_html(res, flavor='html5lib')[0]
            for col in df:
                df[col] = df[col].astype('str').str.replace(',', '').str.replace('$', '')
            df[['Price', 'Market Cap', 'Trading Volume']] = df[['Price', 'Market Cap', 'Trading Volume']].apply(
                pd.to_numeric)
            return df

        def get_sign_map(res):
            """Scrapes for the sign of the percent change"""
            soup = BeautifulSoup(res, 'html5lib')
            sign_map = {}
            for coin in soup.findAll("td", {"class": "text-center td-market_cap"}):
                amount = coin.text.strip().split().pop().replace('%', '')
                sign = 1 if coin.find('i', {'class': 'fa fa-caret-up'}) else -1
                sign_map[amount] = sign
            return sign_map

        def clean_first_coin_row(row):  # DEPRECATED
            # first row has messed up spacing which failes `clean_coin_col()`
            return row.replace(row[0:row.index(' ')], row[0:row.index(' ')] + ' ').replace('$', ' $').replace('฿', ' ฿')

        def clean_coin_col(col):
            """Split coin info section into columns"""
            for r in col:
                # Make all lists the same length, pad with '(N/A)'
                if r[2] == '-':
                    r[2] = 'N/A'
                if len(r) > 4:  # merge speed and hash
                    r[2] = r[2] + ' ' + r.pop(3)
                r[2] = r[2].replace('(N/A)', '')
                # r[3] = r[3]
            return col

        def convert_col_type(df):
            """Make strings into list (seperated by '  ')"""
            for col in df.columns:
                if 'score' in col:
                    df[col] = df[col].astype('int')
                else:
                    df[col] = df[col].astype('str').str.split('  ')
            return df

        # Set up data
        sign_map = get_sign_map(self.res)
        asset_df = get_coin_assets(self.res)
        self.timestamp = datetime.utcnow()

        df = pd.read_html(self.res, flavor='html5lib')[0]
        df = df[df.columns[1:13]]
        df.columns = RAW_COLS
        df = convert_col_type(df)

        # Split coin info
        df['coin'] = clean_coin_col(df['coin'])
        df[['abr', 'name', 'hash', 'price usd']] = pd.DataFrame(df['coin'].values.tolist())

        # Split unit features
        df[['market cap', 'percent change']] = pd.DataFrame(df['market cap'].values.tolist())
        df['liquidity'] = pd.DataFrame(df['liquidity'].values.tolist())
        currency_cols = ['market cap', 'liquidity', 'price usd']  # with leading ฿ or $ to strip
        df[currency_cols] = df[currency_cols].replace(['฿', '\$', ','], '', regex=True)
        df['percent change'] = df['percent change'].str.replace('%', '')
        df['percent change'] = df['percent change'].apply(lambda x: sign_map[x] * float(x))

        # Split stats
        df[['stars', 'forks', 'watchers', 'total issues', 'closed issues']] = pd.DataFrame(
            df['dev stats 1'].values.tolist())
        df[['merged pr', 'contributors', 'recent commits']] = pd.DataFrame(df['dev stats 2'].values.tolist())
        df[['subscribers', 'active users', 'posts per hr', 'comments per hr']] = pd.DataFrame(
            df['social stats 1'].values.tolist())
        df[['fb likes', 'twitter followers']] = pd.DataFrame(df['social stats 2'].values.tolist())
        df[['bing results', 'alexa rating']] = pd.DataFrame(df['search stats'].values.tolist())
        df['bing results'] = df['bing results'].str.replace(',', '')

        # Clean and format
        df = df.set_index(df['abr'].values)
        df = df[~df.index.duplicated(keep='first')]  # if duplicate coin keys
        df = pd.concat([asset_df, df], axis=1, join='inner')  # merge plots with data
        df = df.drop(['coin', 'dev stats 1', 'dev stats 2', 'social stats 1', 'social stats 2', 'search stats'], axis=1)
        df[NUMERIC] = df[NUMERIC].fillna(0).apply(pd.to_numeric)
        df = df[ORDER]
        return df


if __name__ == "__main__":
    # from db import MongoDB
    # store = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017) # for inside docker
    s = Scraper()
    s.pull()
    print(s.data.head())
    # store.update(s)
    # s.data.to_pickle('test.pkl')
