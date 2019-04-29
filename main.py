import asyncio
import aiohttp
from discord import Game
from discord.ext.commands import Bot
import datetime
import pyodbc
import math

db_host = '10.59.68.25'
db_name = 'AprilKnights'
db_user = 'KnightsBot'
db_password = "this aint my db password"
connection_string = 'Driver={ODBC Driver 17 for SQL Server};Server=' + db_host + ';Database=' + db_name + ';UID=' + \
                    db_user + ';PWD=' + db_password + ';'

BOT_PREFIX = ("?", "!")
client = Bot(command_prefix=BOT_PREFIX)
TOKEN = "this aint my token"


@client.event
async def on_ready():
    print("Ready to record!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "?usercheck" in message.content.lower():
        content = message.content.split()
        if "?usercheck help" == message.content.lower():
            msg = "To check a user's status, please use usercheck as such:" + \
                  "``?usercheck discordID discordID``, ``?usercheck discordH " + \
                  " discord#handle`` (not nickname), or ``?usercheck reddit username``"

        if len(content) != 3:
            msg = "I'm sorry you've used the wrong amount of arguments. Please use usercheck as such" +\
                  "``?usercheck discordID discordID``, ``?usercheck discordH " + \
                " discord#handle`` (not nickname), or ``?usercheck reddit username``"
            await client.send_message(message.channel, msg.format(message))
            return
        method = content[1]
        user = content[2]
        if method.lower() == 'discordid':
            method = 'discord_id'
        elif method.lower() == 'discordh':
            method = 'discord_handle'
        elif method.lower() == 'reddit':
            method = 'reddit_username'
        else:
            msg = throw_usercheck_error('wrong method').format(message)
            await client.send_message(message.channel, msg.format(message))
            return
        sql_string = "SELECT discord_handle, discord_id, reddit_username, in_knights, in_swarm, in_snakeroom" + \
            " FROM dbo.user_groups WHERE " + method + " LIKE '%' + '" + user + "' + '%'"
        query_data = sql_read(sql_string)
        msg = "Results:\n"
        for user in query_data:
            msg = msg + "\nDiscord Handle: "+ str(user[0]) + "\nReddit Username: " + str(user[2]) + "\nDiscord ID: " + \
                str(user[1]) + ","


            if int(user[3]) == 1:
                inKnights = "Knights, "
            else:
                inKnights = ""
            if int(user[4]) == 1:
                inSwarm = "Swarm, "
            else:
                inSwarm = ""
            if int(user[5]) == 1:
                inSnake = "Snakeroom"
            else:
                inSnake = ""
            if (inKnights + inSwarm + inSnake == ""):
                inNothing = "0 important reddit april fools groups"
            else:
                inNothing = ""
            msg = msg + "\nBelongs in: " + inKnights + inSwarm + inSnake + inNothing + "\n"
        await client.send_message(message.channel, msg.format(msg))

    if "?useradd" in message.content.lower():
        if "?useradd help" == message.content.lower():
            msg = "?useradd should be used as such ``?userAdd discord#Handle discordID PrimaryGroup(Knight, Swarm," \
                  " or Snake)`` Example: ``?userAdd yewhotook#6969 123456789 Knight`` Multiple groups can be added later us" \
                  "ing ?userEdit. The reddit username can be added there as well"
            await client.send_message(message.channel, msg.format(message))
            return
        else:
            content = message.content.split()
            discord_handle = content[1]
            if '#' not in discord_handle:
                msg = throw_usercheck_error('grabbed nickname')
                await client.send_message(message.channel, msg.format(message))
                return
            if len(content) != 4:
                msg = throw_usercheck_error('add few args')
                await client.send_message(message.channel, msg.format(message))
                return

            discord_id = content[2]
            group = content[3]
            if group.lower() == 'knight':
                group = 'in_knights'
                not_group = "in_swarm, in_snakeroom"
            elif group.lower() == 'swarm':
                group = 'in_swarm'
                not_group = "in_knights, in_snakeroom"
            elif group.lower() == 'snake':
                group = 'in_snakeroom'
                not_group = 'in_knights, in_swarm'
            else:
                msg = throw_usercheck_error('wrong group').format(message)
                await client.send_message(message.channel, msg)
                return
            sql_string = "INSERT INTO dbo.user_groups (discord_handle,discord_id," + group + "," + not_group + ") VALUES ('" + \
                discord_handle + "','" + discord_id + "','1','0','0')"

            sql_write(sql_string)

                # msg = throw_usercheck_error('failed write').format(message)
                # await client.send_message(message.channel, msg)
                # return
            msg = "Person added successfully! Edit them using ``?userEdit``"
            await client.send_message(message.channel, msg)
    if '?useredit' in content.message.lower():
        if '?useredit help' == content.message.lower():
            msg = "To edit a users info run ``?userEdit ExamplediscordID [discordId,discordHandle,reddit] newInfo``. To change" \
                  "group affiliation type ``?userEdit group add/remove ExamplediscordID [Knights, Snake, Swarm]. Run " \
                  "``?userCheck`` to grab the discord ID if you don't know it"
        if '?useredit group' in content.message.lower():
            content = message.split()
            groups = grabTheRestOfTheString(4, content)
            add_or_remove = content[2].lower()
            if add_or_remove != 'add' or add_or_remove != 'remove':
                msg = throw_usercheck_error('wrong group change')





def sql_write(sql_string):
    db = pyodbc.connect(connection_string)
    cursor = db.cursor()
    cursor.execute(sql_string)
    cursor.commit()
    cursor.close()
    db.close()


def sql_read(sql_string):
    query_data = []
    db = pyodbc.connect(connection_string)
    cursor = db.cursor()
    cursor.execute(sql_string)
    for row in cursor.fetchall():
        query_data.append(row)
    cursor.commit()
    cursor.close()
    db.close()
    return query_data

def grabTheRestOfTheString(idx0, splitString):
    returnString = ""
    for idx, val in enumerate(splitString):
        if idx >= idx0:
            returnString = returnString + " " + val
            if idx == idx0:
                returnString = returnString.strip()
    return returnString
def throw_usercheck_error(error_string):
    if error_string == 'wrong method':
        msg = "I'm sorry but it seems as if you've put in the wrong argument for the type of identification. " + \
            "Please use ``discordID``, ``discordH``, or ``reddit``. \nSee ``?userCheck help`` for more details."

    elif error_string == 'failed write':
        msg = "I'm sorry but it seems I couldn't write to the database. If this issue persists, contact yew."
    elif error_string == 'wrong group':
        msg = "I'm sorry but you've entered an invalid group for ?userAdd. It should be Knight, Swarm, or Snake"
    elif error_string == 'add few args':
        msg = "I'm sorry but you've entered the wrong amount of arguments for ?userAdd. Please run ?userAdd help for " \
              "details."
    elif error_string == 'grabbed nickname':
        msg = "Whoops, it looks like you've grabbed their nickname and not their handle. Look for the name with the #" \
              "in it"

    return msg


client.run(TOKEN)