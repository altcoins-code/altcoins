import pandas as pd
import pytz

def create_plots(data):
    # iterate of array of raw data and make svg plot
    plots = []
    for i, row in enumerate(data):
        id = 'plot%d' % i
        fcn = "plot('%s', %s)" % (id, str(row))
        svg_str = '<svg id="%s" onload="%s"/>' % (id, fcn)
        plots.append(svg_str)
    return plots


def url_from_coin(name):
    coin_url = 'https://coinmarketcap.com/currencies/' + name.lower()
    return '<a href="%s" target="_blank">%s</a>' % (coin_url, name)


def df_to_html(df, ORDER):
    pd.set_option('display.max_colwidth', -1)
    df = df[ORDER].sort_values('overall score', ascending=False)
    df['week data'] = create_plots(df['week data'].values)
    df['name'] = df['name'].apply(url_from_coin)
    # df = df.drop(['week data'], axis=1)
    cols = list(df)  # reorder
    cols.insert(0, cols.pop(cols.index('img')))
    cols.insert(9, cols.pop(cols.index('week data')))
    df = df[cols]
    return df.to_html(escape=False).replace('class="dataframe"', 'class="sortable"')


def get_df_from_db(db):
    entry = db.pop()
    date = entry['date'].replace(tzinfo=pytz.UTC)
    timestamp = date.astimezone(pytz.timezone('US/Pacific')).strftime('%m-%d-%Y %H:%M')
    return pd.DataFrame(entry['data']).T, timestamp


def save_html(html, path):
    with open(path, 'w') as f:
        f.write(html)
