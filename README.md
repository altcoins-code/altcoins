docker-scraper
-----

* run all: `docker-compose up`
* build: `docker-compose build`
* delete: `docker-compose rm` or `docker-compose rm db or web`
* list active: `docker-compose ps`


###  MongoDB
* make sure mongo db is running (`docker-compose up` or `docker-compose run db`)
* backup: `docker exec -t  crypto_db_1 mongodump --out /data/db/backup`
* Note: from outside container you can remote in and backup (windows): `mongodump --host 10.0.75.1 --port 27017  --out [folder]`
* restore: `docker exec -t  crypto_db_1 mongorestore /data/db/backup/coins -d coins` (replace coins with db name)
* shell inside (for inspecting): `docker exec -it  crypto_db_1 /bin/bash`
* clear: shell inside, then:
```
$ mongo
use {database_name};
db.dropDatabase();
```
