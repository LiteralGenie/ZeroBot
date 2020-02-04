from utils import utils, globals
import requests, re, asyncio, json, copy

from bs4 import BeautifulSoup as bs


def parseUpdateDiv(dv):
    ret= {
        "chLink": "N/A",
        "chNum": "-1",
        "chId": "-1",

        "sLink": "N/A",
        "sName": "N/A",
        "sId": "-1"
    }

    linkDiv= dv.find("div", class_="media media-comic-card")
    infoDiv= dv.find("div", class_="list-body")

    ret['chLink']= linkDiv.find("a")['href'].strip()
    ret['chNum']= linkDiv.find("span", class_="badge badge-md text-uppercase bg-darker-overlay").text.strip()
    ret['chId']= re.search(r"(\d+)/(\d+)[/|$]*", ret['chLink']).group(2)

    ret['sLink']= infoDiv.find("a")['href'].strip()
    ret['sName']= infoDiv.find("a").text.strip()
    ret['sId']= re.search(r"comics/(\d+)", ret['sLink']).group(1)

    # print(ret['sName'], ret['sId'], ret['sLink'], ret['chNum'], ret["chId"], ret['chLink'])
    return ret

def getUpdates(l="https://zeroscans.com/latest"):
    updateList= []
    html= requests.get(l).text

    soup= bs(html, "html.parser")
    divs= soup.find_all("div", class_="list-item rounded")
    for dv in divs:
        updateList.append(parseUpdateDiv(dv))

    return updateList

async def handleUpdates(handler, cache, cacheFile, delay=1):
    updateList= getUpdates()
    for update in updateList:
        id= update['chId'] + "|" + update['sId']
        if id not in cache['seen']:
            print("Updating", update)
            await handler(update)

            cache['seen'].append(id)
            utils.dumpJson(cache, cacheFile)

            updateSeriesData(update)
        await asyncio.sleep(delay)

def getUpdateMessage(update, mentionDict):
    message= ""
    sid= update['sId']

    mentions= [mentionDict['-1']]
    if sid in mentionDict: mentions+= [mentionDict[sid]]
    else: print("WARNING:", update['sName'], update['sId'], "does not have a mention role.")

    message= f"<@&{'> <@&'.join(mentions)}> **{update['sName']}** **{update['chNum']}** {update['chLink']}"

    return message

def updateSeriesData(update):
    sid= update['sId']
    data= utils.loadJson(globals.SERIES_FILE)

    if sid not in data:
        data[sid]= update['sName']

    utils.dumpJson(data, globals.SERIES_FILE)