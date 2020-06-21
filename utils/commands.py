from utils import utils, globals, statUtils
import copy, json

cmdList= {
    "settings": {
        "desc": "Display bot settings",
        "args": ""
    },
    "series": {
      "desc": "Lists series + ids",
      "args": ""
    },
    "setdelay": {
        "desc": "Interval between updates (seconds)",
        "args": "`(integer)`"
    },
    "setdiscorddelay": {
        "desc": "Delay before update is published (seconds)",
        "args": "`(integer)`"
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
    },
    "addrole": {
        "desc": "Add role mention for a specific series",
        "args": "`(series_id)` `(role_id)`"
    },
    "removerole": {
        "desc": "Remove role mention for a specific series",
        "args": "`(series_id)` `(role_id)`"
    },
    "help": {
        "desc": "Display command list",
        "args": ""
    },
    "listroles": {
        "desc": "List role ids",
        "args": ""
    }
}

async def listRoles(message, client):
    roles= await client.get_guild(401178214258704384).fetch_roles()
    ret= ""
    for r in roles:
        ret+= f"{r.name.ljust(15)} {r.id}\n"

    while len(ret) > 1600:
        await message.channel.send(f"```py\n{ret[:1600]}```")
        ret= ret[1600:]
    if ret: await message.channel.send(f"```py\n{ret[:1600]}```")

def getUseString(cmd, client):
    t= f"`{client.prefix}{cmd}`"
    print(cmd)
    print(cmdList[cmd])
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
    print(val)
    val= val.replace("<","").replace("#","").replace("@","").replace(">","").replace("&","")
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
    text+= "\nContact Literal Genie#2222 for issues."

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

    await message.channel.send(f"Updates will be checked every `{val}` seconds (from `{oldDelay}`).")
	
async def setDiscordDelay(message, client):
    split= message.content.split()
    correctUsageString= getUseString("setdelay", client)

    if await checkMinArgs(message, 1, correctUsageString): return

    val= await checkInt(message, split[1], correctUsageString)
    if val is False: return
    if val < 0: return await sendError(message, "Delay interval must be positive", correctUsageString)

    config= utils.loadJson(globals.CONFIG_FILE)
    oldDelay= config["DISCORD_DELAY"]
    config["DISCORD_DELAY"]= val
    utils.dumpJson(config, globals.CONFIG_FILE)

    await message.channel.send(f"Updates are delayed `{val}` seconds (from `{oldDelay}`).")

async def modChannel(message, client, typ):
    split= message.content.split()
    correctUsageString= getUseString(typ + "channel", client)

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
    correctUsageString= getUseString(typ + "user", client)

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

async def modMention(message, client, typ):
    split= message.content.split()
    correctUsageString= getUseString(typ + "role", client)

    if await checkMinArgs(message, 2, correctUsageString): return

    sid= await checkInt(message, split[1], correctUsageString)
    if sid is False: return

    rid= await checkInt(message, split[2], correctUsageString)
    if rid is False: return

    role= message.guild.get_role(int(rid))
    if not role: return await sendError(message, f"{split[2]} is not a valid role id.", correctUsageString)

    mentions= utils.loadJson(globals.MENTION_FILE)

    sData= utils.loadJson(globals.SERIES_FILE)
    sName= str(sid)
    if str(sid) in sData: sName= f"{sData[str(sid)]['title']} ({sName})"

    if typ == "add":
        if str(sid) not in mentions: mentions[str(sid)]= []
        if str(rid) in mentions[str(sid)]: return await message.channel.send(f"Error. `{role.name} ({rid})` is already a mentioned role for series `{sName}`.")
        mentions[str(sid)].append(str(rid))
    elif typ == "remove":
        if str(rid) not in mentions[str(sid)]: return await message.channel.send(f"Error. `{role.name} ({rid})` is not a mentioned role for series `{sName}`.")
        mentions[str(sid)]= [x for x in mentions[str(sid)] if str(x) != str(rid)]

    lst= []
    for x in mentions[str(sid)]:
        role= message.guild.get_role(int(rid))
        if role: name= role.name
        else:
            continue
            name= "unknown"

        lst.append(f"`{name} ({x})`")
    await message.channel.send(f"Pinged roles for **`{sName}`**: " + ", ".join(lst))

    utils.dumpJson(mentions, globals.MENTION_FILE)

async def settings(message, client):
    config= utils.loadJson(globals.CONFIG_FILE)
    config['mentions']= utils.loadJson(globals.MENTION_FILE)
    del config["DISCORD_KEY"]


    # Make channels readable
    cpy= []
    for chid in config['UPDATE_CHANNELS']:
        uCh= client.get_channel(int(chid))
        if int(uCh.guild.id) != int(message.guild.id): cpy.append(uCh.id)
        else: cpy.append(f"{uCh.name} ({uCh.id})")
    config['UPDATE_CHANNELS']= cpy


    # Make roles readable
    sData= utils.loadJson(path=globals.SERIES_FILE)
    cpy= copy.deepcopy(config['mentions'])
    for sid in cpy:
        for mid in cpy[sid]:
            mid= int(mid)
            role= message.guild.get_role(mid)
            if role: name= role.name
            else:
                if sid in config['mentions']:
                    config['mentions'][sid].remove(str(mid))
                    if sid in config['mentions'] and not config['mentions'][sid]: del config['mentions'][sid]
                continue
                name= "unknown"

            if str(sid) not in sData and str(sid) != "-1":
                stitle= "unknown"
                print("WARNING:", sid, "is an unknown series.")
            elif str(sid) != "-1":
                stitle= sData[str(sid)]['title']

            if sid != "-1": key= f"{stitle} ({sid})"
            else: key= "ALL (-1)"
            val= f"{name} ({mid})"

            if key not in config['mentions']:
                config['mentions'][key]= []
                del config['mentions'][sid]
            config['mentions'][key].append(val)

    # Make admins readable
    users= []
    for uid in config["ADMINS"]:
        user= client.get_user(int(uid))

        if user: name= user.name
        else: name= "unknown"

        val= f"{name} ({uid})"
        users.append(val)
    config['ADMINS']= users
	
    text= utils.breakMessage(json.dumps(config, indent=2), codeblock=True)

    for t in text:
        await message.channel.send(t)

async def listSeries(message, client):
    sData= utils.loadJson(globals.SERIES_FILE)
    lst= []

    for sid in sData:
        lst+= [f"[{utils.zeroPad(sid)}] {sData[sid]['title']}"]

    join= '\n'.join(lst)
    text= f"```css\n{join}\n```"
    await message.channel.send(text)

async def stats(message, client):
    split= message.content.split(maxsplit=1)

    data= utils.loadJson(globals.PARSED_FILE)
    tallies = statUtils.getTallies(data)

    if len(split) == 1:
        gStats= statUtils.getGlobalStats(tallies, data, num=3)

        h1 = ['Type', '30 Days', 'All-time']
        h2 = ['Type', 'Users (30 days)', 'Users (all)']
        p1= utils.pprint(gStats['all'], headers=h1)
        p2= utils.pprint(gStats['users'], headers=h2)

        p1= "\n".join(p1.split("\n")[:-1]) + "\n" + "".join(["-"]*len(p1.split("\n")[0])) + "\n" + p1.split("\n")[-1]

        title= "@ All Users"
        s= f"""```py\n\n{title}\n\n{p1}\n\n{p2}\n```"""
        s= utils.breakMessage(s, codeblock=True, lang="py")

        for m in s:
            await message.channel.send(m)
        return
    else:
        spl= split[1].split()
        catStats= statUtils.getCatStats(tallies)

        username= None
        for x in data['members']:
            if all([y.lower() in data['members'][x].lower() for y in spl]):
                username= data['members'][x]
                break

        if not username: return await message.channel.send(f"Error. `{split[1]}` is not a known user.")

        uStats= statUtils.getUserStats(username, data, tallies)
        for x in uStats['stats']:
            cat= x[0].lower()
            rankRecent= 1+catStats[cat]['recent'].index(int(x[1]))
            rankAll= 1+catStats[cat]['all'].index(int(x[2]))
            x[1]= f"{x[1].ljust(3)}" + f"(rank-{rankRecent})".rjust(10)
            x[2]= f"{x[2].ljust(3)}" + f"(rank-{rankAll})".rjust(10)

        h1= ['Type'.ljust(7), '30 Days', 'All-time']
        h2= ['Type'.ljust(7), 'Days Ago', 'Chap', 'Series']

        p1 = utils.pprint(uStats['stats'], headers=h1)
        p1= "\n".join(p1.split("\n")[:-1]) + "\n" + "".join(["-"]*len(p1.split("\n")[0])) + "\n" + p1.split("\n")[-1]

        if uStats['recent']: p2= "\n\n"+utils.pprint(uStats['recent'], headers=h2)
        else: p2= ""

        title= f"@ {username}"
        s= f"""```py\n{title}\n\n{p1}{p2}\n```"""
        s= utils.breakMessage(s, codeblock=True, lang="py")

        for msg in s:
            await message.channel.send(msg)
        return
