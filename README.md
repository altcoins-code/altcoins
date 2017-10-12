docker-scraper
-----

* run all: `docker-compose up`
* build: `docker-compose build`
* delete: `docker-compose rm` or `docker-compose rm db or web`
* list active: `docker-compose ps`

### Scraper
* witchraft python that scrapes crypto apis
* builds coin features
* stores into mongo (not efficiently)
* pushes to git for github.io Note: need to setup ssh in .ssh-sample if you want to push the site to github.io

### Webapp
* runs locally on your localhost port 5000
* could be hosted on a server
* could be fetched and pushed to github
* `static/` and `templates/`

###  MongoDB
* make sure mongo db is running (`docker-compose up` or `docker-compose run db`)
* create a folder in this dir called `mongodb-backup`

* backup:
`docker exec -t  crypto_db_1 mongodump --out /data/db/backup`

* Note: from outside container you can remote in and backup (windows): `mongodump --host 10.0.75.1 --port 27017  --out [folder]`
* restore:
`docker exec -t  crypto_db_1 mongorestore /data/db/backup/coins -d coins` (replace coins with db name)

* delete:
 `docker exec -t  crypto_db_1 mongo coins --eval "db.dropDatabase()"`

* forward port
`ssh -N -f -L localhost:5000:localhost:5000 jk@128.95.116.87`


another way to connect to mongo
* shell inside: `docker exec -it  crypto_db_1 /bin/bash`
* lots of commands in consolse like to delete....
```
$ mongo
use {database_name};
db.dropDatabase();
```
