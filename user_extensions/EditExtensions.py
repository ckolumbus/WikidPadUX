# Edit Extensions plugin for WikidPad 
# by alessandro orsi, 21 Jul 2009
# licence: GPL
# tested with: wikidpad 2.0beta5_1 on Windows XP SP2
# version: 0.1a
# see ReadMe.txt for more information


# === Modules ===

import wx

import re

import locale


# === Locale === 
# set the locale to the system locale for sorting ===

locale.setlocale(locale.LC_ALL, '')


# === wx classes ===


# Following dialog used by "Insert before/after lines", "Enclose selection" and "StripFirstChars"
#
# Parameters: 	parent(=wiki), dialogue_title, label_of_first_text_box, label_of_second_text_box, 
#				number_of_controls_to_show, x_size_of_the_frame, y_size_of_the_frame
#
# If number_of_controls_to_show is 2, shows both text boxes, otherwise only one

class UserInputDlg(wx.Dialog):

	first_txtctrl_value = ""
	second_txtctrl_value = ""
	controls_num = 0

	def __init__(self, parent, title, label_first_txtctrl, label_second_txtctrl, num_of_controls, x_size, y_size):
		wx.Dialog.__init__(self, parent, -1, title, size=(x_size, y_size))
		
		# Same color as Wikidpad dialogs
		self.SetBackgroundColour('#E0DFE3') 

		self.controls_num = num_of_controls
	
		
		# === Define widgets ===
		
		# Static text widget for first text control
		self.LabelFirstTxtCtrl = wx.StaticText(self, label=label_first_txtctrl)
		
		# Input field for first text control
		self.InputFieldFirstTxtCtrl = wx.TextCtrl(self, size=wx.Size(195, -1))


		if self.controls_num == 2:
			
			# Static text widget for second text control
			self.LabelSecondTxtCtrl = wx.StaticText(self, label=label_second_txtctrl)
		
			# Input field for second text control
			self.InputFieldSecondTxtCtrl = wx.TextCtrl(self, size=wx.Size(195, -1))
		
		
		# Ok/Cancel buttons
		BtnSize = wx.Button.GetDefaultSize()
		
		self.OkBtn = wx.Button(self, wx.ID_OK, '', (0, 0), BtnSize )
		
		self.CancelBtn = wx.Button( self, wx.ID_CANCEL, '', (120, 0), BtnSize )


		# === Define sizers ===
		
		# == Horizontal sizer for buttons ==
		self.HorizSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		# Add buttons to sizer
		self.HorizSizer.Add(self.OkBtn, 0)
		
		self.HorizSizer.Add(self.CancelBtn, 0, wx.LEFT, 15)
		
		
		# == Vertical sizer for labels, input boxes and buttons ==
		self.VertSizer = wx.BoxSizer(wx.VERTICAL)

		# Add first text control label and input box to sizer
		self.VertSizer.Add(self.LabelFirstTxtCtrl, 0, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
		
		self.VertSizer.Add(self.InputFieldFirstTxtCtrl, 0, wx.BOTTOM | wx.LEFT, 5)
		
		if self.controls_num == 2:
			# Add second text control label and input box to sizer
			self.VertSizer.Add(self.LabelSecondTxtCtrl, 0, wx.TOP | wx.BOTTOM | wx.LEFT, 5)
		
			self.VertSizer.Add(self.InputFieldSecondTxtCtrl, 0, wx.BOTTOM | wx.LEFT, 5)
		
		# Add horizontal sizer containing buttons to vertical sizer
		self.VertSizer.Add(self.HorizSizer, 0, wx.ALIGN_CENTER | wx.TOP, 10)
		
		# Set sizers
		self.SetSizer(self.VertSizer)
		
		# Button events
		self.OkBtn.Bind(wx.EVT_BUTTON, self.Ok)

		self.CancelBtn.Bind(wx.EVT_BUTTON, self.Cancel)


	# === Events handling functions === 
	
	def Ok(self, event):
		
		# Store values entered in the input boxes
		self.first_txtctrl_value = self.InputFieldFirstTxtCtrl.GetValue()
		
		if self.controls_num == 2:
			self.second_txtctrl_value = self.InputFieldSecondTxtCtrl.GetValue()
		

		# Check if both values are empty (user didn't enter any value)
		if self.first_txtctrl_value == self.second_txtctrl_value == "":
			self.EndModal(wx.ID_CANCEL)
			return
		
		self.EndModal(wx.ID_OK)
		return
		
	
	def Cancel(self, event):
		self.EndModal(wx.ID_CANCEL)
		return
		



# === Common functions ===

def GetSelection(wiki):
	# Get selection
	SelectedText = wiki.getActiveEditor().GetSelectedText()
	
	# Check if selection is empty
	if SelectedText == "":
		WarnMsg("Select some text first.")
		return None

	else:
		#Trim spaces
		SelectedText = SelectedText.strip()
		return SelectedText	
	

def WarnMsg(msg_text):
	msg = wx.MessageDialog(None, msg_text, 'Edit Extensions', wx.OK)
	msg.ShowModal()
	return
	


# === Menu items ===

# descriptor for EditorFunctions plugin type
WIKIDPAD_PLUGIN = (("MenuFunctions",1),)

def describeMenuItems(wiki):
	global nextNumber
	return ((Uppercase, "Edit Extensions|UPPERCASE\tAlt-U", "Turns selected text to uppercase"),
			(Lowercase, "Edit Extensions|lowercase\tAlt-L", "Turns selected text to lowercase"),
			(SentenceCase, "Edit Extensions|Sentence case\tAlt-S", "Capitalize the first character of each line in the selected text"),
			(TitleCase, "Edit Extensions|Title Case\tAlt-T", "Capitalize the first character of each word in the selected text"),
			(SwapCase, "Edit Extensions|sWAP cASE\tAlt-P", "Swap the case of each character in the selected text"),
			(SortLines, "Edit Extensions|Sort lines\tAlt-O", "Sort alphabetically the lines of the selected text"),
			(EncloseSelection, "Edit Extensions|Enclose selection\tAlt-N", "Add chosen text before and/or after the selected text"),
			(InsertBeforeAfter, "Edit Extensions|Insert before/after lines\tAlt-I", "Add chosen text before and/or after each line in selection"),
			(StripFirstChars, "Edit Extensions|Strip from the beginning of line\tAlt-B", "Delete n characters from the beginning of each line in the selected text"),
			(StripLastChars, "Edit Extensions|Strip from the end of line\tAlt-E", "Delete n characters from the end of each line in the selected text"),
			(RemoveSpaces, "Edit Extensions|Remove spaces\tAlt-R", "Removesspaces from the beginning and the end of each line in the selected text"),
			(CompressSpaces, "Edit Extensions|Compress spaces\tAlt-M", "Remove multiple spaces between words in the selected text"),
			(ShowHideSpaces, "Edit Extensions|Show/Hide white spaces", "Show or hide white spaces and tabs markers"),
			(ShowHideEOL, "Edit Extensions|Show/Hide end of line marker", "Show or hide a marker at the end of each line"),)
	


# === Functions ===

def Uppercase(wiki, evt):

	if GetSelection(wiki) is not None:
	
		text = GetSelection(wiki)	

		text = text.upper()

		wiki.getActiveEditor().ReplaceSelection(text)
		

def Lowercase(wiki, evt):

	if GetSelection(wiki) is not None:

		text = GetSelection(wiki)	

		text = text.lower()

		wiki.getActiveEditor().ReplaceSelection(text)
	

def SentenceCase(wiki, evt):

	if GetSelection(wiki) is not None:

		text = GetSelection(wiki)
		
		# Store lines in a list
		lines = text.rsplit('\n')

		for id in range(len(lines)):	
				
			lines[id] = lines[id].capitalize()

		# Convert the list in a string
		modified_lines = "\n".join(lines)

		wiki.getActiveEditor().ReplaceSelection(modified_lines)


def TitleCase(wiki, evt):

	if GetSelection(wiki) is not None:

		text = GetSelection(wiki)	

		text = text.title()

		wiki.getActiveEditor().ReplaceSelection(text)
	

def SwapCase(wiki, evt):

	if GetSelection(wiki) is not None:

		text = GetSelection(wiki)	

		text = text.swapcase()

		wiki.getActiveEditor().ReplaceSelection(text)
	

def SortLines(wiki, evt):
	
	if GetSelection(wiki) is not None:
	
		text = GetSelection(wiki)	
		
		# Store lines in a list
		lines = text.rsplit('\n')

		# Sort according to the system locale. Works in Windows, needs testing on other systems
		lines.sort(cmp=locale.strcoll)
		
		sorted_lines = "\n".join(lines)
		
		wiki.getActiveEditor().ReplaceSelection(sorted_lines)



def EncloseSelection(wiki, evt):
	
	if GetSelection(wiki) is not None:
	
		text = GetSelection(wiki)
		
		Dialog = UserInputDlg(wiki, "Enclose selection", "Insert before selection:", "Insert after selection:", 2, 215, 180)
		Dialog.Centre()
		
		if Dialog.ShowModal() == wx.ID_OK:
			
			prepend = Dialog.first_txtctrl_value
			
			append = Dialog.second_txtctrl_value	
			
			text = prepend + text + append
			
			wiki.getActiveEditor().ReplaceSelection(text)
	


def InsertBeforeAfter(wiki, evt):

	if GetSelection(wiki) is not None:
	
		text = GetSelection(wiki)

		Dialog = UserInputDlg(wiki, "Insert before/after lines", "Insert before:", "Insert after:", 2, 215, 180)
		Dialog.Centre()
		
		if Dialog.ShowModal() == wx.ID_OK:
			
			prepend = Dialog.first_txtctrl_value
			
			append = Dialog.second_txtctrl_value	
			
			# Store lines in a list
			lines = text.rsplit('\n')
			
			for id in range(len(lines)):
				
				# Modify line only if it's not blank
				if lines[id] != "":
					lines[id] = prepend + lines[id] + append
				
			# Convert the list in a string
			modified_lines = "\n".join(lines)

			wiki.getActiveEditor().ReplaceSelection(modified_lines)



def StripFirstChars(wiki, evt):
	StripChars(wiki, evt, "Strip from beginning of line", True)


	
def StripLastChars(wiki, evt):
	StripChars(wiki, evt, "Strip from end of line", False)



def StripChars(wiki, evt, title, from_beginning):

	if GetSelection(wiki) is not None:

		text = GetSelection(wiki)	
		
		Dialog = UserInputDlg(wiki, title, "Number of characters to delete:", "", 1, 215, 120)
		Dialog.Centre()
		
		if Dialog.ShowModal() == wx.ID_OK:
			
			strip_n_chars = Dialog.first_txtctrl_value
			
			# Check if the entered value is a number
			if not strip_n_chars.isdigit():
				WarnMsg("Only numbers allowed.")
				return
				
			strip_n_chars = int(strip_n_chars)
			
			# Store lines in a list
			lines = text.rsplit('\n')
			
			for id in range(len(lines)):
				
				line_length = len(lines[id])

				# Strip characters only when the number of characters to strip is less than
				# the total length of the line
				if strip_n_chars <  line_length:
					
					actual_line = lines[id]
					
					if from_beginning == True:
						lines[id] = actual_line[strip_n_chars:line_length]
					
					else:
						
						lines[id] = actual_line[:-strip_n_chars]

						
			
			stripped_lines = "\n".join(lines)

			wiki.getActiveEditor().ReplaceSelection(stripped_lines)



def RemoveSpaces(wiki, env):

	if GetSelection(wiki) is not None:

			text = GetSelection(wiki)
			
			# Store lines in a list
			lines = text.rsplit('\n')

			for id in range(len(lines)):	
					
				lines[id] = lines[id].strip()

			# Convert the list in a string
			modified_lines = "\n".join(lines)

			wiki.getActiveEditor().ReplaceSelection(modified_lines)	



def CompressSpaces(wiki, env):

	if GetSelection(wiki) is not None:

		text = GetSelection(wiki)	

		text = re.sub(r'[ ]{2,}', " ", text)

		wiki.getActiveEditor().ReplaceSelection(text)



def ShowHideSpaces(wiki, env):

	state = wiki.getActiveEditor().GetViewWhiteSpace()
	
	if state == 0:
	
		# 1: turn on markers
		wiki.getActiveEditor().SetViewWhiteSpace(1)
		
		# Show markers in red (#FF0000)
		wiki.getActiveEditor().SetWhitespaceForeground(1, "#FF0000")
		
		
	else:
		
		# 0: turn off markers
		wiki.getActiveEditor().SetViewWhiteSpace(0)
		

def ShowHideEOL(wiki, env):

	state = wiki.getActiveEditor().GetViewEOL()
	
	if state == 0:
	
		# 1: turn on markers
		wiki.getActiveEditor().SetViewEOL(1)
		
		# Show markers in red (#FF0000)
		wiki.getActiveEditor().SetWhitespaceForeground(1, "#FF0000")
		
		
	else:
		
		# 0: turn off markers
		wiki.getActiveEditor().SetViewEOL(0)



#EOF