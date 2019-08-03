while true; do
    sleep 10
    ps up `cat /tmp/mydaemon.pid` >/dev/null && echo "Script 1 is running" || python3 main.py &
done
