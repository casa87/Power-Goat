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
            print  self.sizeof_date(delay)
        elif mode in ('size', 's'):
            self.mode = 'size'
            print self.sizeof_fmt(delay)
        else:
            usage(True)

    def sizeof_fmt(self, num):
        """transform human size into int"""
        size_letter = ['K','M','G','T']
        if len(num) > 1:
            if str(num)[-1]:
                if str(num)[-1] in size_letter:
                    index = size_letter.index(str(num)[-1])
                    delay = int(num[:-1]) * (1024**(index+1))
                    return int(delay)
                elif str(num)[-1] in "0123456789":
                    return int(num)
                else:
                    usage(True)
        return num
            
    def sizeof_date(self, num):
        """transform date diff to date"""
        date_letter = ['m', 'h', 'd', 'w']
        date_convertion = [1, 60, 24*60, 24*60*7]
        if len(num) > 1:
            if str(num)[-1]:
                if str(num)[-1] in date_letter:
                    index = date_letter.index(str(num)[-1])
                    return int(num[:-1]) * date_convertion[index]
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