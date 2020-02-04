from utils import discordUtils, utils, updateUtils, globals
import os, asyncio

# SETUP ----------------------
client= None

def reload():
    global CONFIG, CACHE, MENTIONS
    CONFIG= utils.loadJson(globals.CONFIG_FILE)
    CACHE= utils.loadJson(globals.CACHE_FILE, default= {"seen": []})
    MENTIONS= utils.loadJson(globals.MENTION_FILE)
reload()
    

# ASYNC FUNCTIONS ------------------
async def updateHandler(update):
    while not client.is_ready(): await asyncio.sleep(1)

    updateMessage= updateUtils.getUpdateMessage(update=update, mentionDict=MENTIONS)

    for chid in CONFIG['UPDATE_CHANNELS']:
        updateChannel= client.get_channel(int(chid))
        await updateChannel.send(updateMessage)

async def checkUpdates():
    while True:
        reload()
        await updateUtils.handleUpdates(handler=updateHandler, cache=CACHE, cacheFile=globals.CACHE_FILE, delay=CONFIG['DISCORD_DELAY'])
        await asyncio.sleep(CONFIG['UPDATE_DELAY'])

async def runBot():
    global client
    client= discordUtils.Client()
    client.load()
    await client.start(CONFIG['DISCORD_KEY'])



# RUN ----------------------
async def main():
    await asyncio.gather(
        runBot(),
        checkUpdates()
	)

if __name__ == "__main__":
    asyncio.run(main())
