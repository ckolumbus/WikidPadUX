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

from pwiki.SystemInfo import isWindows
from WikidPadStarter import VERSION_STRING

WIKIDPAD_VERSION = VERSION_STRING[9:12]

from FileManager import FileManager

# ////////////////////   
#   Helper functions
# \\\\\\\\\\\\\\\\\\\\


def check_wikidpad_version():
    """ Checks if we are running on Wikidpad 1.9 """
    if WIKIDPAD_VERSION == '1.9':
        dlg = wx.MessageDialog(None, 'This version of File Manager  plugin is not compatible with Wikidpad 1.9.', 
                               'File Manager', style=wx.OK | wx.ICON_EXCLAMATION)
        dlg.ShowModal()
        return(True)

# //////////////////////   
#    WIKIDPAD HOOKS
# \\\\\\\\\\\\\\\\\\\\\\

# Descriptor for File Manager plugin
WIKIDPAD_PLUGIN = (('MenuFunctions',1),('Options', 0))


# /// Register menu item \\\
def describeMenuItems(wiki):
    keybindings = wiki.getKeyBindings()

    kb = keybindings.FileManager
    if kb == '':
        kb = u'Ctrl-Alt-M'

    return ((file_manager, u'File Manager' + u'\t' + kb , ''),)


# ///////////////////////////////////////
#    Main function called by Wikidpad 
# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def file_manager(wiki, evt):

    """ File Manager main function called by WikidPad """ 

    # Check compatible versions
    #if check_wikidpad_version():
    #    return

    file_manager_window = wiki.FindWindowByName('file_manager_window_frame')

    if  file_manager_window is not None:
        file_manager_window.Raise()
        return

    file_manager_window = FileManager(wiki, '/home/chris', "Wiki File")
    file_manager_window.Show()
    file_manager_window.Raise() 


#EOF
