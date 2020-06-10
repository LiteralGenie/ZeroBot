## Description
Discord bot to display updates from https://zeroscans.com/latest with series-specific pings. Contact `Literal Genie#2222` for concerns or whatever.

![Release preview](https://i.imgur.com/WfPHj8J.png)

---

Secondary functions include tracking scanlation progress of staff via Discord messages. 

Messages must be within a specified channel and of the format `[Project Name] Chapter [Number] [Job] [Next Person]`, where `Number` may be a range or comma delimited list.

A short summary per user can also be displayed on Discord for bragging purposes.

![Stat preview](https://i.imgur.com/qk9G33p.png)

All progress data is logged to a Google Sheets page which can be further filtered / searched through.

![Sheet preview](https://i.imgur.com/v0k6Y73.png)

## Setup 
1. Clone repo and install the listed modules in `requirements.txt`.
2. Obtain a Google service account key and save as `./gcreds.json`.
3. Modify the Discord key, update channels, and admin users in `./data/bot_config.json` appropriately.
   -  (Channel and admins can be later modified using commands on Discord)
   -  Also modify the google spreadsheet id. (The link / id might also be hard-coded somewhere, i forget.)
4. Run `main.py` and see `!help` for the command list.

## TODO
- Logging shit
- Customizable update messages
  - Pretty embeds
- Less bootleg way to pull updates
  - Generalizable with rss?
- Warning channel
- Update requirements
