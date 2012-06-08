#!/usr/bin/env python

"""
log daemon to push log files on Amazon S3
and rotate them

Christopphe Boudet 2012
"""

import os
import sys
import time
import datetime


class Logger():

    def __init__(self, mode, delay, files):
        if mode in ('date', 'd'):
            self.mode = 'date'
            self.delay = self.sizeof_date(delay)
        elif mode in ('size', 's'):
            self.mode = 'size'
            self.delay = self.sizeof_fmt(delay)
        else:
            usage(True)
        self.files = files

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
                    return int(num[:-1]) * date_convertion[index] * 60
        usage(True)

    def get_file_to_rotate(self, files):
        """return list of file to rotate"""
        rotate = []
        for file in files:
            if os.path.isfile(file):
                if self.mode == 'size':
                    if os.path.getsize(file) >= self.delay:
                        rotate.append(file)
                else:
                    created = os.path.getctime(file)
                    now = time.time()
                    if now - created >= self.delay:
                        rotate.append(file)
            else:
                print "{0} is not a file".format(file)
        return rotate

    def check_file(self):
        """"check file to rotate"""
        self.file_rotate = self.get_file_to_rotate(self.files)
        if not self.file_rotate:
            print "no rotation"
            sys.exit()

    def rotate(self, max_copy):
        """rotate file"""
        max_copy = int(max_copy)
        for file in self.file_rotate:
            i = max_copy
            name = os.path.basename(file)
            path = os.path.dirname(file)
            #rotate older files
            while i:
                file_name = "{0}{1}".format(name, i)
                if os.path.exists(os.path.join(path, file_name)):
                    #delete
                    if i == max_copy:
                        os.remove(os.path.join(path, file_name))
                    #move
                    else:
                        new_file_name = "{0}{1}".format(name, i+1)
                        os.rename(os.path.join(path, file_name), os.path.join(path, new_file_name))
                i -= 1
            #rotate last one
            if max_copy:
                os.rename(os.path.join(path, name), os.path.join(path, "{0}1".format(name)))

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
    if len(sys.argv) < 4:
        usage(True)
    logger = Logger(sys.argv[1], sys.argv[2], sys.argv[4:])
    logger.check_file()
    logger.rotate(sys.argv[3])

