Chris' WikidPad User Extensions
===============================
All extension listed here are for [WikidPad](http://wikidpad.sourceforge.net), simply the best personal wiki around!

As I don't find much time to develop stuff completly from scratch I usally base it on existing work. Add-in's developed based on others work are listed here together with the references on where to find them and on which original version I based my work on.

HowTo Use
---------

My personal usage is to clone this repository next to my WikidPad.git repository (checkedout via
the `git svn` command) and [symlink](http://schinagl.priv.at/nt/hardlinkshellext/hardlinkshellext.html) the `user_extensions` directory from the `WikidPadUX` to the `WikidPad` repo.

As an alternative just copy the individual files into your local WikdPad `user_extensions` 
directory.


Open Wishlist
-------------

Things I want but maybe didn't even start

  * checkbox lists like Zim or Github Flavored Markdown
  * reStructuredText pages (not whole wiki)
  * export to HTML5/CSS presentation format (dzSlides, S3reloaded)



Changes to existing Add-Ins
---------------------------

For a list of links to the original add-in see below.

DynSearchResults
  * fixed the access to the wikiDataManager for newer WikidPad Versions
    
CalendarControl
  * as I'm in germany some month names have diaeresis in it and that causes
    problems.  As a workaround I hardcoded the english locale within the add-in
    which is fine for me. Maybe someone else can propse a better solution.
                        

InterWikiLinks 
  * I added the functionality to keep the interwiki link
    mapping in an external YAML file instead of having it
    hardcoded within the add-in. It will be automatically
    created within the `GlobalConfigSubDir` if it doesn't
    exist yet. There are some examples listed and the file
    can then be edded with any text editor. The format
    should be obvious from the examples.

Blog
  * added 'Blog ' to each page name to avoid clash with the CalendarControl
    addin

TodoExtension
  * added 'yyyymmdd' date format 

Own Development
---------------

### FileManager Plugin

(should) simplify the handling of files in the wiki-local storage section.
Still *very* rudementary. Maybe better start a full fledged file manger instead
of (re-)prorgramming a new one.

Files:
  * DirTreeCtrl.py
  * FileManager.py
  * FileManagerPlugin.py


### additional parsers

Playing around with parsers to get other major markup languages available
within WikidPad. I'm mainly interested in some reStructredText suppor.

  * EmptyParser.py
  * MarkdownParser.py
  * MediawikiParser.py
  * MiniParser.py
  * RstParser.py


WikidPad Internal Component Extensions
--------------------------------------

Usually I'm working of the latest svn version of WikidPad. My addins are updated with the original code.
Currently base: WikidPad 2.3beta12 

 * `CKolHtmlExporter.py`: based on `extensions/HtmlExporter.py`
 * `CKolWikidPadParser.py` : from `extensions/wikidPadParser/WikidPadParser.py`
 * `CKolHtmlEntityStrings.py`: my addition to list mapping from strings to entities 

Interestingly the `CKolHtmlExporter` seems to replaces the internal default one. Therefore the preview
and standard export already uses the string-to-entity replacement without further actions.
I haven't figured out the detailed workings but for now this is OK for me :-).


Add-In Base Versions
--------------------

 * [Blog.py](https://sites.google.com/site/workbenchofstuff/home/blogger) - 
Version: 1.0.5,
Date: 2008-12-02,
Author: Michael Allison
 * [CalendarControl.py](http://calendarcontrol.wikidot.com/) - 
Version: 009, 
Date: 2011,
Author: Bill Wilkinson
 * [DynSearchResults.py](http://www.fsavard.com/flow/wikidpad-dynamic-search-results/) - 
Version: 2008.10.22,
Author: François Savard
 * [WikidpadInterWiki.py](trac.wikidpad2.webfactional.com/wiki/WikidpadInterWiki) -
Version: 2011-12-16 (wiki change date)
Author: M. Butscher(?)
 * [TodoExtension.py](http://www.ziemski.net/wikidpad/todo_extension.html) - 
Version: 2014-03-02 beta
Author: Christian Ziemski
