import os
from datetime import datetime

from git import Repo

from create_html import save_html, fetch_from_app

# Update site at: https://jake-g.github.io/altcoins/

url = 'http://localhost:5000'
repo_path = '../static/'
fname = 'index.html'


def update_static_page():
    page = fetch_from_app(url).replace('/static/', '')  # replace to fix path to css and js
    save_html(page, os.path.join(repo_path, fname))
    git_push()


def git_push():
    time = datetime.utcnow().strftime('%m-%d-%Y %H:%M')
    repo = Repo(repo_path)
    assert not repo.bare
    repo.git.commit(fname, '-m', time)
    repo.git.push('origin', 'gh-pages')
