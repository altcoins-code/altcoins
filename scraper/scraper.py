import json
import os
import pandas as pd
import requests
import webbrowser
from bs4 import BeautifulSoup
from datetime import datetime

from constants import NUMERIC, ORDER, RAW_COLS


class Scraper:
    def __init__(self):
        self.res = None  # Server response
        self.data = None  # Organized data
        self.timestamp = None
        self.page = 1  # first N pages
        self.btc_usd = None  # for conversion to usd
        self.images = None

    def pull(self):
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
        self.res = requests.get(url).text

    def process(self):
        # process scraped response data

        def get_plots(res):
            # Scrapes for the sign of the percent change
            soup = BeautifulSoup(res, 'html5lib')
            plot_map = {}
            for coin in soup.findAll("tr"):
                info = coin.find("td", {"class": "td-coin"})
                if info:
                    first_nl = info.text.strip().index('\n')
                    key = info.text.strip()[0:first_nl]
                    coin_img = str(info.find('img'))
                    coin_img = coin_img.replace('<img alt="Loader" class="omni-coin-image" data-img', '<img src')
                    data_raw = coin.find("div", {"class": "coin_portfolio_price_chart_mini_plain"})
                    data = json.loads(data_raw.attrs['data-prices'])
                    plot_map[key] = {'img': coin_img, 'week data': data}
            return pd.DataFrame(plot_map).T

        def get_coin_data(coin='bitcoin', cur='usd'):
            url = 'https://www.coingecko.com/en/price_charts/%s/%s' % (coin, cur)
            res = requests.get(url).text
            df = pd.read_html(res, flavor='html5lib')[0]
            for col in df:
                df[col] = df[col].astype('str').str.replace(',', '').str.replace('$', '')
            df[['Price', 'Market Cap', 'Trading Volume']] = df[['Price', 'Market Cap', 'Trading Volume']].apply(
                pd.to_numeric)
            return df

        def get_sign_map(res):
            # Scrapes for the sign of the percent change
            soup = BeautifulSoup(res, 'html5lib')
            sign_map = {}
            for coin in soup.findAll("td", {"class": "text-center td-market_cap"}):
                amount = coin.text.strip().split().pop().replace('%', '')
                sign = 1 if coin.find('i', {'class': 'fa fa-caret-up'}) else -1
                sign_map[amount] = sign
            return sign_map

        def clean_first_coin_row(row):
            # first row has messed up spacing which failes `clean_coin_col()`
            return row.replace(row[0:row.index(' ')], row[0:row.index(' ')] + ' ').replace('$', ' $').replace('฿', ' ฿')

        def clean_coin_col(col):
            # Make all lists the same length, pad with '(N/A)'
            for r in col:
                if r[2] == '-':
                    r[2] = 'N/A'
                if len(r) > 4:  # merge speed and hash
                    r[2] = r[2] + ' ' + r.pop(3)
                r[3] = r[3].replace('฿', '')

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
        plot_map = get_plots(self.res)
        if not self.btc_usd and self.page == 1:  # get btc price on page 1
            self.btc_usd = get_coin_data(coin='bitcoin')['Price'][0]
        self.timestamp = datetime.utcnow()
        df = pd.read_html(self.res, flavor='html5lib')[0]
        df = df[df.columns[1:13]]
        df.columns = RAW_COLS
        # TODO make a clean function that removes all bad chars (btc char, $, % ect) then just clean all cols
        df['coin'][0] = clean_first_coin_row(df['coin'][0])
        df = convert_col_type(df)

        # Split coin info
        df['coin'] = clean_coin_col(df['coin'])
        df[['abr', 'name', 'hash', 'price btc']] = pd.DataFrame(df['coin'].values.tolist())

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
        df = df.set_index(df['abr'].values)
        df = df[~df.index.duplicated(keep='first')]  # if duplicate coin keys
        df = pd.concat([plot_map, df], axis=1, join='inner')  # merge plots with data
        df = df.drop(['coin', 'dev stats 1', 'dev stats 2', 'social stats 1', 'social stats 2', 'search stats'], axis=1)
        df[NUMERIC] = df[NUMERIC].apply(pd.to_numeric)
        df['price usd'] = df['price btc'].apply(lambda x: x * self.btc_usd)
        df = df[ORDER]
        return df

    # TODO abstract this out and combine with flask fcns
    def generate_html(self, name='temp.html'):
        def url_from_coin(name):
            coin_url = 'https://coinmarketcap.com/currencies/' + name.lower()
            return '<a href="%s" target="_blank">%s</a>' % (coin_url, name)

        pd.set_option('display.max_colwidth', -1)
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
        df = self.data
        df = df.drop(['week data'], axis=1)
        cols = list(df)
        cols.insert(0, cols.pop(cols.index('img')))
        df = df[cols]
        df['name'] = df['name'].apply(url_from_coin)
        foot = '''</body></html>'''
        table = df.to_html(escape=False).replace('class="dataframe"', 'class="sortable"')
        path = os.path.abspath(name)
        html = head + table + foot
        with open(path, 'w') as f:
            f.write(html)
        webbrowser.open('file://' + path)


if __name__ == "__main__":
    # from db import MongoDB
    # store = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017) # for inside docker
    s = Scraper()
    s.pull()
    # store.update(s)
    s.data.to_pickle('test.pkl')
    # s.generate_html('temp.html')
