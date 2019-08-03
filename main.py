# ! /usr/bin/env python3

import asyncio
import aiohttp
from discord import Game
from discord.ext.commands import Bot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from functools import reduce
import math, operator
import uuid
import discord
from imgurpython import *
import datetime
import json

import os
import sys
import atexit

pid = str(os.getpid())
pidfile = "/tmp/mydaemon.pid"

if os.path.isfile(pidfile):
    print("%s already exists, exiting" % pidfile)
    sys.exit()
open(pidfile, 'w').write(pid)

BOT_PREFIX = ("?", "!")
client = Bot(command_prefix=BOT_PREFIX)
with open('tokens.json') as f:
    token_json = json.load(f)
discord_token = token_json['DISCORD_TOKEN']
imgur_client_id = token_json['IMGUR_CLIENT_ID']
imgur_client_secret = token_json['IMGUR_CLIENT_SECRET']
imgur_access_token = token_json['IMGUR_ACCESS_TOKEN']
imgur_refresh_token = token_json['IMGUR_REFRESH_TOKEN']

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(chrome_options=options)

imgClient = ImgurClient(imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token)
album = 'b6ZIp1m'
uploadConfig = {
    'album': album,
    'name': 'Updated Summer fools pic',
    'title': 'Update Photo',
    'description': 'Grabbed automatically, hopefully this is important'
}


def pidclose():
    os.unlink(pidfile)


atexit.register(pidclose)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        # self.bg_task = self.loop.create_task(self.check_snekbait())
        self.bg_task = self.loop.create_task(self.check_kairos())

    async def on_ready(self):
        print("Ready to record!")
        channel_id = 476120967580745729
        channel = self.get_channel(channel_id)
        message = "Is it getting hot in here? Or is that just Gryph :wink:"
        await channel.send(message)

    async def check_kairos(self):
        await self.wait_until_ready()
        channel_id = 588704610391293961
        channel = self.get_channel(channel_id)
        while not self.is_closed():
            screenshot_url2 = "https://www.reddit.com/r/ThePathOfKairos"
            try:
                driver.get(screenshot_url2)
                driver.save_screenshot('screenshot2.png')
            except:
                print("Owo what's this?")
                exit(-1)

                # driver.close()
            im1 = Image.open('screenshot2.png')
            im2 = Image.open('screenshot.png')
            h1 = im1.histogram()
            h2 = im2.histogram()
            rms = math.sqrt(reduce(operator.add,
                                   map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1))
            print(rms)
            if rms > 0.5:
                image_is_different = True
            else:
                image_is_different = False
            if image_is_different:
                # msg = "Check snekbait"
                imgur_image = imgClient.upload_from_path('screenshot2.png', config=uploadConfig, anon=False)
                imgur_link = str(imgur_image['link'])
                driver.save_screenshot('screenshot.png')
                msg = "New Path of Kairos message detected:" + imgur_link
                await channel.send(msg)
                # msg = "<@165688608190103552> and <@332245843983990786> and <@126011690419617792>"
                # await channel.send(msg)
            # else:
            # msg = "For debugging only"
            # await channel.send(msg)

            await asyncio.sleep(60)



    async def on_disconnect(self):
        driver.close()

    async def on_message(self, message):
        if message.author == client.user:
            return
        if '?update' in message.content:
            screenshot_url2 = "https://www.reddit.com/r/ThePathOfKairos"
            driver.get(screenshot_url2)
            driver.save_screenshot('screenshot.png')
            imgurImage = imgClient.upload_from_path('screenshot2.png', config=uploadConfig, anon=False)
            imgurLink = str(imgurImage['link'])
            msg = "Path of Kairos reset to: " + imgurLink
            await message.channel.send(msg)
        # Insert your code here


client = MyClient()
client.run(discord_token)



