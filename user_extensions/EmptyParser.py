## import hotshot
## _prof = hotshot.Profile("hotshot.prf")


import locale, pprint, time, sys, string, traceback

from textwrap import fill

import wx

from pwiki.rtlibRepl import re
from pwiki.StringOps import UPPERCASE, LOWERCASE, revStr
from pwiki.WikiDocument import WikiDocument
from pwiki.OptionsDialog import PluginOptionsPanel

sys.stderr = sys.stdout

locale.setlocale(locale.LC_ALL, '')

from pwiki.WikiPyparsing import *


WIKIDPAD_PLUGIN = (("WikiParser", 1),)



LETTERS = UPPERCASE + LOWERCASE


# The specialized optimizer in WikiPyParsing can't handle automatic whitespace
# removing
ParserElement.setDefaultWhitespaceChars("")



RE_FLAGS = re.DOTALL | re.UNICODE | re.MULTILINE


# -------------------- API for plugin WikiParser --------------------
# During beta state of the WikidPad version, this API isn't stable yet, 
# so changes may occur!


class _TheParser(object):
    @staticmethod
    def reset():
        """
        Reset possible internal states of a (non-thread-safe) object for
        later reuse.
        """
        pass

    @staticmethod
    def getWikiLanguageName():
        """
        Return the internal name of the wiki language implemented by this
        parser.
        """
        return "wikidpad_empty_1_0"


    @staticmethod
    def parse(intLanguageName, content, formatDetails, threadstop):
        """
        Parse the  content  written in wiki language  intLanguageName  using
        formatDetails  and regularly call  threadstop.testRunning()  to
        raise exception if execution thread is no longer current parsing
        thread.
        """

        if len(content) == 0:
            return buildSyntaxNode([], 0, "text")

        return buildSyntaxNode([buildSyntaxNode(content, 0, "plainText")],
                    0, "text")


THE_PARSER = _TheParser()





class WikiLanguageDetails(object):
    """
    Stores state of wiki language specific options and allows to check if
    two option sets are equivalent.
    """

    def __init__(self, wikiDocument, docPage):
        self.wikiDocument = wikiDocument

    @staticmethod
    def getWikiLanguageName():
        return "wikidpad_empty_1_0"

    def isEquivTo(self, details):
        """
        Compares with other details object if both are "equivalent"
        """
        return self.getWikiLanguageName() == details.getWikiLanguageName()


_RE_LINE_INDENT = re.compile(ur"^[ \t]*")

class _TheHelper(object):
    @staticmethod
    def reset():
        pass

    @staticmethod
    def getWikiLanguageName():
        return "wikidpad_empty_1_0"


    # TODO More descriptive error messages (which character(s) is/are wrong?)
    @staticmethod   # isValidWikiWord
    def checkForInvalidWikiWord(word, wikiDocument=None, settings=None):
        """
        Test if word is syntactically a valid wiki word and no settings
        are against it. The camelCase black list is not checked.
        The function returns None IFF THE WORD IS VALID, an error string
        otherwise
        """
        return None


    @staticmethod
    def extractWikiWordFromLink(word, wikiDocument=None, basePage=None):  # TODO Problems with subpages?
        """
        Strip brackets and other link details if present and return wikiWord
        if a valid wiki word can be extracted, None otherwise.
        """
        return None


    @staticmethod
    def parseTodoValue(todoValue, wikiDocument=None):
        """
        Parse a todo value (right of the colon) and return the node or
        return None if value couldn't be parsed
        """
        return None


    @staticmethod
    def parseTodoEntry(entry, wikiDocument=None):
        """
        Parse a complete todo entry (without end-token) and return the node or
        return None if value couldn't be parsed
        """
        return None


    @staticmethod
    def _createAutoLinkRelaxWordEntryRE(word):
        """
        Get compiled regular expression for one word in autoLink "relax"
        mode.

        Not part of public API.
        """
        # Split into parts of contiguous alphanumeric characters
        parts = AutoLinkRelaxSplitRE.split(word)
        # Filter empty parts
        parts = [p for p in parts if p != u""]

        # Instead of original non-alphanum characters allow arbitrary
        # non-alphanum characters
        pat = ur"\b" + (AutoLinkRelaxJoinPAT.join(parts)) + ur"\b"
        regex = re.compile(pat, AutoLinkRelaxJoinFlags)

        return regex


    @staticmethod
    def buildAutoLinkRelaxInfo(wikiDocument):
        """
        Build some cache info needed to process auto-links in "relax" mode.
        This info will be given back in the formatDetails when calling
        _TheParser.parse().
        The implementation for this plugin creates a list of regular
        expressions and the related wiki words, but this is not mandatory.
        """
        # Build up regular expression
        # First fetch all wiki words
        words = wikiDocument.getWikiData().getAllProducedWikiLinks()

        # Sort longest words first
        words.sort(key=lambda w: len(w), reverse=True)
        
        return [(_TheHelper._createAutoLinkRelaxWordEntryRE(w), w)
                for w in words if w != u""]


    @staticmethod
    def createLinkFromWikiWord(word, wikiPage):    # normalizeWikiWord
        """
        Create a link from word which should be put on wikiPage.
        """
        return ""

    @staticmethod
    def createStableLinksFromWikiWords(words, wikiPage=None):
        """
        Create particularly stable links from a list of words which should be
        put on wikiPage.
        """
        return u"\n".join([u"%s//%s%s" % (BracketStart, w, BracketEnd)
                for w in words])

    @staticmethod
    def createRelativeLinkFromWikiWord(word, baseWord, downwardOnly=True):
        """
        Create a link to wikiword word relative to baseWord.
        If downwardOnly is False, the link may contain parts to go to parents
            or siblings
        in path (in this wiki language, ".." are used for this).
        If downwardOnly is True, the function may return None if a relative
        link can't be constructed.
        """

        wordPath = word.split(u"/")
        baseWordPath = baseWord.split(u"/")
        
        if downwardOnly:
            if len(baseWordPath) >= len(wordPath):
                return None
            if baseWordPath != wordPath[:len(baseWordPath)]:
                return None
            
            return u"/" + u"/".join(wordPath[len(baseWordPath):])
        # TODO test downwardOnly == False
        else:
            # Remove common path elements
            while len(wordPath) > 0 and len(baseWordPath) > 0 and \
                    wordPath[0] == baseWordPath[0]:
                del wordPath[0]
                del baseWordPath[0]
            
            if len(baseWordPath) == 0:
                if len(wordPath):
                    return None  # word == baseWord, TODO return u"." or something
                return u"/" + u"/".join(wordPath[len(baseWordPath):])

            return u"../" * (len(baseWordPath) - 1) + \
                    u"/".join(wordPath[len(baseWordPath):])


    @staticmethod
    def createAttributeFromComponents(key, value, wikiPage=None):
        """
        Build an attribute from key and value.
        TODO: Check for necessary escaping
        """
        return ""

    @staticmethod
    def isCcWikiWord(word):
        return False


    @staticmethod
    def findNextWordForSpellcheck(text, startPos, wikiPage):
        """
        Find in text next word to spellcheck, beginning at position startPos
        
        Returns tuple (start, end, spWord) which is either (None, None, None)
        if no more word can be found or returns start and after-end of the
        spWord to spellcheck.
        """
        return (None, None, None)


    @staticmethod
    def prepareAutoComplete(editor, text, charPos, lineStartCharPos,
            wikiDocument, settings):
        """
        Called when user wants autocompletion.
        text -- Whole text of page
        charPos -- Cursor position in characters
        lineStartCharPos -- For convenience and speed, position of the 
                start of text line in which cursor is.
        wikiDocument -- wiki document object
        closingBracket -- boolean iff a closing bracket should be suggested
                for bracket wikiwords and properties

        returns -- a list of tuples (sortKey, entry, backStepChars) where
            sortKey -- unistring to use for sorting entries alphabetically
                using right collator
            entry -- actual unistring entry to show and to insert if
                selected
            backStepChars -- numbers of chars to delete to the left of cursor
                before inserting entry
        """
        return []


    @staticmethod
    def handleNewLineBeforeEditor(editor, text, charPos, lineStartCharPos,
            wikiDocument, settings):
        """
        Processes pressing of a newline in editor before editor processes it.
        Returns True iff the actual newline should be processed by
            editor yet.
        """
        # autoIndent, autoBullet, autoUnbullet
        
        return True


    @staticmethod
    def handleNewLineAfterEditor(editor, text, charPos, lineStartCharPos,
            wikiDocument, settings):
        """
        Processes pressing of a newline after editor processed it (if 
        handleNewLineBeforeEditor returned True).
        """
        # autoIndent, autoBullet, autoUnbullet

        return


    @staticmethod
    def handleRewrapText(editor, settings):
        pass

    @staticmethod
    def getNewDefaultWikiSettingsPage(mainControl):
        """
        Return default text of the "WikiSettings" page for a new wiki.
        """
        return _(u"""++ Wiki Settings

These are your default global settings.

[global.importance.low.color: grey]
[global.importance.high.bold: true]
[global.contact.icon: contact]
[global.wrap: 70]

[icon: cog]
""")  # TODO Localize differently?


    @staticmethod
    def createWikiLanguageDetails(wikiDocument, docPage):
        """
        Returns a new WikiLanguageDetails object based on current configuration
        """
        return WikiLanguageDetails(wikiDocument, docPage)


THE_LANGUAGE_HELPER = _TheHelper()



def describeWikiLanguage(ver, app):
    """
    API function for "WikiParser" plugins
    Returns a sequence of tuples describing the supported
    insertion keys. Each tuple has the form (intLanguageName, hrLanguageName,
            parserFactory, parserIsThreadsafe, editHelperFactory,
            editHelperIsThreadsafe)
    Where the items mean:
        intLanguageName -- internal unique name (should be ascii only) to
            identify wiki language processed by parser
        hrLanguageName -- human readable language name, unistring
            (TODO: localization)
        parserFactory -- factory function to create parser object(s) fulfilling

        parserIsThreadsafe -- boolean if parser is threadsafe. If not this
            will currently lead to a very inefficient operation
        processHelperFactory -- factory for helper object containing further
            functions needed for editing, tree presentation and so on.
        editHelperIsThreadsafe -- boolean if edit helper functions are
            threadsafe.

    Parameters:

    ver -- API version (can only be 1 currently)
    app -- wxApp object
    """

    return (("wikidpad_empty_1_0", u"WikidPad Empty 1.0", parserFactory,
             True, languageHelperFactory, True),)




def parserFactory(intLanguageName, debugMode):
    """
    Builds up a parser object. If the parser is threadsafe this function is
    allowed to return the same object multiple times (currently it should do
    so for efficiency).
    For seldom needed parsers it is recommended to put the actual parser
    construction as singleton in this function to reduce startup time of WikidPad.
    For non-threadsafe parsers it is required to create one inside this
    function at each call.

    intLanguageName -- internal unique name (should be ascii only) to
        identify wiki language to process by parser
    """
    return THE_PARSER


def languageHelperFactory(intLanguageName, debugMode):
    """
    Builds up a language helper object. If the object is threadsafe this function is
    allowed to return the same object multiple times (currently it should do
    so for efficiency).

    intLanguageName -- internal unique name (should be ascii only) to
        identify wiki language to process by helper
    """
    return THE_LANGUAGE_HELPER

