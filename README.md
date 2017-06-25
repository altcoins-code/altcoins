docker-scraper
-----

* run all: `docker-compose up`
* build: `docker-compose build`
* delete: `docker-compose rm` or `docker-compose rm db or web`
* list active: `docker-compose ps`


###  MongoDB
* make sure mongo db is running (`docker-compose up`)
* backup: `docker exec -t  dockerscraper_db_1 mongodump --out /data/db/backup`
* restore: `docker exec -t  dockerscraper_db_1 mongorestore /data/db/backup/coins -d coins` (replace coins with db name)
* shell inside (for inspecting): `docker exec -it  dockerscraper_db_1 /bin/bash`
* clear: shell inside, then:
```
$ mongo
use {database_name};
db.dropDatabase();
```
