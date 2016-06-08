curl http://centr-001a.prd.mojn001:6000/settings/SiteStatus | python -mjson.tool |  grep "isOk\|: {" | sed 's/isOk//' | tr -d '":,{' | paste - -

