#
# A Blogger extension for Wikidpad. Allows the user to enter a new 
# "blog" entry every day. Adds 2 menu items to the plugins menu, one for
# editing "today's" blog, and another to allow the user to specify an
# arbitrary date.
#
# V1.0.5 - mja 2008-12-01
# Simplify page creation & live update of tree RE: M. Butscher
# Fix Unicode regression on Linux from V1.0.4
#
# V1.0.4 - mja 2008-11-21
# Use different mechanism for replacing the text in pages. Causes proper
# update to the view tree.
#
# V1.0.3 - mja 2008-11-03
# Fix a defect when installed in a brand new Wiki (bad argument on 
# createHelpFile() method).
#
# V1.0.2 - mja 2008-11-02
# Minor localization for OK/Cancel buttons in the date picker. More extensive
# localization needs to wait for a later release.
#
# V1.0.1 - mja 2008-11-01
# Defect repair, make strings unicode to work on Linux. This is a good thing.
#
# V1.0.0 - mja 2008-10-31
# Release to Wikidpad community
#
# V1.0x - mja 2007-11-27 
# Experimental version

#import re

import wx
# f r o m wx.lib.calendar import CalenDlg
# f r o m wx.lib.calendar import Calendar
from wx import DateTime

from datetime import date

#
# Wikidpad blogging functions
#
# Todo:
# - Add functionality for "other page"
# - Add functionality to link to the LogBook page
# - Add functionality to display by calendar date
#

# descriptor for EditorFunctions plugin type
WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

BLOG_TEMPLATE    = u"BlogEntryTemplate"
INSERT_DATE_HERE = u"INSERTDATEHERE"
ENTRY_LIST       = u"ENTRY LIST"
LOG_BOOK         = u"BlogBook"
BLOGGER_HELP     = u"BloggerHelp"
CURRENT_VERSION  = u"1.0.5cd1"
BLOG_HELP_PROP   = u"blog.help"
BLOGGER_VERSION  = u"Blogger v" + CURRENT_VERSION + " 2008-12-02"

# Flag that allows Blogger to check the help page once per run, 
blogger_help_page_checked = False

## ============= Calendar Popup ==========================
## Code from Lorne Michels (wrote the CalenDlg class originally). CalenDlg
## isn't very extensible and general. I really want a DateTime object from the
## dialog, but the existing CalenDlg returns a preparsed object. 
## He suggested writing your own in this post: 
##
## http://archives.devshed.com/forums/python-122/wx-lib-calendar-calendlg-how-to-set-the-yearsrange-2377741.html
##
## I took the code and modified it. The code, as posted, needed heavy fixing for 
## syntatic errors, etc. - mja (2008-02-03)

def GetMonthList():
    monthlist = []
    for i in range(13):
        name = wx.lib.calendar.Month[i]
        if name != None:
            monthlist.append(name)
    return monthlist

class BlogCalenDlg(wx.Dialog):
    datepicker = None
    selected_date  = None

    def __init__( self, parent ):
        but_size = wx.Button.GetDefaultSize()
        wx.Dialog.__init__( self, parent, -1, 'Edit Blog for other day',
                            size = (but_size.GetWidth()*2 + 20, 150) )
        sizer = wx.BoxSizer( wx.VERTICAL )
        self.SetSizer(sizer)

        t = wx.StaticText( self, label=' ' )
        sizer.Add( t )
        dp_size = (but_size.GetWidth()*2, -1)
        self.datepicker = wx.DatePickerCtrl( self, style=wx.DP_DROPDOWN, size=dp_size )
        sizer.Add( self.datepicker, 1, wx.CENTER )
        
        bSizer = wx.BoxSizer( wx.HORIZONTAL )

        btn = wx.Button(self, wx.ID_OK, 'Ok', (0, 0), but_size )
        bSizer.Add( btn )
        self.Bind( wx.EVT_BUTTON, self.Ok, btn )
        btn = wx.Button( self, wx.ID_CANCEL, 'Cancel', (120, 0), but_size )
        bSizer.Add( btn )
        self.Bind( wx.EVT_BUTTON, self.Cancel, btn )

        t = wx.StaticText( self, label=' ' )
        sizer.Add( t )
        sizer.Add( bSizer, 1, wx.CENTER )
        self.Centre()

#
# This next blog of code is experimental code I'm working on. I want to 
# use a better calendar date picker. The default one supplied by wx is 
# not so nice looking. I am not using this since it isn't supported on
# all the versions of wx (as supplied with Wikidpad) that I want to use.
#
###class BlogCalenDlg(CalenDlg):
###    selected_month = 0;
###    selected_year  = 0;
###    calend         = None
###    monthlist      = None
###    date           = None
###    yearText       = None
###    selected_date  = None
    
###    def __init__(self, parent, month=None, day = None, year=None):
###        wx.Dialog.__init__(self, parent, -1, "Event Calendar", wx.DefaultPosition, (280, 360))
###        self.result = None
###        
###        # set the calendar and attributes
###        self.calend = Calendar(self, -1, (20, 60), (240, 200))
###
###        if month == None:
###            self.calend.SetCurrentDay()
###            start_month = self.calend.GetMonth()
###            start_year = self.calend.GetYear()
###        else:
###            self.calend.month = start_month = month
###            self.calend.year = start_year = year
###            self.calend.SetDayValue(day)
###
###        self.selected_month = start_month
###        self.selected_year  = start_year
###            
###        self.calend.HideTitle()
###        self.ResetDisplay()
###        
###        # get month list from DateTime
###        self.monthlist = GetMonthList()
###            
###        # select the month
###        self.date = wx.ComboBox(self, -1, self.monthlist[start_month-1], (20, 20), (90, -1),
###
###                                self.monthlist, wx.CB_DROPDOWN)
###        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.date )
###            
###        # alternate spin button to control the month
###        h = self.date.GetSize().height
###        self.m_spin = wx.SpinButton(self, -1, (115, 20), (h*1.5, h), wx.SP_VERTICAL)
###        self.m_spin.SetRange(1, 12)
###        self.m_spin.SetValue(start_month)
###        self.Bind(wx.EVT_SPIN, self.MonthSpin, self.m_spin)
###        
###        # spin button to control the year
###        self.yearText = wx.TextCtrl(self, -1, str(start_year), (160, 20), (60, -1))
###        h = self.yearText.GetSize().height
###        
###        self.y_spin = wx.SpinButton(self, -1, (225, 20), (h*1.5, h), wx.SP_VERTICAL)
###        self.y_spin.SetRange(1900, 2100 ) # modified code
###        self.y_spin.SetValue(start_year)
###        
###        self.Bind(wx.EVT_SPIN, self.YearSpin, self.y_spin)
###        self.Bind(wx.lib.calendar.EVT_CALENDAR, self.MouseClick, self.calend)
###        
###        x_pos = 50
###        y_pos = 280
###        but_size = (60, 25)
###        
###        btn = wx.Button(self, wx.ID_OK, 'Ok', (x_pos, y_pos), but_size)
###        self.Bind(wx.EVT_BUTTON, self.Ok, btn)
###        
###        btn = wx.Button(self, wx.ID_CANCEL, 'Cancel', (x_pos + 120, y_pos), but_size)
###        self.Bind(wx.EVT_BUTTON, self.Cancel, btn)
###        self.Centre()

    def MonthSpin( self, event ):
        self.selected_month = event.GetPosition()
        self.calend.SetMonth( self.selected_month )
        self.date.SetValue( self.monthlist[self.selected_month-1] )
        self.ResetDisplay()
        return
            
    def YearSpin( self, event ):
        self.selected_year = event.GetPosition()
        self.calend.SetYear( self.selected_year )
        self.yearText.SetValue( str(self.selected_year) )
        self.ResetDisplay()
        return
            
    def Ok( self, event ):
###        cdate = self.calend.GetDate()
###        self.selected_date = wx.DateTime()
###        self.selected_date.Set( cdate[0], cdate[1]-1, cdate[2] )
        self.selected_date = self.datepicker.GetValue()
        self.EndModal(wx.ID_OK)
        return
            
    def Cancel( self, event ):
        self.EndModal(wx.ID_CANCEL)
        return
            
## ======== Extension Core ===========

def describeMenuItems(wiki):
    """
    wiki -- Calling PersonalWikiFrame
    Returns a sequence of tuples to describe the menu items, where each must
    contain (in this order):
        - callback function
        - menu item string
        - menu item description (string to show in status bar)
    It can contain the following additional items (in this order), each of
    them can be replaced by None:
        - icon descriptor (see below, if no icon found, it won't show one)
        - menu item id.

    The  callback function  must take 2 parameters:
        wiki - Calling PersonalWikiFrame
        evt - wx.CommandEvent

    An  icon descriptor  can be one of the following:
        - a wx.Bitmap object
        - the filename of a bitmap (if file not found, no icon is used)
        - a tuple of filenames, first existing file is used
    """
    return ((currentBlog, "Edit Today's Blog\tShift-Ctrl-W", "Edit today's Blog"),
            (otherBlog,   "Other Day's Blog\tShift-Ctrl-O", "Edit other day's Blog"),)

#
# Open the blog page for the current date
#
def currentBlog(wiki, evt):
    # Get the date to construct the blog name.
    now = date.today()
    editBlogEntry( wiki, wx.DateTime.UNow() )

#
# Open a blog entry for another date
#
def otherBlog( wiki, evt):
    dlg = BlogCalenDlg(wiki)

    if dlg.ShowModal() == wx.ID_OK:
        editBlogEntry( wiki, dlg.selected_date )
#    else:
#        print 'No Date Selected'

#
# Edit a specific named Blog page, creating it from the BlogEntryTemplate 
# if needed.
#
def editBlogEntry( wiki, blogDate ):
    wiki.saveAllDocPages()

    conditionallyUpdateHelpPage( wiki )

    year  = blogDate.GetYear()
    month = blogDate.GetMonth()
    day   = blogDate.GetDay()

    name = "Blog " + blogDate.FormatISODate()
    blog_prop  = "blog." + str(year)
    blog_value = "%02d" % (month+1)

    properties = wiki.getWikiData().getPropertiesForWord(name)
    iter = properties.__iter__()
    load_content = True

    # See if the page is set up to be a proper Blog page
    # Rule #1, it needs to have the [blog.YYYY.MM:YYYY-MM-DD] property
    while True:
        try:
            t = iter.next()
            if( t[0] == blog_prop ):
                load_content = False
        except StopIteration:
            break

    # If the page is NOT a proper BLOG, load up the content from the template.
    if( load_content ):
        print "Filling in blog entry " + name 
        try:
            template = wiki.getWikiData().getContent( BLOG_TEMPLATE )
#        except WikiFileNotFoundException:
        except:
            createTemplate( wiki )
            template = wiki.getWikiData().getContent( BLOG_TEMPLATE )

        # Customize the new instance of the blog entry
        template = template.replace( BLOG_TEMPLATE, name )
        template = template.replace( INSERT_DATE_HERE, "["+blog_prop+":"+blog_value+"]" )
        template = template + "\n\n" + BLOGGER_VERSION
        wiki.getWikiDocument().getWikiPageNoError(name).replaceLiveText(template)
    # Link in, just in case it isn't there already
    linkToLogBook( wiki, blogDate, name )
    
    oldFollow = wiki.getConfig().get("main", "tree_auto_follow", "True")
    wiki.getConfig().set("main", "tree_auto_follow", "False")

    try:
        # Edit the page
        wiki.openWikiPage(name)
        wiki.getActiveEditor().SetFocus()
    finally:
        wiki.getConfig().set("main", "tree_auto_follow", oldFollow)


#
# Link the blog page to the log book page.
# This method will not do anything if the link is in the LogBook already.
#
def linkToLogBook( wiki, blogDate, name ):
    month_name = wx.DateTime.GetMonthName( blogDate.GetMonth(), 0 )
    month_category = "*" + month_name + " " +  str(blogDate.GetYear()) + "*"
    try:
        log_content = wiki.getWikiData().getContent( LOG_BOOK )
    except:
        log_content = u"++ Log Book\n\nThis log book exists to prevent each log entry from being an orphan.\nAccess the log entries via \"tree->views->blog\".\n\nYou can, of course, link to this page if you wish.\n\nENTRY LIST"
        wiki.getWikiData().setContent( LOG_BOOK, log_content )

    found = log_content.find( month_category )
    if( found < 0 ):
        # Load up the new month
        log_content = log_content.replace( ENTRY_LIST, ENTRY_LIST + "\n" + month_category + "\n[" + name + "]\n")
        wiki.getWikiDocument().getWikiPage(LOG_BOOK).replaceLiveText(log_content)
    else:
        # Otherwise insert it into the available month
        found = log_content.find( name )
        if( found < 0 ):
            # Insert this in the correct month category.
            new_link = month_category + "\n[" + name + "]"
            new_content = log_content.replace( month_category, new_link )
            wiki.getWikiDocument().getWikiPage(LOG_BOOK).replaceLiveText(new_content)

#
# Return the previous day, as a date time.
# Don't call this if the date is the first. The assumption is that the LogBook
# will be adding a new category (month) and will just add this.
#
def previousDay( blogDate ):
    day = blogDate.day - 1
    month = blogDate.month
    year  = blogDate.year
    yesterday = blogDate.replace( year, month, day )
    return yesterday

#
# Create the template, when it doesn't exist.
# Also creates the Blogger help page.
#
def createTemplate( wiki ):
    print "Creating Blog entry template"
    content = u"++ " + BLOG_TEMPLATE + "\n\nINSERTDATEHERE\n\nFor Today:\n    *\n\n\nBloggerHelp"
    wiki.getWikiDocument().getWikiPageNoError(BLOG_TEMPLATE).replaceLiveText(content)
    
    createHelpPage( wiki )

#
# If the help page has not been updated, or can not be found, update it.
#
def conditionallyUpdateHelpPage( wikid ) :
    global blogger_help_page_checked
    if( not blogger_help_page_checked ):
        create_page = True
        properties = wikid.getWikiData().getPropertiesForWord(BLOGGER_HELP)
        iter = properties.__iter__()
        while True:
            try:
                t = iter.next()
                if( (t[0] == BLOG_HELP_PROP) and
                    (t[1] == CURRENT_VERSION)):
                    create_page = False
            except StopIteration:
                break
        if( create_page ):
            print "Updating Blogger help page"
            createHelpPage( wikid )
    blogger_help_page_checked = True

#
# Create the help page, called when it doesn't exist or an upgrade happens
#
def createHelpPage( wiki ):
    helpContent = u"++ BloggerHelp"
    wiki.getWikiDocument().getWikiPageNoError(BLOGGER_HELP).replaceLiveText(helpContent)
    helpContent = u"""++ Blogger Help \n""" + BLOGGER_VERSION + """\nMichael Allison

*Introduction*

This Blogger, like Wikidpad, is designed for personal blogging on a daily basis. The author developed had given up using a paper based log book for work. In it's place he used a \"personal blog\" which has since ceased to be supported. Personal blogs have the following characteristics.

    * Needs to integrate with a personal Wiki.
    * Must be simple to create a new blog entry.
    * Entries must be dated.
    * Data must be stored in plain text files
    * Some times you don't get to write each day, it must be possible to write tardy entries for the last few days.
    * Some people write stream of conciousness, others write bulleted lists. The format must be customizable.
    * I'm lazy, and others don't share my interest in coding. Install and use must not require coding.

After a relatively fruitless search for replacements, the closest found was Wikidpad. Thus, a Wikidpad based blogging solution was born.

*Installation*

The Blogger is distributed as a single Wikidpad extension file: Blog.py. Perform the following operations to install:
    * Copy Blog.py to the Wikidpad/extensions directory
    * Restart Wikidpad
You are ready to start the blog.

*Use*

The Blog extension adds two menu items to the \"Plugin\" menu
    * Edit Today's Blog
    * Edit Other Day's Blog

Selecting the first item will open a blog page for today. Simply begin editing it and adding your wonderful content. 

Selecting the second item will open a dialog, allowing you to specify a specific date. If the page does not exist, it will be created and opened for you to edit. 

If later in the day you want to re-edit the page, you can select the appropriate menu item and it will be made available for you edit.

Each blog page is tagged with a property _blog_, which creates an entry under _Views_. The entries are hierarchically sorted by year, then by month. From this view you can access any previous blog entries. 

*Customization*

The most typical customization is to change the BlogEntryTemplate. This will change the layout of new blog entries and lets you place any boilerplate text you want on your entries. For the most part you can edit this template freely. There are two important pieces of required text. The first is the string _\BlogEntryTemplate_, which is replaced with the name of blog entry (the date). The second piece of text that must be present is _INSERTDATEHERE_. This piece of text is replaced with a property allowing you to find the blog entry under the tree->blog->year->month. 

*Internal Operation*

The blog software is driven from invoking either of the two menu items. When attempting to edit a blog page, the software attempts to copy the BlogEntryTemplate. If it can not be found, it will create the template from a basic built in format. The software also will add a link from the file LogBook. Linking to LogBook keeps each blog entry from showing up in the parentless view.

*Change Log*
    * V1.0.5 - Use proper coding for page creation, fix Linux regression
    * V1.0.4 - Fixed a defect with tree view update
    * V1.0.3 - Fixed a defect (createHelpFile) on a brand new Wiki"
    * V1.0.2 - Better localization on the OK/Cancel buttons for the date dialog
    * V1.0.1 - Fix unicode strings to allow Linux
    * V1.0.0 - First release

""" + """\n[blog.help:""" + CURRENT_VERSION + """]"""

    wiki.getWikiDocument().getWikiPageNoError(BLOGGER_HELP).replaceLiveText(helpContent)
    wiki.saveCurrentWikiState()
