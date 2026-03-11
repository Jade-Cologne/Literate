import io
from pathlib import Path

import ebooklib
from ebooklib import epub

import html.parser
from html.parser import HTMLParser

bookname = "TheAgeOfReason.epub" # finalname

book = epub.read_epub(bookname, options={"ignore_ncx":True}) #sets up epubbook reader

class bodyparser(HTMLParser): #create htmlparser class and tags
    def handle_starttag(self, tag, attrs):
        if tag == "body":
            # print("open")
            self.isbody = True
    def handle_endtag(self, tag):
        if tag == "body":
            # print("close body")
            self.isbody = False
    def handle_data(self, data):
        if self.isbody == True:
            self.bodytext.append(data)

textget = bodyparser() #declare htmlparser
textget.bodytext = [] #body text handler
textget.isbody = False #body tag boolean

chnum = 0
for chapter_id, linear in book.spine: #iterate through chapter list
    if linear == "yes": #and chapter_id != "titlepage": #get rid of unordered items
        textget.bodytext = [] #reset parser text
        testchapter = book.get_item_with_id(chapter_id) #get chapter item
        textget.feed(testchapter.get_content().decode('utf-8')) #feed the text content of the chapter to the parser
        #chtext = ' '.join(textget.bodytext)
        chwords = ' '.join(textget.bodytext).split() #get words by combining html elements and separating words
        chwc = len(chwords) #get wordcount via length of string array
        if chwc > 100:
            chnum += 1
            print("Chapter",chnum)
            print("Wordcount:",chwc)

#print(testchapter.get_content().decode('utf-8'))
#print(textget.bodytext)
