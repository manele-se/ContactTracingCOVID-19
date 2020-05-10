""" controlling time"""
#client and server must know the time and paus
#read time now
#modify time speed
import time as real_time
import datetime
import threading

#one day takes two minutes
TIME_SPEED = (24 * 60) / 2
SECONDS_PER_DAY = 24 * 60 * 60

#In real time, the world starts 10 May 2020 at midnight UTC
WORLD_START_UNIXTIME = 1589068800

local_storage = threading.local()

def time():
    return (real_time.time() - WORLD_START_UNIXTIME) * TIME_SPEED

def get_today_index():
    now = time()
    today = int(now / SECONDS_PER_DAY)
    return today

def sleep(seconds):
    real_time.sleep(seconds / TIME_SPEED)

def task_sleep(seconds):
    """sleep function for periodic tasks without time skew"""
    #get the current baseline#
    last_baseline = getattr(local_storage, 'last_baseline', None)
    if last_baseline is None:
        last_baseline = time()
    
    #create a new baseline#
    new_baseline = last_baseline + seconds
    
    #sleep the right amount of time#
    diff = new_baseline - time()
    if diff > 0:
        sleep(diff)
    
    #store the new current baseline#
    local_storage.last_baseline = new_baseline
