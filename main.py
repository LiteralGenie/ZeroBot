from utilss import discordUtils, utils, updateUtils, globals
import asyncio, discord, time, copy, traceback, json

# SETUP ----------------------
client= None
lastUpdate= {}

def reload():
    global CONFIG, CACHE, MENTIONS
    CONFIG= utils.loadJson(globals.CONFIG_FILE)
    CACHE= utils.loadJson(globals.CACHE_FILE, default= globals.CACHE_DEFAULT)
    MENTIONS= utils.loadJson(globals.MENTION_FILE)
reload()


# ASYNC FUNCTIONS ------------------
async def updateHandler(update):
    while not client.is_ready(): await asyncio.sleep(1)

    #updateMessage= updateUtils.getUpdateMessage(update=update, mentionDict=MENTIONS)
    updateEmbed, mentions= updateUtils.getUpdateEmbed(update=update, mentionDict=MENTIONS)



    for chid in CONFIG['TEST_CHANNELS']:
        test= client.get_channel(int(chid))
        if test:
            ss= f'Updating in {CONFIG["DISCORD_DELAY"]} seconds:\n```{json.dumps(update, indent=2)}```'
            print(ss)
            try: await test.send(ss)
            except discord.errors.Forbidden: pass

    await asyncio.sleep(delay=CONFIG['DISCORD_DELAY'])

    for chid in CONFIG['UPDATE_CHANNELS']:
        swapped= []
        updateChannel= client.get_channel(int(chid))
        if mentions:
            for roleId in mentions:
                role= updateChannel.guild.get_role(int(roleId))
                if role: #and not role.mentionable:
                    #await role.edit(mentionable=True)
                    swapped.append(role)
            time.sleep(5)
            mentionString= f"<@&{'> <@&'.join(mentions)}> **{updateEmbed['title']}**"
        else: mentionString= ""

        try:
            # Edit last update if same series
            # todo: cleanup caching, chap numbering
            doEdit= False

            global CACHE, lastUpdate
            ls= CACHE['last_sent']
            if "ids" in ls and str(chid) in ls['ids']\
                and ls['update_content'][str(chid)]['sId'] == update['sId']\
                and time.time() - float(ls['time'][str(chid)]) < CONFIG['SIMUL_UPDATE_INTERVAL']:

                if str(chid) not in lastUpdate:
                    try:
                        lastUpdate[str(chid)]= await updateChannel.fetch_message(int(ls['ids'][str(chid)]))
                    except discord.NotFound as e:
                        print("WARNING: Message",ls['ids'][str(chid)], "in", updateChannel.name, f"({updateChannel.id})", "not found.")

                CACHE['last_sent']['update_content'][str(chid)]['chId']+= ", " + update['chId']
                e, __= updateUtils.getUpdateEmbed(CACHE['last_sent']['update_content'][str(chid)], mentionDict=MENTIONS)
                await lastUpdate[str(chid)].edit(embed=discord.Embed.from_dict(e))
                doEdit= True

                CACHE['last_sent']['time'][str(chid)]= time.time()
                utils.dumpJson(dct=CACHE, path=globals.CACHE_FILE)

            if not doEdit:
                # await updateChannel.send(updateMessage)
                lastUpdate[str(chid)]= await updateChannel.send(embed=discord.Embed.from_dict(updateEmbed), content=mentionString)

                CACHE['last_sent']['ids'][str(chid)]= str(lastUpdate[str(chid)].id)
                CACHE['last_sent']['update_content'][str(chid)]= copy.deepcopy(update)
                CACHE['last_sent']['time'][str(chid)]= time.time()
                utils.dumpJson(CACHE, globals.CACHE_FILE)
        except Exception as e:
            print(e)

        time.sleep(5)
        for role in swapped:
            pass#await role.edit(mentionable=False)

async def checkUpdates():
    while True:
        reload()
        await updateUtils.handleUpdates(handler=updateHandler, cache=CACHE, cacheFile=globals.CACHE_FILE)
        await asyncio.sleep(CONFIG['UPDATE_DELAY'])

async def runBot():
    global client
    client= discordUtils.Client(intents=discord.Intents.all())
    client.load(prefix=CONFIG['PREFIX'])
    await client.start(CONFIG['DISCORD_KEY'])



# RUN ----------------------
async def main():
    await asyncio.gather(
        runBot(),
        checkUpdates()
	)

if __name__ == "__main__":
    while True:
        try: asyncio.run(main())
        except KeyboardInterrupt: break
        except Exception as e:
            print("ERROR", e)
            traceback.print_exc()