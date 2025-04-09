#!/usr/bin/env bash

ID=$1

curl -v --negotiate -u : "$SOLR_API_URL/admin/collections" \
  --data-urlencode action=REQUESTSTATUS \
  --data-urlencode requestid=$ID
