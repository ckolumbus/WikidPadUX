# Show the abstract syntax tree (AST) of a page. Helpful when creating/modifying a wiki language
# Works with WikidPad 2.0 and later
# Install: Put the source into "WikidPad/user_extensions/pageAstView.py" and restart WikidPad.

import wx


WIKIDPAD_PLUGIN = (("MenuFunctions", 1),)


def describeMenuItems(wiki):
    return (
            (showPageAstSource, _(u"PageAst source") + u"\t",
            _(u"Show page-ast source")),
            )


class SourceView(wx.TextCtrl):
    def __init__(self, presenter, parent, ID):
        wx.TextCtrl.__init__(self, parent, ID,
                style=wx.TE_MULTILINE | wx.TE_DONTWRAP )
        self.presenter = presenter

        self.visible = False
        self.outOfSync = True
        
        self.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL))


    def close(self):
        pass


    def setLayerVisible(self, vis, scName=""):
        """
        Informs the widget if it is really visible on the screen or not
        """
        if vis:
            docPage = self.presenter.getDocPage()
            if docPage is None:
                return

            pageAst = docPage.getLivePageAst()
            
            self.SetValue(pageAst.pprint())

        self.visible = vis


def showPageAstSource(wiki, evt):
    presenter = wiki.getCurrentDocPagePresenter()
    if presenter is None:
        return

    rc = presenter.getSubControl("pageAst source")
    if rc is None:
        rc = SourceView(presenter, presenter, -1)
        
        presenter.setSubControl("pageAst source", rc)

    presenter.switchSubControl("pageAst source")
