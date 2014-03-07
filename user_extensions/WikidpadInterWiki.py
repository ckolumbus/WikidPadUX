import os, urllib

import wx

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
     return ((u"interwiki", ("wikidpad_language",), InterWikiHandler),)


class InterWikiHandler:
     """
     Class fulfilling the "insertion by key" protocol.
     """
     def __init__(self, app):
         self.app = app

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

         interwiki_map={
                 'Google':"http://www.google.com/search?q=",
                 'Wikipedia':"http://en.wikipedia.org/wiki/",
                 'WikipediaCategory':"http://en.wikipedia.org/wiki/Category:",
                 'Wikibooks':"http://en.wikibooks.org/wiki/",

                 'OtherWiki':gen_wikiPath(exporter,'OtherWiki')
                 }
         for prefix,myurl in interwiki_map.iteritems():
             if insToken.value == prefix:
                 params=u""
                 for i, apx in enumerate(insToken.appendices):
                     params += "%s" % (apx)
                 nice_params=unicode(params).replace("%20"," ").replace("%28","(").replace("%29",")")
                 result = "["+myurl+params+" | "+prefix+": "+nice_params +"]"
         return result


     def getExtraFeatures(self):
         """
         Returns a list of bytestrings describing additional features supported
         by the plugin. Currently not specified further.
         """
         return ()
