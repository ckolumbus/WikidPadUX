"""
Calendar Control plug-in for wikidPad
Rev 0.09 (beta)
Copyright (c) 2011, Bill Wilkinson
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of the <ORGANIZATION> nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

To install Calendar Control:
	* Place this file in ...\WikidPad\user_extensions directory
	* If this file does not have a .py extension, rename to .py
To enable Calendar Control for a wikidPad wiki:
	* Add the property "[global.cc: enabled]" to the wiki's WikiSettings page

See http://calendarcontrol.wikidot.com/ for more information, latest revision and to make a donation
"""

# Scintilla/wxPython editor reference: http://www.yellowbrain.com/stc/index.html

import locale
import re, urllib, string, datetime, calendar, wx.stc, operator
# from pwiki.StringOps import mbcsEnc, mbcsDec
WIKIDPAD_PLUGIN = (("MenuFunctions",1), ("ToolbarFunctions",1), ("hooks", 1),)


# ---------- initialize global variables --------

isNewWikiWord = False
pageType = u'o'
thisWikiWord = deletedWord = ''
prevDay = thisDay = nextDay = dayZero = datetime.date(1900, 1, 1)
# prevMonth = thisMonth = nextMonth = datetime.date(1900, 1, 1)
parentLinksTag = u'links'
dateFormat = '%Y-%m-%d'
monthFormat = '%Y-%m'
yearFormat = 'Y%Y'
sameAsTrue = [u't', u'true', u'y', u'yes', u'enable', u'enabled']
sameAsFalse = [u'f', u'false', u'n', u'no', u'disable', u'disabled']
sameAsAscend = [u'a', u'asc', u'ascend', u'ascending', u'up', u'forward']
sameAsDescend = [u'd', u'desc', u'descend', u'descending', u'down', u'backward', u'reverse']
_dateRE = re.compile(ur'(19|20)[0-9]{2}-[0-1][0-9]-[0-3][0-9]')
_weekRE = re.compile(ur'(19|20)[0-9]{2}-W[0-5][0-9]')
_monthRE = re.compile(ur'(19|20)[0-9]{2}-[0-1][0-9]')
_yearRE = re.compile(ur'Y(19|20)[0-9]{2}')

# ---------- /initialize global variables -------
# ----- calendar control ------------------------
# ---------- menu & toolbar items ---------------

cp="ISO-8859-1"

def my_unicode(s):
    global cp
    return unicode(s, cp)

def describeMenuItems(wiki):
	global nextNumber
	return ((GotoToday, u"Goto Today\tCtrl-Alt-T", u"Goto Today", "select"), (RefreshPage, u"Refresh Page\tF5", u"Refresh Page", ["refresh", "twirl"]), )

def describeToolbarItems(wiki):
	return ((GotoToday, u"Goto Today", u"Goto Today", "select"), (RefreshPage, u"Refresh Page", u"Refresh Page",["refresh", "twirl"]), )

def GotoToday(pwiki, evt):
	"""
	Opens the date, week or month page for the current date. 
	The page is created if it does not exist.
	The page is refreshed if it is already open in current tab.
	"""
	global dateFormat, monthFormat, yearFormat, thisWikiWord, pageType
	if ccCheckEnabled(pwiki):
		thisWikiWord = pwiki.getCurrentWikiWord()
		pageType = getPageType(pwiki, thisWikiWord)
		today = datetime.date.today()
		pwiki.saveAllDocPages()
		if pageType == u'w':
			pageName = weekFormat(today)
		elif pageType == u'm':
			pageName = my_unicode(today.strftime(monthFormat))
		elif pageType == u'y':
			pageName = today.strftime(yearFormat)
		else: 
			pageName = today.strftime(dateFormat)
		pwiki.openWikiPage(pageName, True, False, True)
		# pwiki.stdDialog('text', u'Test', u'This is a test,\nthis is only a test.')
	return

def RefreshPage(pwiki, evt):
	"""
	Refreshes page in current tab.
	"""
	global thisWikiWord, pageType
	if ccCheckEnabled(pwiki):
		thisWikiWord = pwiki.getCurrentWikiWord()
		pageType = getPageType(pwiki, thisWikiWord)
		pwiki.saveAllDocPages()
		pwiki.openWikiPage(thisWikiWord, True, False, True)
	return
	
# ---------- /menu & toolbar items --------------
# ---------- utilities --------------------------

def ccCheckEnabled(wikidPad):
	"""
	Checks for global property '[global.cc: enabled]' or equivalent
	The calendar control add-on is disabled by default and must be turned on to function.
	Returns True/False
	"""
	global sameAsTrue
	ccEnabled = False
	if wikidPad != u'WikidPadHelp':					# never enable on help wiki
		globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
		enabled = globalProps.get(u'global.cc')
		if enabled is None:							# check for alternates
			enabled = globalProps.get(u'global.cc.enable')
		if enabled is None:							
			enabled = globalProps.get(u'global.cc.enabled')
		if enabled is not None:						# one of the alternates was found
			enabled = enabled.lower()
			ccEnabled = enabled in sameAsTrue
	return ccEnabled

def getPageType(wikidPad, wikiWord):
	"""
	Finds page type. Returns single alpha character:
	'd' = day
	'w' = week
	'm' = month
	'y' = year
	'o' = other
	"""
	if len(wikiWord) == 10 and _dateRE.match(wikiWord): type = u'd'
	elif len(wikiWord) == 8 and _weekRE.match(wikiWord): type = u'w'
	elif len(wikiWord) == 7 and _monthRE.match(wikiWord): type = u'm'
	elif len(wikiWord) == 5 and _yearRE.match(wikiWord): type = u'y'
	else: type = u'o'
	return type

def getStartupCheck(wikidPad):
	"""
	Checks for global property '[global.cc.startupcheck]'
	returns true/false
	"""
	global sameAsFalse
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	check = globalProps.get(u'global.cc.startupcheck')
	if check is None: check = globalProps.get(u'global.cc.startup')
	if check is None: check = u'true'
	check = check.lower()
	return not(check in sameAsFalse)

def getHighlightColor(wikidPad):
	"""
	Checks for global property '[global.cc.highlightcolor]'
	returns color or None
	"""
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	color = globalProps.get(u'global.cc.highlightcolor')
	if color is None: color = globalProps.get(u'global.cc.highlightcolour')
	return color

def useWeekNumbers(wikidPad):
	"""
	Checks value of global property '[global.cc.weeknumbers]'
	Returns True/False
	"""
	global sameAsTrue
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	weeknumbers = globalProps.get(u'global.cc.weeknumbers')
	if weeknumbers is None: weeknumbers = globalProps.get(u'global.cc.weekpages')
	if weeknumbers is None: weeknumbers = u'false'
	weeknumbers = weeknumbers.lower()
	return weeknumbers in sameAsTrue

def getDateTemplate(wikidPad):
	"""
	Checks for global property '[global.cc.datetemplate]' or equivalent
	Returns page name or None
	"""
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	template = globalProps.get(u'global.cc.datetemplate')
	if template is None:
		template = globalProps.get(u'global.cc.daytemplate')
	if template is None:
		template = globalProps.get(u'global.cc.datepagetemplate')
	if template is None:
		template = globalProps.get(u'global.cc.daypagetemplate')
	return template

def getWeekTemplate(wikidPad):
	"""
	Checks for global property '[global.cc.weektemplate]' or equivalent
	Returns page name or None
	"""
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	template = globalProps.get(u'global.cc.weektemplate')
	if template is None:
		template = globalProps.get(u'global.cc.weekpagetemplate')
	return template

def getMonthTemplate(wikidPad):
	"""
	Checks for global property '[global.cc.monthtemplate]' or equivalent
	Returns page name or None
	"""
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	template = globalProps.get(u'global.cc.monthtemplate')
	if template is None:
		template = globalProps.get(u'global.cc.monthpagetemplate')
	return template

def getYearTemplate(wikidPad):
	"""
	Checks for global property '[global.cc.yeartemplate]' or equivalent
	Returns page name or None
	"""
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	template = globalProps.get(u'global.cc.yeartemplate')
	if template is None:
		template = globalProps.get(u'global.cc.yearpagetemplate')
	return template

def bracketWord(wikidPad, word):
	"""
	Adds opening and closing brackets to word. Depricated in wikidPad 1.9
	"""
	# formatting = wikidPad.getWikiDocument().getFormatting()
	# return formatting.wikiWordStart() + word + formatting.wikiWordEnd()
	return u'[' + word + u']'
	
def getMyArchive(wikidPad):
	"""
	get user name for MyArchive page, if specified
	"""
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	archive = globalProps.get(u'global.cc.archive')
	if archive is None: archive = u'MyArchive'
	return archive

def getStartPos(editor):
	"""
	returns start position in the form [line, position in line]
	"""
	currentPos = editor.GetCurrentPos()
	line = editor.LineFromPosition(currentPos)
	linePos = editor.GetColumn(currentPos)
	startPos = [line, linePos]
	return startPos

def updateStartPos(editor, startPos, startWindow):
	"""
	update start position by any change in the number of lines before the start position
	"""
	if startPos[0] >= startWindow[1]:
		delta = editor.LineFromPosition(editor.GetCurrentPos()) - startWindow[1]
		editor.GotoPos(editor.PositionFromLine(startPos[0]+delta)+startPos[1])
		editor.SetFocus()
	else:
		editor.GotoPos(editor.PositionFromLine(startPos[0])+startPos[1])
		editor.SetFocus()
	return
		
def setAutoWindow(wikidPad, editor, tagName, warningText=True):
	"""
	Delete page text from startTag to endTag if both are found and in the right order. 
	Otherwise go to end of page and append.
	Write startTag, endTag and optional warning text to define window.
	Set cursor inside window.
	Return [startTag line, endTag line]
	"""
	startTag = bracketWord(wikidPad, u'autotext: ' + tagName)
	endTag = bracketWord(wikidPad, u'end: ' + tagName)
	startText = endText = ''
	if (warningText): 
		startText = u' *~~~ Changes made below this line will not be saved! ~~~*'
		endText = u'*~~~ Changes made above this line will not be saved! ~~~* '
	selStart = editor.FindText(0, editor.GetLength(), startTag, 0)
	selEnd = editor.FindText(0, editor.GetLength(), endTag, 0)
	if selStart > -1 and selStart < selEnd:		# both tags found and in order
		selEnd = selEnd + len(endTag)			# move selEnd to end of endtag
	else:										# insert criteria not met; append to end of page
		editor.GotoPos(editor.GetLength())
		editor.AddText(u'\n\n')					# put blank line(s) between existing and appended text
		selStart = editor.GetLength()
		selEnd = selStart + 1
	startLine = editor.LineFromPosition(selStart)
	endLine = editor.LineFromPosition(selEnd)
	editor.SetSelection(selStart, selEnd)
	editor.ReplaceSelection(startTag + startText + u'\n' + endText + endTag)
	editor.GotoLine(1 + editor.LineFromPosition(selStart))
	# editor.AddText(str(selStart)+ ', ' + str(selEnd))
	return [startLine, endLine]

def ccEvents(wikidPad, wikiWord):
	"""
	returns "event" properties parsed into lists:
	date, value, marker
	"""
	global _dateRE
	dateProps = []
	eventProps = wikidPad.getWikiDocument().getWikiData().getPropertyNamesStartingWith('event')
	if eventProps is not None:
		for event in eventProps:
			values = wikidPad.getWikiDocument().getWikiData().getDistinctPropertyValues(event)
			if values is None: break
			eventSplit = event.split('.')
			l = len(eventSplit)-1
			for value in values:
				if l == 0:
					pass # TODO: lookup date page dates if l = 0
				else:
					date = eventSplit[l]
					if l == 1: dateProps.append([date, value, u'!'])
					if l > 1: 
						marker = eventSplit[1][:1].upper()
						if marker in string.digits: marker = u'!'
						dateProps.append([date, value, marker])
	if dateProps is not None: dateProps.sort()
	return dateProps
	
def getGregorian(isoDay):
	"""
	returns Gregorian date given iso [year, week, day] date 
	
	This method requires that one know the weekday of January 4 of the year 
	in question. Add 3 to the number of this weekday, giving a correction to 
	be used for dates within this year. 

	Method: Multiply the week number by 7, then add the weekday. From this 
	sum subtract the correction for the year. The result is the ordinal 
	date, which can be converted into a calendar date. If the ordinal date 
	thus obtained is zero or negative, the date belongs to the previous 
	calendar year; if greater than the number of days in the year, to the 
	following year. 

	Example: year 2008, week 39, Friday (day 5) 

	Correction for 2008: 5 + 3 = 8 
	(39 * 7) + 5 = 278 
	278 - 8 = 270 
	Ordinal day 270 of a leap year is day 270 - 244 = 26 of September 
	Result September 26, 2008 
	"""
	correction = datetime.date(isoDay[0],1,4).isoweekday() + 3
	ordinal = datetime.date(isoDay[0]-1,12,31).toordinal()
	ordinal = ordinal + 7*isoDay[1] + isoDay[2] - correction
	date = datetime.date.fromordinal(ordinal)
	return date

# ---------- /utilities -------------------------
# ---------- date modules -----------------------

def ccDatePages(wikidPad):
	""""
	returns list of date pages in current wiki
	"""
	global _dateRE
	datePages = wikidPad.getWikiDocument().getWikiData().getAllDefinedWikiPageNames()
	datePages = filter(lambda w: len(w)==10 and _dateRE.match(w), datePages)
	datePages.sort()
	return datePages
	
def getDateFromWikiWord(wikiWord):
	dateString = string.split(wikiWord[:10],"-")
	thisDay = datetime.date(int(dateString[0]),int(dateString[1]),int(dateString[2]))
	return thisDay
	
def makeDatePage(wikidPad, wikiWord):
	"""
	writes skeletal structure for a new date page
	"""
	thisDay = getDateFromWikiWord(wikiWord)
	templateWord = getDateTemplate(wikidPad)
	editor = wikidPad.getActiveEditor()
	editor.GotoPos(editor.GetLineEndPosition(0))
	editor.AddText(unicode(' ' + thisDay.strftime('%A') + '\n'))
	editor.AddText(u'< >\n')
	editor.AddText(u'----\n')
	if templateWord is not None:
		templatePage = wikidPad.getWikiDocument().getWikiPage(templateWord)
		content = templatePage.getContent()
		editor.AddText(content)
	editor.GotoPos(editor.GetLength())
	editor.AddText(u'\n+++ Links\n[autotext: links]\n[end: links]\n')
	editor.GotoLine(3)
	editor.SetFocus()
	wikidPad.saveCurrentDocPage()				# important!
	return

def datePrevUpNext(wikidPad, wikiWord):
	"""
	returns date page previous, up and next links as a string
	"""
	global dateFormat, monthFormat, prevDay, thisDay, nextDay
	datePages = ccDatePages(wikidPad)
	if wikiWord in datePages:
		pDateFormat = '%A [' + dateFormat + ']'
		nDateFormat = '[' + dateFormat + '] %A'
		upFormat = '[' + monthFormat + '|%B]'
		# get date from wikiWord
		linkString = prevLink = upLink = nextLink = ''
		thisDay = getDateFromWikiWord(wikiWord)
		# find previous date
		i = datePages.index(thisDay.strftime(dateFormat))
		if (i > 0): 
			dateString = string.split(datePages[i-1],"-")
			prevDay = datetime.date(int(dateString[0]),int(dateString[1]),int(dateString[2]))
			prevLink = prevDay.strftime(pDateFormat)
		else:
			prevLink = u'(no previous)'
		# find next date
		if (i < len(datePages)-1): 
			dateString = string.split(datePages[i+1],"-")
			nextDay = datetime.date(int(dateString[0]),int(dateString[1]),int(dateString[2]))
		else:
			nextDay = max(thisDay + datetime.timedelta(days=1), datetime.date.today())
		nextLink = nextDay.strftime(nDateFormat)
		# find up link
		isoWeek = ''
		if useWeekNumbers(wikidPad):
			isoWeek = weekFormat(thisDay)
			isoDay = thisDay.isocalendar()
			weekPages = ccWeekPages(wikidPad)
			if len(weekPages) > 0:
				if isoWeek >= weekPages[0]:
					upLink = u'[' + isoWeek + u'|Week ' + isoWeek[6:8] + u'] | '
			elif thisDay >= datetime.date.today():
				upLink = u'[' + isoWeek + u'|Week ' + unicode(isoDay[1]) + u'] | '
		upLink = upLink + thisDay.strftime(upFormat)
		# collect navLinks
		navLinks = [unicode(prevLink), my_unicode(upLink), unicode(nextLink), unicode(prevDay.strftime(dateFormat)), unicode(isoWeek), unicode(thisDay.strftime(monthFormat)), unicode(nextDay.strftime(dateFormat))]
	else: 
		navLinks = [u'error', u'error', u'error']
	return navLinks
	
def isCurrentDate(wikiWord):
	"""
	Determines if wikiWord is today's date. Returns True/False
	"""
	global dateFormat
	current = wikiWord == datetime.date.today().strftime(dateFormat)
	return current
	
# ---------- /date modules ----------------------
# ---------- week modules -----------------------

def weekFormat(dateIn):
	"""
	returns an ISO format year-week string for a given date
	"""
	isoDay = dateIn.isocalendar()
	isoWeek = unicode(isoDay[0]) + u'-W' + unicode(isoDay[1]).rjust(2,'0')
	return isoWeek
	
def ccWeekPages(wikidPad):
	"""
	Returns list of week pages in current wiki
	"""
	global _weekRE
	weekPages = wikidPad.getWikiDocument().getWikiData().getAllDefinedWikiPageNames()
	weekPages = filter(lambda w: _weekRE.match(w), weekPages)
	weekPages.sort()
	return weekPages

def makeWeekPage(wikidPad, wikiWord):
	"""
	writes skeletal structure for a new week page
	"""
	templateWord = getWeekTemplate(wikidPad)
	baseDate = getGregorian([int(wikiWord[:4]), int(wikiWord[6:8]), 1])
	endDate = baseDate + datetime.timedelta(days=6)
	editor = wikidPad.getActiveEditor()
	editor.GotoPos(editor.GetLineEndPosition(0))
	editor.AddText(unicode(' Week ' + wikiWord[6:8] + baseDate.strftime(': %A, %B %d - ') + endDate.strftime('%A, %B %d') + '\n'))
	editor.AddText(u'< >\n')
	editor.AddText(u'----\n')
	if templateWord is not None:
		templatePage = wikidPad.getWikiDocument().getWikiPage(templateWord)
		content = templatePage.getContent()
		editor.AddText(content)
	editor.GotoPos(editor.GetLength())
	editor.AddText(u'\n+++ Week ' + wikiWord + u' Date Pages\n[autotext: week]\n[end: week]\n')
	editor.AddText(u'\n+++ Links\n[autotext: links]\n[end: links]\n')
	editor.GotoLine(3)
	editor.SetFocus()
	wikidPad.saveCurrentDocPage()				# important!
	return

def weekPrevUpNext(wikidPad, wikiWord):
	"""
	returns week page previous, up and next links as a string
	"""
	global monthFormat
	weekPages = ccWeekPages(wikidPad)
	if wikiWord in weekPages:
		prevWeek = nextWeek = ''
		prevLink = upLink = nextLink = ''
		upFormat = '[' + monthFormat + '|%B]'
		baseDate = getGregorian([int(wikiWord[:4]), int(wikiWord[6:8]), 1])
		i = weekPages.index(wikiWord)
		# find previous week
		if (i > 0): 
			prevWeek = weekPages[i-1]
			prevLink = u'Week ' + prevWeek[6:8] + u' [' + prevWeek + u']'
		else:
			prevLink = u'(no previous)'
		# find next week
		if (i < len(weekPages)-1): 
			nextWeek = weekPages[i+1]
		else:
			nextDate = max(baseDate + datetime.timedelta(days=7), datetime.date.today())
			# isoDay = nextDate.isocalendar()
			# nextWeek = unicode(isoDay[0]) + u'-W' + unicode(isoDay[1]).rjust(2,'0')
			nextWeek = weekFormat(nextDate)
		nextLink = u'[' + nextWeek + u'] Week ' + nextWeek[6:8]
		# find up link(s)
		upLink = baseDate.strftime(upFormat)
		endDate = baseDate + datetime.timedelta(days=6)
		if baseDate.month != endDate.month:
			upLink = upLink + u' | ' + endDate.strftime(upFormat)
		# define navLinks
		navLinks = [unicode(prevLink), unicode(upLink), unicode(nextLink), unicode(prevWeek), unicode(nextWeek), unicode(baseDate.strftime(monthFormat)), unicode(endDate.strftime(monthFormat))]
	else: 
		navLinks = [u'error', u'error', u'error']
	return navLinks
	
def isCurrentWeek(wikiWord):
	"""
	Determines if wikiWord is today's date. Returns True/False
	"""
	current = wikiWord == weekFormat(datetime.date.today())
	return current
	
# ---------- /week modules ----------------------
# ---------- month modules ----------------------

def ccMonthPages(wikidPad):
	""""
	returns list of month pages in current wiki
	"""
	global _monthRE
	monthPages = wikidPad.getWikiDocument().getWikiData().getAllDefinedWikiPageNames()
	monthPages = filter(lambda w: len(w)==7 and _monthRE.match(w), monthPages)
	monthPages.sort()
	return monthPages
	
def makeMonthPage(wikidPad, wikiWord):
	"""
	writes skeletal structure for a new month page
	"""
	calendar.setfirstweekday(calendar.SUNDAY)
	monthName = my_unicode(calendar.month_name[int(wikiWord[5:])])
	templateWord = getMonthTemplate(wikidPad)
	editor = wikidPad.getActiveEditor()
	editor.GotoPos(editor.GetLineEndPosition(0))
	editor.AddText(u' ' + monthName + u'\n')
	editor.AddText(u'< >\n')
	editor.AddText(u'----\n')
	if templateWord is not None:
		templatePage = wikidPad.getWikiDocument().getWikiPage(templateWord)
		content = templatePage.getContent()
		editor.AddText(content)
	editor.GotoPos(editor.GetLength())
	editor.AddText(u'\n+++ '+monthName+ u' ' +wikiWord[:4]+ u' Date Pages\n[autotext: month]\n[end: month]\n')
	editor.AddText(u'\n+++ Links\n[autotext: links]\n[end: links]\n\n-----------\n[icon=date]')
	editor.GotoLine(4)
	editor.SetFocus()
	wikidPad.saveCurrentDocPage()				# important!
	return

def monthPrevUpNext(wikidPad, wikiWord):
	"""
	returns month page previous, up and next links as a string
	"""
	global monthFormat, yearFormat
	prevMonth = thisMonth = nextMonth = datetime.date(1900, 1, 1)
	monthPages = ccMonthPages(wikidPad)
	if wikiWord in monthPages:
		pMonthFormat = '%B [' + monthFormat + ']'
		nMonthFormat = '[' + monthFormat + '] %B'
		prevLink = upLink = nextLink = ''
		monthString = string.split(wikiWord[:10],"-")
		thisMonth = datetime.date(int(monthString[0]),int(monthString[1]),1)
		# find previous month
		i = monthPages.index(thisMonth.strftime(monthFormat))
		if (i > 0): 
			monthString = string.split(monthPages[i-1],"-")
			prevMonth = datetime.date(int(monthString[0]),int(monthString[1]), 1)
			prevLink = prevMonth.strftime(pMonthFormat)
		else:
			prevLink = u'(no previous)'
		# find next month
		if (i < len(monthPages)-1): 
			monthString = string.split(monthPages[i+1],"-")
			nextMonth = datetime.date(int(monthString[0]),int(monthString[1]),1)
		else:
			nextMonth = max(thisMonth + datetime.timedelta(days=31), datetime.date.today())
		nextLink = nextMonth.strftime(nMonthFormat)
		# find up link
		upLink = bracketWord(wikidPad, thisMonth.strftime(yearFormat))
		# collect navLinks
		# navLinks = [unicode(prevLink), unicode(upLink), unicode(nextLink), unicode(prevMonth.strftime(monthFormat)), unicode(archive), unicode(nextMonth.strftime(monthFormat))]
		archive = getMyArchive(wikidPad)
		navLinks = [unicode(prevLink), unicode(upLink), unicode(nextLink), unicode(prevMonth.strftime(monthFormat)), unicode(thisMonth.strftime(yearFormat)), unicode(nextMonth.strftime(monthFormat)), unicode(archive)]
	else: 
		navLinks = [u'error', u'error', u'error']
	datePages = ccDatePages(wikidPad)
	datePages = filter(lambda w: w[:7]==thisMonth.strftime(monthFormat), datePages)
	navLinks = navLinks + datePages
	return navLinks

def isCurrentMonth(wikiWord):
	"""
	Determines if wikiWord is today's date. Returns True/False
	"""
	global monthFormat
	current = wikiWord == datetime.date.today().strftime(monthFormat)
	return current
	
# ---------- /month modules ---------------------
# ---------- year modules ----------------------

def ccYearPages(wikidPad):
	""""
	returns list of year pages in current wiki
	"""
	global _yearRE
	yearPages = wikidPad.getWikiDocument().getWikiData().getAllDefinedWikiPageNames()
	yearPages = filter(lambda w: len(w)==5 and _yearRE.match(w), yearPages)
	yearPages.sort()
	return yearPages

def ccYears(wikidPad):
	""""
	returns list of years and months derived from the date & month pages in current wiki
	"""
	global _monthRE
	raw = wikidPad.getWikiDocument().getWikiData().getAllDefinedWikiPageNames()
	raw = filter(lambda w: _monthRE.match(w), raw)
	years = []
	for item in raw:
		i = (item[:4], item[5:7])
		if i not in years: years.append(i)
	return years
	
def makeYearPage(wikidPad, wikiWord):
	"""
	writes skeletal structure for a new year page
	"""
	templateWord = getYearTemplate(wikidPad)
	editor = wikidPad.getActiveEditor()
	editor.GotoPos(editor.GetLineEndPosition(0))
	editor.AddText(u'\n')
	editor.AddText(u'< >\n')
	editor.AddText(u'----\n')
	if templateWord is not None:
		templatePage = wikidPad.getWikiDocument().getWikiPage(templateWord)
		content = templatePage.getContent()
		editor.AddText(content)
	editor.GotoPos(editor.GetLength())
	editor.AddText(u'\n+++ Links\n[autotext: links]\n[end: links]\n')
	editor.GotoLine(3)
	editor.SetFocus()
	wikidPad.saveCurrentDocPage()				# important!
	return

def yearPrevUpNext(wikidPad, wikiWord):
	"""
	returns year page previous, up and next links as a string
	"""
	global yearFormat
	yearPages = ccYearPages(wikidPad)
	if wikiWord in yearPages:
		# get year from wikiWord
		prevLink = upLink = nextLink = ''
		thisYear = datetime.date(int(wikiWord[1:5]),1,1)
		# find previous year
		i = yearPages.index(wikiWord)
		if (i > 0): 
			prevLink = bracketWord(wikidPad, yearPages[i-1])
		else:
			prevLink = u'(no previous)'
		# find next year
		if (i < len(yearPages)-1): 
			nextLink = bracketWord(wikidPad, yearPages[i+1])
		else:
			nextYear = max(thisYear + datetime.timedelta(days=366), datetime.date.today())
			nextLink = bracketWord(wikidPad, nextYear.strftime(yearFormat))
		# find up link
		upLink = bracketWord(wikidPad, getMyArchive(wikidPad))
		navLinks = [unicode(prevLink), unicode(upLink), unicode(nextLink)]
	else: 
		navLinks = [u'error', u'error', u'error']
	return navLinks
	
def isCurrentYear(wikiWord):
	"""
	Determines if wikiWord is today's date. Returns True/False
	"""
	global yearFormat
	current = wikiWord == datetime.date.today().strftime(yearFormat)
	return current
	
# ---------- /year modules ---------------------
# ---------- dynamic content modules ------------

def dynamicNavigationLinks(wikidPad, wikiWord, navLinks):
	"""
	writes "< previous day | this month | next day >" links to top of date pages
	"""
	output = ''
	editor = wikidPad.getActiveEditor()
	# 	startPos[line number, position in line] and 
	# 	startWindow[starting line number, ending line number] 
	# 	are used to hold cursor position
	startPos = getStartPos(editor)
	startWindow = [1, 2]
	# 	write links to line 1 (second line)
	output = u'< ' + navLinks[0] + u' | ' + navLinks[1] + u' | ' + navLinks[2] + u' >'
	sol = editor.PositionFromLine(1)
	eol = editor.PositionFromLine(2)
	# look for "<" and ">" delimiters
	selStart = editor.FindText(sol, eol, u'<', 0)
	selEnd = editor.FindText(sol, eol, u'>', 0) + 1
	if (selStart > 0 and selEnd > selStart):
		editor.SetSelection(selStart, selEnd)
		editor.ReplaceSelection('')
	else:
		# expected delimiters not found; create new line
		editor.GotoLine(1)
		editor.AddText(u'\n')
		startWindow[1] = startWindow[1] + 1
	editor.GotoLine(1)
	editor.AddText(output)
	# get length of new line 1 (second line)
	sol = editor.PositionFromLine(1)
	eol = editor.PositionFromLine(2)	
	len1 = eol - sol - 1
	# write horizontal line to line 2 (third line)
	sol = editor.PositionFromLine(2)
	eol = editor.PositionFromLine(3)
	# look for "----"
	ok = editor.FindText(sol, eol, u'----', 0)
	if ok > 0:
		editor.SetSelection(sol, eol)
		editor.ReplaceSelection('')
	else:
		# expected "----" not found; create new line
		editor.GotoLine(2)
		editor.AddText(u'\n')
		startWindow[1] = startWindow[1] + 1
	editor.GotoLine(2)
	editor.AddText(u'-'*len1+u'\n')
	updateStartPos(editor, startPos, startWindow)
	return

def dynamicParentLinks(wikidPad, wikiWord, navLinks):
	"""
	Write a list of parent links for the current wikiWord in an Autogen Window
	"""
	global parentLinksTag, sameAsFalse, _dateRE, pageType
	dateLinks = True
	value = wikidPad.getWikiDocument().getWikiData().getGlobalProperties().get(u'global.cc.autotextdatelinks')
	if value is not None:
		if value in sameAsFalse: 
			dateLinks = False
	editor = wikidPad.getActiveEditor()
	startPos = getStartPos(editor)
	startWindow = setAutoWindow(wikidPad, editor, parentLinksTag, False)
	parents = wikidPad.getWikiDocument().getWikiData().getParentRelationships(wikiWord)
	if not dateLinks:
		parents = filter(lambda w: (not _dateRE.match(w)) and (not _weekRE.match(w)), parents)
	if pageType == u'd': navLinks = relativeLinks(wikidPad, wikiWord, navLinks, editor)
	parents.sort(key=lambda s: (s.lower(), s))
	count = 0
	for word in parents:
		if not (word in navLinks):
			if count == 0:
				editor.AddText(u'\n')
			editor.AddText(u'\t' + bracketWord(wikidPad, word) + u'#' + wikiWord + u'\n')
			count = count + 1
	if (count > 0):
		editor.AddText(u'\n')
	updateStartPos(editor, startPos, startWindow)
	return

def relativeLinks(wikidPad, wikiWord, navLinks, editor):
	"""
	Creates links to date pages one week, one month and one year prior
	"""
	global pageType, dateFormat
	if pageType == u'd':
		dateString = string.split(wikiWord,"-")
		thisDay = datetime.date(int(dateString[0]),int(dateString[1]),int(dateString[2]))
		datePages = ccDatePages(wikidPad)
		beginDate = min(datePages)
		endDate = max(datePages)
		# week links
		weekDateBefore = (thisDay - datetime.timedelta(days=7)).strftime(dateFormat)
		weekDateAfter = (thisDay + datetime.timedelta(days=7)).strftime(dateFormat)
		if (weekDateBefore >= beginDate) or (weekDateAfter <= endDate):
			output = '< '
			if weekDateBefore >= beginDate:
				if weekDateBefore in datePages:
					output = output + bracketWord(wikidPad, weekDateBefore)
					navLinks.append(weekDateBefore)
				else:
					output = output + ' ' + weekDateBefore + ' '
			else:
				output = output + ' '*12
			output = output + ' One Week  '
			if weekDateAfter <= endDate:
				if weekDateAfter in datePages:
					output = output + bracketWord(wikidPad, weekDateAfter)
					navLinks.append(weekDateAfter)
				else:
					output = output + ' ' + weekDateAfter + ' '
			else:
				output = output + ' '*12
			output = output + ' >\n'
			editor.AddText(unicode(output))
		# month links
		monthDateBefore = (thisDay - datetime.timedelta(days=30)).strftime(dateFormat)
		monthDateAfter = (thisDay + datetime.timedelta(days=30)).strftime(dateFormat)
		if (monthDateBefore >= beginDate) or (monthDateAfter <= endDate):
			output = '< '
			if monthDateBefore >= beginDate:
				if monthDateBefore in datePages:
					output = output + bracketWord(wikidPad, monthDateBefore)
					navLinks.append(monthDateBefore)
				else:
					output = output + ' ' + monthDateBefore + ' '
			else:
				output = output + ' '*12
			output = output + ' One month '
			if monthDateAfter <= endDate:
				if monthDateAfter in datePages:
					output = output + bracketWord(wikidPad, monthDateAfter)
					navLinks.append(monthDateAfter)
				else:
					output = output + ' ' + monthDateAfter + ' '
			else:
				output = output + ' '*12
			output = output + ' >\n'
			editor.AddText(unicode(output))
		# year links
		yearDateBefore = (thisDay - datetime.timedelta(days=364)).strftime(dateFormat)
		yearDateAfter = (thisDay + datetime.timedelta(days=364)).strftime(dateFormat)
		if (yearDateBefore >= beginDate) or (yearDateAfter <= endDate):
			output = '< '
			if yearDateBefore >= beginDate:
				if yearDateBefore in datePages:
					output = output + bracketWord(wikidPad, yearDateBefore)
					navLinks.append(yearDateBefore)
				else:
					output = output + ' ' + yearDateBefore + ' '
			else:
				output = output + ' '*12
			output = output + ' One year  '
			if yearDateAfter <= endDate:
				if yearDateAfter in datePages:
					output = output + bracketWord(wikidPad, yearDateAfter)
					navLinks.append(yearDateAfter)
				else:
					output = output + ' ' + yearDateAfter + ' '
			else:
				output = output + ' '*12
			output = output + ' >\n'
			editor.AddText(unicode(output))
	return navLinks
	
def dynamicWeekCalendar(wikidPad, wikiWord, linkAll=False):
	"""
	writes calendar to week page
	This routine is called with linkAll=True when a week page is opened, and again with linkAll=False when the page is closed.
	"""
	global dateFormat, deletedWord, pageType
	weeknumbers = useWeekNumbers(wikidPad)
	pageType = getPageType(wikidPad, wikiWord)
	if (wikiWord != deletedWord) and (pageType == u'w'):
		# cDateFormat = u'<%a> [' + dateFormat + u'] %d'
		year = int(wikiWord[:4])
		week = int(wikiWord[6:])
		startDate = getGregorian([int(wikiWord[:4]),int(wikiWord[6:8]),1])
		endDate = startDate + datetime.timedelta(days=6)
		datePages = ccDatePages(wikidPad)
		datePages = filter(lambda w: w >= startDate.strftime(dateFormat) and w <= endDate.strftime(dateFormat), datePages)
		dateProps = ccEvents(wikidPad, wikiWord)
		dateProps = filter(lambda w: w[0] >= startDate.strftime(dateFormat) and w[0] <= endDate.strftime(dateFormat), dateProps)
		editor = wikidPad.getActiveEditor()
		startPos = getStartPos(editor)
		startWindow = setAutoWindow(wikidPad, editor, u'week', False)
		editor.AddText(u'\t<<|\n\t*Mon*|*Tue*|*Wed*|*Thu*|*Fri*|*Sat*|*Sun*|\n\t')
		for i in range(7):
			thisDay = startDate + datetime.timedelta(days=i)
			date = thisDay.strftime(dateFormat)
			special = filter(lambda w: w[0] == date, dateProps)
			if linkAll or date in datePages:
				editor.AddText(u'['+date+thisDay.strftime('|%d]'))
			else:
				editor.AddText(unicode(thisDay.strftime(' %d')))
			if len(special) > 0: 
				for s in special:
					editor.AddText(s[2])
				editor.AddText(unicode(thisDay.strftime(' <%a>')))
				for s in special:
					editor.AddText(u' <' + s[1] + u'>')
			else: editor.AddText(unicode(thisDay.strftime('  <%a>')))	
			if i < 6: editor.AddText(u'| \\')
			editor.AddText(u'\n\t')
		# add no-break spaces to standardize column width (HTML doesn't work as of wikidPad1.8)
		rpt = 7
		editor.AddText(u'\t'+(u'\u00A0'*7+u'|')*rpt+u'\n')
		editor.AddText(u'\t>>\n')
		# testing/debug
		# editor.AddText(str(datePages))
		# add event list
		if len(dateProps) > 0: 
			editor.AddText(u'\n\n')
			for props in dateProps:
				editor.AddText(u'\t'+props[0][8:]) 
				editor.AddText(u': '+props[1]+ u'\n')
		editor.AddText(u'\n')
		updateStartPos(editor, startPos, startWindow)
		wikidPad.saveCurrentDocPage(True)
	return
	
def dynamicMonthCalendar(wikidPad, wikiWord, linkAll=False):
	"""
	writes calendar to month page
	This routine is called with linkAll=True when a month page is opened, and again with linkAll=False when the page is closed.
	"""
	weeknumbers = useWeekNumbers(wikidPad)
	if weeknumbers: calendar.setfirstweekday(calendar.MONDAY)
	else: calendar.setfirstweekday(calendar.SUNDAY)
	global dateFormat, deletedWord, pageType
	pageType = getPageType(wikidPad, wikiWord)
	if (wikiWord != deletedWord) and (pageType == u'm'):
		# cDateFormat = u'<%a> [' + dateFormat + u'] %d'
		year = int(wikiWord[:4])
		month = int(wikiWord[5:])
		monthMatrix = calendar.monthcalendar(year, month)
		datePages = ccDatePages(wikidPad)
		datePages = filter(lambda w: w[:7] == wikiWord, datePages)
		dateProps = ccEvents(wikidPad, wikiWord)
		dateProps = filter(lambda w: w[0][:7] == wikiWord, dateProps)
		weekPages = ccWeekPages(wikidPad)
		editor = wikidPad.getActiveEditor()
		startPos = getStartPos(editor)
		startWindow = setAutoWindow(wikidPad, editor, u'month', False)
		# editor.AddText(str(startWindow[0]) + ', ' + str(startWindow[1]))
		if weeknumbers: editor.AddText(u'\t<<|\n\t*Week*|*Mon*|*Tue*|*Wed*|*Thu*|*Fri*|*Sat*|*Sun*|\n\t')
		else: editor.AddText(u'\t<<|\n\t*Sun*|*Mon*|*Tue*|*Wed*|*Thu*|*Fri*|*Sat*|\n\t')
		for week in monthMatrix:
			j = 0
			if weeknumbers:
				isoWeek = weekFormat(datetime.date(year, month, max(week[0],1)))
				output = ''
				if linkAll or isoWeek in weekPages: output = output + u'['
				output = output + isoWeek
				if linkAll or isoWeek in weekPages: output = output + u']'
				output = output + u' | \\\n\t'
				editor.AddText(output)
			for day in week:
				if day > 0: 
					thisDay = datetime.date(year, month, day)
					date = thisDay.strftime(dateFormat)
					special = filter(lambda w: w[0] == date, dateProps)
					if linkAll or date in datePages:
						editor.AddText(unicode('['+date+thisDay.strftime('|%d]')))
					else:
						editor.AddText(unicode(thisDay.strftime(' %d')))
					if len(special) > 0: 
						for s in special:
							editor.AddText(s[2])
						editor.AddText(unicode(thisDay.strftime(' <%a>')))
						for s in special:
							editor.AddText(u' <' + s[1] + u'>')
					else: editor.AddText(unicode(thisDay.strftime('  <%a>')))	
				if j < 6: editor.AddText(u'| \\')
				editor.AddText(u'\n\t')
				j = j+1
		# add no-break spaces to standardize column width (HTML doesn't work as of wikidPad1.8)
		rpt = 7
		if weeknumbers: rpt = 8
		editor.AddText(u'\t'+(u'\u00A0'*7+u'|')*rpt+u'\n')
		editor.AddText(u'\t>>\n')
		# add event list
		if len(dateProps) > 0: 
			editor.AddText(u'\n\n')
			for props in dateProps:
				editor.AddText(u'\t'+props[0][8:]) 
				editor.AddText(u': '+props[1]+ u'\n')
		editor.AddText(u'\n')
		updateStartPos(editor, startPos, startWindow)
		wikidPad.saveCurrentDocPage(True)
	return

def dynamicArchive(wikidPad, wikiWord):
	"""
	lists links to month pages, grouped by year.
	"""
	global sameAsAscend, sameAsDescend, yearFormat
	appendMonthSort = appendYearSort = False
	globalProps = wikidPad.getWikiDocument().getWikiData().getGlobalProperties()
	years = ccYears(wikidPad)
	# sort months
	monthSort = globalProps.get(u'global.cc.monthsort')
	if monthSort is None: 
		monthSort = u'reverse'
		appendMonthSort = True
	if monthSort.lower() in sameAsAscend: 
		years.sort(key=operator.itemgetter(1))
	else: 
		years.sort(key=operator.itemgetter(1), reverse=True)
	# sort years
	yearSort = globalProps.get(u'global.cc.yearsort')
	if yearSort is None: 
		yearSort = u'reverse'
		appendYearSort = True
	if yearSort.lower() in sameAsAscend: 
		years.sort(key=operator.itemgetter(0))
	else: 
		years.sort(key=operator.itemgetter(0), reverse=True)
	# output
	editor = wikidPad.getActiveEditor()
	startPos = getStartPos(editor)
	startWindow = setAutoWindow(wikidPad, editor, u'Archive', False)
	i = 0
	for y in years:
		if y[0] <> i: 
			editor.AddText(u'\n+++ Year '+unicode(y[0])+u'\n\n')
			i = y[0]
			word = u'Y' + y[0]
			editor.AddText(u'\t'+bracketWord(wikidPad, word)+u'\n')
		word = unicode(y[0])+u'-'+unicode(y[1])+u'|'+my_unicode(calendar.month_name[int(y[1])])+u' '+unicode(y[0])
		editor.AddText(u'\t'+bracketWord(wikidPad, word)+u'\n')
	editor.AddText(u'\n')
	# append props if none
	if appendYearSort:
		editor.GotoPos(editor.GetLength())
		word = u'global.cc.yearsort: '+yearSort
		editor.AddText(u'\n'+bracketWord(wikidPad, word))
	if appendMonthSort:
		editor.GotoPos(editor.GetLength())
		word = u'global.cc.monthsort: '+monthSort
		editor.AddText(u'\n'+bracketWord(wikidPad, word))
	updateStartPos(editor, startPos, startWindow)
	return
	
# ---------- /dynamic content modules -----------

def checkCurrentPages(wikidPad):
	"""
	checks if date, (week), month and year pages exist for the current date.
	Opens a dialog box on startup (openedWiki hook) if one or more are missing.
	"""
	global dateFormat, monthFormat, yearFormat
	dialog = False
	output = u''
	today = datetime.date.today()
	# check date pages
	date = today.strftime(dateFormat)
	datePages = ccDatePages(wikidPad)
	if date not in datePages:
		dialog = True
		output = output + u'- It is a new Day\n'
	# check week pages
	if useWeekNumbers(wikidPad):
		week = weekFormat(today)
		weekPages = ccWeekPages(wikidPad)
		if week not in weekPages:
			dialog = True
			output = output + u'- It is a new Week\n'
	# check month pages
	month = today.strftime(monthFormat)
	monthPages = ccMonthPages(wikidPad)
	if month not in monthPages:
		dialog = True
		output = output + u'- It is a new Month\n'
	# check year pages
	year = today.strftime(yearFormat)
	yearPages = ccYearPages(wikidPad)
	if year not in yearPages:
		dialog = True
		output = output + u'- It is a new Year\n'
	# open dialog box if applicable
	if dialog:
		pass # wikidPad.stdDialog('o', u'wikidPad Calendar Control', output)
	return

# ----- /calendar control -----------------------
# ----- hooks -----------------------------------
# This section of code is derived from WikidPadHooks.py distributed as part of the WikidPad program

def startup(wikidPad):
	"""
	Called when application starts
	"""
	pass

def newWiki(wikidPad, wikiName, wikiDir):
	"""
	Called when a new wiki is about to be created.

	wikiName -- name of the wiki (already checked to be a proper CamelCase word)
	wikiDir -- directory to create the wiki in (more precisely the .wiki config
		file). This directory may already exist
	"""
	pass

def createdWiki(wikidPad, wikiName, wikiDir):
	"""
	Called when creation of a new wiki was done successfully.

	The home wiki word (equals name of the wiki) is not yet loaded.

	wikiName -- name of the wiki
	wikiDir -- directory the wiki was created in
	"""
	pass

def openWiki(wikidPad, wikiConfig):
	"""
	Called when an existing wiki is about to be opened.

	wikiConfig -- path to the .wiki config file
	"""
	pass

def openedWiki(wikidPad, wikiName, wikiConfig):
	"""
	Called when an existing wiki was opened successfully

	wikiName -- name of the wiki
	wikiConfig -- path to the .wiki config file
	"""
	if ccCheckEnabled(wikidPad) and getStartupCheck(wikidPad):
		checkCurrentPages(wikidPad)
	return

def openWikiWord(wikidPad, wikiWord):
	"""
	Called when a new or existing wiki word is about to be opened.
	The previous active page is already saved, new one is not yet loaded.

	wikiWord -- name of the wiki word to open
	"""
	global deletedWord, thisWikiWord, pageType
	ccEnabled = ccCheckEnabled(wikidPad)
	if ccEnabled and (thisWikiWord != deletedWord) and (thisWikiWord is not None): 
		if pageType == u'm': dynamicMonthCalendar(wikidPad, thisWikiWord, False)
		if pageType == u'w': dynamicWeekCalendar(wikidPad, thisWikiWord, False)
	deletedWord = ''
	return

def newWikiWord(wikidPad, wikiWord):
	"""
	Called when a new wiki word is about to be created.
	The wikidPad.currentWikiPage of the new word is already available

	wikiWord -- name of the wiki word to create
	"""
	if ccCheckEnabled(wikidPad):
		global isNewWikiWord
		isNewWikiWord = True
	return

def openedWikiWord(wikidPad, wikiWord):
	"""
	Called when a new or existing wiki word was opened successfully.
	wikiWord -- name of the wiki word
	"""
	global thisWikiWord, isNewWikiWord, pageType, prevDay, thisDay, nextDay, dayZero, _dateRE, _weekRE, _monthRE, dateFormat, onOpenedWiki
        locale.setlocale(locale.LC_ALL, "english")
	if ccCheckEnabled(wikidPad):
		# reset values
		prevDay = thisDay = nextDay = dayZero
		thisWikiWord = wikiWord
		pageType = getPageType(wikidPad, wikiWord)
		highlight = False
		# date page controls
		if pageType == u'd': 
			if isNewWikiWord: makeDatePage(wikidPad, wikiWord)
			navLinks = datePrevUpNext(wikidPad, wikiWord)
			dynamicNavigationLinks(wikidPad, wikiWord, navLinks)
			dynamicParentLinks(wikidPad, wikiWord, navLinks)
			highlight = isCurrentDate(wikiWord)
		# week page controls
		if pageType == u'w':
			if isNewWikiWord: makeWeekPage(wikidPad, wikiWord)
			navLinks = weekPrevUpNext(wikidPad, wikiWord)
			dynamicNavigationLinks(wikidPad, wikiWord, navLinks)
			dynamicWeekCalendar(wikidPad, wikiWord, True)
			dynamicParentLinks(wikidPad, wikiWord, navLinks)
			highlight = isCurrentWeek(wikiWord)
		# month page controls
		if pageType == u'm': 
			if isNewWikiWord: makeMonthPage(wikidPad, wikiWord)
			navLinks = monthPrevUpNext(wikidPad, wikiWord)
			dynamicNavigationLinks(wikidPad, wikiWord, navLinks)
			dynamicMonthCalendar(wikidPad, wikiWord, True)
			dynamicParentLinks(wikidPad, wikiWord, navLinks)
			highlight = isCurrentMonth(wikiWord)
		# year page controls
		if pageType == u'y':
			if isNewWikiWord: makeYearPage(wikidPad, wikiWord)
			navLinks = yearPrevUpNext(wikidPad, wikiWord)
			dynamicNavigationLinks(wikidPad, wikiWord, navLinks)
			highlight = isCurrentYear(wikiWord)
		# archive page controls
		if wikiWord == getMyArchive(wikidPad):
			dynamicArchive(wikidPad, wikiWord)

		# manipulate editor color
		editor = wikidPad.getActiveEditor()
		if highlight:
			color = getHighlightColor(wikidPad)
			if color is None: color = 'yellow'
			# color = '#FFFFAA'
		else:
			color = wikidPad.getConfig().get("main", "editor_bg_color")
			if len(color) == 0: color = 'white'
		for i in xrange(32):
			editor.StyleSetBackground(i, color)
		editor.StyleSetBackground(wx.stc.STC_STYLE_DEFAULT, color) 
		
	isNewWikiWord = False
	return

def savingWikiWord(wikidPad, wikiWord):
	"""
	Called when a new or existing wiki word is about to be saved

	wikiWord -- name of the wiki word to create
	"""
	pass

def savedWikiWord(wikidPad, wikiWord):
	"""
	Called when a wiki word was saved successfully

	wikiWord -- name of the wiki word to create
	"""
	pass

def renamedWikiWord(wikidPad, fromWord, toWord):
	"""
	Called when a wiki word was renamed successfully.

	The changed data is already saved in the fileset,
	the GUI is not updated yet, the renamed page is not yet loaded.

	fromWord -- name of the wiki word before renaming
	toWord -- name of the wiki word after renaming
	"""
	pass

def deletedWikiWord(wikidPad, wikiWord):
	"""
	Called when a wiki word was deleted successfully.

	The changed data is already saved in the fileset,
	the GUI is not updated yet, another page (normally
	the last in history before the deleted one) is not yet loaded.

	wikiWord -- name of the deleted wiki word
	"""
	ccEnabled = ccCheckEnabled(wikidPad)
	if ccEnabled:
		global deletedWord
		deletedWord = wikiWord
	return

def exit(wikidPad):
	"""
	Called when the application is about to exit.

	The global and the wiki configuration (if any) are saved already,
	the current wiki page (if any) is saved already.
	"""
	pass

# ----- /hooks ----------------------------------
