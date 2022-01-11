#!/bin/bash
screen -dmS elogger
screen -S elogger -X stuff "python /home/pi/emeter/elogger.py\n"
