#!/usr/bin/python
# name: sentry_lib.py
# version: 0.3 
# date: July 2016


def tidy_flagfiles(tidy_list,logfile):	# remove all files in tidy_list if they exist
    import os
    datestr = get_date()
    for f in tidy_list:
        if os.path.isfile(f):
            update_file("INFO: removing file %s at %s \n" % (f,datestr), logfile)
            os.remove(f)
        else:
            update_file("INFO: will not remove file %s as it does not exist at %s \n" % (f,datestr), logfile)


def sendEmail(emailTo,emailSubject, email_user, email_server, email_password, logfile, filename='',first_line=''):

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    import imaplib

    datestr = get_date()
    # Create the container (outer) email message
    msg = MIMEMultipart()
    msg['Subject'] = emailSubject + ' ' +  datestr
    msg['From'] = email_user
    msg['To'] = emailTo

    if first_line:
        msg.attach(MIMEText(first_line))

    if filename:
        if ('.jpg' in filename.lower()) or ('.bmp' in filename.lower()): # if an image file is being attached 
          with open(filename,'rb') as f:
            img = MIMEImage(f.read(), name=os.path.basename(filename))
            msg.attach(img)

        else:
          with open (filename, 'r') as f:
            attachment = MIMEText(f.read())
            msg.attach(attachment)


    # Send the email via the SMTP server
    datestr = get_date()
    try:
       smtp = smtplib.SMTP(email_server)
       smtp.login(email_user, email_password)
       smtp.sendmail(email_user, emailTo, msg.as_string())
       update_file("INFO: email response sent to " + emailTo + " at: " + datestr + "\n", logfile)

    except smtplib.SMTPException:
       update_file("ERROR: unable to send email response to " + emailTo + " at: " + datestr + "\n", logfile)

def accessPermitted(senderAddress, acl, use_acl):  # return true if senderAddress in ACL list
    if use_acl:			# check access control list for SenderAddress 
       check = False
       for a in acl:
          if (a == senderAddress):
             check = True
             break
    else:			# ignore ACL and return true
       check = True

    return (check)

def getEmailInfo(response_part):

    import email
    msg = email.message_from_string(response_part[1])
    varSubject = msg['subject']
    varFrom = msg['from']

    #remove the brackets around the sender email address
    varFrom = varFrom.replace('<', '')
    varFrom = varFrom.replace('>', '')

    # address = last element from list
    senderAddress =  varFrom.split()[-1]

    # truncate with (...) if subject length is greater than 35 characters
    if len( varSubject ) > 35:
        varSubject = varSubject[0:32] + '...'

    return (senderAddress, varSubject)

def processEmail(email_server, email_user, email_password, logfile, acl, use_acl, emailSubject, verbose, stopfile, tidy_list):

    import smtplib
    import imaplib
    import os
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText

    try: 
        m = imaplib.IMAP4_SSL(email_server)
    except:
        datestr = get_date()
        update_file("ERROR: failed to create IMAP_SSL object for email server %s at %s \n" % (email_server,datestr), logfile)
        sys.exit(1)

    try:
        rv, data = m.login(email_user, email_password)
    except imaplib.IMAP4.error:
        datestr = get_date()
        update_file("ERROR: IMAP login to %s as %s failed at %s \n" % (email_server,email_user,datestr), logfile)
        sys.exit(1)

    m.select('inbox')
    typ, data = m.search(None, "UNSEEN")
    ids = data[0]
    id_list = ids.split()

    # if any new emails have arrived
    if id_list:

        for i in id_list: # for each new email

            typ, data = m.fetch( i, '(RFC822)' )

            for response_part in data: # for each part of the email

                if isinstance(response_part, tuple):	# if the part is a tuple then read email info

                    senderAddress, varSubject = getEmailInfo (response_part)
                    
                    if verbose:
                        datestr = get_date()
                        update_file("INFO: email received from %s, subject = %s,  at %s \n" % (senderAddress, varSubject, datestr), logfile)

                    if accessPermitted(senderAddress, acl, use_acl):

                        if 'cammy:logs' in varSubject.lower(): # logfile requested
                            datestr = get_date()
                            update_file("INFO: A copy of the logfile was requested by %s at %s \n" % (senderAddress, datestr), logfile)
                            sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, logfile,"Here is a copy of the logfile contents:\n")

                        elif 'cammy:help' in varSubject.lower(): # helprequested
                            datestr = get_date()
                            helpMessage = "Help contents - include the following in email subject heading: \n\
cammy:logs \t\t sends the logfile contents\n\
cammy:resetlogs \t resets the logfile\n\
cammy:shutdown \t shuts down the system\n\
cammy:stop \t\t keeps polling for emails but stops motion detection\n\
cammy:resume \t\t will resume motion detection\n\
cammy:hires \t\t will capture a high resolution image and send back\n\
cammy:restert \t\t will shut down the system for keeps\n\
cammy:help \t\t will email this message back!"
                            sendEmail (senderAddress,'',helpMessage)

                        elif 'cammy:resetlogs' in varSubject.lower(): # logfile reset requested
                            os.remove (logfile)
                            datestr = get_date()
                            update_file("INFO: A logfile reset was requested by %s at %s \n" % (senderAddress, datestr), logfile)
                            sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, logfile,"The logfile has been reset, here is the new logfile contents:\n")
                        elif 'cammy:shutdown' in varSubject.lower(): # shutdown requested
                            datestr = get_date()
                            update_file("INFO: A shutdown was requested by %s at %s \n" % (senderAddress, datestr), logfile)
                            sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, '',"Your request to shut down the system has been actioned\n")
                            tidy_flagfiles(tidy_list, logfile)
                            system_shutdown(logfile,restart=False)

                        elif 'cammy:stop' in varSubject.lower(): # request to stop monitoring 
                            datestr = get_date()
                            update_file("INFO: A request to stop monitoring was made by %s at %s \n" % (senderAddress, datestr), logfile)

                            if (not os.path.isfile(stopfile)):
                                open(stopfile, 'a').close()  # create stop file
                                sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, '',"Your request to stop detecting motion has been actioned\n")

                            else:
                                sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, '',"Your request to stop detecting motion has not been actioned since it was already stopped\n")

                        elif 'cammy:resume' in varSubject.lower(): # request to resume monitoring 
                            datestr = get_date()
                            update_file("INFO: A request to resume monitoring was made by %s at %s \n" % (senderAddress, datestr), logfile)

                            if os.path.isfile(stopfile):
                                os.remove(stopfile)
                                sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, '',"Your request to resume detecting motion has been actioned\n")

                            else:
                                sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, '',"Your request to resume detecting motion has not been actioned as it was not stopped\n")

                        elif 'cammy:restart' in varSubject.lower(): # shutdown requested
                            datestr = get_date()
                            update_file("INFO: A reboot was requested by %s at %s \n" % (senderAddress, datestr), logfile)
                            sendEmail (senderAddress, emailSubject, email_user, email_server, email_password, logfile, '',"Your request to reboot the system has been actioned\n")
                            tidy_flagfiles(tidy_list, logfile)
                            system_shutdown(logfile,restart=True)

                        elif 'cammy:hires' in varSubject.lower(): # hi resolution photo requested
                            photo_width = 2592 
                            photo_height = 1944
                            filename = saveImage (photo_width, photo_height)
                            sendEmail (senderAddress,filename,"A high resolution photo was requested - please find the attached image:\n")
                            os.remove (filename)

                        else:
                            filename = saveImage (photo_width, photo_height)
                            sendEmail (senderAddress,filename,"A standard image photo was requested - please find attached image:\n")
                            os.remove (filename)

                    else:
                        datestr = get_date()
                        update_file("WARN: Email address %s not recognised at %s \n" % (senderAddress,datestr), logfile)

        m.logout()






def checkIP(IPaddress): #return true if IP address pings OK
    import os
    import subprocess
    with open(os.devnull, 'w') as fNull:
      response = False
      res = subprocess.call(['ping', '-q','-c', '1', IPaddress],stdout=fNull, stderr=fNull)

    if res == 0:
        response = True

    return (response)


def checkNetworks(nw_checks, logfile):  # return true if all network interfaces ping OK
    check = True
    for i in nw_checks:
      if not checkIP(i):
        datestr = get_date()
        update_file("WARN: Failed to contact network address %s at %s \n" % (i, datestr), logfile)
        check = False
        break

    return (check)

def get_date(): # return current date and time
        from datetime import datetime
        time = datetime.now()
        return "%02d-%02d-%04d_%02d%02d%02d" % (time.day, time.month, time.year, time.hour, time.minute, time.second)

def update_file(message,filename): # append filename with message
    with open(filename,'a') as f:
        f.write(message)

def representsInt(s):
    try:
        int(s)
        return True

    except ValueError:
        return False

def get_num_file(filename):
    import os
    if os.path.isfile(filename):

        with open(filename, 'r') as f:
            firstLine = f.readline()

        firstList = firstLine.split()
        firstNum = firstList[0]

        if representsInt(firstNum):
            firstInt = int(firstNum)

        else:          # return a default of 0 if no integer value detected
            firstInt = 0

        return firstInt 


def system_shutdown(logfile,restart):
    if restart is True:
        command = "/usr/bin/sudo /sbin/shutdown -r now"

    else:
        command = "/usr/bin/sudo /sbin/shutdown -h now"

    message = "Now issuing command " + command + "\n"
    update_file (message, logfile)

    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]


def dropbox_upload(verbose,logfile,appname,token,uploadfile):
    
  if verbose:
    message = "INFO: using appname = " + appname + " to upload to Dropbox\n"
    update_file (message, logfile)

  import dropbox
  import os.path
  from dropbox.exceptions import ApiError, AuthError
  from dropbox.files import WriteMode

  dbx = dropbox.Dropbox(token)

  try:
    dbx.users_get_current_account()
    if os.path.isfile(uploadfile):
      with open(uploadfile, 'rb') as f:

        filename = '/' + os.path.basename(uploadfile)

        try:
            dbx.files_upload(f, filename, dropbox.files.WriteMode.overwrite)
            if verbose:
               message = "INFO: successfully uploaded file " + uploadfile + " as " + filename + " to Dropbox within application " + appname + " \n"
               update_file (message, logfile)

        except ApiError as err:
          message = "ERROR: an error ocurred attemping to upload file to dropbox\n"
          update_file (message, logfile)

    else:
      message = "ERROR: filename " + uploadfile + " does not exist hence not uploading to Dropbox\n"
      update_file (message, logfile)

  except AuthError as err:
    message = "ERROR: Invalid Dropbox access token\n"
    update_file (message, logfile)
