'''
I'm reusing the license used by WikidPad. I guess it'll make things simpler (?).

---

BSD License

Copyright (c) 2008, Francois Savard (francois@fsavard.com, http://www.fsavard.com)
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    * Neither the name of the  nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

Dynamic search results for WikidPad

2008.10.14: first version, which was using direct insertion in the source text
2008.10.16: now using Insertion mechanism ([:dynsearch: ...]) instead of direct source insertion
2008.10.18: correction for the extension to work with WP 1.8 too, and for results from current page to be excluded
2008.10.22: added support for regular expressions with the "dynsearch_re" syntax
'''

from pwiki.SearchAndReplace import SearchReplaceOperation
import re
import wx
from pwiki.StringOps import uniToGui

RESULTS_TITLE = "Dynamic search results: "
RESULTS_TITLE_REGEXP = "Dynamic search results (regexp): "
RESULTS_END_STRING = "*(end of results)*"
RESULT_INDENT = "\t"

# ----------------------------

WIKIDPAD_PLUGIN = (("InsertionByKey", 1),) 

def describeInsertionKeys(ver, app):

    return (

            (u"dynsearch", ("wikidpad_language",), DynSearchInsertionHandler_NoRegexp),
            (u"dynsearch_re", ("wikidpad_language",), DynSearchInsertionHandler_Regexp),

            )

# ----------------------------

def wikiEscape(name):
    '''
    Escape characters of a Regexp which might not show in Preview.
    '''
    result = []
    for c in name:
        if c == "[" or c == "]" or c == "\\":
            result.append("\\" + c)
        else:
            result.append(c)
    return u"".join(result)

# ----------------------------

indentFindingPattern = re.compile(r"[^\-_\s]")
def findIndent(line):
    global indentFindingPattern

    res = indentFindingPattern.search(line)

    if not res is None:
        left = res.span()[0]
        return left

    # blank-only line
    return None

# ----------------------------

bulletLineRe = re.compile(r"^\s*\*")

def processPage(text, lineMatcher):
    '''
    Pass the whole file and aggregate sections based on lines matched
    by lineMatcher.

    I do it this way since it's simpler to get title levels and
    grab "backward" info (ie. info preceding the keyword). It'll be
    more flexible if other types of sections are added.
    '''
    lines = text.splitlines(False)

    printing = False

    # types of sections: constants
    BULLETS = 1
    PARAGRAPH = 2

    sectionType = 0

    indentLowerLimit = 999

    titleLevel = 1

    resultsArray = []
    curResult = ""

    for l in lines:
        thisLineIndent = -1

        if printing:
            thisLineIndent = findIndent(l)

            if( (sectionType == BULLETS and not thisLineIndent is None
                and thisLineIndent <= indentLowerLimit)
               or (sectionType == PARAGRAPH and thisLineIndent is None)):
                resultsArray.append(curResult)
                curResult = ""
                printing = False

            if printing:
                curResult += RESULT_INDENT + l + "\n"

        if not printing and lineMatcher.search(l):
            if thisLineIndent < 0:
                thisLineIndent = findIndent(l)

            curResult = RESULT_INDENT + l + "\n"

            if bulletLineRe.match(l):
                sectionType = BULLETS
                indentLowerLimit = thisLineIndent
            else:
                sectionType = PARAGRAPH

            printing = True

    if printing:
        resultsArray.append(curResult)

    return resultsArray

# ----------------

def doWikiWideSearch(wikiDocument, regexpString):
    sarOp = SearchReplaceOperation()

    sarOp.wikiWide = True
    sarOp.wildCard = 'regex'
    sarOp.caseSensitive = False

    sarOp.searchStr = regexpString

    return wikiDocument.searchWiki(sarOp)

# ----------------

def extractSections(wikiDocument, regexpString, curWikiWord):
    '''
    Extract one section and output it in the current page.

    Inspired by the code used to replace a WikiWord.
    '''

    wikiWideResults = doWikiWideSearch(wikiDocument, regexpString)

    searchRe = re.compile(regexpString, re.I)

    returnStr = ""

    for resultWord in wikiWideResults:
        # Don't search the current page
        if not curWikiWord is None and resultWord == curWikiWord:
            continue

        wikiPage = wikiDocument.getWikiPage(resultWord)

        text = wikiPage.getLiveTextNoTemplate()
        if text is None:
            continue

        results = processPage(text, searchRe)

        # it is possible we found a page that doesn't contain actual results
        # since the text was contained in a dynamic search results area, so
        # we only print when we're sure we've got results
        if len(results) > 0:
            returnStr += "\n*From *[//" + resultWord + "]:\n" \
                   + "----\n".join(results) \
                   + "----\n"
            #returnStr += "\n*From *[//" + resultWord + "]:\n\n" \
            #        + text + "\n\n" \
            #        + "----\n"

    return returnStr

# ---------------------------

dynsearchReplacerRe = re.compile(r"\[:dynsearch: (.*?)\]")

def createContentBase(exporter, regexpString, title):

    wikiDataManager = None

    if hasattr(exporter, "wikiDataManager"):
        wikiDataManager = exporter.wikiDataManager
    elif hasattr(exporter, "getWikiDataManager"):
        wikiDataManager = exporter.getWikiDataManager()
    elif hasattr(exporter, "getWikiDocument"):
        wikiDataManager = exporter.getWikiDocument()
    else:
        return "Error: dynsearch could not be performed (no pointer to WikiDataManager)."

    exportedWikiWord = None

    if hasattr(exporter, "wikiWord"):
        exportedWikiWord = exporter.wikiWord

    results = extractSections(wikiDataManager, regexpString, exportedWikiWord)

    # We must replace [:dynsearch: ...] strings, otherwise we end up
    # in an infinite loop, called again and again by the exporter
    def replaceFunc(match):
        return "--Escaped dynsearch for \"" + match.group(1) + "\"--"

    results = dynsearchReplacerRe.sub(replaceFunc, results)

    return "+++ " + title + "\n----" \
            + results \
            + RESULTS_END_STRING + "\n----\n"

class DynSearchInsertionHandler_Base:
    def __init__(self, app):
        self.app = app

    def taskStart(self, exporter, exportType):
        pass

    def taskEnd(self):
        pass

    def createContent(self, exporter, exportType, insToken):
        pass

    def getExtraFeatures(self):
        return ()

class DynSearchInsertionHandler_NoRegexp(DynSearchInsertionHandler_Base):

    def createContent(self, exporter, exportType, insToken):
        return createContentBase(exporter, re.escape(insToken.value), RESULTS_TITLE + wikiEscape(insToken.value))

class DynSearchInsertionHandler_Regexp(DynSearchInsertionHandler_Base):

    def createContent(self, exporter, exportType, insToken):
        return createContentBase(exporter, insToken.value, RESULTS_TITLE_REGEXP + wikiEscape(insToken.value))
