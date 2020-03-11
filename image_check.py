from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image
from imgurpython import *
from functools import reduce
import math
import operator
import time
import shutil
import yaml
import json
from discord import Webhook, RequestsWebhookAdapter, File

# Load tokens from JSON
with open('tokens.json') as f:
    token_json = json.load(f)

# Load subs from YAML
# with open("subs.yml", 'r') as stream:
#     try:
#         subreddit_dict = yaml.safe_load(stream)
#     except yaml.YAMLError as exc:
#         print(exc)

imgur_client_id = token_json['IMGUR_CLIENT_ID']
imgur_client_secret = token_json['IMGUR_CLIENT_SECRET']
imgur_access_token = token_json['IMGUR_ACCESS_TOKEN']
imgur_refresh_token = token_json['IMGUR_REFRESH_TOKEN']
reddit_user_agent = token_json['REDDIT_USERAGENT']
reddit_username = token_json['REDDIT_USERNAME']
webhook_id = token_json['WEBHOOK_ID']
webhook_token = token_json['WEBHOOK_TOKEN']

album = 'b6ZIp1m'
uploadConfig = {
    'album': album,
    'name': 'Updated Summer fools pic',
    'title': 'Update Photo',
    'description': 'Grabbed automatically, hopefully this is important'
}
imgClient = ImgurClient(imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token)
webhook = Webhook.partial(webhook_id, webhook_token, adapter=RequestsWebhookAdapter())

# TODO: READ YAML and grab list of subreddits


def main():

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    while True:
        # Load in sub data
        with open("subs.yml", 'r') as stream:
            try:
                subreddit_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # Grab data for subs
        for subreddit in subreddit_dict['SubredditsToGrab']:
            try:
                driver.get("https://old.reddit.com/r/" + subreddit['name'])
                driver.save_screenshot(subreddit['name'] + '2.png')
                print("Saved " + subreddit['name'] + "2.png")
            except Exception as e:
                print(e)
                exit(-1)
        # Check subs and send new info if different
        try:
            t0 = time.time()
            for idx, subreddit in enumerate(subreddit_dict['SubredditsToGrab']):
                sub_title = subreddit['name']
                image_is_different = check_images(sub_title + '.png', sub_title + '2.png')

                if image_is_different:
                    imgur_image = imgClient.upload_from_path(sub_title + '2.png', config=uploadConfig, anon=False)
                    imgur_link = str(imgur_image['link'])
                    webhook.send(subreddit['imgur-link'])
                    shutil.copyfile(sub_title + '2.png', sub_title + '.png')
                    msg = "New " + sub_title + " message detected: " + imgur_link

            t1 = time.time()
            print("Time (s): " + str(t1 - t0))
        except Exception as e:
            print(e)
            webhook.send('https://i.imgur.com/vmAF9A2.png')
        time.sleep(60)


def check_images(image1, image2):
    im1 = Image.open(image1)
    im2 = Image.open(image2)
    h1 = im1.histogram()
    h2 = im2.histogram()
    rms = math.sqrt(reduce(operator.add,
                           map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
    print(rms)
    if rms > 0.5:
        image_is_different = True
    else:
        image_is_different = False
    return image_is_different


if __name__ == '__main__':
    main()
