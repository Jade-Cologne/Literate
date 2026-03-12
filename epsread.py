import warnings #annoying deprication warning in debugging
warnings.filterwarnings("ignore", category=FutureWarning)

import io
from pathlib import Path

import ebooklib
from ebooklib import epub

import html.parser
from html.parser import HTMLParser

def getdata(bookpath):
    book = epub.read_epub(bookpath, options={"ignore_ncx":True}) #sets up epubbook reader

    class bodyparser(HTMLParser): #create htmlparser class and tags
        def handle_starttag(self, tag, attrs): #start tag for body parser
            if tag == "body":
                # print("open")
                self.isbody = True
        def handle_endtag(self, tag): #end tag for body parser
            if tag == "body":
                # print("close body")
                self.isbody = False
        def handle_data(self, data):
            if self.isbody == True:
                self.bodytext.append(data)

    textget = bodyparser() #declare htmlparser
    textget.bodytext = [] #body text handler
    textget.isbody = False #body tag boolean

    # chnum = 0
    wordcounts = [] #list of wordcounts
    maxwc = 0
    avgwc = 0
    
    for chapter_id, linear in book.spine: #iterate through chapter list
        if linear == "yes": #and chapter_id != "titlepage": #get rid of unordered items
            textget.bodytext = [] #reset parser text every chapter
            testchapter = book.get_item_with_id(chapter_id) #get chapter item
            textget.feed(testchapter.get_content().decode('utf-8')) #feed the text content of the chapter to the parser
            # chtext = ' '.join(textget.bodytext) #raw text
            chwords = ' '.join(textget.bodytext).split() #get words by combining html elements and separating words
            chwc = len(chwords) #get wordcount via length of string array | this step could be done inline to get rid of chwords but looks terrible
            if chwc > 100:
                # chnum += 1
                # print("Chapter",chnum)
                wordcounts.append(chwc)
                # print("Wordcount:",chwc)
    maxwc = max(wordcounts)
    avgwc = (sum(wordcounts) // len(wordcounts))
    # print(wordcounts, "max word count=", maxwc, "average word count=", avgwc)
    return wordcounts, maxwc, avgwc

#print(testchapter.get_content().decode('utf-8'))
#print(textget.bodytext)
