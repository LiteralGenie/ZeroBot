from utils import utils, globals
import discord, json, copy

class Client(discord.Client):
    def load(self, prefix="!"):
        self.prefix= prefix

    async def on_ready(self):
        print('Logged in as', self.user.name, self.user.id)

    async def on_message(self, message):
        if message.author.id == self.user.id: return
        if str(message.author.id) not in utils.loadJson(globals.CONFIG_FILE)['ADMINS']: return

        m= message.content.lower().replace(self.prefix, "", 1)
        args= [message, self]

        if m.startswith("help"): await help(*args)
        elif m.startswith("sett"): await settings(*args)
        elif m.startswith("setd"): await setDelay(*args)
        elif m.startswith("addc"): await modChannel(*args, typ="add")
        elif m.startswith("removec"): await modChannel(*args, typ="remove")
        elif m.startswith("addu"): await modUser(*args, typ="add")
        elif m.startswith("removeu"): await modUser(*args, typ="remove")


cmdList= {
    "settings": {
        "desc": "Display bot settings",
        "args": ""
    },
    "setdelay": {
        "desc": "Sets how often the bot checks for updates (seconds)",
        "args": "`(integer)`"
    },
    "help": {
        "desc": "Display command list",
        "args": ""
    },
    "addchannel": {
        "desc": "Adds update channel",
        "args": "`(channel_id)`"
    },
    "removechannel": {
        "desc": "Adds update channel",
        "args": "`(channel_id)`"
    },
    "adduser": {
        "desc": "Grant bot permissions to user",
        "args": "`(user_id)`"
    },
    "removeuser": {
        "desc": "Remove bot permissions from user",
        "args": "`(user_id)`"
    }
}

def getUseString(cmd, client):
    t= f"`{client.prefix}{cmd}`"
    if cmdList[cmd]["args"]: t+= " " + cmdList[cmd]["args"]
    return t

def getError(msg, correctUsageString):
    return f"Error. {msg}\nCorrect Usage: {correctUsageString}"

async def sendError(message, errMsg, correctUsageString):
    await message.channel.send(getError(errMsg, correctUsageString))

async def checkMinArgs(message, numArgs, correctUsageString):
    split= message.content.split()[1:]
    if len(split) < numArgs:
        await sendError(message, "Not enough arguments", correctUsageString)
        return True
    return False

async def checkInt(message, val, correctUsageString):
    try:
        x= int(val)
        return x
    except:
        await sendError(message, f"{val} is not an integer.", correctUsageString)
        return False

async def help(message, client):
    text= ""

    for cmd in cmdList:
        t= getUseString(cmd, client)
        t+= " - " + cmdList[cmd]['desc']
        text+= t + "\n"

    await message.channel.send(text)

async def setDelay(message, client):
    split= message.content.split()
    correctUsageString= getUseString("setdelay", client)

    if await checkMinArgs(message, 1, correctUsageString): return

    val= await checkInt(message, split[1], correctUsageString)
    if val is False: return
    if val < 0: return await sendError(message, "Delay interval must be positive", correctUsageString)

    config= utils.loadJson(globals.CONFIG_FILE)
    oldDelay= config["UPDATE_DELAY"]
    config["UPDATE_DELAY"]= val
    utils.dumpJson(config, globals.CONFIG_FILE)

    await message.channel.send(f"Updates will be checked every {val} seconds (from {oldDelay}).")

async def modChannel(message, client, typ):
    split= message.content.split()
    correctUsageString= getUseString("setdelay", client)

    if await checkMinArgs(message, 1, correctUsageString): return

    val= await checkInt(message, split[1], correctUsageString)
    if val is False: return

    ch= client.get_channel(val)
    if not ch: return await sendError(message, f"{split[1]} is not a valid channel id.", correctUsageString)

    config= utils.loadJson(globals.CONFIG_FILE)

    if typ == "add":
        if str(val) in config["UPDATE_CHANNELS"]: return await message.channel.send(f"Error. <#{val}> is already an update channel.")
        config["UPDATE_CHANNELS"].append(str(val))
    elif typ == "remove":
        if str(val) not in config["UPDATE_CHANNELS"]: return await message.channel.send(f"Error. <#{val}> is not an update channel.")
        config["UPDATE_CHANNELS"]= [x for x in config['UPDATE_CHANNELS'] if x != str(val)]

    lst= [f"<#{x}>" for x in config['UPDATE_CHANNELS']]
    await message.channel.send("Current update channels:" + ", ".join(lst))

    utils.dumpJson(config, globals.CONFIG_FILE)

async def modUser(message, client, typ):
    split= message.content.split()
    correctUsageString= getUseString("setdelay", client)

    if await checkMinArgs(message, 1, correctUsageString): return
    val= await checkInt(message, split[1], correctUsageString)
    if val is False: return
    user= client.get_user(val)
    if not user: return await sendError(message, f"{split[1]} is not a valid user id.", correctUsageString)

    config= utils.loadJson(globals.CONFIG_FILE)

    if typ == "add":
        if str(val) in config["ADMINS"]: return await message.channel.send(f"Error. {user.name} ({val}) is already a bot admin.")
        config["ADMINS"].append(str(val))
    elif typ == "remove":
        if str(val) not in config["ADMINS"]: return await message.channel.send(f"Error. {user.name} ({val}) is not a bot admin.")
        config["ADMINS"]= [x for x in config['ADMINS'] if x != str(val)]

    lst= []
    for x in config['ADMINS']:
        user= client.get_user(int(x))
        if user: name= user.name
        else: name= "unknown"

        lst.append(f"`{name} ({x})`")
    await message.channel.send("Current admins: " + ", ".join(lst))

    utils.dumpJson(config, globals.CONFIG_FILE)

async def settings(message, client):
    config= utils.loadJson(globals.CONFIG_FILE)
    config['mentions']= utils.loadJson(globals.MENTION_FILE)
    del config["DISCORD_KEY"]


    # Make channels readable
    cpy= []
    for chid in config['UPDATE_CHANNELS']:
        uCh= client.get_channel(int(chid))
        cpy.append(f"{uCh.name} ({uCh.id})")
    config['UPDATE_CHANNELS']= cpy


    # Make roles readable
    sData= utils.loadJson(path=globals.SERIES_FILE)
    cpy= copy.deepcopy(config['mentions'])
    for sid in cpy:
        mid= int(cpy[sid])
        name= message.guild.get_role(mid).name

        if sid not in sData and sid != "-1": print("WARNING:", sid, "is an unknown series.")

        if sid != "-1": key= f"{sData[sid]} ({sid})"
        else: key= "ALL"
        val= f"{name} ({mid})"

        config['mentions'][key]= val
        del config['mentions'][sid]

    # Make admins readable
    users= []
    for uid in config["ADMINS"]:
        user= client.get_user(int(uid))

        if user: name= user.name
        else: name= "unknown"

        val= f"{name} ({uid})"
        users.append(val)
    config['ADMINS']= users

    await message.channel.send(f"```yaml\n{json.dumps(config, indent=2)}```")
