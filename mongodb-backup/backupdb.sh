#!/usr/bin/env bash

echo 'Current containers'
docker ps

echo 'Dumping backup from crypto_db_1 mongodump...'
docker exec -t  crypto_db_1 mongodump --out /data/db/backup