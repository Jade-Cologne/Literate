import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import re
from statistics import stdev

import ebooklib
from ebooklib import epub
from html.parser import HTMLParser
import pyphen

minwc = 200
_dic  = pyphen.Pyphen(lang='en_US')


def _flatten_toc(toc):
    titles = {}
    for item in toc:
        if isinstance(item, epub.Link):
            href = item.href.split('#')[0]
            titles[href] = item.title
        elif isinstance(item, tuple):
            section, children = item
            if hasattr(section, 'href') and section.href:
                href = section.href.split('#')[0]
                titles[href] = section.title
            titles.update(_flatten_toc(children))
    return titles


def _syllables(word):
    result = _dic.inserted(word)
    if '-' in result:
        return len(result.split('-'))
    return max(1, len(re.findall(r'[aeiou]+', word)))


def _dialogue_ratio(text):
    # Curly quotes are directional — no apostrophe ambiguity
    double_curly  = re.findall(r'\u201c[^\u201d]{1,3000}\u201d', text)
    single_curly  = re.findall(r'\u2018[^\u2019]{1,3000}\u2019', text)
    # Straight double quotes
    double_straight = re.findall(r'"[^"]{1,3000}"', text)
    # Straight single quotes: only where not preceded/followed by a word character
    # (excludes contractions like "it's", possessives like "John's")
    single_straight = re.findall(r"(?<!\w)'[^']{1,3000}'(?!\w)", text)

    all_spans   = double_curly + single_curly + double_straight + single_straight
    quoted_words = sum(len(s.split()) for s in all_spans)
    total_words  = len(text.split())
    return quoted_words / total_words if total_words else 0.0


def getdata(bookpath):
    book = epub.read_epub(bookpath, options={"ignore_ncx": True})
    toc_titles = _flatten_toc(book.toc)

    class bodyparser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == "body":
                self.isbody = True
        def handle_endtag(self, tag):
            if tag == "body":
                self.isbody = False
        def handle_data(self, data):
            if self.isbody:
                self.bodytext.append(data)

    textget = bodyparser()
    textget.bodytext = []
    textget.isbody   = False

    wordcounts       = []
    chapter_titles   = []
    chapter_dialogue = []
    all_words        = []
    total_sentences  = 0
    total_syllables  = 0
    total_dialogue_words = 0

    for chapter_id, linear in book.spine:
        if linear == "yes":
            textget.bodytext = []
            item = book.get_item_with_id(chapter_id)
            textget.feed(item.get_content().decode('utf-8'))
            text    = ' '.join(textget.bodytext)
            chwords = text.split()
            chwc    = len(chwords)

            if chwc > minwc:
                wordcounts.append(chwc)

                clean_words = [re.sub(r"[^a-z']", '', w.lower()) for w in chwords]
                clean_words = [w for w in clean_words if w]
                all_words.extend(clean_words)

                total_sentences += max(len(re.findall(r'[.!?]+(?:\s|$)', text)), 1)
                total_syllables += sum(_syllables(w) for w in clean_words)

                ratio = _dialogue_ratio(text)
                chapter_dialogue.append(ratio)
                total_dialogue_words += ratio * chwc

                item_name = item.get_name()
                title = toc_titles.get(item_name) or toc_titles.get(item_name.split('/')[-1], f"Chapter {len(wordcounts)}")
                chapter_titles.append(title)

    total_words      = len(all_words)
    avg_sentence_len = total_words / total_sentences if total_sentences else 0
    avg_syllables    = total_syllables / total_words if total_words else 0
    fk_grade         = max(0.0, 0.39 * avg_sentence_len + 11.8 * avg_syllables - 15.59)
    lexical_diversity = len(set(all_words)) / total_words if total_words else 0
    chapter_std      = stdev(wordcounts) if len(wordcounts) > 1 else 0
    book_dialogue    = total_dialogue_words / sum(wordcounts) if wordcounts else 0

    stats = {
        'lexical_diversity':   lexical_diversity,
        'avg_sentence_length': avg_sentence_len,
        'flesch_kincaid':      fk_grade,
        'chapter_std':         chapter_std,
        'dialogue_density':    book_dialogue,
    }

    book_title = f"{book.get_metadata('DC', 'creator')[0][0]} - {book.get_metadata('DC', 'title')[0][0]}"

    return wordcounts, chapter_titles, chapter_dialogue, book_title, stats
