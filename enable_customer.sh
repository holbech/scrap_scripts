#!/bin/bash

curl http://centr-001a.prd.mojn001:6000/settings/$1/SiteStatus | sed 's/"approved":false/"approved":true/' > ss_$1
curl -i -X POST centr-001a.prd.mojn001:6000/settings/$1/SiteStatus -H "Content-Type: application/json" --data-binary "@./ss_$1"
rm ss_$1

