#!/usr/bin/python
# name: cammy.py
# version: 0.1 
# date: August 2016

import time
import sys
import os
import signal
from datetime import datetime
from ConfigParser import SafeConfigParser

from cammy_lib import get_date
from cammy_lib import update_file 
from cammy_lib import checkNetworks
from cammy_lib import processEmail

def readConfigFile(cfg_file):
    # read variables from config file
    parser = SafeConfigParser()
    parser.read (cfg_file)

    global email_server; email_server = parser.get('EmailSetup', 'email_server')
    global email_user; email_user = parser.get('EmailSetup', 'email_user')
    global email_alert_user; email_alert_user = parser.get('EmailSetup', 'email_alert_user')
    global email_password; email_password = parser.get('EmailSetup', 'email_password')
    global emailSubject; emailSubject = parser.get('EmailSetup', 'emailSubject')
    global email_polling; email_polling= parser.getint('EmailSetup', 'email_polling')

    global internet_gw; internet_gw = parser.get('EmailSetup', 'internet_gw')
    global nw_checks; nw_checks = parser.get('EmailSetup', 'nw_checks')
    nw_checks; nw_checks = nw_checks.split(',')

    global logdir; logdir = parser.get('PathSetup', 'logdir')
    global logfile; logfile = parser.get('PathSetup', 'logfile')
    global tmpdir; tmpdir = parser.get('PathSetup', 'tmpdir')
    global tmpfile; tmpfile = parser.get('PathSetup', 'tmpfile')
    global running_flag; running_flag = parser.get('PathSetup', 'running_flag')
    global stopfile; stopfile = parser.get('PathSetup', 'stopfile')
    global filepath; filepath = parser.get('PathSetup', 'filepath')
    global filenamePrefix; filenamePrefix = parser.get('PathSetup', 'filenamePrefix')
    global tidy_list; tidy_list = parser.get('PathSetup','tidy_list')
    tidy_list = tidy_list.split(',')

    global photo_width; photo_width = parser.getint('CameraSetup','photo_width') 
    global photo_height; photo_height = parser.getint('CameraSetup','photo_height') 
    global pct_quality; pct_quality = parser.getint('CameraSetup','pct_quality') 
    global sensitivity; sensitivity = parser.getint('CameraSetup','sensitivity') 
    global threshold; threshold = parser.getint('CameraSetup','threshold') 
    global test_width;test_width = parser.getint('CameraSetup','test_width') 
    global test_height; test_height = parser.getint('CameraSetup','test_height') 

    global loopThreshold; loopThreshold = parser.getint('GeneralSetup','loopThreshold') 
    global max_second; max_second = parser.getint('GeneralSetup','max_second') 
    global max_running_flag; max_running_flag = parser.getint('GeneralSetup','max_running_flag') 
    global testcount; testcount= parser.getint('GeneralSetup','testcount') 
    global use_acl; use_acl = parser.getboolean('GeneralSetup','use_acl') 
    global verbose; verbose= parser.getboolean('GeneralSetup','verbose') 
    global acl; acl = parser.get('GeneralSetup','acl') 
    acl = acl.split(',')

    global dropbox_token; dropbox_token= parser.get('DropboxSetup','dropbox_token') 
    global dropbox_app; dropbox_app= parser.get('DropboxSetup','dropbox_app') 
    global dropbox_enabled; dropbox_enabled= parser.getboolean('DropboxSetup','dropbox_enabled') 


def sigint_handler(signum, frame):
    os.remove (running_flag) 
    sys.exit("Now exiting because CTRL-C was detected")

cfg_file = '/usr/local/bin/cammy/cammy.ini'

readConfigFile(cfg_file) # read all global variables from external configuration file

signal.signal(signal.SIGINT, sigint_handler)

if verbose: 
    datestr = get_date()
    update_file("INFO: program started in verbose mode at %s \n" % (datestr), logfile)

if os.path.isfile(running_flag): 
    datestr = get_date()
    update_file("ERROR: Running flag %s detected at %s hence aborting\n" % (running_flag, datestr), logfile)
    sys.exit("Now exiting because running_flag was detected")

else:
    open(running_flag, 'a').close()

while True:

    if checkNetworks(nw_checks, logfile):
        print "Procesing email ..."
        networks_okay = True 
        processEmail(email_server, email_user, email_password, logfile, acl, use_acl, emailSubject, verbose, stopfile, tidy_list, photo_width, photo_height, pct_quality, filepath, filenamePrefix)
    else:
        networks_okay = False 
        print "network failure detected ..."

    if (not os.path.isfile(stopfile)): # if monitoring has not bee instructed to stop
        n1 = datetime.now()
        while True:
            time.sleep (0.5)
            print "detecting movement ..."
            n2 = datetime.now()
            elapsed_time = (n2 - n1).total_seconds()
            if elapsed_time > email_polling:
                break
    else:
        time.sleep (10)
        if verbose:
            datestr = get_date()
            update_file("INFO: Stop flag %s detected at %s hence aborting\n" % (stopfile, datestr), logfile)

