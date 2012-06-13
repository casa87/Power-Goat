#!/usr/bin/env python

"""
log daemon to push log files on Amazon S3
and rotate them

Christophe Boudet 2012
"""

import os
import sys
import boto
import time
import datetime
import subprocess
from boto.s3.key import Key


class Logger():

    def __init__(self, mode, delay, bucket, files):
        if mode in ('date', 'd'):
            self.mode = 'date'
            self.delay = self.sizeof_date(delay)
        elif mode in ('size', 's'):
            self.mode = 'size'
            self.delay = self.sizeof_fmt(delay)
        else:
            usage(True)
        self.files = files
        self.bucket = bucket

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
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        for file in self.file_rotate:
            name = os.path.basename(file)
            new_name = os.path.splitext(name)[0]
            path = os.path.dirname(file)
            #rotate older files
            old_files = []
            for filename in os.listdir(path):
                if filename.startswith('{0}_'.format(new_name)):
                    old_files.append(filename)
            old_files = sorted(old_files, key=lambda x: int(x[len(new_name)+1:]), reverse=True)
            print old_files
            if len(old_files) >= max_copy - 1:
                for file_delete in old_files[max_copy - 1:]:
                    os.remove(os.path.join(path, file_delete))
            #rotate last one
            #compress it with lzop if available
            if os.path.exists('/usr/bin/lzop'):
                subprocess.call(['/usr/bin/lzop', '-o', os.path.join(path, name), os.path.join(path, "{0}_{1}".format(new_name, timestamp))])
            else:
                os.rename(os.path.join(path, name), os.path.join(path, "{0}_{1}".format(new_name, timestamp)))
            #push on s3
            try:
                access_key =  os.environ['S3_ACCESS_KEY']
                secret_key =  os.environ['S3_SECRET_KEY']
            except:
                print "declare your S3 access and secret key as environement variable"
                print
                print "S3_ACCESS_KEY"
                print "S3_SECRET_KEY"
            try:
                s3_conn = boto.connect_s3(access_key, secret_key)
            except:
                print "S3 authentication failed"
            key_name = "{0}/{1}_{2}".format(datetime.datetime.now().strftime('%Y/%m/%d'), new_name, timestamp)
            bucket = s3_conn.get_bucket(self.bucket)
            k = Key(bucket)
            k.key = key_name
            k.set_contents_from_filename(os.path.join(path, "{0}_{1}".format(new_name, timestamp)))
            print key_name
        
       
           
def usage(exit=False):
    print
    print 'Log daemon'
    print 
    print '{0} size/date max #copy bucket file1 file2 .. fileN'.format(sys.argv[0])
    print 'size 100M N bucket       rotate every 100Mo'
    print 'date 10d  N bucket     rotate every 10 days'
    print 'N                number of copy'
    print 'bucket         bucket name'
    print
    if exit:
        sys.exit(1)



if __name__ == "__main__":
    if len(sys.argv) < 5:
        usage(True)
    logger = Logger(sys.argv[1], sys.argv[2], sys.argv[4], sys.argv[5:])
    logger.check_file()
    logger.rotate(sys.argv[3])

