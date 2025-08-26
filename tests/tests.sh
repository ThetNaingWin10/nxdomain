#!/bin/bash

# first install coverage.py:
# https://coverage.readthedocs.io/en/latest/install.html

coverage erase
#file not found error
coverage run --append /Users/thetnaingwin/Desktop/INFO1112/"Assignment 2"/nxdomain/server.py invalidfile
sleep 2
echo fake recursor sends EXIT
printf '!EXIT\n' | nc localhost 1024
sleep 0.1
#too many arguments, also covered less arguments
coverage run --append /Users/thetnaingwin/Desktop/INFO1112/"Assignment 2"/nxdomain/server.py adsf adfads
sleep 2
echo fake recursor sends EXIT
printf '!EXIT\n' | nc localhost 1024
sleep 0.1

coverage run --append /Users/thetnaingwin/Desktop/INFO1112/"Assignment 2"/nxdomain/server.py sample.conf &
sleep 2
echo fake recursor sends EXIT
printf '!EXIT\n' | nc localhost 1024
sleep 0.1

coverage report -m


