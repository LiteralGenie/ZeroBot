import time, pickle, os.path, copy
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def parseData(data):
	updateData= []
	memberData= {}
	warningData= []
	for entry in data['parsed']:
		name= data['members'][str(entry['author']['id'])]
		title= entry['parsed']['title'][:20]
		chapters= entry['parsed']['chapters']
		type_= entry['parsed']['type']
		daysSince= int((time.time()-entry['epoch']) / 86400)
		date= time.strftime('%b-%m, %Y', time.localtime(entry['epoch']))
		link= f"=HYPERLINK(\"{entry['url']}\", \"msg_link\")"

		for ch in chapters:
			if str(ch)[-1] == '0': ch= int(ch)
			if not title: title= "??????"
			updateData.append([name, type_, str(daysSince), title, str(ch), date, link])

		if name not in memberData:
			memberData[name]= {}
			memberData[name]['daysSeen']= daysSince
			memberData[name]['dateSeen']= date
		elif daysSince <= memberData[name]['daysSeen']:
			memberData[name]['daysSeen']= daysSince
			memberData[name]['dateSeen']= date

	for w in data['warnings']:
		link= f"=HYPERLINK(\"{w['url']}\", \"msg_link\")"
		daysAgo= int((time.time()-w['epoch']) / 86400)
		author= data['members'][str(w['author']['id'])]
		for f in w['failed']:
			# if int((time.time()-w['epoch']) / 86400) <= 30:
			# 	warningData= [f, link] + warningData
			warningData= [[author, daysAgo, f, link]] + warningData
	warningData= [["WARNINGS"] + [None]*3, ["Author", "# Days Ago", "Message", "Link"]] + warningData
	return updateData, memberData, warningData

def toLetter(num):
	assert int(num) < 26
	s= "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

	return s[num]

def getService():
	"""Shows basic usage of the Sheets API.
	Prints values from a sample spreadsheet.
	"""
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if os.path.exists('./data/token.pickle'):
		with open('./data/token.pickle', 'rb') as token:
			creds = pickle.load(token)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
		        './data/gcreds.json', SCOPES)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('./data/token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('sheets', 'v4', credentials=creds)

	return service

def createRecentSheet(updateData):
	ret= updateData
	ret= [['Name', 'Type', '# Days Ago', 'Series', 'Chapter', 'DD-MM-YY', "Link"]] + ret
	return ret

def createMemberSheet(memberData):
	ret= [['Name', '# Days Ago', 'Date Last Seen']]
	contentKeys= ['daysSeen', 'dateSeen']

	sortedKeys= list(memberData.keys())
	sortedKeys.sort()

	for member in sortedKeys:
		ret+= [[member] + [str(memberData[member][x]) for x in contentKeys]]

	return ret

def update(sheets, data, range, sid):
	body= {"values": data}
	result= sheets.values().update(
	    spreadsheetId=sid, range=range,
	    valueInputOption="USER_ENTERED", body=body).execute()
	return result

def msgToDict(msg):
	ret= {
	    "content": msg.content,
	    "author": {
	        "name": msg.author.name,
	        "id": msg.author.id
	    },
	    "time": msg.created_at.strftime("%Y%m%d - %H:%M"),
	    "epoch": msg.created_at.timestamp(),
	    "url": msg.jump_url,
	    "id": msg.id
	}
	return ret

def getMaxCell(data):
	return f"{toLetter(len(data[0])-1)}{len(data)}"

def getMCF(shid, inputCell, startRow, startCol, endRow, endCol, conditionCell):
	my_range = {
	    'sheetId': shid,
	    'startRowIndex': startRow,
	    'endRowIndex': endRow,
	    'startColumnIndex': startCol,
	    'endColumnIndex': endCol,
	}
	requests = [{
	    'addConditionalFormatRule': {
	        'rule': {
	            'ranges': [my_range],
	            'booleanRule': {
	                'condition': {
	                    'type': 'CUSTOM_FORMULA',
	                    'values': [{
	                        'userEnteredValue':
	                            f'={inputCell} >= {conditionCell}'
	                    }]
	                },
	                'format': {
	                    'backgroundColor': {
	                        'red': 0.9,
		                    'green': 0.6,
		                    'blue': 0.6
	                    }
	                }
	            }
	        },
	        'index': 0
	    }
	}]
	body = {
	    'requests': requests
	}

	return body

def checkFormat(sheets, CONFIG, sid, sheetIndex):
	a= sheets.get(key=CONFIG["GOOGLE_KEY"], spreadsheetId=sid, includeGridData=True).execute()
	s= a['sheets'][sheetIndex]
	return 'conditionalFormats' in s and bool(s['conditionalFormats'])

def getRepeatRequest(shid, formula, endRowIndex, endColIndex, startRowIndex=0, startColIndex=0):
	req= {
		"repeatCell": {
			"range": {
				"sheetId": shid,
				"startRowIndex": startRowIndex,
				"endRowIndex": endRowIndex,
				"startColumnIndex": startColIndex,
				"endColumnIndex": endColIndex
			},
			"cell": {
				"userEnteredValue": {
					"formulaValue": formula
				}
			},
			"fields": "userEnteredValue"
		}
	}
	return req

def getBody(requests):
	return { "requests": requests }

def getSelectiveData(cells, maxCellRow=None, maxCellCol=None, data=None, input=True):
	if data is None:
		assert maxCellCol is not None
		assert maxCellRow is not None

		row= [None]*maxCellCol
		data= []
		for i in range(maxCellRow):
			data+= copy.deepcopy([row])

	for cell in cells:
		r= cells[cell][0]
		c= cells[cell][1]

		data[r][c]= cell
		if input: data[r][c+1]= cells[cell][2]


	return data