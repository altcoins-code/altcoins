import os
import pandas as pd
from flask import Flask, render_template

from scraper.db import MongoDB
from scraper.constants import ORDER

app = Flask(__name__)

# TODO set up dev flag that loads a pandas df rather than mongo
db = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017)  # for inside docker
# db = MongoDB(host='localhost', port=27017)  # debug

def create_plots(data):
    # iterate of array of raw data and make svg plot
    plots = []
    for i, row in enumerate(data):
        id = 'plot%d' % i
        fcn = "plot('%s', %s)" % (id, str(row))
        svg_str = '<svg id="%s" onload="%s"/>' % (id, fcn)
        plots.append(svg_str)
    return plots


def df_to_html(df):
    pd.set_option('display.max_colwidth', -1)
    df['week data'] = create_plots(df['week data'].values)
    # df = df.drop(['week data'], axis=1)
    cols = list(df)  # reorder
    cols.insert(0, cols.pop(cols.index('img')))
    cols.insert(9, cols.pop(cols.index('week data')))
    df = df[cols]
    return df.to_html(escape=False).replace('class="dataframe"', 'class="sortable"')


@app.route('/')
def update():
    print("Updating coin data...")
    entry = db.pop()
    timestamp = entry['date'].strftime('%m-%d-%Y %H:%M')
    df = pd.DataFrame(entry['data']).T
    df = df[ORDER].sort_values('overall score', ascending=False)
    html_table = df_to_html(df)
    return render_template('data.html', timestamp=timestamp, table=html_table)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
