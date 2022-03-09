import asyncio
import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from functools import reduce
import math
import operator
from imgurpython import *
import json
import os
import atexit
import asyncpraw
from praw.models import Message

client = commands.Bot(command_prefix="?")
with open('tokens.json') as f:
    token_json = json.load(f)

discord_token = token_json['DISCORD_TOKEN']
imgur_client_id = token_json['IMGUR_CLIENT_ID']
imgur_client_secret = token_json['IMGUR_CLIENT_SECRET']
imgur_access_token = token_json['IMGUR_ACCESS_TOKEN']
imgur_refresh_token = token_json['IMGUR_REFRESH_TOKEN']
reddit_client_id = token_json['REDDIT_CLIENT_ID']
reddit_client_secret = token_json['REDDIT_CLIENT_SECRET']
reddit_password = token_json['REDDIT_PASSWORD']
reddit_user_agent = 'python:Sir Lopez II:v1.0 (by /u/SirLopezII)'
reddit_username = 'SirLopezII'

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

imgClient = ImgurClient(imgur_client_id, imgur_client_secret,
                        imgur_access_token, imgur_refresh_token)
album = 'zUSjPD7'
uploadConfig = {
    'album': album,
    'name': 'Updated Summer fools pic',
    'title': 'Update Photo',
    'description': 'Grabbed automatically, hopefully this is important'
}
april_channel = 950560400661938197
test_channel = 748831892312424508

reddit = asyncpraw.Reddit(client_id=reddit_client_id,
                          client_secret=reddit_client_secret,
                          password=reddit_password,
                          user_agent=reddit_user_agent,
                          username=reddit_username)


class MyClient(discord.Client):
    driver = webdriver.Chrome(options=options)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.check_kairos())

    async def on_ready(self):
        await client.change_presence(
            status=discord.Status.online,
            activity=discord.Streaming(
                platform='YouTube',
                name='April Knights',
                url='https://www.youtube.com/watch?v=7FOETnVmpLM&t=970s'))
        print("Ready to record!")
        channel = client.get_channel(april_channel)
        message = "Is it getting hot in here? ||Or is that just Gryph :wink:||"
        await channel.send(message)

#check Kairos

    async def check_kairos(self):
        await self.wait_until_ready()
        channel = self.get_channel(april_channel)
        while not self.is_closed():
            screen_kairos = "https://old.reddit.com/r/ThePathOfKairos"
            try:
                driver.get(screen_kairos)
                driver.execute_script("window.scrollTo(0,30)", "")
                driver.save_screenshot('kairos_1.png')
            except:
                print("Owo what's this?")
                exit(-1)

            im1 = Image.open('kairos_1.png')
            im2 = Image.open('kairos_2.png')
            h1 = im1.histogram()
            h2 = im2.histogram()
            rms = math.sqrt(
                reduce(operator.add, map(lambda a, b:
                                         (a - b)**2, h1, h2)) / len(h1))
            if rms > 0.5:
                image_is_different = True
            else:
                image_is_different = False
            if image_is_different:
                print(rms)
                imgur_image = imgClient.upload_from_path('kairos_1.png',
                                                         config=uploadConfig,
                                                         anon=False)
                imgur_link = str(imgur_image['link'])
                driver.save_screenshot('kairos_2.png')
                msg = "New __**Path of Kairos**__ change detected: " + imgur_link
                await channel.send(msg)
            await asyncio.sleep(20)

    async def on_message(self, message):
        if message.author == client.user:
            return
        if '?update' in message.content.lower():
            split_message = message.content.split()
            if split_message[0].lower() != '?update':
                return
            screenshot_url2 = "https://www.reddit.com/r/ThePathOfKairos"
            driver.get(screenshot_url2)
            driver.execute_script("window.scrollTo(0,30)", "")
            driver.save_screenshot('screenshot.png')
            imgur_image = imgClient.upload_from_path('screenshot2.png',
                                                     config=uploadConfig,
                                                     anon=False)
            imgur_link = str(imgur_image['link'])
            msg = "Path of Kairos reset to: " + imgur_link
            await message.channel.send(msg)
            return

client = MyClient()
client.run(discord_token)
