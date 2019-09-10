while true; do
    sleep 10
    ps up `cat /tmp/mydaemon.pid` >/dev/null && echo "Script 1 is running" || python3 main.py &
    sleep 5
    ps up `cat /tmp/imagedaemon.pid` >/dev/null && echo "Script 2 is running" || python3 image_check.py
done
