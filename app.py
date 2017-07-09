from flask import Flask, render_template
import os

from scraper.create_html import get_df_from_db, df_to_html
from scraper.db import MongoDB

app = Flask(__name__)

# TODO set up dev flag that loads a pandas df rather than mongo
db = MongoDB(host=os.environ['DB_PORT_27017_TCP_ADDR'], port=27017)  # for inside docker
# db = MongoDB(host='localhost', port=27017)  # debug


@app.route('/')
def update():
    print("Updating coin data...")
    df, timestamp = get_df_from_db(db)
    html_table = df_to_html(df)
    return render_template('data.html', timestamp=timestamp, table=html_table)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
