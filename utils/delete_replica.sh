#!/usr/bin/env bash

COL=$1
SHARD=$2
REPLICA=$3

ID=$(uuidgen)

curl -v --negotiate -u : "$SOLR_API_URL/admin/collections" \
  --data-urlencode action=DELETEREPLICA \
  --data-urlencode collection=$COL \
  --data-urlencode shard=$SHARD \
  --data-urlencode replica=$REPLICA \
  --data-urlencode async=$ID

echo $ID
