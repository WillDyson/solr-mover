#!/usr/bin/env bash

COL=$1
REPLICA=$2
TARGET_NODE=$3

ID=$(uuidgen)

curl -v --negotiate -u : "$SOLR_API_URL/admin/collections" \
  --data-urlencode action=MOVEREPLICA \
  --data-urlencode collection=$COL \
  --data-urlencode targetNode=$TARGET_NODE \
  --data-urlencode replica=$REPLICA \
  --data-urlencode async=$ID

echo $ID
