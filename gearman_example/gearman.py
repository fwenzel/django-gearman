"""
Example Gearman Job File.
Needs to be called gearman.py and reside inside a registered Django app.
"""
import time

from django_gearman.decorators import gearman_job


@gearman_job
def reverse(input):
    print "Reversing string: %s" % input
    """Reverse a string"""
    return input[::-1]

@gearman_job
def background_counting(arg=None):
    """
    Do some incredibly useful counting to 20
    Takes no arguments, returns nothing to the caller.
    """
    print "Counting from 1 to 20."
    for i in range(1,21):
        print i
        time.sleep(1)

