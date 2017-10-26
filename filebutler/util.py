import time

fbTimeFmt = "%Y%m%d-%H%M%S"

def time2str(t):
    return time.strftime(fbTimeFmt, time.localtime(t))
