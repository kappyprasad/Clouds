#!/bin/bash

clear
message=.messages/$(ls -rt .messages/ | grep -v Message.json | tail -1)
pyson.py -c $message

./myMessages.py $message

child=.messages/$(pyson.py -td MessageId $message).Message.json

pyson.py -td Message $message \
| tee $child \
| pyson.py -c

./myMessages.py $child
