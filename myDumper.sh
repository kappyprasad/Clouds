#!/bin/bash

BUCKET=$(myStorage.py -l | grep edson-ums)

myStorage.py -b $BUCKET -d | xargs -r myStorage.py -b $BUCKET -g 

