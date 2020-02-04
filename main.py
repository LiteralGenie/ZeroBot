from utils import discordUtils, utils, updateUtils, globals
import asyncio, discord, time, copy

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

    for chid in CONFIG['UPDATE_CHANNELS']:
        updateChannel= client.get_channel(int(chid))
        m= [x for x in mentions if updateChannel.guild.get_role(int(x))]
        if m: mentionString= f"<@&{'> <@&'.join(m)}>"
        else: mentionString= ""

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

async def checkUpdates():
    while True:
        reload()
        await updateUtils.handleUpdates(handler=updateHandler, cache=CACHE, cacheFile=globals.CACHE_FILE, delay=CONFIG['DISCORD_DELAY'])
        await asyncio.sleep(CONFIG['UPDATE_DELAY'])

async def runBot():
    global client
    client= discordUtils.Client()
    client.load(prefix=CONFIG['PREFIX'])
    await client.start(CONFIG['DISCORD_KEY'])



# RUN ----------------------
async def main():
    await asyncio.gather(
        runBot(),
        checkUpdates()
	)

if __name__ == "__main__":
    asyncio.run(main())