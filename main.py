#!  /usr/bin/env python3

import asyncio
import aiohttp
from discord import Game
from discord.ext import tasks
from discord.ext.commands import Bot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
import yaml
import datetime
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
driver = webdriver.Chrome(options=options)

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
    driver = webdriver.Chrome(options=options)
    list_of_subs = ["ThePathOfKairos", "Layers", "Layer_layers", "Page_pages", "seed_seeds", "digit_digits"]
    list_of_good_boys = ""
    list_of_bad_boys = ""
    list_of_big_boys = ""
    mega_imgur_list = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.check_subs())
        self.bg_task = self.loop.create_task(self.check_inbox())

    def knight_auth(self, user_id):
        if str(user_id) in self.list_of_big_boys or str(user_id) in self.list_of_good_boys:
            return True
        else:
            return False

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
        channel_id = 588704610391293961
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
            await asyncio.sleep(60)

    async def check_subs(self):
        await self.wait_until_ready()
        channel_id = 585303573613510680
        channel = self.get_channel(channel_id)
        while not self.is_closed():
            # Check for a difference and then send it if there is
            # Load list of subs
            with open("subs.yml", 'r') as stream:
                try:
                    subreddit_dict = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
            for subreddit in subreddit_dict['SubredditsToGrab']:
                if subreddit['imgur-link'] not in self.mega_imgur_list:
                    msg = subreddit['name'] + " has updated!\n" + subreddit['imgur-link']
                    self.mega_imgur_list.append(subreddit['imgur-link'])
                    await channel.send(msg)
            await asyncio.sleep(60)

    # async def on_disconnect(self):
    #     driver.close()

    async def on_message(self, message):
        if message.author == client.user:
            return
        # TODO: Command system is gross. Use Discord's or make this cleaner.
        if '?update' in message.content.lower():
            msg = "Whoopsy! This don't work no more!"
            await message.channel.send(msg)

        elif '?subadd' in message.content.lower():
            split_message = message.content.split()
            if split_message[0].lower() != '?subadd' or not self.knight_auth(message.author.id):
                return
            if len(split_message) != 2:
                msg = "I'm sorry but it looks like you sent too much. Please use ``?subadd sub_title``"
            else:
                new_subreddit = {'name': split_message[1], 'date-added': datetime.datetime.today(), 'imgur-link':
                                 "http://bing.com"}
                try:
                    # Grab sub list
                    with open("subs.yml", 'r') as stream:
                        try:
                            subreddit_dict = yaml.safe_load(stream)
                        except yaml.YAMLError as exc:
                            print(exc)
                    # Add new subreddit
                    subreddit_dict['SubredditsToGrab'].append(new_subreddit)
                    #W Write sub list
                    with open("subs.yml", 'w') as stream:
                        try:
                            yaml.dump(subreddit_dict, stream)
                        except yaml.YAMLError as exc:
                            print(exc)
                    # Create a base image so the code will trigger once.
                    shutil.copyfile("BASE_IMG.png", split_message[1] + '.png')
                    msg = "I've added this to be checked. There should be a new update soon."
                    await message.channel.send(msg)
                except Exception as e:
                    print(e)
                    msg = "Whoops! Looks like it didn't work. Try again?"
                    await message.channel.send(msg)

        elif "?subremove" in message.content.lower():
            split_message = message.content.split()
            if split_message[0].lower() != '?subremove' or not self.knight_auth(message.author.id):
                return
            if len(split_message) != 2:
                msg = "I'm sorry but it looks like you sent too much. Please use ``?subremove sub_title``"
            else:
                try:
                    # Load the subs list
                    with open("subs.yml", 'r') as stream:
                        try:
                            subreddit_dict = yaml.safe_load(stream)
                        except yaml.YAMLError as exc:
                            print(exc)
                    # Remove the identified sub
                    for idx, subreddit in enumerate(subreddit_dict['SubredditsToGrab']):
                        if split_message[1].lower() == subreddit['name']:
                            del subreddit_dict['SubredditsToGrab'][idx]
                    # Rewrite the subs list
                    with open("subs.yml", 'w') as stream:
                        try:
                            yaml.dump(subreddit_dict, stream)
                        except yaml.YAMLError as exc:
                            print(exc)
                    msg = "Sub removed. Shouldn't update anymore."
                    print("Removed sub uwu")
                    await message.channel.send(msg)
                except Exception as e:
                    print(e)
                    msg = "Whoops I couldn't remove that. Please try again or ping yew."
                    message.channel.send(msg)

        # ModMsg Mostly provided by Satan#0001
        elif '?modmsg' in message.content.lower():
            split_message = message.content.split()
            if split_message[0].lower() != '?modmsg' or not self.knight_auth(message.author.id):
                return
            if len(split_message) > 1:
                solution = " ".join(split_message[1:])
                if "spam" in solution.lower():
                    await message.channel.send("The word 'spam' is blocked due to "
                                               "Reddit's auto help system picking it up. Sorry :(")
                else:
                    try:
                        reddit.subreddit('ThePathOfKairos').message(solution, solution)
                        await message.channel.send("Solution sent!")
                    except:
                        await message.channel.send("Owo looks like yew made a fucky wucky. A weal FUCKO BOINGO")
            else:
                await message.channel.send("No message provided, I'm not sending blank lines....")

        elif '?inbox' in message.content.lower():
            split_message = message.content.split()
            if split_message[0].lower() != '?inbox' or not self.knight_auth(message.author.id):
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
            channel = message.author
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
