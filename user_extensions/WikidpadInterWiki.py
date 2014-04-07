"""
= InterWiki inside WikidPad =
Wouldn't you like to use a proper InterWiki syntax in your WikidPad?

Means - have Shortcuts for URLs outside your WikidPad (types: http, file, etc...), based on your "interwiki map"
See Also (explanations on what is interwiki and examples of usage):
 * http://en.wikipedia.org/wiki/Interwiki
 * http://en.wikipedia.org/wiki/Help:Interwiki_linking
 * http://moinmoin.wikiwikiweb.de/InterWiki
 * And even in Trac: InterWiki

All you have to do is Add a file named interWiki.py to your user_extensions.

How to use:

Add in a page (example):
{{{
[:interwiki:Wikibooks;///C++_Programming/Code/Design_Patterns///]
[:interwiki:Wikipedia;///Design_pattern_(computer_science%29///]
}}}

In "Preview" you will see:
{{{
Wikibooks: C++_Programming/Code/Design_Patterns 
Wikipedia: Design_pattern_(computer_science) 
}}}
When the text above is linked to the desired target.
Note: There is some problem with closing (right) paren - no way to keep it inside the link...

"""

import os, urllib
import wx
from yaml import load,dump


from Consts import CONFIG_GLOBALS_DIRNAME

WIKIDPAD_PLUGIN = (("InsertionByKey", 1),)

def describeInsertionKeys(ver, app):
     """
     API function for "InsertionByKey" plugins
     Returns a sequence of tuples describing the supported
     insertion keys. Each tuple has the form (insKey, exportTypes, handlerFactory)
     where insKey is the insertion key handled, exportTypes is a sequence of
     strings describing the supported export types and handlerFactory is
     a factory function (normally a class) taking the wxApp object as
     parameter and returning a handler object fulfilling the protocol
     for "insertion by key" (see EqnHandler as example).

     This plugin uses the special export type "wikidpad_language" which is
     not a real type like HTML export, but allows to return a string
     which conforms to WikidPad wiki syntax and is postprocessed before
     exporting.
     Therefore this plugin is not bound to a specific export type.

     ver -- API version (can only be 1 currently)
     app -- wxApp object
     """
     return ((u"interwiki", ("wikidpad_language",), InterWikiHandler),(u"iw", ("wikidpad_language",), InterWikiHandler), )


class InterWikiHandler:
     """
     Class fulfilling the "insertion by key" protocol.
     """
     def __init__(self, app):
         self.app = app
         self.configFileName = os.path.join(app.getGlobalConfigSubDir(),"InterWiki.yml" )
         self.interwiki_map = {}
         # shortcut for wikis located in dataDir
         self.dataWikiPrefix="dwiki://" 
         # try to load yaml config file from GlobalConfigSubDir
         try:
            # http://effbot.org/zone/python-with-statement.htm
            # with is more safe to open file
            with open(self.configFileName,'r') as fh:
                self.interwiki_map = load(fh)
         except :
         # ... if it's not found, set to default ...
             self.interwiki_map={
                     'Google':"http://www.google.com/search?q=",
                     'Wikipedia':"http://en.wikipedia.org/wiki/",
                     'WikipediaCategory':"http://en.wikipedia.org/wiki/Category:",
                     'Wikibooks':"http://en.wikibooks.org/wiki/",

                     'OtherWiki':'wiki:///C:/tmp/OtherWiki/OtherWiki.wiki?page=',
                     'YetAnotherWiki':'dwiki://YetAnotherWiki'
                     }
         # ... and store as example to disk
             with open(self.configFileName,'w') as fh:
                dump(self.interwiki_map, fh, default_flow_style=False)


     def taskStart(self, exporter, exportType):
         """
         This is called before any call to createContent() during an
         export task.
         An export task can be a single HTML page for
         preview or a single page or a set of pages for export.
         exporter -- Exporter object calling the handler
         exportType -- string describing the export type

         Calls to createContent() will only happen after a
         call to taskStart() and before the call to taskEnd()
         """
         pass


     def taskEnd(self):
         """
         Called after export task ended and after the last call to
         createContent().
         """
         pass


     def createContent(self, exporter, exportType, insToken):
         """
         Handle an insertion and create the appropriate content.

         exporter -- Exporter object calling the handler
         exportType -- string describing the export type
         insToken -- insertion token to create content for (see also
                 PageAst.Insertion)

         An insertion token has the following member variables:
             key: insertion key (unistring)
             value: value of an insertion (unistring)
             appendices: sequence of strings with the appendices

         Meaning and type of return value is solely defined by the type
         of the calling exporter.

         For HtmlXmlExporter a unistring is returned with the HTML code
         to insert instead of the insertion.
         """
         def gen_wikiPath(exporter,input):
             remove_me="/"+unicode(exporter.getMainControl().wikiName)+"/data"
             mydir=unicode(exporter.getMainControl().dataDir)
             mydir=mydir.replace(':\\',':/').replace(' ','%20').replace('\\','/').replace(remove_me,'')
             return "wiki:///"+mydir+"/"+input+"/"+input+".wiki?page="

         # param
         params=u""
         for i, apx in enumerate(insToken.appendices):
             params += "%s" % (apx)
         nice_params=unicode(params).replace("%20"," ").replace("%28","(").replace("%29",")")

         result = None

         #'OtherWiki':gen_wikiPath(exporter,'wiki://OtherWiki')
         for prefix,myurl in self.interwiki_map.iteritems():
             # wiki result string

             if insToken.value == prefix:

                 if myurl[:len(self.dataWikiPrefix)] == self.dataWikiPrefix:
                     myurl = gen_wikiPath(exporter, myurl[len(self.dataWikiPrefix):])
                 result = "["+myurl+params+" | "+prefix
                 if len(params) > 0:
                     result += ": "+nice_params +"]"
                 else:
                     result += "]"
                 break

         if result is None :
             result = "*InterwikiLink not found*: '%s/%s' " % (insToken.value , params)

         return result


     def getExtraFeatures(self):
         """
         Returns a list of bytestrings describing additional features supported
         by the plugin. Currently not specified further.
         """
         return ()

