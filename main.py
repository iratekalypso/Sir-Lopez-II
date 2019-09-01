#!  /usr/bin/env python3

import asyncio
import aiohttp
from discord import Game
from discord.ext import tasks
from discord.ext.commands import Bot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from functools import reduce
import math
import operator
import discord
from imgurpython import *
import json
import os
import sys
import atexit
import praw
from praw.models import Message
import requests
import time
import shutil

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
reddit_client_id = token_json['REDDIT_CLIENT_ID']
reddit_client_secret = token_json['REDDIT_CLIENT_SECRET']
reddit_password = token_json['REDDIT_PASSWORD']
reddit_user_agent = token_json['REDDIT_USERAGENT']
reddit_username = token_json['REDDIT_USERNAME']

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

reddit = praw.Reddit(client_id=reddit_client_id,
                     client_secret=reddit_client_secret,
                     password=reddit_password,
                     user_agent=reddit_user_agent,
                     username=reddit_username)


def pidclose():
    os.unlink(pidfile)


atexit.register(pidclose)


class MyClient(discord.Client):
    driver = webdriver.Chrome(chrome_options=options)
    list_of_subs = ["ThePathOfKairos", "Layer", "Layers", "Layer_layers", "Page_pages", "seed_seeds", "digit_digits"]
    list_of_good_boys = ""
    list_of_bad_boys = ""
    list_of_big_boys = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.check_subs())
        self.bg_task = self.loop.create_task(self.check_inbox())

    def check_images(self, image1, image2):
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

    async def knight_auth_init(self):
        guild = self.get_guild(295643919553921035)
        roles = guild.roles
        user_roles = [429776126676697101, 295645777072750592, 430856798527029261, 430856947277758474, 430857042643648553]
        big_boy_roles = [524643194626113536, 295644396739756034]
        bad_boy_roles = [431083896080433162, 444334246232850452]
        # Let all knights participate
        for role in user_roles:
            role_obj = guild.get_role(role)
            role_members = role_obj.members
            self.list_of_good_boys += str(role_members)
        # Let admins use big boy commands
        for role in big_boy_roles:
            role_obj = guild.get_role(role)
            role_members = role_obj.members
            self.list_of_big_boys += str(role_members)
        # Leave sassy commands when bad boys try
        for role in bad_boy_roles:
            role_obj = guild.get_role(role)
            role_members = role_obj.members
            self.list_of_bad_boys += str(role_members)

    async def on_ready(self):
        print("Ready to record!")
        channel_id = 585303573613510680
        channel = self.get_channel(channel_id)
        message = "Is it getting hot in here? Or is that just Gryph :wink:"
        await channel.send(message)
        await self.knight_auth_init()

    async def check_inbox(self):
        await self.wait_until_ready()
        msg_count = 0
        channel_id = 476120967580745729
        channel = self.get_channel(channel_id)
        while not self.is_closed():
            msg = ""
            for item in reddit.inbox.unread(limit=None):
                if isinstance(item, Message):
                    if str(item.author) == 'None':
                        author_print = 'Sub mods'
                    else:
                        author_print = str(item.author)
                    msg += ("From: " + author_print + "\nSubject: " + str(item.body) + "\n")
                    msg_count += 1
                    # await channel.send(msg)
                    item.mark_read()
                    print(msg)
            if msg != "":
                message = "Message reply received from mods: \n" + msg
                await channel.send(message)
            await asyncio.sleep(29)

    async def check_subs(self):
        await self.wait_until_ready()
        channel_id = 476120967580745729
        channel = self.get_channel(channel_id)
        while not self.is_closed():
            t0 = time.time()
            for subreddit in self.list_of_subs:

                image_is_different = self.check_images(subreddit + '.png', subreddit + '2.png')

                if image_is_different:
                    imgur_image = imgClient.upload_from_path(subreddit + '2.png', config=uploadConfig, anon=False)
                    imgur_link = str(imgur_image['link'])
                    shutil.copyfile(subreddit + '2.png', subreddit + '.png')
                    msg = "New " + subreddit + " message detected: " + imgur_link
                    await channel.send(msg)
            t1 = time.time()
            print("Time (s): " + str(t1 - t0))
            await asyncio.sleep(60)

    # async def on_disconnect(self):
    #     driver.close()

    async def on_message(self, message):
        if message.author == client.user:
            return
        if str(message.author.id) in self.list_of_bad_boys:
            msg = "https://gph.is/2l3ekKZ"
            await message.channel.send(msg)
            return
        elif str(message.author.id) not in self.list_of_good_boys:
            msg = "Sorry, looks like you're missing a Knight role or two. Ping an officer for any questions..."
            await message.channel.send(msg)
            return
        else:
            # TODO: Fix this function
            if '?update' in message.content.lower():
                split_message = message.content.split()
                if split_message[0].lower() != '?update':
                    return
                screenshot_url2 = "https://www.reddit.com/r/ThePathOfKairos"
                driver.get(screenshot_url2)
                driver.save_screenshot('screenshot.png')
                imgur_image = imgClient.upload_from_path('screenshot2.png', config=uploadConfig, anon=False)
                imgur_link = str(imgur_image['link'])
                msg = "Path of Kairos reset to: " + imgur_link
                await message.channel.send(msg)

            # ModMsg Mostly provided by Satan#0001
            elif '?modmsg' in message.content.lower():
                split_message = message.content.split()
                if split_message[0].lower() != '?modmsg':
                    return
                if len(split_message) > 1:
                    solution = " ".join(split_message[1:])
                    if "spam" in solution.lower():
                        await message.channel.send("The word 'spam' is blocked due to "
                                                   "Reddit's auto help system picking it up. Sorry :(")
                    else:
                        try:
                            # TODO: Change the sub back to the og one
                            reddit.subreddit('ghostisedoesnotsuck').message(solution, solution)
                            await message.channel.send("Solution sent!")
                        except:
                            await message.channel.send("Owo looks like yew made a fucky wucky. A weal FUCKO BOINGO")
                else:
                    await message.channel.send("No message provided, I'm not sending blank lines....")

            elif '?inbox' in message.content.lower():
                split_message = message.content.split()
                if split_message[0].lower() != '?inbox':
                    return
                msg_count = 0
                for item in reddit.inbox.unread(limit=None):
                    if isinstance(item, Message):
                        if str(item.author) == 'None':
                            author_print = 'Sub mods'
                        else:
                            author_print = str(item.author)
                        msg = ("From: " + author_print + "\nMessage: " + str(item.body) + "\n")
                        msg_count += 1
                        await message.channel.send(msg)
                        item.mark_read()
                if msg_count == 0:
                    msg = "Sorry, inbox is empty..."
                    await message.channel.send(msg)
            # Overly complex function that uses regular requests for speed but defaults to asyncio requests after
            elif '?tiny' in message.content.lower():
                split_message = message.content.split()
                if split_message[0].lower() != '?tiny':
                    return
                if len(split_message) > 2:
                    msg = "I'm sorry but it looks like you sent too much. Please use ``?link linkGuess``"
                else:
                    try:
                        tiny_url = requests.head("https://tinyurl.com/" + str(split_message[1]))
                        if tiny_url.ok:
                            msg = "Looks like " + str(tiny_url.url) + " is a valid link. Czech it out!"
                        else:
                            msg = "Doesn't look like " + str(tiny_url.url) + " is legit. 9/10 a little " \
                                                                             "something for everybody"
                    except:
                        try:
                            async with aiohttp.ClientSession() as session:
                                async with session.get("https://tinyurl.com/" + str(split_message[1])) as tiny_url:
                                    if tiny_url.real_url:
                                        msg = "Looks like " + str(tiny_url.url) + " is a valid link. Czech it out!"
                                    else:
                                        msg = "Doesn't look like " + str(tiny_url.url) + " is legit. 9/10 a little " \
                                                                                         "something for everybody"
                        except:
                            msg = "Grabbing the url didn't work? Try again and/or ping Yew"
                await message.channel.send(msg)
            elif "?help" == message.content.lower():
                msg = "Help for Sir Lopez 2 The Electric Boogaloo\n" \
                      "Sir Lopez's Automatic features:\n" \
                      "Inbox:\n" \
                      "\tMonitors the bot's inbox and sends the messages it receives\n" \
                      "Path of Kairos:\n" \
                      "\tMonitors the Path of Kairos and screenshots it upon the subreddit changing or the bot failing\n" \
                      "====================================\n" \
                      "Sir Lopez's Manual Features (~~$69~~ FREE Premium DLC)\n" \
                      "``?update``: \n" \
                      "\tManually checks Path of Kairos and resets the ref. image to what it takes a picture of then\n" \
                      "``?inbox``:\n" \
                      "\tChecks the inbox and reports any unread messages.\n" \
                      "``modmsg <Message to send to mods>``:\n" \
                      "\tSends the mods of Path of Kairos the message you specify.\n" \
                      "``?tiny <URLPART>``:\n" \
                      "\tChecks https://tinyurl.com/URLPART and sees if it is a valid link or not.\n" \
                      "====================================\n" \
                      "Sir Lopez's Restricted functions: Won't work for anyone who can't handle the neutron style:\n" \
                      "``?reboot``:\n" \
                      "\tReboots Sir Lopez, great for when he's acting rudely.\n" \
                      "``?sleep <XX>``:\n:" \
                      "\tPuts Sir Lopez into an absolute slumber for XX minutes (CANNOT BE WOKEN UP AT ALL). " \
                      "You can't kill a god, but you may make him slumber...\n"
                channel = message.author.dm_channel
                await channel.send(msg)

            elif "?reboot" == message.content.lower() and \
                    (message.author.id == 165688608190103552 or str(message.author.id) in self.list_of_big_boys):
                exit(-1)

            elif "?sleep" in message.content.lower() and \
                    (message.author.id == 165688608190103552 or str(message.author.id) in self.list_of_big_boys):

                split_content = message.content.split()
                if len(split_content) != 2:
                    return
                else:
                    try:
                        time_to_sleep_in_min = int(split_content[1])
                        msg = "Going to sleep for " + split_content[1] + " minutes... See you later alligators"
                        await message.channel.send(msg)
                        time.sleep(time_to_sleep_in_min * 60)
                        msg = "I'm back y'all"
                        await message.channel.send(msg)
                    except:
                        return


client = MyClient()
client.run(discord_token)
