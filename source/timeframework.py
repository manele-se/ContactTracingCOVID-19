""" controlling time"""
#client and server must know the time and paus
#read time now
#modify time speed
import time
import datetime

TIME_SPEED= 720
SECONDS_PAR_DAY=24*60*60


def get_today_index(self):
    return int(time.time()/TIME_SPEED/SECONDS_PAR_DAY)
    