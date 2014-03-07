""" Tags.py
    Functions and plugins for using the tag metaphor from within wikidpad
    includes:
        - a plugin that inserts a list of pages that are tagged with the tags entered into a textentry box
        - functions to get list of pages with a list of tags, and to show list of pages with a list of tags
"""
"""
jaysen naidoo 2007/03/20
changelog:
    v1.2 - 20080303: add [import_scripts:ScriptsForTagPages] statement to bottom of any gen'd Tag page.to genTags()
    
todo:
    #TODO: a FindPagesByTags form with a TagCloud
    #TODO: include negative tags here. eg. tag1+tag2-tag3
    #TODO: combine CategoryPages with Tags?? showing all pages with tags
"""

import string, wx
from WikidPadStarter import VERSION_STRING        # e.g. "wikidPad 1.8beta6"
version = VERSION_STRING[9:12]

def setArea(ed,headerStr = 'auto',showTime=True):
    """ Selects the Auto Generated Area between the '++ <headerStr>' & '+++ end of <headerStr>' markers
    and clears it. leaving the cursor ready for insertion in the (now empty) area
    if showTime is True, timestamp "..Generated at %Y.%m.%d - %X:\n" is added
    """
    sectBegin = '+++ %s' %headerStr
    sectEnd   = '+++ end of %s' %headerStr
    endpos = ed.GetLength()
    pos1 = ed.FindText(0, endpos, sectBegin, 0)
    pos2 = ed.FindText(0, endpos, sectEnd,   0)

    if pos1<0:  #opening header not found
        ed.AppendText('\n\n%s\n'%sectBegin)
        ed.AppendText('\n%s\n'%sectEnd)
        pos1 = ed.PositionFromLine(ed.LineFromPosition(ed.GetLength())-3)
        pos2 = ed.PositionFromLine(ed.LineFromPosition(ed.GetLength())-2)
    else:       #opening header found, but...
        if pos2<0:  #closing header not found
            ed.GotoPos(ed.PositionFromLine(ed.LineFromPosition(pos1)+1))
            ed.AddText('\n\n%s\n'%sectEnd)
            pos2 = ed.PositionFromLine(ed.LineFromPosition(pos1)+2)
        else:       #both found
            pos2 = pos2-1
    pos1 = ed.PositionFromLine(ed.LineFromPosition(pos1)+1)
    ed.SetSelection(pos1, pos2)
    ed.ReplaceSelection("\n\n")
    ed.GotoPos(pos1)
    if showTime == True:         # write date and time of generation:
        from time import strftime
        ed.ReplaceSelection(strftime("..Generated at %Y.%m.%d - %X:\n"))  

#---wikiword functions---#000000#FEC849------------------------------------------
def getEditorControl(wikidPad):
    """ returns the editor control"""
##    ##check version no for changing API:
##    from WikidPadStarter import VERSION_STRING # e.g. "wikidPad 1.8beta6"
##    version=VERSION_STRING[9:12] # e.g. "1.8"
##    if version < "1.9":
##        return wikidPad.getActiveEditor()
##    else:
##        return wikidPad.getSubControl("textedit")
    ## TODO: getEditorControl isnt working by version now ... fix it.
    return wikidPad.getActiveEditor()

def isWikiWord(wikidPad,str):
    """ returns true if str is a wikiword """
    if version > "1.9":
        # Retrieve internal name of current wiki language
        wikiLang = wikidPad.getWikiDocument().getWikiDefaultWikiLanguage()

        # Get language helper (an instance of WikidPadParser._TheHelper)
        langHelper = wx.GetApp().createWikiLanguageHelper(wikiLang)

        # For the newly published 2.0alpha01_03 it is then:
        #langHelper.isCcWikiWord(...)
    else:
        langHelper = wikidPad.getFormatting()
    return langHelper.isCcWikiWord(str)

def splitCamelCase(ccWord):
    """ splits ccWord into a list of words
        returns that list
    """
    words = []; nextword = ''
    for letter in ccWord:
        if not letter.isupper():
            nextword = nextword+letter
        else:
            if len(nextword)>0: words.append(nextword)
            nextword = letter
    words.append(nextword)
    return words

def getWikiPageTitle(wikiWord):   # static
    import re
    title = re.sub(ur'([A-Z\xc0-\xde]+)([A-Z\xc0-\xde][a-z\xdf-\xff])', r'\1 \2', wikiWord)
    title = re.sub(ur'([a-z\xdf-\xff])([A-Z\xc0-\xde])', r'\1 \2', title)
    return title

#---TagView functions---#000000#FEC849------------------------------------------

def getPagesByAllTags(wikidPad,tags):
    """ returns a list of pages that have ALL the tags in taglist (Tag-Intersection)
    """
    allpages = []
    firsttag=True
    for tag in tags:
        if firsttag:
            allpages = list(set(w for w,k,v in wikidPad.getWikiDocument().getPropertyTriples(None, 'tag', tag.lower())))
            firsttag = False
        else:
            allpages = set(allpages) & set(list(set(w for w,k,v in wikidPad.getWikiDocument().getPropertyTriples(None, 'tag', tag.lower()))))
    return list(allpages)


def showPagesByAllTags(wikidPad,tags,sorted=True,heading=''):
    """ displays in wikipage the list of pages that have ALL of the tags in taglist.(Tag-Intersection)
        if sorted is True, sort page names alphabetically
        if heading is supplied its used instead of the default
    """
    ed = getEditorControl(wikidPad)
    #ed.AppendText(str(wikidPad))    
    pages = getPagesByAllTags(wikidPad,tags) 

    #set area and display pages:    
    for tag in tags:
        if tag == tags[0]:                  # is this is the first tag?
            tagnames = '*'+tag+'*'
        else:
            tagnames += " AND " + '*'+tag+'*'
    if heading == '':
        heading = 'pages with TAGS = ' + tagnames
        setArea(ed,heading)
    else:
        setArea(ed,heading)
        ed.AddText('pages with TAGS = %s\n' %tagnames)
    
    if sorted:
        pages.sort()
    if version > "1.9":
        # Retrieve internal name of current wiki language
        wikiLang = wikidPad.getWikiDocument().getWikiDefaultWikiLanguage()

        # Get language helper (an instance of WikidPadParser._TheHelper)
        format = wx.GetApp().createWikiLanguageHelper(wikiLang)

        # For the newly published 2.0alpha01_03 it is then:
        #langHelper.isCcWikiWord(...)
    else:
        format = wikidPad.getFormatting()
    #format = wikidPad.getFormatting()
    for pagename in pages:
# [CD]: allow Tag pages to be subpages
            ed.AddText("* [//%s]\n" % pagename)
#        if format.isCcWikiWord(pagename):
#            ed.AddText("* %s\n" % pagename)
#        else:
#            ed.AddText("* [%s]\n" % pagename)
# [/CD]

def genTags(wikidPad,wikiWord):
    """ Dynamically generates list of pages Tagged with tags embedded in wikiname
        of the form TagDevPython (tags = dev,python)
    """
    if wikiWord[3].isupper(): #check if the wikiname is TagSomething instead of say, TaggingSomething..
        if isWikiWord(wikidPad,wikiWord[3:]):
            tags = splitCamelCase(wikiWord[3:])
        else:
            tags =[wikiWord[3:]] #handles single tag
        ed = wikidPad.getActiveEditor()
        showPagesByAllTags(wikidPad,tags)
        
        # add [import_scripts: ScriptsForTagPages]
        ##importStr = "[import_scripts:ScriptsForTagPages]"
        ##if ed.FindText(0, ed.GetLength(), importStr,   0)<0:
        ##    ed.AppendText(importStr)

def clearPageList(wikidPad,wikiWord):
    ed = getEditorControl(wikidPad)
    setArea(ed,'pages')


#---Tag Plugins---#000000#FEC849------------------------------------------------
WIKIDPAD_PLUGIN = (("hooks", 1),("MenuFunctions",1),)

def openedWikiWord(docPagePresenter, wikiWordFull):
    # [CD]: allow Tag pages to be subpages
    # get last subpage of wikiword
    wikiWord = wikiWordFull.split("/")[-1]
    # [/CD]
    if (wikiWord[:3] == "Tag") and (wikiWord[3].isupper()):
        genTags(docPagePresenter, wikiWord)

def describeMenuItems(wiki):
    global nextNumber
    return ((addTag, "Tagger\tCtrl-F1", "add text to create a tag"),
            (displayPagesByTags, "Pages By Tags\tCtrl-F3", "print pages by tags"))

def displayPagesByTags(wiki,evt):
    """ asks for a list of tags,(seperate multiple tags by '+' without spaces), 
    and prints out a list of pages with all those tags
    """
    taglist = wiki.stdDialog("text","Show pages with following Tags","insert Tags you're looking for  (seperate multiple tags by '+' without spaces)")
    if taglist=='':
        return
    else:
        tags = taglist.split('+')
        #TODO: open TAGview page
        showPagesByAllTags(wiki.getCurrentDocPagePresenter(),tags,heading = 'pages with ALL Tags' )

def addTag(wiki,evt):
    """ prints the text needed to create a tag '[tag:' at the cursor
    """ 
    ed = getEditorControl(wiki)
    ed.AddText('[tag:')
    tagNamePos = ed.GetCurrentPos()
    ed.AddText(']\n')
    ed.GotoPos(tagNamePos)
