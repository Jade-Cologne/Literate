import tkinter as tk
from tkinter import filedialog
import webbrowser
import tkinter.font as tkFont
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import reader

bgcolor  = "gray55"
pancolor = "gray45"
grcolor  = "0.7"
msgcolor = "white"
fontfam  = "Ubuntu"
esguix   = 1400
esguiy   = 800

# App state
chwc             = []
chapter_titles   = []
chapter_dialogue = []
bookname         = ""
book_stats       = {}
active_cursor    = None


def get_wpm():
    try:
        val = int(userwpm.get())
        return val if val > 0 else None
    except (ValueError, tk.TclError):
        return None


def fmt_time(total_mins):
    h, m = divmod(int(total_mins), 60)
    return f"{h}h {m}m" if h else f"{m}m"


def fk_descriptor(grade):
    if grade < 6:  return "Elementary"
    if grade < 9:  return "Middle school"
    if grade < 11: return "High school"
    if grade < 13: return "Advanced"
    return "College level"


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text   = text
        self.tip    = None
        self._job   = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self.hide)

    def _schedule(self, event):
        self._job = self.widget.after(0, self._show)

    def _show(self):
        if self.tip:
            return
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.withdraw()
        lbl = tk.Label(self.tip, text=self.text, bg="#f5f5dc", fg="#111",
                       font=("Ubuntu", 10), wraplength=260, justify="left",
                       padx=8, pady=5, relief="solid", bd=1)
        lbl.pack()
        self.tip.update_idletasks()
        tw = self.tip.winfo_reqwidth()
        th = self.tip.winfo_reqheight()
        wx = self.widget.winfo_rootx()
        wy = self.widget.winfo_rooty()
        wh = self.widget.winfo_height()
        x  = wx - tw - 8
        y  = wy + (wh // 2) - (th // 2)
        self.tip.wm_geometry(f"+{x}+{y}")
        self.tip.deiconify()

    def hide(self, event=None):
        if self._job:
            self.widget.after_cancel(self._job)
            self._job = None
        if self.tip:
            self.tip.destroy()
            self.tip = None


def update_panel():
    if not chwc:
        return

    wpm   = get_wpm()
    avg   = sum(chwc) // len(chwc)
    total = sum(chwc)

    basic = f"Average chapter: {avg:,} words\nTotal chapters: {len(chwc)}\nTotal words: {total:,}"
    avgstat.config(text=basic)

    if wpm:
        readingtime_label.config(text=f"Estimated reading time: {fmt_time(total / wpm)}")
    else:
        readingtime_label.config(text="Enter WPM for reading time estimate")

    if book_stats:
        ld  = book_stats['lexical_diversity']
        asl = book_stats['avg_sentence_length']
        fk  = book_stats['flesch_kincaid']
        std = book_stats['chapter_std']
        cv  = std / avg if avg else 0

        diversity_label.config(text=f"Lexical diversity: {ld:.1%} unique words")
        sentence_label.config(text=f"Avg sentence length: {asl:.1f} words")
        fk_label.config(text=f"Flesch-Kincaid: Grade {fk:.1f}  ({fk_descriptor(fk)})")

        if cv < 0.2:   consistency = "Very consistent chapter lengths"
        elif cv < 0.5: consistency = "Moderately varied chapter lengths"
        else:          consistency = "Highly variable chapter lengths"
        consistency_label.config(text=consistency)

        dd = book_stats['dialogue_density']
        dialogue_label.config(text=f"Dialogue density: {dd:.1%}")


def draw_graph():
    global active_cursor

    if not chwc:
        return

    wpm = get_wpm()

    graxes.clear()
    graxes.grid(True)

    if active_cursor:
        try:
            active_cursor.remove()
        except Exception:
            pass
        active_cursor = None

    xdata = list(range(1, len(chwc) + 1))
    ydata = list(chwc)

    graxes.plot(xdata, ydata)
    scatter = graxes.scatter(xdata, ydata)

    cursor = mplcursors.cursor(scatter, hover=2)  # transient: hide when cursor leaves point

    @cursor.connect("add")
    def on_add(sel):
        idx   = int(sel.index)
        parts = []

        if show_names.get() and idx < len(chapter_titles):
            parts.append(chapter_titles[idx])
        else:
            parts.append(f"Chapter {idx + 1}")

        if show_wc.get():
            parts.append(f"{chwc[idx]:,} words")

        if show_time.get() and wpm:
            parts.append(fmt_time(chwc[idx] / wpm))

        if show_dialogue.get() and idx < len(chapter_dialogue):
            parts.append(f"{chapter_dialogue[idx]:.0%} dialogue")

        sel.annotation.set_text("\n".join(parts))

    active_cursor = cursor

    miny     = min(ydata)
    maxy     = max(ydata)
    minchnum = ydata.index(miny) + 1
    maxchnum = ydata.index(maxy) + 1
    avgy     = sum(ydata) / len(ydata)

    graxes.annotate("Longest",  xy=(maxchnum, maxy), xytext=(0,  10), textcoords="offset points", ha="center", va="bottom")
    graxes.annotate("Shortest", xy=(minchnum, miny), xytext=(0, -10), textcoords="offset points", ha="center", va="top")
    graxes.axhline(y=avgy)
    graxes.text(len(chwc) + 0.5, avgy, f" Average\n length:\n {int(avgy):,}\n words", va='center')

    graxes.set_xticks(xdata)
    graxes.set_title(bookname)
    graxes.set_xlabel("Chapters")
    graxes.set_ylabel("Word count")

    litgraph.tight_layout()
    grcanvas.draw()


def getfile():
    global chwc, chapter_titles, bookname, book_stats

    filepath = filedialog.askopenfilename(filetypes=[("Epub filetype", "*.epub")])
    if not filepath:
        return

    chwc, chapter_titles, chapter_dialogue, bookname, book_stats = reader.getdata(filepath)

    update_panel()
    draw_graph()

    landframe.pack_forget()
    infoframe.pack(fill="both", expand=True)


def open_new():
    global chwc, chapter_titles, chapter_dialogue, bookname, book_stats
    chwc             = []
    chapter_titles   = []
    chapter_dialogue = []
    bookname         = ""
    book_stats       = {}
    graxes.clear()
    grcanvas.draw()
    infoframe.pack_forget()
    landframe.pack(fill="both", expand=True)


def on_wpm_change(*args):
    update_panel()
    if chwc and show_time.get():
        draw_graph()


# tkinter setup

litgui = tk.Tk(className="Literate")
litgui.geometry(f"{esguix}x{esguiy}")
litgui.configure(bg=bgcolor)

msgfont  = tkFont.Font(family=fontfam, size=14, weight="bold")
btnfont  = tkFont.Font(family=fontfam, size=12)
statfont   = tkFont.Font(family=fontfam, size=11)
headerfont = tkFont.Font(family=fontfam, size=22, weight="bold")

show_names    = tk.BooleanVar(value=False)
show_wc       = tk.BooleanVar(value=True)
show_time     = tk.BooleanVar(value=True)
show_dialogue = tk.BooleanVar(value=False)
userwpm       = tk.StringVar()
userwpm.trace_add("write", on_wpm_change)


# Landing page

landframe = tk.Frame(bg=bgcolor)
landframe.pack(fill="both", expand=True)

uploadbtn = tk.Button(landframe, text="Open EPub", width=20, padx=10, pady=10, command=getfile)
uploadbtn.pack(pady=50)


# Info page

infoframe = tk.Frame(bg=bgcolor)

# Side panel

statsframe = tk.Frame(infoframe, bg=pancolor, width=400)
statsframe.pack(side="right", fill="both", expand=True)
statsframe.pack_propagate(False)

# Header

tk.Label(statsframe, text="Literate", fg=msgcolor, bg=pancolor, font=headerfont).pack(pady=(15, 0))

# Basic book stats

avgstat = tk.Label(statsframe, fg=msgcolor, bg=pancolor, font=msgfont, wraplength=380, justify="left")
avgstat.pack(pady=(20, 2), padx=10, anchor="w")

readingtime_label = tk.Label(statsframe, fg=msgcolor, bg=pancolor, font=statfont, wraplength=380, justify="left")
readingtime_label.pack(padx=10, anchor="w")

# Reading analysis box

analysisframe = tk.LabelFrame(statsframe, text="Reading analysis", fg=msgcolor, bg=pancolor, font=btnfont, padx=10, pady=5)
analysisframe.pack(fill="x", padx=10, pady=(12, 6))

lbl_args = dict(fg=msgcolor, bg=pancolor, font=statfont, wraplength=340, justify="left", anchor="w")

diversity_label    = tk.Label(analysisframe, **lbl_args)
sentence_label     = tk.Label(analysisframe, **lbl_args)
fk_label           = tk.Label(analysisframe, **lbl_args)
consistency_label  = tk.Label(analysisframe, **lbl_args)
dialogue_label     = tk.Label(analysisframe, **lbl_args)

diversity_label.pack(fill="x")
sentence_label.pack(fill="x")
fk_label.pack(fill="x")
consistency_label.pack(fill="x")
dialogue_label.pack(fill="x")

Tooltip(diversity_label,   "Unique words ÷ total words. Measures vocabulary variety.\n\nTypical novels: 5–20%. Literary fiction tends toward the higher end.")
Tooltip(sentence_label,    "Mean words per sentence.\n\nConversational prose: 10–15 words.\nComplex literary fiction: 20–40+.\n\nLonger sentences generally make text harder to parse.")
Tooltip(fk_label,          "Estimates the US school grade level needed to read the text. Based on sentence length and syllables per word.\n\nGrade 6 = accessible\nGrade 12+ = advanced\n\nNote: designed for non-fiction — less reliable for experimental or stream-of-consciousness prose.")
Tooltip(consistency_label, "Based on the spread of chapter lengths relative to the average.\n\nVery consistent: chapters are similar lengths.\nModerately varied: some spread between short and long.\nHighly variable: wide range — common in thrillers with short climax chapters.")
Tooltip(dialogue_label,    "Percentage of text inside quotation marks, counting both double (\u201c\u201d) and single (\u2018\u2019) quotes.\n\nIncludes both dialogue and attributed internal thought. A high score suggests a character-voice-driven narrative; a low score suggests more narration or description.")

# Chapter info toggle box

chapterinfo = tk.LabelFrame(statsframe, text="Chapter info", fg=msgcolor, bg=pancolor, font=btnfont, padx=10, pady=5)
chapterinfo.pack(fill="x", padx=10, pady=6)

checkargs = dict(
    bg=pancolor, fg=msgcolor, font=btnfont, selectcolor=pancolor,
    activeforeground=msgcolor, activebackground=pancolor,
    anchor="w", command=lambda: draw_graph() if chwc else None
)

namescheck    = tk.Checkbutton(chapterinfo, text="Chapter names",    variable=show_names,    **checkargs)
wccheck       = tk.Checkbutton(chapterinfo, text="Word count",       variable=show_wc,       **checkargs)
timecheck     = tk.Checkbutton(chapterinfo, text="Reading time",     variable=show_time,     **checkargs)
dialoguecheck = tk.Checkbutton(chapterinfo, text="Dialogue density", variable=show_dialogue, **checkargs)

namescheck.pack(fill="x")
wccheck.pack(fill="x")
timecheck.pack(fill="x")
dialoguecheck.pack(fill="x")

openanother = tk.Button(statsframe, text="Open another book", width=20, font=btnfont, command=open_new)
openanother.pack(pady=(16, 5))

closebutton = tk.Button(statsframe, text="Close", width=20, font=btnfont, command=litgui.destroy)
closebutton.pack(side="bottom", pady=20)


# Data frame (left side)

dataframe = tk.Frame(infoframe, bg=bgcolor)
dataframe.pack(side="left", fill="both", expand=True)

wpmlink = tk.Button(
    dataframe, text="Don't know your WPM? Click here to test!", width=40, font=btnfont,
    command=lambda: webbrowser.open("https://swiftread.com/reading-speed-test")
)
wpmlink.pack(side="bottom", pady=20)

wpmframe      = tk.Frame(dataframe, bg=bgcolor)
wpmframe.pack(side="bottom")

wpmlabelleft  = tk.Label(wpmframe, text="Reading speed: ", fg=msgcolor, font=msgfont, bg=bgcolor)
wpminput      = tk.Entry(wpmframe, textvariable=userwpm, justify="right", width=4,
                          fg=msgcolor, font=msgfont, bg="gray30", bd=0, relief="sunken")
wpmlabelright = tk.Label(wpmframe, text=" WPM", fg=msgcolor, font=msgfont, bg=bgcolor)

wpmlabelleft.grid(row=0, column=0)
wpminput.grid(row=0, column=1)
wpmlabelright.grid(row=0, column=2)


# Graph

matplotlib.rcParams.update({
    "figure.facecolor": grcolor,
    "axes.facecolor":   grcolor,
    "axes.edgecolor":   grcolor,
    "text.color":       msgcolor,
    "grid.color":       "0.8",
    "grid.linestyle":   "--",
    "lines.markersize": 9,
    "lines.linewidth":  3,
    "lines.color":      "orange",
    "font.family":      "Ubuntu",
    "axes.labelcolor":  msgcolor,
    "xtick.color":      msgcolor,
    "ytick.color":      msgcolor,
})

litgraph = Figure(figsize=(10, 7), dpi=100)
graxes   = litgraph.add_subplot(111)
graxes.grid(True)

grframe = tk.Frame(dataframe)
grframe.pack()

grcanvas = FigureCanvasTkAgg(litgraph, master=grframe)
grcanvas.get_tk_widget().pack()

litgui.mainloop()
