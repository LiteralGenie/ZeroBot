from utilss import utils, globals
from utilss.commands import *
import utilss.sheetUtils.sheetUtils as sheetUtils
import discord, json, traceback

import utilss.sheetUtils.parseMsgs as parse
import utilss.sheetUtils.createSheet as sheet

CONFIG= utils.loadJson(globals.CONFIG_FILE)

class Client(discord.Client):
    def load(self, prefix="$"):
        self.prefix = prefix

    async def on_ready(self):
        print('Logged in as', self.user.name, self.user.id)
        act = discord.Activity(name=f"{self.prefix}help for commands", type=discord.ActivityType.playing)
        await self.change_presence(activity=act)

    async def on_message(self, message):
        if message.author.id == self.user.id: return

        m = message.content.lower().replace(self.prefix, "", 1)
        args = [message, self]

        isAdmin= str(message.author.id) in utils.loadJson(globals.CONFIG_FILE)['ADMINS']
        if isAdmin:
            print(message.author.name, message.content)
            if m.startswith("help"):
                await help(*args)
            elif m.startswith("sett"):
                await settings(*args)
            elif m.startswith("setde"):
                await setDelay(*args)
            elif m.startswith("setdis"):
                await setDiscordDelay(*args)
            elif m.startswith("addc"):
                await modChannel(*args, typ="add")
            elif m.startswith("removec"):
                await modChannel(*args, typ="remove")
            elif m.startswith("addu"):
                await modUser(*args, typ="add")
            elif m.startswith("removeu"):
                await modUser(*args, typ="remove")
            elif m.startswith("addr"):
                await modMention(*args, typ="add")
            elif m.startswith("remover"):
                await modMention(*args, typ="remove")
            elif m.startswith("ser"):
                await listSeries(*args)
            elif m.startswith("listr"):
                await listRoles(*args)

        if isAdmin or message.guild.id == 425423910759170049:
            if m.startswith("stat"):
                print(message.author.name, message.content)
                await scanMessages(self, last=True)
                await stats(*args)
            elif m.startswith("update"):
                await updateSheet(self, message)


async def scanMessages(client, last=False):
    channel = client.get_channel(int(CONFIG['SUBMISSION_CHANNEL']))

    log= None
    if last: log= utils.loadJson(globals.MSG_FILE)
    if not log: log= {"log": [], "members": {}, "last_parsed": ""}

    try:
        if last and log["last_parsed"]: last= await channel.fetch_message(log['last_parsed'])
        else: last= None
    except:
        last=None
        print("resetting log")
        log= {"log": [], "members": {}, "last_parsed": ""}

    async for msg in channel.history(limit=None, oldest_first=True, after=last):
        print("Scanning", msg.content)
        log['log'].append(sheetUtils.msgToDict(msg))
        log['members'][msg.author.id] = msg.author.name
        log['last_parsed'] = msg.id

    with open("data/msg_log.json", "w+") as file:
        json.dump(log, file, indent=2)

    parse.parse()

    return len(log['log'])


async def updateSheet(client, message):


    try:
        async with message.channel.typing():
            await message.channel.send("Scanning messages...")
            print("Scanning")
            numMsgs= await scanMessages(client)

        async with message.channel.typing():
            await message.channel.send(f"Parsing {numMsgs} messages...")
            print(f"Parsing {numMsgs} messages...")
            parse.parse()

        # async with message.channel.typing():
        #     await message.channel.send("Uploading...")
        #     print("Uploading")
        sheet.make()
        #     print("Done")

        # await message.channel.send("Done: <https://docs.google.com/spreadsheets/d/blah>")
        await message.channel.send("Done")
    except Exception as e:
        traceback.print_exc()
        await message.channel.send(str(e) + "\n<@113843036965830657>")
