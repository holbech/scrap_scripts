#!/bin/bash

s3cmd ls -r $1 | cut -c17-29 | tr -d ' ' | python -c "import sys; print \"$1: \" + str(sum( int(l.strip()) for l in sys.stdin if l.strip() )/1000000000) + \"G\""


