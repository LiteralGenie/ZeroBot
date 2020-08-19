from utilss import utils, globals
import requests, re, asyncio, json, copy, time
from bs4 import BeautifulSoup as bs

CONFIG= utils.loadJson(globals.CONFIG_FILE)

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
    ret['chId']= re.search(r"/(\d+)/(\d+)[/|$]*", ret['chLink']).group(2)
    ret['cover']= "https://zeroscans.com/" + re.search(r"(/storage/.+)\);", linkDiv.find("a")['style']).group(1)

    ret['sLink']= infoDiv.find("a")['href'].strip()
    ret['sName']= infoDiv.find("a").text.strip()
    ret['sId']= re.search(r"comics/(\d+)", ret['sLink']).group(1)

    # print(ret['sName'], ret['sId'], ret['sLink'], ret['chNum'], ret["chId"], ret['chLink'])
    return ret

def getUpdates(l=CONFIG['UPDATE_LINK']):
    updateList= []
    html= requests.get(l, verify=False).text

    soup= bs(html, "html.parser")
    divs= soup.find_all("div", class_="list-item rounded")
    for dv in divs:
        updateList.append(parseUpdateDiv(dv))

    return list(reversed(updateList))

lastDelay= time.time()
async def handleUpdates(handler, cache, cacheFile):
    updateList= getUpdates()
    for update in updateList:
        id= update['chId'] + "|" + update['sId']
        if id not in cache['seen']:
            print("Updating", update)

            #global lastDelay
            #if time.time() - lastDelay > delay:
            #    print("Sleeping", delay)
            #    lastDelay= time.time()

            updateSeriesData(update)
            await handler(update)

            cache['seen'].append(id)
            utils.dumpJson(cache, cacheFile)

def getUpdateMessage(update, mentionDict):
    message= ""
    sid= update['sId']

    mentions= copy.deepcopy([mentionDict['-1']])
    if sid in mentionDict: mentions+= [copy.deepcopy(mentionDict[sid])]
    else: print("WARNING:", update['sName'], update['sId'], "does not have a mention role.")

    message= f"<@&{'> <@&'.join(mentions)}> **{update['sName']}** **{update['chNum']}** {update['chLink']}"

    return message

def getUpdateEmbed(update, mentionDict):
    template={
        "title": "",
        "url": "",
        "description": "",
        "color": 5771148,
        "thumbnail": {
            "url": ""
        },
        "fields": [
            { "name": "Links",
            "value": "",
            "inline": True, },
            # { "name": "Mentions",
            # "value": "",
            # "inline": True, },
        ]
    }
    sid= update['sId']
    sData= getSeriesData(sid)

    utm= r"?utm_source=discord&utm_medium=discord&utm_campaign=discord"

    mentions= copy.deepcopy(mentionDict['-1'])
    if str(sid) in mentionDict:
        mentions+= copy.deepcopy(mentionDict[str(sid)])
    else: print("WARNING:", update['sName'], update['sId'], "does not have a mention role.")
    # mentionString= f"<@&{'> <@&'.join(mentions)}>"

    template['title']= f"{update['sName']} - Chapter {update['chId']}"
    template['url']= update['chLink'] + utm
    template['description']= sData['description']
    template['thumbnail']['url']= sData['cover']
    template['fields'][0]['value']= f"[[Chapter]]({update['chLink'] + utm}) • [[Series]]({update['sLink'] + utm})"
    # template['fields'][1]['value']= mentionString

    return template, mentions

def updateSeriesData(update):
    sid= update['sId']
    data= utils.loadJson(globals.SERIES_FILE)

    if sid not in data or True:
        data[sid]= {}
        data[sid]['title']= update['sName']
        data[sid]['link']= update['sLink']
        data[sid]['cover']= update['cover']

        html= requests.get(update['sLink']).text
        soup= bs(html, 'html.parser')
        desc= soup.find("div", class_="col-lg-9 col-md-8 col-xs-12 text-muted").findAll(text=True, recursive=False)
        desc= ''.join(desc).strip()
        data[sid]['description']= desc

    utils.dumpJson(data, globals.SERIES_FILE)

def getSeriesData(sid):
    data= utils.loadJson(globals.SERIES_FILE)
    return data[str(sid)]