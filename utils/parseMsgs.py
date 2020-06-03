import json, re, copy
from utils import utils, globals


regex= r"([^\d\n]+)(?: |chapters?|ch\.?)+\(?((?:[\d\.]+[(),\-& ]*)+)\)? *(?:([\w ]+))*[^<]*(?:<@!?(\d{13,})>)*" # THE ONE
titleFixes= {
	"a 008": "a Zero-Zero-Eight", # kimi wa 008
	"as 008": "a Zero-Zero-Eight",
	"okgo 2": "okgo Two"
}


def cleanRawLine(text):
	text= re.sub(r"[*_`|]", "", text).strip()
	for wrong in titleFixes:
		text= text.replace(wrong, titleFixes[wrong])
	return text

def cleanMatch(m):
	ret= []
	for i in range(len(m.groups())):
		if m.groups()[i] is not None: ret.append(m.groups()[i])
		else: ret.append("")
	return ret

def scanMessage(msg):
	text= msg['content'].split("\n")
	matches= []
	failures= []
	for line in text:
		line= cleanRawLine(line)
		if not line: continue

		m= re.search(regex, line, flags=re.IGNORECASE)
		if m: matches.append(cleanMatch(m))
		else: failures.append(line)

	return matches, failures

def listToDict(lst):
	return {
		"title": lst[0],
		"chapters": lst[1],
		"type": lst[2]
	}

def cleanTitle(title):
	return re.sub(r"(?:chapter|ch\.?)", "", title, flags=re.IGNORECASE).strip()

def cleanChapterNum(num):
	ret= []

	num= re.sub(r"[()]", "", num)
	split= re.split("[,&]", num)
	for x in split:
		if "-" not in x:
			ret+= [float(y) for y in x.split()]
		else:
			s2= x.split("-")
			s2= [x for x in s2 if x.strip()]
			if len(s2) < 2: ret+= [float(s2[0])]
			elif len(s2) == 2:
				lower= int(s2[0])
				upper= int(s2[1])
				assert lower < upper

				k= lower
				while k <= upper:
					ret+= [float(k)]
					k+= 1
			elif len(s2) > 2: raise ValueError

	return ret

def cleanType(typ):
	if "chap" in typ.lower(): return typ
	maps= {
		"Proofreading (PR)": {
			"start": ["proo"],
			"contain": ["pring", "proo"],
			"exact": ["pr"]
		},
		"Cleaning (CL)": {
			"start": ["cle"],
			"contain": ["clean"],
			"exact": ["cl"]
		},
		"Translating (TL)": {
			"start": ["trans", "tl"],
			"contain": ["tl", "trans"],
			"exact": [""]
		},
		"Typesetting (TS)": {
			"start": ["typ"],
			"contain": ["typeset", "tsing"],
			"exact": ["ts"]
		},
		"Quality Checking (QC)": {
			"start": ["qc", "qua"],
			"contain": ["qc", "qua"],
			"exact": [""]
		}
	}

	typ= typ.strip().lower()
	for job in maps:
		if any([typ.startswith(x) for x in maps[job]['start']]) \
		or any([x in typ for x in maps[job]['contain']])\
		or any([x == typ for x in maps[job]['exact']]):
			return job

	return typ

def cleanMatches(matches):
	for m in matches:
		m['title']= cleanTitle(m['title'])
		m['type']= cleanType(m['type'])
		try: m['chapters']= cleanChapterNum(m['chapters'])
		except: pass

	return matches


def debugPrint(matches, warningLog):
	cpy= []
	for x in matches:
		cpy.append([x['title'], str(x['chapters']), x['type']])

	for i,match in enumerate(cpy):
		for j in range(len(cpy[i])):
			cpy[i][j]= cpy[i][j][:30]
	print(utils.pprint(cpy[-20:], headers=["Title", "Chapter", "Role"]))

	for x in warningLog:
		print(x['url'],"\n\t","\n\t".join(x['failed']))
	print(sum([len(x['failed']) for x in warningLog]), "warnings.")

def parse():
	data= utils.loadJson(globals.MSG_FILE)

	i,warningCount= 0,0
	matches= []
	warningLog= []
	parsedData= []
	for msg in data['log']:
		text= msg['content'].split("\n")

		m, failures= scanMessage(msg)
		if not m:
			# print('here',m, failures)
			continue
		if failures:
			cpy= copy.deepcopy(msg)
			cpy['failed']= failures
			warningLog.append(cpy)

		dct= listToDict(m[0])
		msg['parsed']= dct
		matches.append(dct)
		parsedData.append(msg)

	matches= cleanMatches(matches)

	debugPrint(matches, warningLog)

	with open("../data/parsedLog.json", "w+") as file:
		d= {
			"parsed": parsedData,
			"warnings": warningLog,
			"members": data['members']
		}
		json.dump(d, file, indent=2)

