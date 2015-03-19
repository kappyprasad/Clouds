#!/bin/bash

for json in $*
do
    #pyson.py -c $json
    message=$(echo $json | sed -e "s/.json/.Message.json/")
    pyson.py -td Message $json > $message
    ./myMessages.py -t Message $message
done
