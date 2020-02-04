import json, os

def loadJson(path, default=None):
    if not default: default= {}
    data= default

    assert path.lower().endswith(".json")
    if not os.path.exists(path):
        return data
    else:
        try: return json.load(open(path))
        except json.JSONDecodeError as e:
            print("Not a valid JSON", "|", default, "|", path)
            return data

def dumpJson(dct, path):
    with open(path, "w+") as file:
        json.dump(dct, file, indent=2)