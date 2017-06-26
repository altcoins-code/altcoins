import os

import pandas as pd
from flask import Flask, render_template

from scraper.db import MongoDB
from scraper.constants import ORDER

app = Flask(__name__)

db = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017)  # for inside docker
# db = MongoDB(host='localhost', port=27017)  # debug


def df_to_html(df):
    pd.set_option('display.max_colwidth', -1)
    df = df.drop(['week data'], axis=1)
    cols = list(df)
    cols.insert(0, cols.pop(cols.index('img')))
    df = df[cols]
    return df.to_html(escape=False).replace('class="dataframe"', 'class="sortable"')


@app.route('/')
def update():
    print("Updating coin data...")
    entry = db.pop()
    timestamp = entry['date']
    df = pd.DataFrame(entry['data']).T
    df = df[ORDER].sort_values('overall score', ascending=False)
    html_table = df_to_html(df)
    return render_template('data.html', timestamp=timestamp, table=html_table)


# @app.route('/new', methods=['POST'])
# def new():
#
#     item_doc = {
#         'name': request.form['name'],
#         'description': request.form['description']
#     }
#     db.tododb.insert_one(item_doc)
#
#     return redirect(url_for('todo'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
