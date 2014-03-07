import os, urllib, re
import wx

# Extension handles :vector: insertion by calling external rasterizer to convert vector image to png.
# Also adds toolbar and menu options to launch external vector graphics editor.

from pwiki.StringOps import mbcsEnc

WIKIDPAD_PLUGIN = (("InsertionByKey", 1), ("Options", 1), ("MenuFunctions",1), ("ToolbarFunctions",1))

def describeMenuItems(wiki):
    return ((VectorEditor, "Vector graphics editor\t", "Run external graphics editor"),)

def describeToolbarItems(wiki):
    return ((VectorEditor, "Vector graphics editor", "Run external graphics editor", ("brush",)),)

def VectorEditor(wiki, evt):
    editor_path = wiki.getConfig().get("main", "plugin_rasterizer_editor", "")
    seltext = wiki.getActiveEditor().GetSelectedText()
    seltext_files = re.findall('[a-zA-Z0-9]+\.[a-zA-Z0-9]{3}',seltext)
    if len(seltext_files) !=0:
        cmdline = '"%s\\%s"' % (wiki.wikiData.wikiData.dataDir, seltext_files[0])
    else:
        cmdline = '"%s\\sketch.svg"' % (wiki.wikiData.wikiData.dataDir)
        wiki.getActiveEditor().AddText('[:vector: sketch.svg]')
    try:
        os.spawnl(os.P_NOWAIT, editor_path, editor_path, cmdline)
    except:
        wiki.stdDialog('o', 'Error running external graphics editor', 'Please check plugin options.\nCommand line:\n%s %s' % (editor_path, cmdline), additional=None)

def describeInsertionKeys(ver, app):
    return ((u"vector", ("html_single", "html_previewWX", "html_preview",
            "html_multi"), RasterizerHandler),)

class RasterizerHandler:
    """
    Class fulfilling the "insertion by key" protocol.
    """
    def __init__(self, app):
        self.app = app
        self.RasterizerExe = None

    def taskStart(self, exporter, exportType):
        # Find rasterizer executable by configuration setting
        self.RasterizerExe = self.app.getGlobalConfig().get("main", "plugin_rasterizer_exePath", "")
        self.inSwitch = self.app.getGlobalConfig().get("main", "plugin_rasterizer_inSwitch", "")
        self.outSwitch = self.app.getGlobalConfig().get("main", "plugin_rasterizer_outSwitch", "")
        self.otherSwitch = self.app.getGlobalConfig().get("main", "plugin_rasterizer_otherSwitch", "")

    def taskEnd(self):
        pass

    def createContent(self, exporter, exportType, insToken):

        file_path = exporter.wikiDocument.getDataDir() + '\\' + insToken.value
        if not os.access(file_path, os.F_OK):
            return u"<pre>[Image unavailable: %s]</pre>" % file_path

        if self.RasterizerExe == "":
            # No path to rasterizer executable -> show message
            return "<pre>[Please set path to Rasterizer executable]</pre>"

        # Get exporters temporary file set (manages creation and deletion of
        # temporary files)
        tfs = exporter.getTempFileSet()

        pythonUrl = (exportType != "html_previewWX")
        dstFullPath = tfs.createTempFile("", ".png", relativeTo="")
        url = tfs.getRelativeUrl(None, dstFullPath, pythonUrl=pythonUrl)
        cmdline = '%s "%s" %s "%s" %s' % (self.inSwitch, file_path, self.outSwitch, dstFullPath, self.otherSwitch)
        try:
            # Run external application
            os.spawnl(os.P_WAIT, self.RasterizerExe, self.RasterizerExe, cmdline)
        except:
            return u"<pre>[ Error occured while converting to png] </pre>"

        # Return appropriate HTML code for the image
        if exportType == "html_previewWX":
            # Workaround for internal HTML renderer
            return u'<img src="%s" border="0" align="bottom" />&nbsp;' % url
        else:
            return u'<img src="%s" border="0" align="bottom" />' % url

    def getExtraFeatures(self):
        return ()

def registerOptions(ver, app):
    # Register option
    app.getDefaultGlobalConfigDict()[("main", "plugin_rasterizer_exePath")] = u""
    app.getDefaultGlobalConfigDict()[("main", "plugin_rasterizer_inSwitch")] = u""
    app.getDefaultGlobalConfigDict()[("main", "plugin_rasterizer_outSwitch")] = u"-o"
    app.getDefaultGlobalConfigDict()[("main", "plugin_rasterizer_otherSwitch")] = u"-x png"
    app.getDefaultGlobalConfigDict()[("main", "plugin_rasterizer_editor")] = u""
    # Register panel in options dialog
    app.addOptionsDlgPanel(RasterizerOptionsPanel, u"  Rasterizer")

class RasterizerOptionsPanel(wx.Panel):
    def __init__(self, parent, optionsDlg, app):
        wx.Panel.__init__(self, parent)
        self.app = app

        pt = self.app.getGlobalConfig().get("main", "plugin_rasterizer_exePath", u"")
        self.rsPath = wx.TextCtrl(self, -1, pt)

        pt = self.app.getGlobalConfig().get("main", "plugin_rasterizer_inSwitch", u"")
        self.inSwitch = wx.TextCtrl(self, -1, pt)

        pt = self.app.getGlobalConfig().get("main", "plugin_rasterizer_outSwitch", u"-o")
        self.outSwitch = wx.TextCtrl(self, -1, pt)

        pt = self.app.getGlobalConfig().get("main", "plugin_rasterizer_otherSwitch", u"-x png")
        self.otherSwitch = wx.TextCtrl(self, -1, pt)

        pt = self.app.getGlobalConfig().get("main", "plugin_rasterizer_editor", u"-x png")
        self.edPath = wx.TextCtrl(self, -1, pt)

        mainsizer = wx.FlexGridSizer(5, 2, 0, 0)

        mainsizer.AddGrowableCol(1, 1)

        mainsizer.Add(wx.StaticText(self, -1, _(u"Path to rasterizer:")), 0,
                wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(self.rsPath, 1, wx.ALL | wx.EXPAND, 5)

        mainsizer.Add(wx.StaticText(self, -1, _(u"Input file switch:")), 0,
                wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(self.inSwitch, 1, wx.ALL | wx.EXPAND, 5)

        mainsizer.Add(wx.StaticText(self, -1, _(u"Output file switch:")), 0,
                wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(self.outSwitch, 1, wx.ALL | wx.EXPAND, 5)

        mainsizer.Add(wx.StaticText(self, -1, _(u"Other commandline options:")), 0,
                wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(self.otherSwitch, 1, wx.ALL | wx.EXPAND, 5)

        mainsizer.Add(wx.StaticText(self, -1, _(u"Path to editor:")), 0,
                wx.ALL | wx.EXPAND, 5)
        mainsizer.Add(self.edPath, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(mainsizer)
        self.Fit()

    def setVisible(self, vis):
        return True

    def checkOk(self):
        return True

    def handleOk(self):
        pt = self.rsPath.GetValue()
        self.app.getGlobalConfig().set("main", "plugin_rasterizer_exePath", pt)

        pt = self.inSwitch.GetValue()
        self.app.getGlobalConfig().set("main", "plugin_rasterizer_inSwitch", pt)

        pt = self.outSwitch.GetValue()
        self.app.getGlobalConfig().set("main", "plugin_rasterizer_outSwitch", pt)

        pt = self.otherSwitch.GetValue()
        self.app.getGlobalConfig().set("main", "plugin_rasterizer_otherSwitch", pt)

        pt = self.edPath.GetValue()
        self.app.getGlobalConfig().set("main", "plugin_rasterizer_editor", pt)