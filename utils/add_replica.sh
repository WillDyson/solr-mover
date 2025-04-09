#!/usr/bin/env bash

COL=$1
SHARD=$2
NODE=$3

ID=$(uuidgen)

curl -v --negotiate -u : "$SOLR_API_URL/admin/collections" \
  --data-urlencode action=ADDREPLICA \
  --data-urlencode collection=$COL \
  --data-urlencode shard=$SHARD \
  --data-urlencode node=$NODE \
  --data-urlencode async=$ID

echo $ID
