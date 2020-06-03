import os

DATA_DIR= os.path.abspath("./data") + "/"
CONFIG_FILE= DATA_DIR + "bot_config.json"
CACHE_FILE= DATA_DIR + "cache.json"
MENTION_FILE= DATA_DIR + "mentions.json"
SERIES_FILE= DATA_DIR + "sdata.json"
MSG_FILE= DATA_DIR + "msg_log.json"
PARSED_FILE= DATA_DIR + "parsedLog.json"

CACHE_DEFAULT= {
    "seen": [],
    "last_sent": {
        "ids": {},
        "update_content": {},
        "time": {}
    }
}