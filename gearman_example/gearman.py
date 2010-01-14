"""
Example Gearman Job File.
Needs to be called gearman.py and reside inside a registered Django app.
"""
from django_gearman.decorators import gearman_job

@gearman_job
def reverse(input):
    """Reverse a string"""
    return input[::-1]

