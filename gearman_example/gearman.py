"""
Example Gearman Job File.
Needs to be called gearman.py and reside inside a registered Django app.
"""

def reverse(input):
    """Reverse a string"""
    return input[::-1]

