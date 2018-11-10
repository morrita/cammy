#!/usr/bin/python3
# name: cammy.py
# version: 0.3 
# date: March 2018 

import time
import sys
import os
import signal
from datetime import datetime
import configparser

from cammy_lib import get_date
from cammy_lib import update_file 
from cammy_lib import checkNetworks
from cammy_lib import processEmail
from cammy_lib import sendEmail
from cammy_lib import detect_motion 
from cammy_lib import dropbox_upload 
from cammy_lib import dropbox_cleanup
from cammy_lib import dropbox_create_shared_link 
from cammy_lib import saveFilm
from cammy_lib import access_keepalive

def readConfigFile(cfg_file):
    # read variables from config file
    parser = configparser.ConfigParser()
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
    global running_flag; running_flag = parser.get('PathSetup', 'running_flag')
    global stopfile; stopfile = parser.get('PathSetup', 'stopfile')
    global filepath; filepath = parser.get('PathSetup', 'filepath')
    global keepalive_file; keepalive_file = parser.get('PathSetup', 'keepalive_file')
    global keepalive_threshold; keepalive_threshold = parser.getint('PathSetup', 'keepalive_threshold')
    global filenamePrefix; filenamePrefix = parser.get('PathSetup', 'filenamePrefix')
    global tidy_list; tidy_list = parser.get('PathSetup','tidy_list')
    tidy_list = tidy_list.split(',')

    global film_width; film_width = parser.getint('CameraSetup','film_width') 
    global film_height; film_height = parser.getint('CameraSetup','film_height') 
    global photo_width; photo_width = parser.getint('CameraSetup','photo_width') 
    global photo_height; photo_height = parser.getint('CameraSetup','photo_height') 
    global pct_quality; pct_quality = parser.getint('CameraSetup','pct_quality') 
    global sensitivity; sensitivity = parser.getint('CameraSetup','sensitivity') 
    global threshold; threshold = parser.getint('CameraSetup','threshold') 
    global test_width;test_width = parser.getint('CameraSetup','test_width') 
    global test_height; test_height = parser.getint('CameraSetup','test_height') 
    global camera_timeout; camera_timeout = parser.getfloat('CameraSetup','camera_timeout') 
    global camera_busy_flag; camera_busy_flag = parser.get('CameraSetup', 'camera_busy_flag')

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
    global dropbox_folder; dropbox_folder= parser.get('DropboxSetup','dropbox_folder') 
    global dropbox_keep_files; dropbox_keep_files= parser.getint('DropboxSetup','dropbox_keep_files') 
    global film_duration; film_duration= parser.getint('DropboxSetup','film_duration')
    global film_enable; film_enable= parser.getboolean('DropboxSetup','film_enable')
    global dropbox_film_folder; dropbox_film_folder= parser.get('DropboxSetup','dropbox_film_folder')

    if debug_mode:
        update_file ("*********************************************************\n", logfile)
        update_file ("Content listing of file: %s\n" % (cfg_file), logfile)
        update_file ("*********************************************************\n", logfile)
        update_file ("\n", logfile)
        for section_name in parser.sections():
            update_file ("Section: %s\n" % (section_name), logfile)
            update_file ("  Options: %s\n" % (parser.options(section_name)), logfile)
            for name, value in parser.items(section_name):
                update_file ("  %s = %s\n" % (name, value), logfile)
            update_file ("\n", logfile)

def sigint_handler(signum, frame):
    os.remove (running_flag) 
    datestr = get_date()
    update_file("INFO: program received an interrupt signal at %s \n" % (datestr), logfile)
    sys.exit("Now exiting because CTRL-C was detected")


def sighup_handler(signum, frame):
    os.remove (running_flag) 
    datestr = get_date()
    update_file("INFO: program received a HUP signal at %s \n" % (datestr), logfile)
    sys.exit("Now exiting because an HUP signal was received")

#debug_mode = True 
debug_mode = False 
cfg_file = '/usr/local/bin/cammy/cammy.ini'

readConfigFile(cfg_file) # read all global variables from external configuration file

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGHUP, sighup_handler)

if debug_mode:
    # print all global variables
    update_file ("***********************************************\n", logfile)
    update_file ("Listing of file all glogal variables declared\n", logfile)
    update_file ("***********************************************\n", logfile)
    update_file ("\n", logfile)
    vardict = globals()
    for key,val in list(vardict.items()):
        if (key != 'vardict') and (not key.startswith('__')):
            update_file ("%s => %s\n" % (key, val), logfile)

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
        networks_okay = True
        datestr = get_date()
        update_file("INFO: Network checks all OK at %s\n" % (datestr), logfile)

        access_type = "respond"
        access_keepalive (verbose,keepalive_file, access_type, tidy_list, logfile, keepalive_threshold)
         
        email_okay = processEmail(email_server, email_user, email_password, logfile, keepalive_file, acl, use_acl, emailSubject, verbose, stopfile, tidy_list, photo_width, photo_height, pct_quality, filepath, filenamePrefix)

        if verbose:
            datestr = get_date()
            update_file("INFO: email_okay = %s at %s\n" % (str(email_okay), datestr), logfile)

        if email_okay is False:
            datestr = get_date()
            update_file("ERROR: Email failure detected at %s\n" %  (datestr), logfile)

    else:
        networks_okay = False 
        email_okay = False
        datestr = get_date()
        update_file("ERROR: Network failure detected at %s\n" %  (datestr), logfile)

    if (not os.path.isfile(stopfile)): # if monitoring has not bee instructed to stop
        n1 = datetime.now()
        while True:

            filename = detect_motion(film_enable, film_width, film_height, film_duration,photo_width, photo_height,test_width, test_height, pct_quality, filepath, filenamePrefix, logfile, email_alert_user, sensitivity, threshold, verbose, tidy_list, camera_timeout, camera_busy_flag)

            if filename and networks_okay and email_okay:

                if dropbox_enabled and film_enable:
                    dropbox_upload(verbose, logfile, dropbox_app, dropbox_token, filename, dropbox_folder)
                    dropbox_url = dropbox_create_shared_link(verbose, logfile, dropbox_app, dropbox_token, filename, dropbox_folder)
                    dropbox_cleanup(verbose,logfile,dropbox_app,dropbox_token,dropbox_folder, dropbox_keep_files)

                    emailSubject = "Motion detected! Movie file uploaded to Dropbox"
                    first_line="Motion detected! Movie file uploaded to <html><body> <a href='%s'>Dropbox</a></body></html>" % (dropbox_url)
                    sendEmail(email_alert_user,emailSubject, email_user, email_server, email_password, logfile, filename,first_line)
                    datestr = get_date()
                    update_file("INFO: Motion detected! Film recorded - notification of file %s emailed to %s at %s\n" % (filename, email_alert_user, datestr), logfile)
                    dropbox_folder = dropbox_film_folder

                else:
                    sendEmail(email_alert_user,emailSubject, email_user, email_server, email_password, logfile, filename,first_line='Motion detected! Please find attached image:')
                    datestr = get_date()
                    update_file("INFO: Motion detected! File %s emailed to %s at %s\n" % (filename, email_alert_user, datestr), logfile)

                os.remove(filename)

            n2 = datetime.now()
            elapsed_time = (n2 - n1).total_seconds()
            if elapsed_time > email_polling:
                datestr = get_date()
                update_file("INFO: elapsed image scanning time has exceeded %d seconds at %s hence now checking for emails...\n" % (email_polling, datestr), logfile)

                break
    else:
        time.sleep (30)
        if verbose:
            datestr = get_date()
            update_file("INFO: Stop flag %s detected at %s hence aborting\n" % (stopfile, datestr), logfile)

