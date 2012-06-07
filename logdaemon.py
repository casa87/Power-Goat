#!/usr/bin/env python

"""
log daemon to push log file on Amazon S3
and rotate them

Christopphe Boudet 2012
"""

import sys

class Logger():
    
    def __init__(self, mode, delay):
        if mode in ('date', 'd'):
            self.mode = 'date'
        elif mode in ('size', 's'):
            self.mode = 'size'
        else:
            usage(True)

def usage(exit=False):
    print
    print 'Log daemon'
    print 
    print '{0} : '.format(sys.argv[0])
    print 'size 100M        rotate every 100Mo'
    print 'date 10d        rotate every 10 days'
    print
    if exit:
        sys.exit(1)
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage(True)
    logger = Logger(sys.argv[1], sys.argv[2])