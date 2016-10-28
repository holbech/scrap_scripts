#!/bin/bash

cat $1 | python -mjson.tool > $1_ && mv $1_ $1

