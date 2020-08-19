from utilss import globals, utils
import utilss.sheetUtils.sheetUtils as sheetUtils
import datetime

def make():
    data= utils.loadJson(globals.PARSED_FILE)
    CONFIG= utils.loadJson(globals.CONFIG_FILE)
    sheets= sheetUtils.getService().spreadsheets()

    sid= CONFIG['SHEET_ID']
    sNames= ["just_use_this_one", "DATA_1", "DATA_2"]
    shids= [0, 257642594, 1611039960]

    rColOffset= 2
    rRowOffset= 4
    mRowOffset= 3


    updateData, memberData, warningData= sheetUtils.parseData(data)

    rData= sheetUtils.createRecentSheet(list(reversed(updateData)))
    rRange= f"{sNames[2]}!A1:{sheetUtils.getMaxCell(rData)}"
    rResult= sheetUtils.update(sheets=sheets, data=rData, range=rRange, sid=sid)
    print('Recents: {0} cells updated.'.format(rResult.get('updatedCells')))

    mData= sheetUtils.createMemberSheet(memberData)
    mRange= f"{sNames[1]}!A1:{sheetUtils.getMaxCell(mData)}"
    mResult= sheetUtils.update(sheets=sheets, data=mData, range=mRange, sid=sid)
    print('Members: {0} cells updated.'.format(mResult.get('updatedCells')))

    wRowOffset= 5
    wCol= 14
    wData= warningData
    wRange= f"{sNames[0]}!{sheetUtils.toLetter(wCol)}{wRowOffset}:{sheetUtils.toLetter(wCol+len(warningData[0]))}{wRowOffset+len(warningData)}"
    wResult= sheetUtils.update(sheets=sheets, data=wData, range=wRange, sid=sid)
    print('Warnings: {0} cells updated.'.format(wResult.get('updatedCells')))

    mHeadRequest= sheetUtils.getRepeatRequest(shid=shids[0], formula=f"={sNames[1]}!A1",
                                              startRowIndex=mRowOffset,
                                              endRowIndex=mRowOffset+1, endColIndex=len(mData[0]))
    rHeadRequest= sheetUtils.getRepeatRequest(shid=shids[0], formula=f"={sNames[2]}!A1",
                                              startRowIndex=rRowOffset, startColIndex=len(mData[0])+rColOffset,
                                              endRowIndex=rRowOffset+1, endColIndex=len(mData[0])+rColOffset+len(rData[0]))
    searchBody= sheetUtils.getBody([mHeadRequest, rHeadRequest])
    searchResult= sheets.batchUpdate(spreadsheetId=sid, body=searchBody).execute()
    print('Headers: {0} cells updated.'.format(len(searchResult.get('replies'))))


    # Range where the input cells are defined -- just needs to be suff. large
    maxCellRow= max(rRowOffset, mRowOffset)+10
    maxCellCol= len(mData[0])+rColOffset+len(rData[0])+10
    maxRange= f"A1:{sheetUtils.toLetter(maxCellCol)}{maxCellRow}"

    rColStart= len(mData[0])+rColOffset
    mInputCells= { "HIGHLIGHT": [0,0, 30],
                   "MAX_DAYS": [1,0, 120]}
    rInputCells= { "USER": [0, rColStart+1, ""],
                   "ROLE": [1, rColStart+1, ""],
                   "SERIES": [2, rColStart+1, ""],
                   "MAX_DAYS": [0, rColStart+1+3, 120],
                   "MIN_DAYS": [1, rColStart+1+3, 0],
                  }
    extras= {
           "Last Update": [2, 14, str(datetime.date.today())],
            f"Tips": [0,14, "| for OR,     .* for wildcard"],
            f"Example": [1,14, "(akai|kr.*le)"]
    }

    mHideCell= f"${sheetUtils.toLetter(mInputCells['MAX_DAYS'][1]+1)}${mInputCells['MAX_DAYS'][0]+1}"
    rm= len(rData)
    rCond1= f"{sNames[2]}!C2:C{rm} <= ${sheetUtils.toLetter(rInputCells['MAX_DAYS'][1]+1)}${rInputCells['MAX_DAYS'][0]+1}"
    rCond2= f"{sNames[2]}!C2:C{rm} >= ${sheetUtils.toLetter(rInputCells['MIN_DAYS'][1]+1)}${rInputCells['MIN_DAYS'][0]+1}"
    rCond3= f"REGEXMATCH({sNames[2]}!A2:A{rm}, \"(?i)\"&${sheetUtils.toLetter(rInputCells['USER'][1]+1)}${rInputCells['USER'][0]+1})"
    rCond4= f"REGEXMATCH({sNames[2]}!B2:B{rm}, \"(?i)\"&${sheetUtils.toLetter(rInputCells['ROLE'][1]+1)}${rInputCells['ROLE'][0]+1})"
    rCond5= f"REGEXMATCH({sNames[2]}!D2:D{rm}, \"(?i)\"&${sheetUtils.toLetter(rInputCells['SERIES'][1]+1)}${rInputCells['SERIES'][0]+1})"
    filters= {
        f"=FILTER({sNames[1]}!A2:C, {sNames[1]}!B2:B <= {mHideCell})": [mRowOffset+1,0],
        f"=FILTER(DATA_2!A2:G{rm}, {rCond1}, {rCond2}, {rCond3}, {rCond4}, {rCond5})": [rRowOffset+1, rColStart],
    }

    selData= sheetUtils.getSelectiveData(cells=mInputCells, maxCellRow=maxCellRow, maxCellCol=maxCellCol)
    selData= sheetUtils.getSelectiveData(cells=rInputCells, data=selData)
    selData= sheetUtils.getSelectiveData(cells=filters, data=selData, input=False)
    selData= sheetUtils.getSelectiveData(cells=extras, data=selData)

    selResult= sheetUtils.update(sheets=sheets, data=selData, range=maxRange, sid=sid)
    print('Members: {0} cells updated.'.format(selResult.get('updatedCells')))



    # Highlight
    # isFormatted= sheetUtils.checkFormat(sheets=sheets, CONFIG=CONFIG, sid=sid, sheetIndex=0)
    # if not isFormatted:
    #     conditionCell= f"{sNames[0]}!${sheetUtils.toLetter(mInputCells['HIGHLIGHT'][1]+1)}${mInputCells['HIGHLIGHT'][0]+1}"
    #     cfBody= sheetUtils.getMCF(shid=shids[0], inputCell=f"{sNames[0]}!$B{mRowOffset+2}",
    #                               startRow=mRowOffset+1, startCol=0, endRow=len(memberData), endCol=len(mData[0]),
    #                               conditionCell=conditionCell)
    #     cfResult= sheets.batchUpdate(spreadsheetId=sid, body=cfBody).execute()
    #     print('CF: {0} cells updated.'.format(len(cfResult.get('replies'))))