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

def zeroPad(x, numDec=7):
    sx= str(x)
    ix= int(x)

    padSize= numDec-len(x)
    x= "".join(["0"]*padSize) + x

    return x

def pprint(lst, div="|", spc=1, headers=None, quoteWrap=False, links=None):
    num = len(lst[0])
    widths = [0] * (num)

    for i in range(num):
        widths[i] = max([len(str(x[i])) for x in lst])
        if headers: widths[i]= max(widths[i], len(headers[i]))

        widths[i]= widths[i] + 1 + spc

    htext = ""
    if headers:
        line= ""
        for j in range(len(headers)):
            padding= widths[j]-len(headers[j])

            line+= headers[j] + " ".join([""]*padding) + div + " "
        if quoteWrap: htext+= f"`{line}`\n"
        else: htext+= f"{line}\n"

    text = ""
    for i in range(len(lst)):
        line= ""
        for j in range(num):
            if lst[i][j] is None: lst[i][j]= ""
            padding= widths[j]-len(lst[i][j])

            line+= lst[i][j] + " ".join([""]*padding) + div + " "

        if quoteWrap: text+= f"`{line}`\n"
        else: text+= f"{line}\n"

    text= text[:-1]

    m= max([len(x) for x in text.split("\n")])
    if quoteWrap: m=m-2

    div= "".join(["-"]*m)
    if quoteWrap: div= f"`{div}`\n"
    else: div+= "\n"

    if quoteWrap and links:
        split= text.split("\n")
        split= [split[i] + links[i] for i in range(len(split))]
        text= "\n".join(split)

    return htext + div + text

def breakMessage(msg, codeblock=True, lang="", maxLen=1700):
    text= []

    if codeblock: msg= msg.replace("```" + lang,"").replace("```","")

    splt = msg.split("\n")
    txt= ""
    while len("\n".join(splt)) > 1700:
        if codeblock: txt= "```" + lang + "\n"
        else: txt= ""

        while len(txt) < 1700:
            txt+= splt[0] + "\n"
            splt= splt[1:]

        if codeblock: txt+= "```"
        else: txt+= ""

        if len(txt) > 3: text.append(txt)

    if codeblock: text.append("```" + lang + "\n" + "\n".join(splt) + "```")
    else: text.append("\n".join(splt))

    return text