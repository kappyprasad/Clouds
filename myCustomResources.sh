#!/bin/bash

./myCloudForge.py -n ladon-$(date +%Y%m%d%H%M%S) CloudFoundry/myCloud.json  | pyson.py -c
