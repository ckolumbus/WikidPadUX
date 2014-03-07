# vim: set fileencoding=utf-8 :
########################################################################
#
# PasteHtml.py
# ------------
# HTML parser for Wikidpad
#
# v0.3 by xkjq@ymail.com
#
# As usual thanks to Michael for all his work on WikidPad and sorting
# out a cross platform way to retrieve html text from the clipboard.
#
# A plugin that retrieves HTML text from the clipboard and converts it
# to a wikidpad compatable format.
#
# The script is customisable so it shouldn't be too hard to modify it
# for custom parsers. Beware its still early days and stuff is likely
# to change in future versions.
#
# Note: Formating can only be retrived if it is defined by html tags,
#       CSS formating will be ignored. 
#
# TODO: Clean up the code and maybe even give the script a nice GUI
#       for configuration
#
########################################################################
#
# The following settings define how the text is formated. If the
# defaults are not to your liking they can be changed here.
# 
# If you use a custom parser chances are you *will* need to change this.
#
#
# START CONFIGURATION
#
# Some html tags have no equivelent in the default wikiParser language. 
# If (like me) you haven't got round to adding them to your parser, but
# still want to keep the formating add them below.

tags_to_keep = set(["u", "sup", "sub"])

#
# tags_to_sub defines which html tags should be converted into wikiparser
# format and what their replacements should be
# 
#       html_tag : ("wikiParser_start_tag", "wikidParser_end_tag")
#
# i.e.  u"b" : (u"*", u"*") 
# would cause   <b>Hello World!</b>
# to become       *Hello World!*
#

tags_to_sub = {
                u"b" : (u"*", u"*"),
                u"strong" : (u"*", u"*"),
                u"i" : (u"_", u"_"),
                u"em" : (u"_", u"_"),

                u"p" : (u"\n", u"\n"),

                u"h1" : (u"\n++", u"\n"),
                u"h2" : (u"\n+++", u"\n"),
                u"h3" : (u"\n++++", u"\n"),
                u"h4" : (u"\n+++++", u"\n"),
                u"h5" : (u"\n++++++", u"\n"),
                u"h6" : (u"\n+++++++", u"\n"),
                u"h7" : (u"\n++++++++", u"\n"),
                u"h8" : (u"\n+++++++++", u"\n"),

                u"br" : (u"\n", u""),

                # Links
                u"a" : (u"[", u"]"),

                # TODO: split into class tags
                # for OHCExam
                u"HD" : (u"", u"\n"),

                # Tags that don't exist in HTML
                u"box" : (u"<<!", u"\n>>\n"),
                }

# 
# This defines how tables should be formated. If we are in a table
# the script will check for tags in here prior to those defined
# above.

format_table = {
                u"table": (u"\n<<|\n", u">>\n"),
                u"tr": (u"", u"\n"),
                u"td": (u"|", u""),
                # th is used in the header row. Currently wikipad, default parser
                # at least, does not distinguish the table header.
                u"th": (u"|", u""),

                u"caption": (u"", u""),

                # Previously defined tags can be overriden whilst 
                # inside tables. i.e. br should become "\newline"
                # instead of just "newline" for the default parser
                u"br" : (u"\\\n", u""), 

                u"p" : (u"", u""), 

}

STRIP_CONTENT_WHITESPACE_FROM_TAGS = (u"li", u"p", u"a", u"caption", u"td", u"tr", u"h1", u"h2", u"h3", u"h4", u"h5", u"table")

ADVANCE_TABLE_FORMATING = True


#
# Setting variable below to True would cause table formating to be 
# ignored if no table start tag has been encountered.

ignore_table_formatting_when_not_in_table = False

# If table not open will open table on any tag present in
# format_table (and not defined below)

open_tables_if_needed = True # will override 
# ignore_table_formatting_when_not_in_table

# Only these tags can start a table automatically
table_start_tags = set([u"tr", u"td", u"th", u"caption"]) 

close_open_tables = True # Useful when only pasting part of a table

# Defines what formating from format_table is used when opening a
# table. Probably best to leave this as default
table_start = u"table" #

# If true tags which have no associated text and are not specified 
# below will be ignored. Can solve some issues but may create others.
# i.e.  <h2></h2> will be ignored
#       <h2>TEST</h2> would not
ignore_empty_tags = True
allowed_empty_tags = set(["img", "p", "br"]) # Should any others be in here?

# List tags defined below will be converted to wikidpad format.
# The unordered list start tag (default: *) can be customized, ordered
# lists cannot.

lists_format = {
    "ul" : "*",
    "ol" : "ordered" # Not customisable 
}

IGNORE_P_IN_LISTS = True

#
#
# spacer defines the seperator to be used for lists
# i.e use
# spacer = "\t"
# if you want to use tab indented lists

spacer = "    "

#
# If allow_extra_ol_formats is false all ordered lists will be converted 
# to numbered lists. If true the list type will be maintained (I don't
# think the default parser supports this at the moment). This includes
# alphabetical and roman numeral based lists

allow_extra_ol_formats = True

#
#
# If true, images will be replaced by their src attribute (i.e. their
# url). If false images are ignored. As such images should function
# correctly in preview mode (providing the link is absolute not
# relative?).
# TODO: Add option to save image locally

add_image_src = True

# If set image size is set automatically for the images
maintain_image_resizes = True

# Is this customisable?? If so what about s/r/a etc?
wikipad_url_appendix_delimiter = ">"

#
# URL handling
# If true all anchors will be converted to wikipad format

maintain_links = False
wikipad_link_delimiter = "|"
use_wikidpad_anchor_format = True
KEEP_ANCHOR_ANCHORS = False

#
#
# pre_blocks_maintain_formating: if set to true formating within pre tags 
# will be maintained and surrounded with tags defined in pre_block_tags. 
# TODO: make a few changes this up so its actually useful

pre_blocks_maintain_formating = False
pre_block_tags = ("<<pre\n", "\n>>")


attempt_to_clean_formatting_tags = True
attempt_to_clean_formatting_tags_across_linebreaks = True


REMOVE_LINE_BREAKS_FROM_PARAGRAPHS = False

ATTEMPT_TO_KEEP_DIV_BOXES = True
BOX_CLASSES = (u"SIDEBAR BOX", )


#
# Custom replaces
# ---------------
# These are custom rules to be run on the text. Can be handy to remove 
# unwanted formating (from sites such as wikipedia etc.) automatically.
#
# custom_replace is a standard python replace(a, b) function where all 
# occurances of a are replaced by b.
# custom_replace_regex a re.sub.
#
# NOTE: These are run after the html has been parser

enable_custom_replace = True

custom_replace = [
    #("[edit]", ""), # Remove some unwanted wikipedia formating
    #("<sup>[_citation needed_]</sup>", ""),


    # Hack, should be fixed in parser
    ("<<!\n\n+", "<<!\n+"),

    ]

custom_replace_regex = [
    (r"<sup>(\[\d*\])?</sup>", r""), # Remove wikipedia refs, e.g. [2]
    (r"\+\*_(.*)_\*", r"+\1"), # 
    (r"\+_\*(.*)\*_", r"+\1"), # 
    (r"\+\*(.*)\*", r"+\1"), # 
    (r"(\n *)*\n *\n", r"\n\n"), # Remove excessive line breaks
    ]
# 
#
# END SCRIPT CONFIGURATION
# You shouldn't (!) have to edit anything below here
html_character_entities = [
    (u"&lt;",    u"<"),
    (u"&gt;",    u">"),
    (u"&amp;",   u"&"),
    (u"&cent;",  u"Â¢"),
    (u"&pound;", u"Â£"),
    (u"&yen;",   u"Â¥"),
    (u"&euro;",  u"â¬"),
    (u"&sect;",  u"Â§"),
    (u"&copy;",  u"Â©"),
    (u"&reg;",   u"Â®"),
    (u"&trade;", u"â¢"),
    ]
########################################################################
import sys, wx, re

from HTMLParser import HTMLParser

try:
    # If runnig from source we need to import as such
    from lib.pwiki.wxHelper import getHtmlFromClipboard, getTextFromClipboard
except ImportError:
    # This should handle the windows binary case
    from pwiki.wxHelper import getHtmlFromClipboard, getTextFromClipboard 



WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

def describeMenuItems(wiki):
        global nextnumber
        return ((Paste, "Paste HTML\tCtrl-Shift-V", "Pastes HTML in a wikipad compatable format"),)


# Custom lists conversion
numeral_map = zip(
    (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
    ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
)

def intToRoman(i):
    """
    Converts integer to roman numeral
    """
    result = []
    for integer, numeral in numeral_map:
        count = int(i / integer)
        result.append(numeral * count)
        i -= integer * count
    return ''.join(result)

letters = "0ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def intToLetter(i):
    """
    Converts integer to letter format

    Will work up to ZZ (26*26)
    """
    if i > 26:
        f = letters[i // 26]
        s = letters[i % 26]
        return "".join([f, s])
    else:
        return letters[i]


class HTMLStripper(HTMLParser):
    """
    Strips all HTML tags other than those defined in
    tags_to_keep
    """
    def __init__(self):
        self.reset()
        self.fed = []


        self.spacer = spacer

        self.tags_to_keep = tags_to_keep
        self.tags_to_sub = tags_to_sub
        self.lists_format = lists_format

        self.list_structure = []

        self.list_numbers = []

        # Is it realistic to handle tables within tables?
        self.in_table = 0
        self.table_start_pos = 0 # position in the self.fed list

        self.in_paragraph = False

        self.span_tags = []
        self.div_tags = []

        
        self.new_table_row = True
        self.table_cell_appendix = None

        self.last_tag = None

        self.link_anchor = None

    def handle_starttag(self, tag, attrs):
        """
        Called whenever an opening tag is reach

        Generally we add the wikipad equivelent to the
        list self.fed
        """

        self.previous_tag = self.last_tag
        self.last_tag = tag

        if tag == u"p":
            if IGNORE_P_IN_LISTS and len(self.list_structure) > 0:
                return
            self.in_paragraph = True

        if tag == u"img":
            self.handle_image(attrs)
            return

        # If we're in a table check table formatting first
        if tag in format_table:

            if tag == table_start:
                self.in_table += 1
                self.table_start_pos = len(self.fed)
            if tag == u"tr":
                self.new_table_row = True

            if self.in_table < 1: # Table not started
                if open_tables_if_needed and tag in \
                        table_start_tags: # Start table

                    self.in_table += 1
                    self.table_start_pos = len(self.fed)
                    self.fed.append(format_table[table_start][0])

                    self.handle_table_tag(tag, attrs)
                    return

                elif ignore_table_formatting_when_not_in_table:
                    pass
            else:
                self.handle_table_tag(tag, attrs)
                return

        # Extract some style from span's
        # expand to include divs and others? 
        # TODO: SHOULD GENERALISE
        if tag == u"span":
            span_tags_to_add = []
            styles_list = self.get_attribute(attrs, "style", False)
            if styles_list:
                styles_list = styles_list.split(u";")

                styles = {}
                for style in styles_list:
                    try:
                        a, b = style.split(u":")
                        styles[a.strip()] = b.strip()
                    except ValueError:
                        pass

                if u"font-style" in styles:
                    if styles[u"font-style"] == u"italic":
                        span_tags_to_add.append(u"i")

                if u"font-weight" in styles:
                    try:
                        if styles[u"font-weight"] == u"bold":
                            span_tags_to_add.append(u"b")
                        elif int(styles[u"font-weight"]) > 400:
                            span_tags_to_add.append(u"b")
                    except ValueError:
                        pass


                for i in span_tags_to_add:
                    self.handle_starttag(i, None)

            self.span_tags.append(span_tags_to_add)
            return

        if tag == u"div":
            div_tags_to_add = []

            # ----------------------------------------------
            # Code below is for importing from OHCExam
            css_class = self.get_attribute(attrs, "class", False)

            if css_class and css_class.startswith("TLV"):
                self.fed.append(u"\n\n++{0}".format(int(css_class[3]) * u"+"))
                #div_tags_to_add.append(u"h{0}".format(int(css_class[3]) + 1))
                #self.handle_starttag(
            elif css_class == u"HD":
                div_tags_to_add.append(u"HD")
            elif css_class == u"P":
                if self.previous_tag != u"li":
                    div_tags_to_add.append(u"HD")
                    div_tags_to_add.append(u"p")
            elif ATTEMPT_TO_KEEP_DIV_BOXES and css_class in BOX_CLASSES:
                    div_tags_to_add.append(u"box")

            # ----------------------------------------------

            styles_list = self.get_attribute(attrs, "style", False)
            if styles_list:
                styles_list = styles_list.split(u";")

                styles = {}
                for style in styles_list:
                    try:
                        a, b = style.split(u":")
                        styles[a.strip()] = b.strip()
                    except ValueError:
                        pass

                if u"font-style" in styles:
                    if styles[u"font-style"] == u"italic":
                        div_tags_to_add.append(u"i")

                if u"font-weight" in styles:
                    try:
                        if styles[u"font-weight"] == u"bold":
                            div_tags_to_add.append(u"b")
                        elif int(styles[u"font-weight"]) > 400:
                            div_tags_to_add.append(u"b")
                    except ValueError:
                        pass


            for i in div_tags_to_add:
                self.handle_starttag(i, None)

            self.div_tags.append(div_tags_to_add)

            return
                    

        if tag in self.tags_to_keep:
            self.fed.append(u"<{0}>".format(tag))
            return

        if tag in self.tags_to_sub:
            
            # Parse anchors start tag
            if tag == u"a":
                if KEEP_ANCHOR_ANCHORS and self.get_attribute(attrs, "name", False):
                    self.fed.append("anchor: {0}\n".format(self.get_attribute(attrs, "name", False)))
                if maintain_links:
                    link = self.get_attribute(attrs, u"href", u"Unable to find link")
                    anchor = u""
                    if use_wikidpad_anchor_format and u"#" in link:
                        link, anchor = link.split(u"#")
                        self.link_anchor = "!{0}".format(anchor)

                    self.fed.append("".join([self.tags_to_sub[tag][0], link, wikipad_link_delimiter]))
                else:
                    # Add blank object so it can be removed if necessary
                    self.fed.append(u"")
                return

            self.fed.append(self.tags_to_sub[tag][0])

        # Handle lists
        if tag in self.lists_format:

            list_type = self.get_attribute(attrs, u"type")

            self.list_structure.append((self.lists_format[tag], list_type))
            self.list_numbers.append(0)
        
        if tag == u"li" and len(self.list_structure) > 0: 
            list_item_number = self.list_numbers[-1]+1
            self.list_numbers[-1] = list_item_number

            list_start = self.list_structure[-1][0]

            if list_start == u"ordered": # Ordered list

                n = list_item_number

                if allow_extra_ol_formats:
                    
                    if self.list_structure[-1][1] == u"A": # Capital letters
                        n = intToLetter(list_item_number)

                    if self.list_structure[-1][1] == u"a": # Lower letters
                        n = intToLetter(list_item_number).lower()

                    if self.list_structure[-1][1] == u"I": # Roman letters
                        n = intToRoman(list_item_number)

                    if self.list_structure[-1][1] == u"i": # Roman lower letters
                        n = intToRoman(list_item_number).lower()

                list_start = u"{0}.".format(n)
                
            # List items must start on a new line (in wikidpad)
            if self.fed and not (self.fed[-1].endswith(u"\n") or 
                    self.fed[-1].strip() == u""):
                self.fed.append(u"\n")

            self.fed.append(u"{0}{1} ".format(self.spacer*len(self.list_structure), list_start))
           
            
    def handle_startendtag(self, tag, attrs):
        """
        Self closing tags are handled here
        e.g.    <img scr="...." />
                <br />

        For now just redirects to handle_starttag()
        
        Are their any situations in which this shouldn't
        happen?
        """
        self.handle_starttag(tag, attrs)

        
    def handle_endtag(self, tag):
        """
        Called as the tag is closed
        """
        # Strip whitespace from the previous content if required
        if tag in STRIP_CONTENT_WHITESPACE_FROM_TAGS:
            self.fed[-1] = self.fed[-1].rstrip()

        self.last_end_tag = tag

        if tag == u"p":
            if IGNORE_P_IN_LISTS and len(self.list_structure) > 0:
                return
            self.in_paragraph = False
        
        if ignore_empty_tags:
            if tag in self.tags_to_keep or tag in self.tags_to_sub:
                if tag == self.last_tag and tag not in allowed_empty_tags:
                    del self.fed[-1]
                    self.last_tag = None
                    return


        if tag == u"span":
            tags = self.span_tags.pop()
            tags.reverse()

            for i in tags:
                self.handle_endtag(i)

        elif tag == u"div":
            tags = self.div_tags.pop()
            tags.reverse()

            for i in tags:
                self.handle_endtag(i)

        if tag in format_table:
            if self.in_table > 0:
                #if tag == u"caption":
                #    self.fed.append(format_table[table_start][0])
                #    return
                if tag == u"caption":
                    d = self.end_temp_feed()
                    self.add_table_arg(self.table_start_pos, u"C")
                    self.fed.insert(self.table_start_pos+1, d+"\n")

                if tag == table_start:
                    self.in_table -= 1
                self.fed.append(format_table[tag][1])

                if self.table_cell_appendix is not None:
                    self.fed.append(self.table_cell_appendix)
                    self.table_cell_appendix = None
                return

        if tag == u"a":
            if maintain_links:
                self.fed.append(self.tags_to_sub[tag][1])
                if self.link_anchor is not None:
                    self.fed.append(self.link_anchor)
                    self.link_anchor = None
            return
                
        if tag in self.tags_to_keep:
            self.fed.append(u"</{0}>".format(tag))
            return

        if tag in self.tags_to_sub:

            self.fed.append(self.tags_to_sub[tag][1])

        #if tag == u"li" and len(self.list_structure) > 0: 
        #    self.fed.append(u"\n")

        if tag in self.lists_format:
            del self.list_structure[-1]

            if not self.list_structure:
                self.fed.append(u"\n")

    def add_table_arg(self, table_start_pos, arg):
        start_block = self.fed[table_start_pos]

        if not start_block.startswith(format_table["table"][0]):
            return False

        to_add = u""
        if start_block.endswith("\n"):
            start_block = start_block[:-1]
            to_add = u"\n"

        if self.fed[table_start_pos] == format_table["table"][0]:
            self.fed[table_start_pos] = start_block + arg + to_add
        else:
            self.fed[table_start_pos] = start_block + ";" + arg + to_add

        
    def handle_data(self, d):
        try:
            if d == u" " and self.fed[-1] == u" ":
                return
        except IndexError:
            pass

        # Ignore empty lines within list
        if len(self.list_structure) > 0:
            if len(d.strip()) < 1:
                return
        
        if self.in_paragraph and REMOVE_LINE_BREAKS_FROM_PARAGRAPHS:
            d = d.replace(u"\n", u" ")

        # Remove style tags?
        if self.last_tag == u"style":
            self.last_tag = None
            return

        if self.last_tag in STRIP_CONTENT_WHITESPACE_FROM_TAGS:
            d = d.lstrip()

        self.last_tag = None

        self.fed.append(d)

    def get_data(self):
        if close_open_tables:
            while self.in_table > 0:
                self.fed.append(format_table[table_start][1])
                self.in_table -= 1
        return u''.join(self.fed)

    def start_temp_feed(self):
        self.fed_bak = self.fed[:]

        self.fed = []

    def end_temp_feed(self):
        data = self.fed[:]
        self.fed = self.fed_bak[:]

        self.fed_bak = []

        return "".join(data)

    def handle_table_tag(self, tag, attrs=None):

        # Captions need to be inserted before the table start
        if ADVANCE_TABLE_FORMATING and tag ==  u"caption" :
#            # Caption should always be immediatly after table start
#            # so we can just delete the last item, add the caption
#            # and start the table again on its close tag
#            del self.fed[-1]
#            return
# NOTE: not all captions are defined in the correct position so we have to
#       be a bit more careful
            self.start_temp_feed()

                

        # Special case for p
        if tag == u"p":
            if self.last_end_tag == u"p":
                self.fed.append(u"\\\n")

        # Special case is needed for td
        if tag == u"td" or tag == u"th":
            
            if ADVANCE_TABLE_FORMATING:
                # Get attributes that will be placed into table appendix
                colspan = self.get_attribute(attrs, "colspan", False)
                rowspan = self.get_attribute(attrs, "rowspan", False)

                # Could also pull some style info here, e.g. text-align
                appendix = []
                if colspan:
                    appendix.append('c{0}'.format(colspan))
                if rowspan:
                    appendix.append('r{0}'.format(rowspan))

                if appendix:
                    self.table_cell_appendix = ";{0}".format(";".join(appendix))


            if not self.new_table_row:
                # need spaces or blank cell will be ignored
                self.fed.append(u" {0} ".format(format_table[tag][0]))
                return
            else:
                self.new_table_row = False
                return
        else:
            self.fed.append(format_table[tag][0])

    def handle_image(self, attrs):
        if add_image_src:
            appendix = ""
            if maintain_image_resizes:
                width = self.get_attribute(attrs, "width", False)
                height = self.get_attribute(attrs, "height", False)

                # Currently only deals with img for which both width and height are
                # specified
                if width and height:
                    size_type = "s" # default size in pixels

                    # HTML can handle images with 1 dimension in %
                    # and the other in pixel but wikidpad (default
                    # parser at least) cannot.
                    if width[-1] == "%":
                        size_type = "r"

                    appendix = "".join([wikipad_url_appendix_delimiter, size_type,
                                    width, "x", height, " "])
                    
                
            self.fed.append("".join([self.get_attribute(attrs, "src"), appendix]))

    def get_attribute(self, attrs, attr, not_found=""):
        """
        Loops through all attributes returning the requested one
        if found.
        
        attrs is a list of turples, quotations (") are not included 
        [(name, value), (name2, value2), ...]
        """

        if len(attrs) > 0:
            for name, value in attrs:
                if name == attr:
                    return value
        return not_found


def strip_tags(html):
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

def getData(d):

    # Remove html character entities
    for a, b in html_character_entities:
        d = d.replace(a, b)
    
    if pre_blocks_maintain_formating:
        # Pre blocks have to be handled before we remove whitespace
        pre_blocks = []
        a = re.search(r"<pre(?:>| [\s\S]*?>)([\s\S]*?)</pre(?:>| [\s\S]*?>)", d)
        while a:
            d = d.replace(a.group(0), "$_PREBLOCK-{0}_$".format(len(pre_blocks)))
            pre_blocks.append(a.group(1)) 
            a = re.search(r"<pre(?:>| [\s\S]*?>)([\s\S]{1,}?)</pre(?:>| [\s\S]*?>)", d)


    # Remove whitespace (ignored in html anyway)
    d = " ".join(d.split())

    if attempt_to_clean_formatting_tags:
        for i in ("i", "b", "u"):
            d = re.sub("[(?<=\w)\n](<{0}>)\n. .[(?=\w)]".format(i), r"\1 ", d)
            d = re.sub("[(?<=\w)\n][\n ].(<\/{0}>)[(?=\w)\n]".format(i), r"\1 ", d)

    if attempt_to_clean_formatting_tags_across_linebreaks:
        for i in ("i", "b", "u"):
            d = re.sub("(?<=\w) .\n(<\/{0}>)(?=\w)|\n".format(i), r"\1\n", d)
            d = re.sub("(?<=\w)(<{0}>) .\n(?=\w)|\n".format(i), r"\1\n", d)


    d = strip_tags(d)
    
    # Clean up some spaces
    d = d.replace("     ", "    ")


    if pre_blocks_maintain_formating:
        # Add pre blocks back in
        for i in range(len(pre_blocks)):
            d = d.replace("$_PREBLOCK-{0}_$".format(i), "{0}{1}{2}".format(pre_block_tags[0], pre_blocks[i], pre_block_tags[1]))


    # Perform custom replaces (if enabled)
    if enable_custom_replace:
        if len(custom_replace) > 0:
            for a, b in custom_replace:
                d = d.replace(a, b)

        if len(custom_replace_regex) > 0:
            for a, b in custom_replace_regex:
                d = re.sub(a, b, d)

    return d.lstrip()


def Paste(pwiki, evt):

    editor = pwiki.getActiveEditor()
            
    html = getHtmlFromClipboard()[0]

    if html is not None:
        text = getData(html)
        editor.ReplaceSelection(text)
        
    else:
        text = getTextFromClipboard()
        editor.ReplaceSelection(text)

