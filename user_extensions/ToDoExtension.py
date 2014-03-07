# -*- coding: utf-8 -*-
"""
   ToDoExtension.py                 Todo-Extension for WikidPad (http://www.wikidpad.net)

   Written by Christian Ziemski     http://www.ziemski.net/wikidpad/todo_extension.html
   
   <<<
   hacked a bit by Bjorn Johansson, a search for the phrase "changed here" reveals all changes.
   
   Now, if the todo is untagged but placed on a page where the page name is a date, this date gets 
   added as a tag (only if the todo has not already been dated in the normal way). 
   Perhaps this could/should be extended to other categories than dates ie it could be detected if
   the todo is placed under a page that is called SomeDay for example.
   
   fixed by Christian a bit, so not all "changed here" from Bjorn are still there...
    >>>

Why all that?
-------------

I was looking for a good To-Do/Notes/PIM application for a long time and found WikidPad.

Loosely based on the following extensions I wrote my own todo-extension:

    http://wikidpad.python-hosting.com/wiki/GettingThingsDone
        The starting point. NextActions by Eric Neumann
        Enhanced by icosahedral to organize by context instead of by project name.

    http://wikidpad.python-hosting.com/wiki/SortedTodos
        JaysenNaidoo version to sort the page according to tags  (todo.<tag>:)
        Mike Crowe added dynamic tags

I added date calculations, date sorting, a separate calendar page and a configuration section.
(The formulae for date calculation from week number I found somewhere in 'the internet'.)


Description:
------------

If a wikiWord beginning with "ToDo" is created or selected (viewed) it automatically
collects all 'todo' entries from all other pages and inserts them here (after a placemark).
Of course you can write own text before that placemark without being changed.

If the wikiWord has additional characters after the "ToDo" like "ToDoPrivate"
those characters "Private" are used as filter (case insensitive).
If there are spaces or underlines between "ToDo" and the following characters (e.g "ToDo_Private")
these are ignored and so still the filter is "Private". (This may be better readable.)
Only Todos containing that filter string (in its name or in the full entry) are collected.
(Behavior depends on configuration option "filterTodos" below.)
If the wikiword for example is "ToDo_Done_Private" the filter is "Done" AND "Private".
So all Todos containing both of the words are selected.

Note: If the optional Calendar feature is enabled below,
      it is "ToDoCalendar" and "ToDoCalendarPrivate" in the example above.)


The todos are sorted by 'tag' the following way:

  1.) Completely untagged                                e.g. 'todo: shopping'

  2.) Tagged with special tags (at End-Of-Tag!)          e.g. 'todo.High: pay taxes'
        Sort order and display see config section below

  3.) Tagged with a date (at End-Of-Tag!)
        Sorted by date (earliest first in list)
        Marked as 'GONE', 'TODAY', 'n hours left', 'n days left' dependent on dayrange below
        Displayed in different formats, dependent the same way.

        The following date formats are recognized:
          "yyyy-mm-dd"   # standard date                               e.g. todo.2006-10-31: Halloween 2006
          "mm/dd/yyyy"   # GB/US date
          "dd.mm.yyyy"   # European date
          "yyyy-mm-*"    # complete month mm (every day) of year yyyy  e.g. todo.2010-07-*:  One month for summer vacations
          "*-mm-*"       # complete month mm (every day); every year   e.g. todo.*-12-*:     Buy Christmas gifts
          "yyyy-Wnn-d"   # DayOfWeek in given week+year (Mon=1,Sun=7)  e.g. todo.2007-W03-2: Tuesday of 3rd week in 2007
          "*-W*-d"       # DayOfWeek in every week+year (Mon=1,Sun=7)  e.g. todo.*-W*-1:     go to work on Monday
          "yyyy-Wnn"     # complete week in a given year               e.g. todo.2008-W12:   complete week 12 in 2008
          "*-Wnn"        # complete week, every year                   e.g. todo.*-W52:      prepare end of year
          "CWnn"         #   same as above: Calendar Week
          "KWnn"         #   same as above: Calendar Week (German: Kalender Woche)
          "*-mm-dd"      # a date every year                           e.g. todo.*-10-31:    Halloween, in every year
          "*-*-dd"       # a day every month, every year               e.g. todo.*-*-01:     Every month, the 1st day
          "*-*-*"        # every day
          "*-mm-dd+d"    # every DayOfWeek before(-)/after(+) dd'th day of month mm
          "*-*-dd+d"     # every DayOfWeek before(-)/after(+) dd'th day every month   e.g.  todo.*-*-31-1: Monthly report (last Monday of the month)
          "*-E+ddd"      # Easter +- ddd days



        The dates with "*" are optimistic ones: if such a date is in the past
        it is assumed as "for next week/month/year" and not as "GONE"!

        If there are subtags like the string "Peter" in "todo.Peter.2008-09-16: Birthday"
        the subtag is listed in parentheses on the todo page.


  4.) otherwise tagged                                       e.g. 'todo.family: holidays'


  Subtags are possible:  e.g. 'todo.business.Next: talk to boss'
                              'todo.family.party.2009-06-14: invite friends'
                              'todo.business.office: tidy up'



The following WikiDocumentAttributes will be added to that generated page
(Only if there isn't already a custom [icon: ...] set, see configuration below):

  [icon: spanner]
  [color: magenta]
  [bookmarked=true]


Note: Within the WikidPad help wiki this hook/extension does nothing.
"""
##################################################################################################
"""
History:
--------

  2006-10-30 first version
  2006-11-02 bug fixes
  2006-11-09 Fix to work with pages named like [no wiki word] as well  (beta)
  2006-11-10 Fix to work with pages named like [no WikiWord] as well  (beta)
  2006-11-11 Use internal function to check WikiWord
  2006-11-16 several small mods (config, filter, color)
  2007-01-31 fixes to run in WikidPad up to 1.8 and in the new 1.9 as well
  2007-06-16 fixes tags with sub-text and date; text without trailing LF at ToDo page
  2007-06-18 fix for problem with multiple-tabs (todos on wrong page inserted)
  2007-07-27 fix for displayMessage in 1.9 (up to 1.9beta7)
  2007-07-27 above fix removed because no longer necessary due to 1.9beta8
  2007-07-31 if (onlyRealTodos == 0): that other category (like done, question ...) is shown in list
  2007-08-03 only a fix for above
  2007-09-08 new config option extendedLinks for links with search capability (only in editor window(?)) (test for Christopher)
  2007-10-02 new config: setBookmark added // list of todos sorted within every tag block
  2007-10-09 new config added: realDatesLast for sorting and infoPopupTimeDelta for suppressing frequent popups
  2007-10-11 time calculation changed a bit (tip from Jouni)
  2007-10-17 display weekday for dates // optional split of real-date-todos and normal ones into separate pages (wish from Jouni)
  2007-10-19 little config changes, some cleaning up
  2007-10-20 fixes // display week number for dates
  2007-10-22 display possible tags in entries on ToDoCalendar page too
  2007-12-06 fix for a bug if onlyRealTodos==True and todos with embedded ':' in their text
  2008-01-22 some checking for valid dates
  2008-02-20 Begin of rewrite, thanks to Marko Mahnic.
  2008-02-23 new outDateFormat configuration option
  2008-02-24 fix: new outDateFormat configuration option doesn't work on Windows automatically. Fallback implemented.
  2008-02-24 added a configuration file ToDoExtension.cfg for local changes
  2008-11-23 added new date formats "*-Wnn" for 'Monday of every week nn, every year' and "*-W*-d" for 'every d weekday (Monday=1, Tuesday=2...)'; fixes in date format CWnn and KWnn (suggested by Jouni Miettunen)
  2009-01-24 fix: optional filter for todo page (changed configuration option) / add: config option for deleting attributes from todo entry (suggested by Kurt Woodham)
  2009-02-02 Works with WikidPad 2.0alpha too now. Some fixes (e.g. bug when realDatesSeparate=True)
  2009-02-03 Better error message for invalid dates, but still needs more work
  2009-02-05 removed unused srePersistent / modified version check / new config option: showVersion
  2009-03-11 several internal changes / fixed wrong categorized special multi-tags
  2009-03-12 more fixes regarding sections
  2009-03-15 cleanup, debug, new config handling & syntax
  2009-04-05 no longer initialize on every todo page again (thanks to Michael) / wiki-local configuration page added
  2009-04-06 bugfix for empty ToDoConfiguration page problem
  2009-04-22 made timestamp in placemark configurable with todoTimestamp*... (be careful)
  2009-04-26 bugfix: if tagstring was in title todo might not be listed / special handling for multiple tags removed / new sortTagsCaseInsensitive
  2009-05-05 bugfixes: multiple tags could be sorted into one todo by mistake (old one ...) / fixed regression from 2009-04-26
  2009-05-11 bugfix: Closing a ToDo page and opening another one could lead to errors
  2009-07-26 bugfix: Better checking for and handling of invalid date entries (problem reported by Jens S.)
  2010-01-05 bugfix: thisweek was wrong, now using week number as of ISO 8601:1988 (%V instead of %W) (problem reported by Jens S.)
  2010-01-09 bugfix: regression on Windows platform fixed (reported by Andy M., solution suggested by Jens S.). More fixes in week calculation.
  2010-01-10 New date formats (suggested by Jens S.)
  2010-01-25 bugfix: another little bug in the date calculation fixed (reported by Jens S.)
  2010-03-31 bugfix: grouping error of similar tags Low/VeryLow fixed (reported by Andy M.). Date check for "*-*-dd+d" fixed.
  2010-03-31 added: showInfoOnPage (suggested by Andy M.) + pgInfoFrame, pgInfoPrefix. Asterisks in headlines disabled
  2010-04-10 fix: temporary hack to make it work with new WikidPad 2.1 alpha
  2010-12-03 fix: todos with date format "*-W*-d" sometimes not sorted correctly (reported by Jens S.)
  2010-12-07 added: date format '*-E+-ddd' to calculate by Easter (by Jens Sp.)
  2011-05-15 added Bjorn's hack, description see above and inline
  2011-06-05 improved/fixed handling of 'done's. new config option 'ignoreDones'
  2011-06-06 little optical improvement by Bjorn
  2011-08-02 enhanced filter handling (AND)
  2012-07-24 new option filterTodos=3 to search in page names too
  2012-07-25 fix: bug in filterTodos=3
  2014-03-02 fix: Sorting of todos when multiple tags are used (need still to be checked a bit)
"""
version = "2014-03-02-beta"


##################################################################################################

# todo: how to avoid double initialization of the complete hook? -> Michael
#       see: 04.02.2009 09:26: Re: [wikidPad] Bug? Extensions are "called" twice on initialization
#       http://groups.yahoo.com/group/wikidPad/message/4894
# todo: see inline ones below
# todo: add field to cfg{} to indicate what can be modified where
# todo: online help or help page or ...
# todo: remove more complexity wherever possible
# todo: auto refresh or so

##################################################################################################


WIKIDPAD_PLUGIN = (("hooks", 1),)

def startup(pWiki):
    # startup() is called rather early during initialization.
    # This is done here to avoid later checking of existence of
    # the member variable "externalPlugin_ToDo_todoext".
    # Member variables starting with "externalPlugin_" will never be used for WikidPad core.
    pWiki.externalPlugin_ToDo_todoext = None

    # Alternatively (it depends on code in Todo.__init__() if this works or not):
    # (Some necessary set-up may be missing due to early startup())
    # (In this extension the first version above seems to be the safe/possible one.)
    #
    #pWiki.externalPlugin_ToDo_todoext = Todo(pWiki)


# Only a single hook for this original function from WikidPadHooks.py is installed herein

def openedWikiWord(docPagePresenter, wikiWord):
    """
    Called when a new or existing wiki word was opened successfully.

    wikiWord -- name of the wiki word to create
    """

    if (wikiWord[:4] == "ToDo"):

        # get the already initialized instance of this extension or "None" on first call
        if wpversion < "1.9":
            wikiname = docPagePresenter.wikiName
            todoext = docPagePresenter.externalPlugin_ToDo_todoext
        else:
            wikiname = docPagePresenter.getMainControl().wikiName
            todoext = docPagePresenter.getMainControl().externalPlugin_ToDo_todoext

        # to avoid modification of help-wiki
        if wikiname == "WikidPadHelp":
            return


        # Only initialize the extension once ...
        # (Note: Following block could be omitted if second alternative above for startup() would be used)
        if todoext is None:                   # if not yet instantiated
            todoext = Todo(docPagePresenter)  # do it now
            if wpversion < "1.9":
                docPagePresenter.externalPlugin_ToDo_todoext = todoext
            else:
                docPagePresenter.getMainControl().externalPlugin_ToDo_todoext = todoext

        # ... but update to current docPagePresenter (reference to wxPanel) on every call
        # this way:
        # todoext.wikidpad = docPagePresenter
        # or that way:
        todoext.setDocPagePresenter(docPagePresenter)

        todoext.ProcessTodoPage(wikiWord) # then do the work


#========================================================================================

CFG_FILE="ToDoExtension.cfg"

import os, sys
import locale
import wx
import pprint
from re       import compile, match, search, IGNORECASE #added search, changed here !
from time     import strftime, strptime, mktime, localtime, time
from datetime import date, timedelta  #datetime
from string   import join
import inspect

# Get WikidPad's version. More infos in Consts.py
#   VERSION_TUPLE = ("wikidPad", 2, 0, 1, 4)
#   VERSION_STRING = "wikidPad 2.0alpha01_04"
try:
    from WikidPadStarter import VERSION_TUPLE, VERSION_STRING
    (vbr,vmaj,vmin,vsam,vpat) = VERSION_TUPLE
    wpversion = "%d.%d" % (vmaj,vmin)
    wpversionstr = VERSION_STRING
except:
    # Attention: This determination of the version is not foolproof!
    # Coded this way to remain compatible back to WikidPad 1.8
    from WikidPadStarter import VERSION_STRING        # e.g. "wikidPad 1.8beta6", "wikidPad 2.0alpha01_03"
    wpversionstr = VERSION_STRING
    wpversion = VERSION_STRING[9:12]                  # e.g. "1.8"

#--- some functions ----------------------------------------------------------------------
#
# from http://www.merlyn.demon.co.uk/weekcalc.htm  (as of 2006), fixed in 2010
#
def LeapYr(y):
    if (y % 4):
        return False;
    if (y % 100):
        return True
    return not(y % 400)

def Jan1DoWG(y):
    y = y - 1
    return (int(1.25 * y) - int(y / 100) + int(y / 400) + 1) % 7

def DoYLtoMonth(J,L):
    if (J < 32):
       return 1
    return 1 + int((303 + 5 * (J - 59 - L)) / 153)

def DoYMLtoDate(J,M,L):
    if (M < 3):
        return J - (31 * (M - 1))
    return J - (int((153 * M - 2) / 5) - 32 + L)

def RevWN(Y,W,D):
    Yr = Y
    Leap = LeapYr(Yr)

    X = (Jan1DoWG(Yr) + 2) % 7
    J = 7 * W + D - X - 4
    Mth = int(DoYLtoMonth(J, Leap))
    Dte = int(DoYMLtoDate(J, Mth, Leap))

    if (Mth == 13):
        Yr = Yr + 1
        Mth = 1
    if (Dte < 1):
        Yr = Yr - 1
        Mth = 12
        Dte = Dte + 31
    return [Yr, Mth, Dte]

#------------

def LastDayOfMonth(y, m):
    nextm = date(y, m, 1) + timedelta(days=31)
    thatlast = date(nextm.year, nextm.month, 1) - timedelta(days=1)
    return thatlast.day

def easter(year):
    """
    Calculates the date of Easter Sunday 
    According to Anonymous Gregorian algorithm
    from http://en.wikipedia.org/wiki/Computus#Anonymous_Gregorian_algorithm
    """
    # Expression				Y = 1961 	Y = 2009
    y = year
    # a = Y mod 19				a = 4 	a = 14
    a = y % 19
    # b = floor (Y / 100)			b = 19 	b = 20
    b = y/100
    # c = Y mod 100				c = 61 	c = 9
    c = y % 100
    # d = floor (b / 4)				d = 4 	d = 5
    d = b/4
    # e = b mod 4				e = 3 	e = 0
    e = b % 4
    # f = floor ((b + 8) / 25) 			f = 1 	f = 1
    f = (b+8)/25
    # g = floor ((b - f + 1) / 3)		g = 6   g = 6
    g = (b-f+1)/3
    # h = (19a + b - d - g + 15) mod 30		h = 10  h = 20
    h = (19*a+b-d-g+15) % 30
    # i = floor (c / 4)				i = 15 	i = 2
    i = c/4
    # k = c mod 4				k = 1 	k = 1
    k = c % 4
    # L = (32 + 2e + 2i - h - k) mod 7		L = 1   L = 1
    L = (32 + 2*e + 2*i - h - k) % 7
    # m = floor ((a + 11h + 22L) / 451)		m = 0 	m = 0
    m = (a +11*h + 22*L)/451
    # month = floor ((h + L - 7m + 114) / 31)	month = 4 (April)   month = 4 (April)
    month = (h + L - 7*m + 114)/31
    # day = ((h + L - 7m + 114) mod 31) + 1	day = 2 day = 12
    day = ((h + L - 7*m + 114) % 31) + 1
    return (year,month,day)
    

#-----------------------------------------------------------------------------------------

class Todo:
    def __init__(self, wikidpad):
        self.wikidpad = wikidpad
        #print "=== wikidpad            =", wikidpad

        self.config_set_defaults()

        self.cfg_file = os.path.join(os.path.dirname(os.path.realpath(os.sys.argv[0])), "user_extensions", CFG_FILE)
        #todo: easier? perhaps the current path is stored somewhere already?!

        if os.path.exists(self.cfg_file):
            try:
                cfg = open(self.cfg_file)
                self.config_read(cfg.readlines(), self.cfg_file, globalCfg=True)
                cfg.close()
            except:
                pass

        if self.cfg["isConfigPageActive"]:
            if wpversion < "1.9":
                if self.wikidpad.getWikiData().isDefinedWikiWord(self.cfg["configPage"]):
                    config = self.wikidpad.getWikiData().getContent(self.cfg["configPage"]).split("\n")
                    self.config_read(config, self.cfg["configPage"], globalCfg=False)
            elif wpversion < "2.0":
                if self.wikidpad.getWikiDocument().isDefinedWikiWord(self.cfg["configPage"]):
                    config = self.wikidpad.getWikiDocument().getWikiData().getContent(self.cfg["configPage"]).split("\n")
                    self.config_read(config, self.cfg["configPage"], globalCfg=False)
            else:
                if self.wikidpad.getWikiDocument().isDefinedWikiLink(self.cfg["configPage"]):
                    config = self.wikidpad.getWikiDocument().getWikiData().getContent(self.cfg["configPage"]).split("\n")
                    self.config_read(config, self.cfg["configPage"], globalCfg=False)

        if self.cfg["debug"]:
            pprint.pprint(self.cfg)


    def config_read(self, config, cfg_file, globalCfg=False):

        #print "*v*"
        #print "cfg_file=", cfg_file
        #pprint.pprint(config)
        #print "*^*"
        conf_count = 0

        for cfgline in config:    # todo: multi-line entries

            #print "cfgline =", cfgline
            cfgline = cfgline.strip()

            if cfgline.startswith("+"): continue   # skip header line(s)
            if cfgline.startswith("#"): continue   # skip comments                #todo: improve!
            if cfgline.startswith(";"): continue   # skip semicolon comments      #todo: improve!
            if cfgline == "": continue             # skip empty lines             #todo: improve!

            if cfgline.startswith("self."):        # check for old/invalid entries  (e.g. self.tags)
                self.wikidpad.displayMessage("Warning!", "Old syntax in configuration '" + cfg_file + "'\n\nRemove the 'self.' from " + cfgline[0:15] + "...")
                cfgline = cfgline[5:]

            #print "cfgline =", cfgline

            if cfgline.count("=") == 0:
                continue

            cfgentry = cfgline[0 : cfgline.index("=")].strip()   # todo: more robust!
            cfgvalue = cfgline[cfgline.index("=")+1:].strip()    # todo: more robust!

            #if cfgvalue.count("#") > 0:   #todo: that is not reliable because of possible ' in string value!
            #    cfgvalue = cfgvalue[0:cfgvalue.index("#")].strip()

            #print "cfgentry = cfgvalue >>%s=%s<< " %(cfgentry, cfgvalue)

            if not globalCfg:
                if cfgentry in ['isConfigPageActive', 'configPage']:
                    continue

            if not self.cfg.has_key(cfgentry):     # check for unknown entries
                self.wikidpad.displayMessage("Warning!", "Error: Unknown entry in configuration '" + cfg_file + "'\n\n" + cfgentry + " ignored.")
                continue

            if cfgentry == "predefinedTags":   # is usually multiline...
                self.wikidpad.displayMessage("Problem!", "Multiline config entries are not yet implemented\nin '" + cfg_file + "'\n\n" + cfgentry + " = " + cfgvalue[0:10] + "...\n\nRest of configuration ignored!")
                break

            if cfgvalue.startswith("[") and not cfgvalue.endswith("]"):
                self.wikidpad.displayMessage("Problem!", "Multiline config entries are not yet implemented\nin '" + cfg_file + "'\n\n" + cfgentry + " = " + cfgvalue[0:10] + "...\n\nRest of configuration ignored!")
                break

            try:
                exec "cfgvalue_tmp=" + cfgvalue         #todo: choose a more secure way in favour of exec! And even more error handling
                self.cfg[cfgentry] = cfgvalue_tmp
                conf_count += 1
            except:
                self.wikidpad.displayMessage("Error!", "Syntax error in configuration:\n\n" + cfg_file + "\n\n" + cfgline + "\n\n" + str(sys.exc_info()[1]))


        # make sure that UNTAGGED is always there
        if [t[0] for t in self.cfg["predefinedTags"]].count(u'UNTAGGED') == 0:
            self.cfg["predefinedTags"].insert(0, (u'UNTAGGED',     '++++ Not yet tagged') )

        #print self.cfg["placemark"]
        #print type(self.cfg["placemark"])

        return conf_count


    def config_set_defaults(self):
        """
        Default configuration values
        ----------------------------

        ATTENTION:
        Don't change them here since they will be overwritten by the next update of this program.
        Instead maintain your own local configuration in file "user_extensions/ToDoExtension.cfg".

        Simply set config values in that file using the normal Python syntax: 'name = value'
        Please note: Multiline entries aren't supported yet. So 'predefinedTags' can't be changed that way.
        """

        #------------------------------------------------------------------------------------------

        self.cfgDefaults = [

            ('debug', False, """Print out some debugging info on the console"""),

            ('configPage', 'ToDoConfiguration',  """Name of the optional wiki page for wiki-local configuration"""),
            ('isConfigPageActive', True, """Activation switch for 'configPage'"""),
                                                      # (Note: these two can't be changed on this very wiki page!)

            ('predefinedTags', [
                      (u'UNTAGGED',     '++++ Not yet tagged'),    # tag 'UNTAGGED' is MANDANTORY. Don't touch!
                      (u'High',         '+++  HIGH!'),
                      (u'Next',         '++++ Next Actions'),
                      (u'ThisWeek',     '++++ This Week'),
                      (u'SomeDay',      '++++ SomeDay / Maybe'),
                      (u'TimeToTime',   '++++ From time to time'),
                      (u'Low',          '++++ Tagged as LOW'),
                      (u'VeryLow',      '++++ Tagged as Very LOW'),
                  ], """predefinedTags contains (Tag, TagHeader).
                        TagHeaders are the descriptive headings that will be shown for each category.
                        Tag 'UNTAGGED' is a special one (mandantory!) to collect the untagged todo's"""),

            ('onlyRealTodos', True, """True = ignore the todos like 'done', 'wait', 'question' etc.
                                       False = all from wikidPads todo-like category"""),

            ('ignoreDones', False, """False = treat 'done' like 'wait', 'question' etc.
                                      True = don't show the dones, except on the filter page "ToDoDone"
                                      (only effective if 'onlyRealTodos' is False).. """),
                                      
            ('realDatesLast', False, """ False: sorting is: untagged - known tags - dates - newly tagged  (the default)
                                         True:  sorting is: untagged - known tags - newly tagged - dates  (test for Jouni)"""),

            ('realDatesSeparate', False, """False: all todos in one page: ToDo
                                         True:  todos with real dates on a page 'ToDoCalendar', all others on the normal page 'ToDo'"""),

            ('filterTodos', 1, """0 = no filtering: ignore characters after 'ToDo'
                                  1 = case insensitive filter string after 'ToDo', only in todo's name
                                  2 = case insensitive filter string after 'ToDo', in complete todo entry (line)
                                  3 = case insensitive filter string after 'ToDo', in complete todo entry (line) OR in page name/title"""),

            ('sortTagsCaseInsensitive', True, ''),

            # Please note: Changing this placemark may double the todo page on the first call
            #              if there was generated content with the old placemark before
            ('placemark', '++++ ________auto-collected todos________', """Fixed part of the divider between manual edited text and automatically generated todos"""),

            # Be very careful when modifying these three values! All three MUST match!
            ('todoTimestampFormat', '(@ %s)', """String after placemark with timestamp of this todo generation. %s will be replaced by date..."""),
            ('todoTimestampDateFormat', '%Y-%m-%d %H:%M', """Format of timestamp used after placemark"""),
            ('todoTimestampRegex', '\(@ ([0-9]{4}-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9])\)', """MUST match todoTimestampDateFormat and todoTimestampFormat! And the date+time itself MUST be grouped!"""),

            ('underline', '_______', ''),
            ('spacerline', '----', ''),
            ('bullet', '   * ', ''),

            ('colorStringNormal', '[color: black]', """Colors for normal ToDo entries in the tree"""),
            ('colorStringNext', '[color: orange]', """Colors for 'next' ToDo entries in the tree"""),
            ('colorStringToday', '[color: red]', """Colors for 'todays' ToDo entries in the tree"""),
            ('colorStringMissed', '[color: magenta]', """Colors for 'missed' ToDo entries in the tree"""),

            ('notagHeading', '++++ ', """Heading for unknown tagged entries"""),
            ('dateHeading', '++++ ', """Heading for date entries far away (distance see below)"""),
            ('dateHeadingX', '+++  ', """Heading for date entries in near future or missed in past"""),

            ('missedString', ' ___ (+GONE+)', """Additional info"""),
            ('nowString', ' ___ !!! TODAY !!!', """Additional info"""),

            ('outDateFormat', '', """If this is set = '' the local date format is used, else set it to '%m/%d/%Y', '%d.%m.%Y' or '%Y-%m-%d' for example.
                                     :Note: On Windows the determination of the locale doesn't work yet. So you have to set it manually here.
                                     :      Or it defaults to '%Y-%m-%d'.
                                     Please use only %m, %d  for month and day  and %y, %Y for 2-/4-digit year
                                     (Otherwise the optional separation of date driven todos may fail.)"""),

            ('showWeekday', True, """show weekday after dates"""),
            ('weekdayFormat', ' (%s,', """%s is replaced by the weekday as in the config value 'weekdays',
                                          Together with the optional week number (see below) it gives e.g. ' (Fri, W42)'"""),

            ('weekdays', ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], """ Names for the weekdays
                             ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']        # English, 2 chars
                             ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']        # German
                             ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] # English, 3 chars"""),

            ('showWeeknumber', True, """Show the weeknumber after dates"""),
            ('weeknumberFormat', ' W%02d)', """ %02d is replaced by the weeknumber (2 digits with leading 0-padded)"""),

            ('dayrange', 7, """Date entries in that range are marked as 'more important' than the ones in 'far' future"""),

            ('deleteAttributes', 1, """0 = let possible attributes [...:...] in a todo entry alone
                                       1 = delete possible attributes [...:...] from a todo entry to avoid multiple attribute errors"""),

            ('extendedLinks', False, """This feature works, but doesn't look nice, really! So better let it disabled...
                                        True  = create links with search capability on target page (only working in editor window!?)
                                        False = create normal links"""),

            ('iconString', '[icon: spanner]', """Set the icon of the todo list"""),

            ('setBookmark', True,  """Set the ToDo page [bookmarked=true] so it is listed in the Bookmark popup (Shift-Ctrl-B)"""),

            ('showInfoPopup', True, """Show summary info popup about todos for today / missed ones"""),

            ('showInfoOnPage', True,"""Show summary info about todos for today / missed ones on todo page"""),

            ('pgInfoFrame', '<<pre\n%s\n>>',"""Frame around the summary info about todos for today / missed ones on todo page. %s will be replaced by the text."""),

            ('pgInfoPrefix', ' ',"""Prefix for every entry of the summary info about todos for today / missed ones on todo page"""),

            ('infoPopupTimeDelta',  2, """Number of minutes where no new popup is shown after last visit of ToDo page"""),

            ('showVersion', False, """Show version of WikidPad and extension (mainly for debugging)"""),

            ('showConfigLink', True, """Show a link to the configuration page  (only if 'isConfigPageActive' == True)"""),

            ]

        self.cfg = {}
        self.cfgDoc = {}

        for ce in self.cfgDefaults:
            self.cfg[ce[0]] = ce[1]
            self.cfgDoc[ce[0]] = join(["# " + ce1.strip().lstrip(":") for ce1 in ce[2].split("\n")], "\n")

        #pprint.pprint(self.cfg)
        #pprint.pprint(self.cfgDoc)

    def delAttribs(self, s):

        sattr = compile("\[[^:]+? *: *[^:]+?\]")
        result = sattr.search(s)
        while result:
            s = s[0:result.start()] + s[result.end():]
            result = sattr.search(s)
        return s


    def setDocPagePresenter(self, docPagePresenter):    # update the docPagePresenter for this run
        #print "=== setDocPagePresenter =", docPagePresenter
        self.wikidpad = docPagePresenter


    def ProcessTodoPage(self, wikiWord):

        global wpversion

        missedTodos      = 0
        todosForToday    = 0
        todosForNextDays = 0

        colorStringFlag  = 1     # set color string per default, checked later below

        myNow     = strftime(self.cfg["todoTimestampDateFormat"], localtime(time()))
        myToday   = date.isoformat(date.today())   # strftime("%Y-%m-%d", localtime(time()))   # => YYYY-MM-DD
        thismonth = int(myToday[5:7])
        thisday   = int(myToday[8:10])
        #(xxthisyear,thismonth,thisday,xxthishour,xxthisminute,xxthisecond,xxthiswday,xxthisdoy,xxthisdst) = localtime(time())  # xx* not used yet
        (thisyear, thisweek, thiswday) = date.today().isocalendar()     # Note: week and weekday are ISO ones (starting with "01", Monday=1=First day of week)

        warndate  = strftime("%Y-%m-%d", localtime(time() + self.cfg["dayrange"]*24*60*60))

        if self.cfg["outDateFormat"] == "":
            try:
                locale.setlocale(locale.LC_ALL, '')
                self.cfg["outDateFormat"] = locale.nl_langinfo(locale.D_FMT)
            except:
                self.cfg["outDateFormat"] = "%Y-%m-%d"
                
        ''' this definition was moved to here from below, changed here ! '''
        dateChecks = [
                       ( compile("[0-9]{4}-[0-1][0-9]-[0-3][0-9]$"),    "yyyy-mm-dd" ),  # specific date; ISO
                       ( compile("[0-1][0-9]/[0-3][0-9]/[0-9]{4}$"),    "mm/dd/yyyy" ),  # specific date; US
                       ( compile("[0-3][0-9].[0-1][0-9].[0-9]{4}$"),    "dd.mm.yyyy" ),  # specific date; Germany etc.
                       ( compile("[0-9]{4}-W[0-9]{2}-[0-7]$"),          "yyyy-Wnn-d" ),  # on given DayOfWeek in week nn; "d" is Mon(1)-Sun(7)
                       ( compile("[0-9]{4}-W[0-9]{2}$"),                "yyyy-Wnn" ),    # complete week nn of year yyyy
                       ( compile("\*-W[0-9]{2}$"),                      "*-Wnn" ),       # complete week nn; every year
                       ( compile("CW[0-9]{2}$"),                        "CWnn" ),        #   same as above: Calendar Week.  todo: is "CW" the correct name in English?
                       ( compile("KW[0-9]{2}$"),                        "KWnn" ),        #   same as above: German: Kalender-Woche
                       ( compile("[0-9]{4}-[0-1][0-9]-\*$"),            "yyyy-mm-*" ),   # complete month mm (every day) of year yyyy
                       ( compile("\*-[0-1][0-9]-\*$"),                  "*-mm-*" ),      # complete month mm (every day); every year
                       ( compile("\*-W\*-[0-7]$"),                      "*-W*-d" ),      # on given DayOfWeek in every week; "d" is Mon(1)-Sun(7)
                       ( compile("\*-[0-1][0-9]-[0-3][0-9]$"),          "*-mm-dd" ),     # every dd'th day of month mm
                       ( compile("\*-\*-[0-3][0-9]$"),                  "*-*-dd" ),      # every dd'th day; every month
                       ( compile("\*-\*-\*$"),                          "*-*-*" ),       # every day
                       ( compile("\*-[0-1][0-9]-[0-3][0-9][-+][0-7]$"), "*-mm-dd+d" ),   # every DayOfWeek before(-)/after(+) dd'th day of month mm
                       ( compile("\*-\*-[0-3][0-9][-+][0-7]$"),         "*-*-dd+d" ),    # every DayOfWeek before(-)/after(+) dd'th day every month
                       ( compile("\*-E[-+][0-9]{3}$"),                  "*-E+ddd" )      # Easter +- ddd days
                       #( compile("[0-9]{4}-[0-1][0-9]-[0-3][0-9]([-_][0-9]{2}[-.][0-9]{2})?$"),    "yyyy-mm-dd_hh-MM" ),  # specific date; ISO  Optional time????  TODO: how to display? TODO: implement that really? Better not since it is going to be too complicated!
                     ]

        if wpversion < "1.9":
            todosFull = self.wikidpad.wikiData.getTodos()
            editor    = self.wikidpad.getActiveEditor()
        elif wpversion < "2.1":
            todosFull = self.wikidpad.getMainControl().wikiData.getTodos()
            editor    = self.wikidpad.getSubControl("textedit")
        else:
            todosFullN = self.wikidpad.getMainControl().wikiData.getTodos()
            
            ''' This part os new, changed here'''
            for index,todo in enumerate(todosFullN):
                if match("\d{4}-\d{2}-\d{2}",todo[0]) and not [True for datecheck in dateChecks if search(datecheck[0],todo[1])]:
                    todosFullN[index] = (todo[0], todo[1]+"."+todo[0], todo[2])
            ''' until here...'''
            
            todosFull = [ (t[0], t[1] + ":" + t[2].strip()) for t in todosFullN ]
            editor    = self.wikidpad.getSubControl("textedit")
            

        if self.cfg["debug"]:
            print "todosFull=",
            pprint.pprint(todosFull)


        # to be able to use langHelper.isCcWikiWord()
        if wpversion <= "1.9":
            langHelper = self.wikidpad.getFormatting()
        else:
            # Retrieve internal name of current wiki language
            wikiLang = self.wikidpad.getWikiDocument().getWikiDefaultWikiLanguage()
            # Get language helper (an instance of WikidPadParser._TheHelper)
            langHelper = wx.GetApp().createWikiLanguageHelper(wikiLang)

        srchstr = wikiWord[4:]

        if wikiWord == self.cfg["configPage"]:
            if self.cfg["isConfigPageActive"]:
                #self.wikidpad.saveCurrentDocPage(force = True)
                self.wikidpad.displayMessage("Info", "Please note: \nThis configuration page is evaluated on WikidPad startup\nand/or after closing and reopening(!) this page after changes!\n\nSide effect: The configuration file\n ...%s \nis re-read first as well." % self.cfg_file[-50:])

                # First reset the defaults and then re-read the global configuration file
                self.config_set_defaults()
                if os.path.exists(self.cfg_file):
                    try:
                        cfg = open(self.cfg_file)
                        self.config_read(cfg.readlines(), self.cfg_file, globalCfg=False)
                        cfg.close()
                    except:
                        pass

                conf_count = 0

                # then evaluate the local configuration page
                if wpversion < "1.9":
                    if self.wikidpad.getWikiData().isDefinedWikiWord(self.cfg["configPage"]):
                        config = self.wikidpad.getWikiData().getContent(self.cfg["configPage"]).split("\n")
                        conf_count = self.config_read(config, self.cfg["configPage"], globalCfg=False)
                elif wpversion < "2.0":
                    if self.wikidpad.getWikiDocument().isDefinedWikiWord(self.cfg["configPage"]):
                        config = self.wikidpad.getWikiDocument().getWikiData().getContent(self.cfg["configPage"]).split("\n")
                        conf_count = self.config_read(config, self.cfg["configPage"], globalCfg=False)
                else:
                    if self.wikidpad.getWikiDocument().isDefinedWikiLink(self.cfg["configPage"]):
                        config = self.wikidpad.getWikiDocument().getWikiData().getContent(self.cfg["configPage"]).split("\n")
                        conf_count = self.config_read(config, self.cfg["configPage"], globalCfg=False)

                if conf_count == 0:
                    rtn = self.wikidpad.stdDialog("yn", "Info", "There are no (active) configuration items on this page.\nShould it be filled with the current values?")
                    #print "rtn=", rtn

                    if rtn == None:
                        self.wikidpad.displayMessage("Problem", "Please note: \n\nDue to a bug in WikidPad up to 1.9rc03 it isn't possible to read your choice.\nSo it defaults to 'yes' here.\n\nYou may want to have a look at\nhttp://groups-beta.google.com/group/wikidpad-devel/t/b3b6c2b2b03a88c7 ")
                        rtn = "yes"

                    if rtn == "yes":
                        editor.GotoPos(editor.GetLength())          # goto end of page
                        editor.AddText("\n\n")
                        oldpos= editor.GetCurrentPos()
                        editor.AddText("# The config values on this page are local to this wiki. (There are a few more not to be set here.)\n")
                        editor.AddText("# They take precedence over the default ones from the source code and the ones from the configuration file 'user_extensions\%s'\n" % (CFG_FILE))
                        editor.AddText("# Tip: You should only uncomment (remove leading semicolon) configuration values you want to have changed here.\n\n")

                        for ciEntry in self.cfgDefaults:
                            ci = ciEntry[0]
                            if ci in ['predefinedTags', 'isConfigPageActive', 'configPage']:
                                continue
                            if ci == 'showConfigPage' and not self.cfg['isConfigPageActive']:
                                continue
                            editor.AddText("# -- %s --\n" % ci)
                            if self.cfgDoc[ci] != '':
                                editor.AddText(self.cfgDoc[ci] + "\n")
                            editor.AddText("; %s = %s" % (ci, repr(self.cfg[ci]).replace("\\\\", "\\")))
                            editor.AddText("\n\n")
                        editor.GotoPos(oldpos)          # goto begin of insertion again

                return


        isCalendar = False
        if srchstr.startswith("Calendar"):             #todo: or better check for equality?
            srchstr = srchstr[8:]          # remove that "Calendar" from srchstr to get the real one
            isCalendar = True

        srchstr = srchstr.strip(" _")      # remove possible leading/trailing spaces and underscores from srchstr
        
        srchstr_4re = srchstr.replace("_","|")
        srchstr_set = set(srchstr.upper().split("_"))
        #print "seachr-set=", srchstr_set
        myre = compile(srchstr_4re, IGNORECASE)
        
        # optionally filter the todos
        if self.cfg["filterTodos"] == 0:
            todos = [todo for todo in todosFull]                                            # without checking srchstr
        elif self.cfg["filterTodos"] == 1:
            #todos = [todo for todo in todosFull if (srchstr.upper() in todo[1][0:todo[1].find(":")].upper()) ]   # case insensitive search in todo's name
            todos = [todo for todo in todosFull if (srchstr_set.issubset(set(myre.findall(todo[1][0:todo[1].find(":")].upper() )))) ]   # case insensitive search in todo's name
            #todos = []
            #for todo in todosFull:
            #   s1 = set(myre.findall(todo[1][0:todo[1].find(":")].upper() ))
            #   print s1
            #   if srchstr_set.issubset(s1):
            #       print "matched"
            #       todos.append(todo)
            #
            #print todos
            
        elif self.cfg["filterTodos"] == 2:
            #todos = [todo for todo in todosFull if (srchstr.upper() in todo[1].upper()) ]   # case insensitive in complete todo entry (the todo line)
            todos = [todo for todo in todosFull if (srchstr_set.issubset(set(myre.findall(todo[1].upper() )))) ]   # case insensitive in complete todo entry (the todo line)
            #todos = []
            #for todo in todosFull:
            #   s1 = set(myre.findall(todo[1].upper() ))
            #   print s1
            #   if srchstr_set.issubset(s1):
            #       print "matched"
            #       todos.append(todo)
            #
            #print todos
            
        elif self.cfg["filterTodos"] == 3:
            todos = [todo for todo in todosFull if (srchstr_set.issubset(set(myre.findall("_".join(todo[0:2]).upper() )))) ]        # case insensitive in complete todo entry (the todo line) and in page name/title    
            #todos = []
            #for todo in todosFull:
            #   s1 = set(myre.findall("_".join(todo[0:2]).upper() ))
            #   print s1
            #   if srchstr_set.issubset(s1):
            #       print "matched"
            #       todos.append(todo)
            #
            #print todos


        if (self.cfg["filterTodos"] > 0) and (srchstr.upper().startswith("DONE")):
            pass
        else:
            if self.cfg["onlyRealTodos"]:
                todos = [todo for todo in todos if todo[1][0:4] == "todo" ]
            else:
               if self.cfg["ignoreDones"]:
                  todos = [todo for todo in todos if todo[1][0:4] != "done" ]

        # prepare text page to insert the collected todos after placemark

        nowstamp = self.cfg["todoTimestampFormat"] % (myNow)  # e.g. "(@ 2007-10-28 22:09)"
        tscheck = compile(self.cfg["todoTimestampRegex"])

        st = editor.FindText(0, editor.GetLength(), self.cfg["placemark"], 0)

        if st != -1:                                    # if placemark found
            # select text to be replaced with new todos, beginning just after placemark, before timestamp
            editor.SetSelection(st + len(self.cfg["placemark"]), editor.GetLength())

            sel = editor.GetSelectedText()[0:len(nowstamp)+1]   # get the timestamp from just after the placemark
            result = tscheck.search(sel)
            if result:
                lastCreation = mktime(strptime(result.groups()[0], self.cfg["todoTimestampDateFormat"]))   #todo: easier!?!?
            else:
                lastCreation = 0.0

            editor.ReplaceSelection(" %s %s" % (nowstamp, self.cfg["underline"]))    # add the new timestamp

            if srchstr != "" and self.cfg["filterTodos"]:                       # optionally add filter info
                editor.AddText(" (filter: '%s (%s)')" % (srchstr, self.cfg["filterTodos"]))
            editor.AddText("\n\n")

        else:                                           # if no placemark found
            editor.GotoPos(editor.GetLength())          #    add the placemark and todos at end of page
            lastCreation = 0.0
            editor.AddText("\n\n%s %s %s" % (self.cfg["placemark"], nowstamp, self.cfg["underline"]))

            if srchstr != "" and self.cfg["filterTodos"]:
                editor.AddText(" (filter: '%s (%s)')" % (srchstr, self.cfg["filterTodos"]))
            editor.AddText("\n\n\n")

        st = editor.FindText(0, editor.GetLength(), "[icon:", 0)
        if st != -1:                                        # if there already is an icon:string:
            self.cfg["iconString"] = ""                     #   don't add our own

        st = editor.FindText(0, editor.GetLength(), "[color:", 0)
        if st != -1:                                        # if there already is an color:string:
            colorStringFlag = 0                             #   don't add our own


        self.tags = [ t + ("","") for t in self.cfg["predefinedTags"] ]

        # determine tags

        checkTags = [tag[0] for tag in self.tags]           # first part

        if self.cfg["debug"]:
            print "line number", inspect.currentframe().f_back.f_lineno
            print "checkTags="
            pprint.pprint(checkTags)

        newtags = []

        for todo in todos:                           ## [(u'pagename', u'todo.tag1.tag2: text')...
            allTodo = todo[1].split(":")             ## [u'todo.tag1.tag2', u' text'] ...

            words = allTodo[0].split(".",1)          ## [u'todo', u'tag1.tag2'] ...
                                                     ## (keep additionally dotted parts together)! o.k.?

            for word in words[1:]:                   ## u'tag1.tag2'
                newtags.append( (word) )

        newtags = sorted(set(newtags))

        if self.cfg["debug"]:
            print "newtags="
            pprint.pprint(newtags)


        #---------------------------------------------------



        newtagsdata = []

        # check all tags for being a date of special format

        for newtag in newtags:

            for dateCheck in dateChecks:            # any match?
                result = dateCheck[0].search(newtag)
                if result:
                    break

            if not result:                          # not a date like the above, perhaps no date at all
                #newtagLast = newtag.split(".")[-1]
                if newtag.find(".") > -1:
                    newtagsdata.append( (newtag, newtag, 0, newtag[0:newtag.rfind(".")]) )
                else:
                    newtagsdata.append( (newtag, newtag, 0, "") )   ##?? or newtag?

            else:

                t = newtag[0:-len(dateCheck[1])]

                if dateCheck[1] == "yyyy-mm-dd":
                    y = result.group()[0:4]
                    m = result.group()[5:7]
                    d = result.group()[8:10]

                elif dateCheck[1] == "mm/dd/yyyy":
                    m = result.group()[0:2]
                    d = result.group()[3:5]
                    y = result.group()[6:10]

                elif dateCheck[1] == "dd.mm.yyyy":
                    d = result.group()[0:2]
                    m = result.group()[3:5]
                    y = result.group()[6:10]

                elif dateCheck[1] == "yyyy-Wnn-d":
                    y = int(result.group()[0:4])
                    w = int(result.group()[6:8])
                    wday = int(result.group()[9:10])
                    y,m,d = RevWN(y, w, wday)                   # eval year, month, day from week [and day_of_week]

                elif dateCheck[1] == "yyyy-Wnn":
                    y = int(result.group()[0:4])
                    w = int(result.group()[6:8])
                    if (y == thisyear) and (w == thisweek):
                        wday = thiswday   # current weekday for current week
                    else:
                        wday = 1          # Monday for future weeks
                        # And last weekday of that (ISO-)week: Sunday  for recent (gone) weeks
                        if y < thisyear or (y == thisyear and w < thisweek):
                            wday = 7
                    y,m,d = RevWN(y, w, wday)

                elif dateCheck[1] == "KWnn" or dateCheck[1] == "CWnn":
                    w = int(result.group()[2:4])
                    wday = 1    # Monday for recent and future weeks
                    y = thisyear
                    if w == thisweek:
                        wday = thiswday  # current weekday for current week
                    else:
                        if w < thisweek:
                            y = y + 1
                    y,m,d = RevWN(y, w, wday)

                elif dateCheck[1] == "*-Wnn":
                    w = int(result.group()[3:5])
                    wday = 1    # Monday for recent and future weeks
                    y = thisyear
                    if w == thisweek:
                        wday = thiswday  # current weekday for current week
                    else:
                        if w < thisweek:
                            y = y + 1
                    y,m,d = RevWN(y, w, wday)

                elif dateCheck[1] ==  "*-W*-d":
                    dw = int(result.group()[5:6])
                    y,m,d = RevWN(thisyear, thisweek, dw)                   # eval year, month, day from week  [and day]
                    if dw < thiswday:
                        if m < 12  or (m == 12 and d < 25):
                            y,m,d = RevWN(thisyear, thisweek+1, dw)
                        else:
                            y,m,d = RevWN(thisyear+1, 1, dw)

                elif dateCheck[1] == "*-mm-dd":
                    y = thisyear
                    m = int(result.group()[2:4])
                    d = int(result.group()[5:7])
                    if m < thismonth  or (m == thismonth and d < thisday):
                        y = y + 1

                elif dateCheck[1] == "yyyy-mm-*":
                    y = int(result.group()[0:4])
                    m = int(result.group()[5:7])

                    d = 1    # for future months
                    if (y == thisyear) and (m == thismonth):
                        d = thisday  # current day for current month
                    else:
                        if y < thisyear or (y == thisyear and m < thismonth):  # for recent months
                            d = LastDayOfMonth(y, m)

                elif dateCheck[1] == "*-mm-*":
                    y = thisyear
                    m = int(result.group()[2:4])

                    d = 1    # for recent and future months
                    if m == thismonth:
                        d = thisday  # current day for current month
                    else:
                        if m < thismonth:
                            y = y + 1

                elif dateCheck[1] == "*-mm-dd+d":
                    y = thisyear
                    m = int(result.group()[2:4])
                    d = int(result.group()[5:7])
                    direction = result.group()[7:8]
                    dwShould = int(result.group()[8:9])

                    date_error = False
                    try:
                        base = date(y,m,d)
                    except ValueError:
                        if d >= 29 and d <= 31:             # silently assume last day of month
                            d = LastDayOfMonth(y,m)
                        else:
                            date_error = True
                            d = thisday
                            m = thismonth
                        base = date(y,m,d)

                    if date_error:
                        self.wikidpad.displayMessage("Error!", "Todo entry with invalid date: %s\n\nDate is set to 'TODAY' temporarily.\n\nPlease check." % (newtag))
                    else:
                        dwIs = base.isoweekday()  # Mon=1 and Sun=7

                        ddiff = dwShould - dwIs
                        if direction == '+' and ddiff < 0:
                            ddiff += 7
                        elif direction == '-' and ddiff > 0:
                            ddiff -= 7
                        tagday = base + timedelta(days = ddiff)

                        if tagday < date.today() or (tagday == date.today() and d == thisday):
                            try:
                                base = date(y + 1, m, d)
                            except ValueError:
                                if d >= 29 and d <= 31:             # silently assume last day of month
                                    d = LastDayOfMonth(y,m)
                                base = date(y + 1, m, d)

                            dwIs = base.isoweekday()  # Mon=1 and Sun=7

                            ddiff = dwShould - dwIs
                            if direction == '+' and ddiff < 0:
                                ddiff += 7
                            elif direction == '-' and ddiff > 0:
                                ddiff -= 7
                            tagday = base + timedelta(days = ddiff)

                        y = tagday.year
                        m = tagday.month
                        d = tagday.day

                elif dateCheck[1] == "*-*-dd+d":
                    y = thisyear
                    m = thismonth
                    d = int(result.group()[4:6])
                    direction = result.group()[6:7]
                    dwShould = int(result.group()[7:9])

                    date_error = False
                    try:
                        base = date(y,m,d)
                    except ValueError:
                        if d >= 29 and d <= 31:             # silently assume last day of month
                            d = LastDayOfMonth(y,m)
                        else:
                            date_error = True
                            d = thisday
                            d0 = d
                        base = date(y,m,d)

                    dwIs = base.isoweekday()  # Mon=1 and Sun=7

                    ddiff = dwShould - dwIs
                    if direction == '+' and ddiff < 0:
                        ddiff += 7
                    elif direction == '-' and ddiff > 0:
                        ddiff -= 7
                    tagday = base + timedelta(days = ddiff)

                    if tagday < date.today() or (tagday == date.today() and d == thisday):
                        #print "newtag=", newtag, "tagday=", tagday, d, m, y
                        m += 1
                        if m > 12:
                            m = 1
                            y += 1

                        try:
                            base = date(y, m, d)
                        except ValueError:
                            if d >= 29 and d <= 31:             # silently assume last day of month
                                d = LastDayOfMonth(y, m)
                            base = date(y, m, d)

                        dwIs = base.isoweekday()  # Mon=1 and Sun=7

                        ddiff = dwShould - dwIs
                        if direction == '+' and ddiff < 0:
                            ddiff += 7
                        elif direction == '-' and ddiff > 0:
                            ddiff -= 7
                        tagday = base + timedelta(days = ddiff)

                    y = tagday.year
                    m = tagday.month
                    d = tagday.day

                    if date_error:
                        self.wikidpad.displayMessage("Error!", "Todo entry with invalid date: %s\n\nDate is set to a valid one temporarily.\n\n(Based on %4d-%02d-%02d)\n\nPlease check." % (newtag,y,m,d0))

                elif dateCheck[1] == "*-*-dd":
                    y = thisyear
                    m = thismonth
                    d = int(result.group()[4:6])
                    if d < thisday:
                        m = m + 1
                        if m > 12:
                            m = 1
                            y = y + 1

                elif dateCheck[1] == "*-*-*":
                    y = thisyear
                    m = thismonth
                    d = thisday
                    
                elif dateCheck[1] ==  "*-E+ddd":
                    #import pdb; pdb.set_trace()
                    diffstr = newtag[3:7]
                    diffint = int(diffstr)
                    diff = timedelta(days=diffint)
                    t = newtag[0:-7]
 
                    y = thisyear   # and if date already gone: use next year ...
                    for yc in (0,1):
                        (ey,em,ed) = easter(y + yc)
                        tagday = date(ey,em,ed) + diff

                        y = tagday.year
                        m = tagday.month
                        d = tagday.day

                        if not (m < thismonth  or (m == thismonth and d < thisday)):
                            break
                            
 
                # check whether date is valid. If not: Show message and set to "today" for manual fixing
                try:
                    xnewdate = str(y) + "-" + str(m).zfill(2) + "-" + str(d).zfill(2)
                    xtest = strftime(self.cfg["outDateFormat"],strptime(xnewdate, "%Y-%m-%d"))
                    xyear,xweek,xwday = date.isocalendar(date(int(y), int(m), int(d)))
                except ValueError:
                    self.wikidpad.displayMessage("Error!", "Todo entry with invalid date: " + newtag +  "\n\nDate is set to 'TODAY' temporarily.\n\nPlease fix it manually and try again.")
                    y = thisyear
                    m = thismonth
                    d = thisday

                xnewdate = str(y) + "-" + str(m).zfill(2) + "-" + str(d).zfill(2)

                # with flag = 1 to mark as date entry
                newtagsdata.append( (xnewdate, newtag, 1, t[0:t.rfind(".")]) )    # todo: save date format for later display

        if self.cfg["debug"]:
            print "newtagsdata="
            pprint.pprint(newtagsdata)

        newtagsdata = sorted(set(newtagsdata))

        if self.cfg["debug"]:
            print "newtagsdata(unique)="
            pprint.pprint(newtagsdata)
            print "self.tags="
            pprint.pprint(self.tags)

        # ==> newtagsdata = [ ( "yyyy-mm-dd" , "some date string" , 1, "tag(s) before date")  # for date tags
        #                     ( tagstring    , tagstring          , 0, "n-1 tag(s)")          # for multiple tags
        #                     ( tagstring    , tagstring          , 0, "")                    # for simple tags

        #---------------------------------------------------

        # search for tags not in defined list and automatically add them in correct order

        #if realDatesSeparate:    # perhaps not necessary, but may reduce calculations below?
        #    if isCalendar:
        #        newtagsdata = [ t for t in sorted(newtagsdata) if t[2]==1 ]
        #    else:
        #        newtagsdata = [ t for t in sorted(newtagsdata) if t[2]==0 ]
        #else:


        newtagsdata_text = [ t for t in newtagsdata if t[2]==0 ]
        newtagsdata_date = sorted([ t for t in newtagsdata if t[2]==1 ])

        #todo: check if the order of tags is correct for sorting. Currently the last one has highest precedence.
        
        # pre-sort
        if self.cfg["sortTagsCaseInsensitive"]:
            mytuples = [(".".join(sorted(x[0].lower().split("."), reverse=True)), x) for x in newtagsdata_text]
        else:
            mytuples = [(".".join(sorted(x[0].split("."), reverse=True)), x) for x in newtagsdata_text]

        mytuples.sort()
        newtagsdata_text = [x[1] for x in mytuples]

        if self.cfg["realDatesLast"]:
            newtagsdata = newtagsdata_text[:]
            newtagsdata.extend(newtagsdata_date)
        else:
            newtagsdata = newtagsdata_date[:]
            newtagsdata.extend(newtagsdata_text)
            
        if self.cfg["debug"]:
            print "newtagsdata(sorted)="
            pprint.pprint(newtagsdata)
            print "checkTags="
            pprint.pprint(checkTags)

        for sortednewtag in newtagsdata:

            if self.cfg["debug"]:
                print "sortednewtag=",
                pprint.pprint(sortednewtag)

            if not sortednewtag[1] in checkTags:     # only if not already in tag list

                if self.cfg["debug"]:
                    print "... not in checkTags"

                if sortednewtag[2] == 0:             # if not a recognized date

                    newtagLast = sortednewtag[0].split(".")[-1]

                    if self.cfg["debug"]:
                        print "... not a recognized date"
                        print "newtagLast=", newtagLast

                    if newtagLast in checkTags:
                        tagidx = checkTags.index(newtagLast)

                        if self.cfg["debug"]:
                            print "is in checkTags", tagidx, self.tags[tagidx][1]
                            print "newtagLast=", newtagLast, tagidx, len(checkTags), checkTags

                        if tagidx < len(checkTags)-1:
                            while checkTags[tagidx+1].endswith("." + newtagLast):
                                tagidx += 1
                                if self.cfg["debug"]:
                                    print ">>>>>>>> checkTags[tagidx]=", checkTags[tagidx]
                                #if checkTags[tagidx] > newtagLast:    #todo:  what was that intended for??? Is already sorted...
                                #    if self.cfg["debug"]:
                                #        print ">>>>     break"
                                #    break

                        self.tags.insert(tagidx + 1, (sortednewtag[0], self.tags[tagidx][1], sortednewtag[1], "") )  # really fixed this way?
                        checkTags.insert(tagidx + 1, sortednewtag[1])

                        if self.cfg["debug"]:
                            print ">>>>>>>> checkTags=", checkTags
                    else:
                        self.tags.append( (sortednewtag[0], self.cfg["notagHeading"], sortednewtag[1], "") )
                        checkTags.append(sortednewtag[1])

                else:                                # if a date

                    if self.cfg["debug"]:
                        print "... it's a recognized date"

                    # "2007-10-19" ==> (2007, 42, 5) ==> "Friday Week42"
                    weekDay    = ""
                    weekNumber = ""

                    # validity of dates has been checked earlier. So there should be no problem here...
                    xDate = date(int(sortednewtag[0][0:4]), int(sortednewtag[0][5:7]), int(sortednewtag[0][8:10]))
                    xyear,xweek,xwday = date.isocalendar(xDate)
                    if self.cfg["showWeekday"]:     weekDay    = self.cfg["weekdayFormat"] % self.cfg["weekdays"][xwday-1]    # because ISO-day begins with 1
                    if self.cfg["showWeeknumber"]:  weekNumber = self.cfg["weeknumberFormat"] % xweek

                    outDate = strftime(self.cfg["outDateFormat"],strptime(sortednewtag[0], "%Y-%m-%d"))

                    if sortednewtag[0] <= warndate:
                        if sortednewtag[0] < myToday:
                            missedTodos += 1
                            self.tags.append( (sortednewtag[1], self.cfg["dateHeadingX"], outDate + weekDay + weekNumber + self.cfg["missedString"], sortednewtag[3] ) )
                        elif sortednewtag[0] == myToday:
                            todosForToday += 1
                            self.tags.append( (sortednewtag[1], self.cfg["dateHeadingX"], outDate + weekDay + weekNumber + self.cfg["nowString"], sortednewtag[3] ) )
                        else:
                            todosForNextDays += 1
                            n = (mktime(strptime(sortednewtag[0],"%Y-%m-%d")) - time()) / (60*60*24)
                            plural = ""
                            if n <= 1:
                                if int(n*24) > 1: plural = "s"
                                self.tags.append( (sortednewtag[1], self.cfg["dateHeadingX"], outDate + weekDay + weekNumber + " ___ " + str(int(n*24)) + " hour" + plural + " left", sortednewtag[3]) )
                            else:
                                if int(n) > 1: plural = "s"
                                self.tags.append( (sortednewtag[1], self.cfg["dateHeadingX"], outDate + weekDay + weekNumber + " ___ " + str(int(n)) + " day" + plural + " left", sortednewtag[3]) )
                    else:

                        self.tags.append( (sortednewtag[1], self.cfg["dateHeading"], outDate + weekDay + weekNumber, sortednewtag[3] ) )

                    checkTags.append(sortednewtag[1])

        # ==> self.tags = [ ( "some date string", "heading" , "YYYY-MM-DD ....", "tags before date-string")   # for new dates
        # ==> self.tags = [ ( "some string",      "heading" , "some string"    , "tags before last one")      # for other ones   ??

        # todo: check the last field of self.tags. Seems to be always empty. (In sortednewtag it's filled)
        if self.cfg["debug"]:
            print "checkTags="
            pprint.pprint(checkTags)
            print "self.tags="
            pprint.pprint(self.tags)
            print "sorted(todos)="
            pprint.pprint(sorted(todos))

        #---------------------------------------------------

        # iterate thru all tags now and insert them on page

        msgPop = ""
        msgPag = ""

        if self.cfg["showInfoPopup"]:
            if missedTodos:      msgPop  =   "%2d x missed todo.\n"              % missedTodos
            if todosForToday:    msgPop += "\n%2d x todo for today! \n"          % todosForToday
            if todosForNextDays: msgPop += "\n%2d x todo for the next %d days!"  % (todosForNextDays, self.cfg["dayrange"])

        if self.cfg["showInfoOnPage"]:
            if missedTodos:      msgPag  = self.cfg["pgInfoPrefix"] + " %2d x missed todo.\n"              % missedTodos
            if todosForToday:    msgPag += self.cfg["pgInfoPrefix"] + " %2d x todo for today! \n"          % todosForToday
            if todosForNextDays: msgPag += self.cfg["pgInfoPrefix"] + " %2d x todo for the next %d days!"  % (todosForNextDays, self.cfg["dayrange"])

        lasttag1 = u""
        lasttag2 = u""
        newtext  = u""

        if self.cfg["showInfoOnPage"] and msgPag != "":
            if self.cfg["pgInfoFrame"].count("%s") == 1:
                newtext = self.cfg["pgInfoFrame"] % msgPag
            else:
                newtext = msgPag

            newtext += "\n"


        wroteHeader = False
        tagAdded    = False

        #dcheck = compile("[0-9]{4}-[0-1][0-9]-[0-3][0-9]")   # YYYY-MM-DD
        # trying to honor self.cfg["outDateFormat"] (e.g. "%Y-%m-%d"):   # todo: more flexible
        dexpr = self.cfg["outDateFormat"].replace("%d","[0-3][0-9]").replace("%m","[0-1][0-9]").replace("%Y","[0-9]{4}").replace("%y","[0-9]{2}")
        dcheck = compile(dexpr)

        if not isCalendar or self.cfg["realDatesSeparate"]:

            for tag in self.tags:

                if self.cfg["debug"]:
                    print "** tag : ", tag
                    print "   lasttag1 =", lasttag1
                    print "   lasttag2 =", lasttag2

                if self.cfg["realDatesSeparate"]:
                    result = dcheck.search(tag[2])
                    if not isCalendar and result:
                        continue
                    if isCalendar and not result:
                        continue

                tagContinued = False

                if self.cfg["debug"]:
                    print "wroteHeader=", wroteHeader

                if tag[2] == "":

                    ##if wroteHeader and (lasttag1 != "") and (tag[1] != "") and ((lasttag1 == tag[1]) or (tag[3] != "" and tag[0].startswith(tag[3]))):   #todo: check
                    #todo: check whether tag[1] could be empty at all : make it easier...
                    if wroteHeader and (lasttag1 != "") and (tag[1] != "") and (lasttag1 == tag[1]) :
                        tagContinued = True

                        if self.cfg["debug"]:
                            print "tagContinued set by 1"
                    else:
                        lasttag1 = tag[1]
                else:

                    if lasttag2 == tag[2]:
                        tagContinued = True

                        if self.cfg["debug"]:
                            print "tagContinued set by 2"
                        #lasttag1 = u""
                    else:
                        lasttag2 = tag[2]

                if self.cfg["debug"]:
                    print "tagContinued=", tagContinued



                # write SPACER to the tag list:

                if tagAdded and not tagContinued:
                    newtext += '\n' + self.cfg["spacerline"]
                    tagAdded = False


                if not tagContinued:
                    wroteHeader = False   # write header only once per tag


                # handle untagged todos

                if tag[0] == u'UNTAGGED':

                    if self.cfg["debug"]:
                        print "... is UNTAGGED"

                    for todo in sorted(todos):

                        if self.cfg["debug"]:
                            print "==> todo untagged", todo

                        tcs = todo[1].split(":")[0]  # only the tag(s)
                        tcsp = tcs.find(".")         # only the part after "todo."
                        foundTag = False
                        if tcsp > -1:                # if tag there
                            tcs = tcs[tcsp+1:]
                            for t in self.tags:          # check if this todo's tag is already known => will be listed under that tag later
                                if t[0] == tcs:
                                    foundTag = True
                                    break

                        if not foundTag:           # if this todo is untagged
                            if not wroteHeader:
                                newtext += '\n' + tag[1] + '\n'
                                wroteHeader = True

                            s = todo[1]
                            if self.cfg["deleteAttributes"]:
                                s = self.delAttribs(s)

                            # handle "unreal" todos (like 'done' ...)
                            s1 = ""
                            if (not self.cfg["onlyRealTodos"]) and (s[0:4] != "todo"):
                                s1 = "  {%s}" % s[0:s.find(':')]

                            # create links
                            ww1 = todo[0]
                            #if not self.wikidpad.getFormatting().isCcWikiWord(ww1):
                            if not langHelper.isCcWikiWord(ww1):
                                ww1 = "[%s]" % ww1

                            if self.cfg["extendedLinks"]:  newtext += "%s%s#%s : %s%s\n"  % (self.cfg["bullet"], ww1, s.replace(" ","# "), s[s.find(':')+1:], s1)
                            else:                          newtext += "%s%s: %s%s\n"      % (self.cfg["bullet"], ww1, s[s.find(':')+1:], s1)

                            tagAdded = True

                else:

                    # handle tagged todos

                    if self.cfg["debug"]:
                        print "... is tagged"


                    for todo in sorted(todos):

                        if self.cfg["debug"]:
                            print "todo=", todo

                        tcs = todo[1][todo[1].find(".")+1:todo[1].find(":")]          # the tag(s) alone

                        #if self.cfg["debug"]:
                        #    print "tcs=", tcs
                        #    print "tag=", tag
                            
                        if tag[0] == tcs:     # if current tag matches current todo's tag

                            if not wroteHeader and not tagContinued:
                                if   tag[2] == "":     ntxt = tag[1]            # normal tag of known type
                                elif tag[2] != tag[0]: ntxt = tag[1] + tag[2]   # tag with date and add. info
                                else:                  ntxt = tag[1] + tag[0]   # tag of unknown type and std. dates YYYY-MM-DD without info #todo: correct descr.???

                                #print "ntxt=", ntxt
                                if ntxt.find("*") != -1:      # if contains asterisks disable formatting meaning
                                    ntxt = "%s<< %s >>" % (tag[1], ntxt[len(tag[1]):])   # or:
                                    #ntxt = ntxt.replace("*","\*")

                                newtext += '\n' + ntxt + '\n'
                                
                                wroteHeader = True

                            s = todo[1]
                            if self.cfg["deleteAttributes"]:
                                s = self.delAttribs(s)

                            # optionally handle "unreal" todos (like 'done' ...)
                            if (not self.cfg["onlyRealTodos"]) and (s[0:4] != "todo"):
                                st,dummy = s.split(':', 1)
                                st,dummy = st.split('.', 1)
                                s1 = "  {" + st + "}"
                            else:
                                s1 = ""

                            # create the links
                            ww1 = todo[0]
                            if not langHelper.isCcWikiWord(ww1):
                                ww1 = "[%s]" % ww1

                            # possible tags before date string
                            if tag[3] != "":
                                ti = " (%s)" % tag[3]
                            else:
                                ti = ""

                            if self.cfg["extendedLinks"]: newtext += "%s%s#%s : %s %s%s\n"  % (self.cfg["bullet"], ww1, s.replace(" ","# "), ti, s[s.find(':')+1:], s1)
                            else:                         newtext += "%s%s:%s %s%s\n"       % (self.cfg["bullet"], ww1, ti, s[s.find(':')+1:], s1)

                            tagAdded = True


        # and finally the footer

        newtext += '\n' + self.cfg["spacerline"]

        if self.cfg["realDatesSeparate"]:
            if isCalendar:
                newtext += self.cfg["spacerline"] + "\nDue to configuration option there may be the main todo page: ToDo ..."
            else:
                newtext += self.cfg["spacerline"] + "\nDue to configuration option there may be an additional page: ToDoCalendar ..."
            newtext += '\n' + 2 * self.cfg["spacerline"]

        if self.cfg["iconString"] != "" or colorStringFlag:
            newtext += '\n\n'
            if self.cfg["iconString"] != "":
                newtext += self.cfg["iconString"] + "\n"
            if colorStringFlag:
                if missedTodos:        newtext += self.cfg["colorStringMissed"]
                elif todosForToday:    newtext += self.cfg["colorStringToday"]
                elif todosForNextDays: newtext += self.cfg["colorStringNext"]
                else:                  newtext += self.cfg["colorStringNormal"]

        if self.cfg["setBookmark"]:
            newtext += '\n[bookmarked=true]\n'

        if self.cfg["showVersion"]:
            newtext += "\n*** Created by Todo-Extension version %s in %s ***\n" % (version, wpversionstr)

        if self.cfg["isConfigPageActive"] and self.cfg["showConfigLink"]:
            newtext += "*** Configuration can be changed locally on page %s ***\n" % (self.cfg["configPage"])

        if not self.cfg["realDatesSeparate"] and isCalendar and not tagAdded:
            newtext = "Due to configuration option there are no entries on this page.\nHave a look at the main todo page: ToDo"

        editor.AddText(newtext)    # put all the new text into the editor page
        editor.GotoPos(0)          # and navigate to BeginOfFile    #todo: better than nothing, but perhaps can be optimized

        if self.cfg["showInfoPopup"] and msgPop != "":
            if (self.cfg["realDatesSeparate"] and isCalendar) or (not self.cfg["realDatesSeparate"] and not isCalendar):
                if lastCreation < (time() - self.cfg["infoPopupTimeDelta"] * 60):
                    self.wikidpad.displayMessage("Info from %s" % wikiWord, msgPop)
