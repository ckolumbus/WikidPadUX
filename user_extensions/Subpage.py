# Install: Put the source below into "WikidPad/user_extensions/Subpage.py"
# and restart WikidPad.
# Press CTRL-ALT-S to insert a link to a subpage of the current page.
# Look into the code if you want to customize the link; it's easy.

WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

def describeMenuItems(wiki):
	return ((subPagePlugin, "Create Subpage\tCtrl-Alt-S", "Create Subpage"),)

def subPagePlugin(pwiki, evt):
	editor=pwiki.getActiveEditor()
	oldPos=editor.GetCurrentPos()
	editor.AddText("[ - "+pwiki.getCurrentWikiWord()+"]")
	editor.SetCurrentPos(oldPos+1)
	editor.SetAnchor(oldPos+1)