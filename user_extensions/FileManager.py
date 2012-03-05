# -*- coding: utf-8 -*-
"""
    filemanager
    
    @summary: a file manager plugin for WikidPad to insert and maintain local
              files from within WikidPad
    @author: Chris Drexler
    @date:   4-Mar-2012
    @license: GPL
    @version: 0.1.0
        
    @todo:
        - allow multi selects
        - add file drops on manager to insert files into file storage
        - add function that "copy file" on drop utiles current directory
          selection
"""


import wx
import os
import sys


import DirTreeCtrl

# Adopted from http://wiki.wxpython.org/TreeCtrlDnD
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, tree):
        wx.FileDropTarget.__init__(self)
        self.tree = tree
        self.selections=[]

    def OnDropFiles(self, x, y, filenames):
        try:
		item, flags = self.tree.HitTest((x,y))
		dir = self.tree.GetPyData(item).directory
		if not os.path.isdir(dir):
		   dir = os.path.dirname(dir)
		print(dir)
		for name in filenames:
		    print(name)
	except:
		pass
            
    def _saveSelection(self):
       self.selections = self.tree.GetSelections()
       self.tree.UnselectAll()
    
    def _restoreSelection(self):
       self.tree.UnselectAll()
       for i in self.selections:
           self.tree.SelectItem(i)
       self.selections=[]
       
    def OnEnter(self, x, y, d):
       self._saveSelection()
       return d
    
    def OnLeave(self):
       self._restoreSelection()
    
    def OnDrop(self, x, y):
       self._restoreSelection()
       #item, flags = self.tree.HitTest((x, y))
       #print "got an drop event at", x, y
       return True
    
    def OnDragOver(self, x, y, d):
       # provide visual feedback by selecting the item the mouse is over
       item, flags = self.tree.HitTest((x,y))
       selections = self.tree.GetSelections()
       if item:
           if selections != [item]:
               self.tree.UnselectAll()
               self.tree.SelectItem(item)
       elif selections:
           self.tree.UnselectAll()
           
       return d          
           
class FileManager(wx.Frame):
    def __init__(self, parent, root, name = None):
        wx.Frame.__init__(self, parent, -1, "File Manager", size=(250, 650),
                          name='file_manager_window_frame' )

        self.tree = DirTreeCtrl.DirTreeCtrl(self)
        self.tree.SetRootDir(root, name)

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDirCtrlDragInit, id=self.tree.GetId())
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelect, id=self.tree.GetId())

        dt = MyFileDropTarget(self.tree)
        self.tree.SetDropTarget(dt)
        
        self.OnSelect(0)
        self.Centre()
        self.Show(True)

    def OnSelect(self, event):
        return

    def OnDirCtrlDragInit(self, event):
        f = None
        #item = self.tree.GetSelection()
        item, flags = self.tree.HitTest(event.GetPoint())
        f = self.tree.GetPyData(item).directory

        tdo = wx.FileDataObject()
        tdo.AddFile(f)
        tds = wx.DropSource(self.tree)
        tds.SetData(tdo)
        tds.DoDragDrop(True)


if __name__ == "__main__":
    app = wx.App()
    FileManager (None, '/', "RootName")
    app.MainLoop()

#EOF
