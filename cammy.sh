#!/bin/sh
# /etc/init.d/cammy
# starts the cammy service
### BEGIN INIT INFO
# Provides:          cammy
# Required-Start:
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# X-Interactive:     true
# Short-Description: Start/stop cammy application server
### END INIT INFO
 
CAMMY_HOME="/usr/local/bin/cammy"
CAMMY_USER="pi"
CAMMY_ERRORLOG="/var/log/cammy/cammy_errors.log"

case "$1" in

start)
  CAMMY_PID=`ps -ef | grep cammy.py | grep -v grep | awk '{ print $2 }'`
  if [ -n "$CAMMY_PID" ]
  then
    echo "CAMMY is already running (pid: $CAMMY_PID)"
  else
    # Start cammy 
    echo "Starting cammy"
    sudo /bin/su - -c "cd $CAMMY_HOME && nohup $CAMMY_HOME/cammy.py >> $CAMMY_ERRORLOG 2>&1 &" $CAMMY_USER
  fi
  return 0
  ;;

stop)
  CAMMY_PID=`ps -ef | grep cammy.py | grep -v grep | awk '{ print $2 }'`
  if [ -n "$CAMMY_PID" ]
  then
    # stop cammy 
    echo "Stopping cammy with kill -1 then checking after 5 seconds..."
    sudo /bin/su - -c "kill -1 $CAMMY_PID" $CAMMY_USER
    echo "Sleeping for 5 seconds..."
    sleep 5

    CAMMY_PID=`ps -ef | grep cammy.py | grep -v grep | awk '{ print $2 }'`
    if [ -n "$CAMMY_PID" ]
    then
      # stop cammy 
      echo "Stopping cammy with second kill -1 signal..."
      sudo /bin/su - -c "kill -1 $CAMMY_PID" $CAMMY_USER

    else
      echo "... process killed on first attempt"

    fi

  else
    echo "CAMMY is not running"
  fi
  return 0
  ;;
*)
  echo "Usage: $0 {start|stop}"
  exit 1
  ;;
esac
