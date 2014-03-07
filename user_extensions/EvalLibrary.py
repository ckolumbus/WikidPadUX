from pwiki.StringOps import urlFromPathname, strftimeUB

def now():
    return strftimeUB("%x %I:%M %p")

def addDateTime(editor):
    return editor.AddText(now())

def date():
    return strftimeUB("%x")

def addDate(editor):
    return editor.AddText(date())

def time():
    return strftimeUB("%I:%M %p")

def addTime(editor):
    return editor.AddText(time())

def encodeSelection(editor):
    text = editor.GetSelectedText()
    url = urlFromPathname(text)
    editor.ReplaceSelection("file:%s" % url)
    
def getOccurences(pwiki, pattern, sec1="\\A", sec2="\\Z"):
		import re
		content = pwiki.getCurrentDocPage().getContent()
		result = -1
		try:
			section =  re.search(sec1+"(.*)"+sec2, content, re.M|re.S).group(1)
			result = len(re.findall(pattern,section))
		except:
			pass
		return result
		
def sortSelection(editor):
		text = editor.GetSelectedText()
		a = text.splitlines()
		a.sort()
		t2 = '\n'.join(a)
		editor.ReplaceSelection(t2)
		
def listFiles(editor, startdir, recurse=False):
		for root, dirs, files in os.walk(startdir):
			if not recurse:
				break 
			pass