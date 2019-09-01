from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import atexit
import sys

list_of_subs = ["ThePathOfKairos", "Layer", "Layers", "Layer_layers", "Page_pages", "seed_seeds", "digit_digits"]

pid = str(os.getpid())
pidfile = "/tmp/imagedaemon.pid"
if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    sys.exit()
open(pidfile, 'w').write(pid)

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)


def pidclose():
    os.unlink(pidfile)


atexit.register(pidclose)

while True:
    for subreddit in list_of_subs:
        try:
            driver.get("https://old.reddit.com/r/" + subreddit)
            driver.save_screenshot(subreddit + '2.png')
            print("Saved " + subreddit + "2.png")
        except:
            exit(-1)
    time.sleep(60)
