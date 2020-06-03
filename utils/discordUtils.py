from utils import utils, globals, sheetUtils
from utils.commands import *
import discord, json

class Client(discord.Client):
    def load(self, prefix="$"):
        self.prefix= prefix

    async def on_ready(self):
        print('Logged in as', self.user.name, self.user.id)
        act= discord.Activity(name=f"{self.prefix}help for commands", type=discord.ActivityType.playing)
        await self.change_presence(activity=act)

    async def on_message(self, message):
        if message.author.id == self.user.id: return

        m= message.content.lower().replace(self.prefix, "", 1)
        args= [message, self]

        if str(message.author.id) in utils.loadJson(globals.CONFIG_FILE)['ADMINS']:
            if m.startswith("help"): await help(*args)
            elif m.startswith("sett"): await settings(*args)
            elif m.startswith("setd"): await setDelay(*args)
            elif m.startswith("addc"): await modChannel(*args, typ="add")
            elif m.startswith("removec"): await modChannel(*args, typ="remove")
            elif m.startswith("addu"): await modUser(*args, typ="add")
            elif m.startswith("removeu"): await modUser(*args, typ="remove")
            elif m.startswith("addr"): await modMention(*args, typ="add")
            elif m.startswith("remover"): await modMention(*args, typ="remove")
            elif m.startswith("ser"): await listSeries(*args)
            elif m.startswith("update"): await updateSheet(self)

        if message.guild.id == 425423910759170049:
            pass


async def scanMessages(client, last=None):
    channel= client.get_channel(425992635086405632)
    log= utils.loadJson(globals.MSG_FILE)
    async for msg in channel.history(limit=None, oldest_first=True, after=last):
        log['log'].append(sheetUtils.msgToDict(msg))
        log['members'][msg.author.id]= msg.author.name
        log['last_parsed']= msg.id

    with open("data/msg_log.json", "r+") as file:
        json.dump(log, file, indent=2)

async def updateSheet(client):
    import utils.parseMsgs, utils.createSheet

    await scanMessages(client)
    utils.parseMsgs.parse()
    utils.createSheet.make()