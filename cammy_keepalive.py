#!/usr/bin/python3

import configparser
import sys

from cammy_lib import access_keepalive 
from cammy_lib import get_date 
from cammy_lib import update_file 

def readConfigFile(cfg_file):
    # read variables from config file
    parser = configparser.ConfigParser()
    parser.read (cfg_file)

    global logdir; logdir = parser.get('PathSetup', 'logdir')
    global logfile; logfile = parser.get('PathSetup', 'logfile')
    global tmpdir; tmpdir = parser.get('PathSetup', 'tmpdir')
    global running_flag; running_flag = parser.get('PathSetup', 'running_flag')
    global stopfile; stopfile = parser.get('PathSetup', 'stopfile')
    global filepath; filepath = parser.get('PathSetup', 'filepath')
    global keepalive_file; keepalive_file = parser.get('PathSetup', 'keepalive_file')
    global keepalive_threshold; keepalive_threshold= parser.getint('PathSetup', 'keepalive_threshold')
    global filenamePrefix; filenamePrefix = parser.get('PathSetup', 'filenamePrefix')
    global tidy_list; tidy_list = parser.get('PathSetup','tidy_list')
    tidy_list = tidy_list.split(',')

    global verbose; verbose= parser.getboolean('GeneralSetup','verbose') 


cfg_file = '/usr/local/bin/cammy/cammy.ini'

readConfigFile(cfg_file) # read all global variables from external configuration file


access_type = "request"
access_keepalive (verbose,keepalive_file, access_type, tidy_list, logfile, keepalive_threshold)
