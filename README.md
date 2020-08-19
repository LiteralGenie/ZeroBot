## Description
Discord bot to display updates from https://zeroscans.com/latest with series-specific pings. Contact `Literal Genie#2222` for concerns or whatever.

![Release preview](https://i.imgur.com/WfPHj8J.png)

---

Secondary functions include tracking scanlation progress of staff via Discord messages. 

Messages must be within a specified channel and of the format `[Project Name] Chapter [Number] [Job] [optional: Next Person]`, where `Number` may be a range or comma delimited list.

A short summary per user can also be displayed on Discord for bragging purposes.

![Stat preview](https://i.imgur.com/qk9G33p.png)

All progress data is logged to a Google Sheets page which can be further filtered / searched through.

![Sheet preview](https://i.imgur.com/v0k6Y73.png)

## Setup 
1. Clone repo and install the listed modules in `requirements.txt`.
2. Obtain a Google service account key and save as `./gcreds.json`.
3. See [below](#Config) for config file instructions 
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

## Config

Create a `./data/bot_config.json` file that looks like this:

```py
{
  "PREFIX": "$",
  "DISCORD_KEY": "blah",
  "GOOGLE_KEY": "blah",
  "SHEET_ID": "blah",
  "UPDATE_DELAY": 6,
  "DISCORD_DELAY": 300,
  "SIMUL_UPDATE_INTERVAL": 3600,
  "UPDATE_LINK": "https://zeroscans.com/latest",
  "UPDATE_CHANNELS": [
    "401180166132334593"
  ],
  "TEST_CHANNELS": [
    "698262899835142184",
    "563523595322785833"
  ],
  "ADMINS": [
    "113843036965830657",
    "260788818167201793",
    "218727338702143498"
  ]
}
```

Where:
   - `UPDATE_DELAY` is how often to check `UPDATE_LINK` for releases.
   - `DISCORD_DELAY` is the interval between when an update is found and when it is posted on Discord.
   - `SIMUL_UPDATE_INTERVAL` is the interval for which updates for a single series are merged into a single Discord message (from first update).
   - `TEST_CHANNELS` is the channel to post debug messages about updates to.