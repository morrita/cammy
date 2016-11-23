#!/usr/bin/python
# name: cammy.py
# version: 2.1 
# date: May 2016

from cammy_lib import update_file 
from cammy_lib import dropbox_upload 
from cammy_lib import dropbox_cleanup
from cammy_lib import saveImage 
from cammy_lib import saveFilm

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

import StringIO  # needed for capturing test images
from PIL import Image

import imaplib
import sys
import email
import time
from datetime import datetime
import subprocess
import os
from ConfigParser import SafeConfigParser

cfg_file = '/usr/local/bin/cammy/cammy.ini'

def get_date(): # return current date and time
        time = datetime.now()
        return "%02d-%02d-%04d_%02d%02d%02d" % (time.day, time.month, time.year, time.hour, time.minute, time.second)
 
def readConfigFile():
    # read variables from config file
    parser = SafeConfigParser()
    parser.read (cfg_file)

    global email_server; email_server = parser.get('EmailSetup', 'email_server')
    global email_user; email_user = parser.get('EmailSetup', 'email_user')
    global email_alert_user; email_alert_user = parser.get('EmailSetup', 'email_alert_user')
    global email_password; email_password = parser.get('EmailSetup', 'email_password')
    global emailSubject; emailSubject = parser.get('EmailSetup', 'emailSubject')

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

    global film_width; film_width = parser.getint('CameraSetup','film_width') 
    global film_height; film_height = parser.getint('CameraSetup','film_height') 
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
    global dropbox_folder; dropbox_folder= parser.get('DropboxSetup','dropbox_folder')
    global dropbox_film_folder; dropbox_film_folder= parser.get('DropboxSetup','dropbox_film_folder')
    global dropbox_keep_files; dropbox_keep_files= parser.getint('DropboxSetup','dropbox_keep_files')
    global film_duration; film_duration= parser.getint('DropboxSetup','film_duration')
    global film_enable; film_enable= parser.getboolean('DropboxSetup','film_enable')



readConfigFile() # read all global variables from external configuration file


if dropbox_enabled:

  if film_enable:
    filename = saveFilm(film_width, film_height, filepath, logfile, film_duration)
    dropbox_upload(verbose, logfile, dropbox_app, dropbox_token, filename, dropbox_film_folder)
    dropbox_cleanup(verbose,logfile,dropbox_app,dropbox_token,dropbox_film_folder, dropbox_keep_files)
    os.remove(filename)

  else:

    filename = saveImage(photo_width, photo_height, pct_quality, filepath, filenamePrefix, logfile)
    dropbox_upload(verbose, logfile, dropbox_app, dropbox_token, filename, dropbox_folder)
    dropbox_cleanup(verbose,logfile,dropbox_app,dropbox_token,dropbox_folder, dropbox_keep_files)
    os.remove(filename)

elif verbose:
  datestr = get_date()
  update_file("INFO: dropbox_enabled set to false hence not uploading image at: " + datestr + "\n", logfile) 
