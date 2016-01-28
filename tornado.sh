#!/bin/sh
# Tornado Server for Catlog
#
workdir=/home/ec2-user/online-parser
 
start() {
    cd $workdir
    /usr/bin/python /home/ec2-user/online-parser/parser.py --port="$1" --debug=Fasle --log_file_prefix=/home/ec2-user/online-parser/logs/tornado-"$1".log &
    echo "Server started."
}
 
stop() {
    pid=`ps -ef | grep '[p]ython /home/ec2-user/online-parser/parser.py --port='"$1" | awk '{ print $2 }'`
    echo $pid
    kill $pid
    sleep 2
    echo "Server killed."
}
 
case "$1" in
  start)
    start "$2"
    ;;
  stop)
    stop "$2"  
    ;;
  restart)
    stop "$2"
    start "$2"
    ;;
  *)
    echo "Usage: ./tornado.sh {start|stop|restart}"
    exit 1
esac
exit 0
