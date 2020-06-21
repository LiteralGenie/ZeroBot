import re, copy, time

keys= ["tl", "cl", "ts", "pr", "qc", "??"]

def getTallies(data, recent=30):
    empty= {"all": 0}
    for k in keys: empty[k]= 0
    empty= {
        "recent": copy.deepcopy(empty),
        "all": copy.deepcopy(empty)
    }

    tallies= copy.deepcopy(empty)
    tallies['members']= {}

    for msg in data['parsed']:
        flag= False
        daysAgo= (time.time()-msg['epoch']) / 86400
        isRecent= daysAgo <= recent

        typ2= "??"
        for k in keys:
            if f"({k})" in msg['parsed']['type'].lower():
                typ2= k
                break

        uid= str(msg['author']['id'])
        if uid not in tallies['members']: tallies['members'][uid]= copy.deepcopy(empty)

        count= len(msg['parsed']['chapters'])
        if isRecent:
            tallies['recent'][typ2]+= count
            tallies['recent']['all']+= count
            tallies['members'][uid]['recent'][typ2]+= count
            tallies['members'][uid]['recent']['all']+= count
        tallies['all'][typ2]+= count
        tallies['all']['all']+= count
        tallies['members'][uid]['all'][typ2]+= count
        tallies['members'][uid]['all']['all']+= count
    return tallies

def getUserStats(name, parsedData, tallies, recent=30):
    ret= {}
    uid= None
    for key in parsedData['members']:
        if parsedData['members'][key] == name:
            uid= key
    assert uid
    data= tallies['members'][uid]

    ret['stats']= []
    for x in keys:
        r= data['recent'][x]
        a= data['all'][x]

        if r or a:
            entry= [x.upper(), str(r), str(a)]
            ret['stats']+= [entry]

    totalRecent= sum([int(x[1]) for x in ret['stats']])
    totalAll= sum([int(x[2]) for x in ret['stats']])
    ret['stats'].append(["All", str(totalRecent), str(totalAll)])

    ret['recent']= []
    for msg in parsedData['parsed']:
        daysAgo= (time.time()-msg['epoch']) / 86400
        if str(msg['author']['id']) == uid and daysAgo <= recent:
            for ch in msg['parsed']['chapters']:
                if str(ch)[-1] == '0': ch= int(ch)
                entry= [msg['parsed']['type'][-3:-1], str(int(daysAgo)), str(ch), msg['parsed']['title']]
                ret['recent']= [entry] + ret['recent']

    return ret

def getGlobalStats(tallies, parsedData, num=3):
	counts= {}
	ret= {"users": [], "all": []}

	for x in keys + ['all']:
		counts[x]= {"recent": [], "all": []}

		for typ in ['recent', 'all']:
			for i in range(num): counts[x][typ].append(copy.deepcopy(["",0]))

			for i in range(num):
				for member in tallies['members']:
					c= tallies['members'][member][typ][x]
					current= counts[x][typ][i][1]
					name= parsedData['members'][member]
					if c > current and name not in [x[0] for x in counts[x][typ]]:
						counts[x][typ][i]= [name, c]

	cl= lambda x: re.sub(r'[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]', '', x)
	for x in keys + ['all']:
		rString= " --- ".join([f"{cl(y[0])} ({y[1]})" for y in counts[x]['recent'] if y[1]])
		aString= " --- ".join([f"{cl(y[0])} ({y[1]})" for y in counts[x]['all'] if y[1]])
		ret['users']+= [[x.upper(), rString, aString]]
		# ret['users'] += [[x.upper(), aString]]

		ret['all']+= [[x.upper(), str(tallies['recent'][x]), str(tallies['all'][x])]]
		# ret['all']+= [[x.upper(), str(tallies['all'][x])]]

	return ret

def getCatStats(tallies):
	ret= {}
	empty= {"recent": [], "all": []}
	for x in keys + ["all", "??"]: ret[x]= copy.deepcopy(empty)

	for x in tallies['members']:
		for y in tallies['members'][x]['recent']:
			ret[y]['recent'].append(tallies['members'][x]['recent'][y])

		for y in tallies['members'][x]['all']:
			ret[y]['all'].append(tallies['members'][x]['all'][y])

	for x in ret:
		ret[x]['recent'].sort(reverse=True)
		ret[x]['all'].sort(reverse=True)

	return ret

if __name__ == "__main__":
	import utils
	import json
	data= json.load(open("C:/programming/zerobot/data/parsedLog.json"))

	tallies= getTallies(data)
	uStats= getUserStats('Akai (赤井)', data, tallies)
	gStats= getGlobalStats(tallies, data)

	h= ['Type', '30 Days', 'All-time']
	print(utils.pprint(uStats['stats'], headers=h))

	h= ['Type', 'Users (30 days)', 'Users (all)']
	print(utils.pprint(gStats['users'], headers=h))

	h= ['Type', '30 Days', 'All-time']
	print(utils.pprint(gStats['all'], headers=h))

	if uStats['recent']:
		h= ['Type', '# Days Ago', 'Ch #', 'Series']
		print(utils.pprint(uStats['recent'], headers=h))