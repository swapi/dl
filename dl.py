#!/usr/bin/python

import requests
import simplejson
import os
import os.path
import threading
import time
import atexit
import sys
import logging

if 'SCRIPTDIR' in os.environ:
    scriptdir = os.environ['SCRIPTDIR']
else:
    scriptdir = '.'

logging.basicConfig(filename=scriptdir+'/dl.log', level=logging.INFO, \
        format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

class Downloader(threading.Thread):
    def __init__(self, downloader, request_path, download_path):
        threading.Thread.__init__(self)
        self.downloader = downloader
        self.request_path = request_path
        self.download_path = download_path

    def run(self):
        logging.debug('start processing request_path = ' + self.request_path)
        self.downloader.download(self.request_path, self.download_path)
        logging.debug('done processing request_path = ' + self.request_path)

if len(sys.argv) == 2:
    CONFILE = sys.argv[1]
else:
    print('Usage: dl.py config-file')
    exit(1)

f = open(CONFILE, 'r')
try:
    dlconfig = simplejson.load(f)
finally:
    f.close()

pidfile = dlconfig['pidfile']

logging.debug('checking pidfile = ' + pidfile)
if os.path.exists(pidfile):
    f = open(pidfile, 'r')
    try:
        pid = f.read().strip()
    finally:
        f.close()
    #check if process exists with given pid 
    #if exists, exit this process here
    try:
        #this will just try to check if process exist
        #if exist does nothing, if not exist throws OSError
        os.kill(int(pid), 0)
        logging.info('downloader process with pid <' + pid + '> already exists')
        exit(1)
    except OSError:
        #no process exists, may be last processes was killed instataneously
        #hence delete the old pidfile
        os.remove(pidfile)

f = open(pidfile, 'w')
try:
    f.write(str(os.getpid()))
    atexit.register(os.remove, pidfile)
finally:
    f.close()

request_base_path = dlconfig['paths']['requests']
download_base_path = dlconfig['paths']['downloads']
supported_requests = dlconfig['downloaders']
   
# get all request types
filelist = [os.path.join(request_base_path, x) for x in os.listdir(request_base_path)]
request_paths = [x for x in filelist if os.path.isdir(x)]

logging.debug('request_paths = ' + str(request_paths))

for p in request_paths:
    logging.debug('checking the path = ' + p)
    if p.endswith(os.path.sep) or p.endswith('/'):
        p = p[:-1]
    request_type = os.path.basename(p)
    if not request_type in supported_requests:
        logging.warning('cannot find the downloader plugin for = ' + request_type)
        continue 
    downloader = supported_requests[request_type]

    try:
        downloader = __import__(downloader)
    except:
        logging.exception('cannot load downloader plugin for = ' + request_type)
        continue
        
    dl = Downloader(downloader, p, os.path.join(download_base_path, request_type))
    dl.start()

