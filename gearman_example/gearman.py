"""
Example Gearman Job File.
Needs to be called gearman_jobs.py and reside inside a registered Django app.
"""
import os
import time

from django_gearman.decorators import gearman_job


@gearman_job
def reverse(input):
    """Reverse a string"""
    print "[%s] Reversing string: %s" % (os.getpid(), input)
    return input[::-1]

@gearman_job
def background_counting(arg=None):
    """
    Do some incredibly useful counting to 5
    Takes no arguments, returns nothing to the caller.
    """
    print "[%s] Counting from 1 to 5." % os.getpid()
    for i in range(1,6):
        print i
        time.sleep(1)

