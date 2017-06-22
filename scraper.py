import os
import webbrowser
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

NUMERIC = ['mining hw cost', 'price', 'market cap', 'percent change', 'liquidity', 'stars', 'forks', 'watchers',
           'total issues', 'closed issues', 'merged pr', 'contributors', 'recent commits', 'subscribers',
           'active users', 'posts per hr', 'comments per hr', 'fb likes', 'twitter followers', 'bing results',
           'alexa rating']
ORDER = ['name', 'price', 'overall score', 'dev score', 'social score', 'search score', 'percent change', 'market cap',
         'liquidity', 'stars', 'forks', 'watchers', 'total issues', 'closed issues', 'merged pr', 'contributors',
         'recent commits', 'subscribers', 'active users', 'posts per hr', 'comments per hr', 'fb likes',
         'twitter followers', 'bing results', 'alexa rating', 'abr', 'hash', 'hash speed', 'mining hw cost']
RAW_COLS = ['coin', 'overall score', 'market cap', 'liquidity', 'dev score', 'dev stats 1',
            'dev stats 2', 'social score', 'social stats 1', 'social stats 2',
            'search score', 'search stats']


class Scraper:
    def __init__(self):
        self.res = None  # Server response
        self.data = None  # Organized data
        self.timestamp = None
        self.url = 'https://www.coingecko.com/en'
        self.db = self.init_db()

    def pull(self):
        # gets features for each coin
        self.fetch()
        self.process()
        self.update_db()

    def fetch(self):
        self.res = requests.get(self.url).text

    def process(self):
        # process scraped response data

        def get_sign_map(res):
            # Scrapes for the sign of the percent change
            soup = BeautifulSoup(res, 'html5lib')
            sign_map = {}
            for coin in soup.findAll("td", {"class": "text-center td-market_cap"}):
                amount = coin.text.strip().split().pop().replace('%', '')
                sign = 1 if coin.find('i', {'class': 'fa fa-caret-up'}) else -1
                sign_map[amount] = sign
            return sign_map

        def clean_coin_col(col):
            # Make all lists the same length, pad with '(N/A)'
            for r in col:
                if r[2] == '-':
                    r[2] = 'N/A'
                r[3] = r[3].replace('(', '').replace(')', '')
                if len(r) < 6:
                    r.insert(4, '')
                else:
                    r[4] = r[4].replace('$', '').replace(',', '')
                r[5] = r[5].replace('฿', '')

            return col

        def convert_col_type(df):
            # Make strings into list (seperated by '  ')
            for col in df.columns:
                if 'score' in col:
                    df[col] = df[col].astype('int')
                else:
                    df[col] = df[col].astype('str').str.split('  ')
            return df

        # Set up data
        sign_map = get_sign_map(self.res)
        self.timestamp = datetime.utcnow()
        df = pd.read_html(self.res, flavor='html5lib')[0]
        df = df[df.columns[1:13]]
        df.columns = RAW_COLS
        df['coin'][0] = df['coin'][0].replace(df['coin'][0][0:3], df['coin'][0][0:3] + ' ').replace('(', ' (').replace(
            '$', ' $').replace('฿', ' ฿')
        df = convert_col_type(df)

        # Split coin info
        df['coin'] = clean_coin_col(df['coin'])
        df[['abr', 'name', 'hash', 'hash speed', 'mining hw cost', 'price']] = pd.DataFrame(df['coin'].values.tolist())

        # Split unit features
        df[['market cap', 'percent change']] = pd.DataFrame(df['market cap'].values.tolist())
        df['liquidity'] = pd.DataFrame(df['liquidity'].values.tolist())
        df['market cap'] = df['market cap'].str.replace('฿', '')
        df['liquidity'] = df['liquidity'].str.replace('฿', '')
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
        df = df.drop(['coin', 'dev stats 1', 'dev stats 2', 'social stats 1', 'social stats 2', 'search stats'], axis=1)
        df[NUMERIC] = df[NUMERIC].apply(pd.to_numeric)
        df = df[ORDER]
        self.data = df

    def generate_html(self, name='temp.html'):
        head = '''
        <!DOCTYPE html><html>
        <head>
        <title>%s</title>
        <link href="style.css" rel="stylesheet">
        <script src="sorttable.js"></script>
        </head>
        <body>
        <b>%s</b>
        ''' % (self.timestamp, self.timestamp)
        foot = '''</body></html>'''
        table = self.data.to_html().replace('class="dataframe"', 'class="sortable"')
        path = os.path.abspath(os.path.join('web', name))
        html = head + table + foot
        with open(path, 'w') as f:
            f.write(html)
        webbrowser.open('file://' + path)

    def init_db(self):
        client = MongoClient("localhost", 27017)
        db = client.coins
        collection = 'timeseries'
        if not collection in db.collection_names():
            print('Creating collection %s in coins db...' % collection)
            db.create_collection('timeseries')
        return db

    def update_db(self):
        self.data = self.data.set_index('abr')  # index by abr
        self.db.timeseries.insert_one({'date': self.timestamp, 'data': self.data.T.to_dict()})



        #
        # def get_images_map(res):
        #     # Scrapes for the sign of the percent change
        #     soup = BeautifulSoup(res, 'html5lib')
        #     img_map = {}
        #     plot_map = {}
        #
        #     for coin in soup.findAll("tr"):
        #         info = coin.find("td", {"class": "td-coin"})
        #         if info:
        #             key = info.text.strip()[0:3]
        #             img = str(info.find('img'))
        #             img = img.replace('<img alt="Loader" class="omni-coin-image"', '<img')
        #             img_map[key] = img
        #
        #             plot = coin.find("div", {"class": "coin_portfolio_price_chart_mini_plain"})
        #             print(plot.find("data-prices"))
        #             plot_map[key] = plot
        #
        #     return img_map


if __name__ == "__main__":
    s = Scraper()
    s.pull()
    # s.data.to_pickle('test.pkl')
    s.generate_html('temp.html')
