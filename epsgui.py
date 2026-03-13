import tkinter as tk
from tkinter import filedialog
import webbrowser
import tkinter.font as tkFont
import matplotlib.style
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors    #Work on this next
import epsread

bgcolor="gray55"
pancolor="gray45"
grcolor="0.7"
msgcolor="white"
fontfam="Ubuntu"
esguix=1400
esguiy=800
graphx=1350
graphy=700
# chapters=[1, 2, 3, 4, 5, 6, 7, 8, 9]
# chwords=[1204, 750, 251, 2145, 3125, 800, 1902, 750, 2400] #sample data
chwc = []
maxwords=0
avgwords=0
bookname = " "

def getfile():
    filepath = filedialog.askopenfilename(filetypes=[("Epub filetype", "*.epub")])
    if not filepath:
        return
    chwc, maxwords, avgwords, bookname = epsread.getdata(filepath)
    # print(chwc, maxwords, avgwords, bookname)
    
    graxes.axhline(y=avgwords) # persistent average chapter length marker
    graxes.plot(range(1, len(chwc)+1), chwc, marker='o') # these have to be set here due to data access
    graxes.set_xticks(range(1, len(chwc)+1)) # set x axis markers at every chapter
    graxes.text(len(chwc) + 1, avgwords, f" Average length:\n {avgwords} words", va='center')
    graxes.set_title(bookname)
    graxes.set_xlabel("Chapters")
    graxes.set_ylabel("Word count")
    epsgraph.tight_layout() # prevent words from exiting bounds
    
    grcanvas.draw() #render graph
    
    landframe.pack_forget()
    infoframe.pack(fill="both", expand=True)

epsgui = tk.Tk(className="E-Pub Stats") #window widget
epsgui.geometry(f"{esguix}x{esguiy}")
epsgui.configure(bg=bgcolor)

msgfont = tkFont.Font(family=fontfam, size=14, weight="bold") #font settings
btnfont = tkFont.Font(family=fontfam, size=12)


#file selection page


landframe = tk.Frame(bg=bgcolor)
landframe.pack()

uploadbtn = tk.Button(landframe, text="Open EPub", width=20, padx=10, pady=10, command=getfile)
uploadbtn.pack(pady=50)



# info page frame


infoframe = tk.Frame(bg=bgcolor)

# side panel frame

statsframe = tk.Frame(infoframe, bg=pancolor, width=400)
statsframe.pack(side="right", fill="both", expand=True)
statsframe.pack_propagate(False)

# side panel widgets

stats = tk.Label(statsframe, text=f"The average chapter length is {avgwords} words.", fg=msgcolor, bg=pancolor, font=msgfont, wraplength=400)
closebutton = tk.Button(statsframe, text="Close", width =20, font=btnfont, command=epsgui.destroy)

stats.pack()
closebutton.pack(side="bottom", pady=20)


# graph and wpm info frame


dataframe = tk.Frame(infoframe, bg=bgcolor) #graph and wpm info frame
dataframe.pack(side="left", fill="both", expand=True)


# left side widgets


wpmlink = tk.Button(dataframe, text="Don't know your WPM? Click here to test!", width =40, font=btnfont, command=lambda: webbrowser.open("https://swiftread.com/reading-speed-test"))
wpmlink.pack(side="bottom", pady=20)


userwpm=tk.StringVar() #stringvar for WPM output


# wpm info frame

wpmframe = tk.Frame(dataframe, bg=bgcolor) #frame for wpm entry , padx=5, 
wpmframe.pack(side="bottom")


wpmlabelleft = tk.Label(wpmframe, text="For reading time estimates, enter your reading speed: ", fg=msgcolor, font=msgfont, bg=bgcolor)
wpminput = tk.Entry(wpmframe, textvariable=userwpm, justify="right", width=3, fg=msgcolor, font=msgfont, bg="gray30", bd=0, relief="sunken")
wpmlabelright = tk.Label(wpmframe, text=" words per minute", fg=msgcolor, font=msgfont, bg=bgcolor)


wpmlabelleft.grid(row=0, column=0)
wpminput.grid(row=0, column=1)
wpmlabelright.grid(row=0, column=2)


# bottom-packed widgets


grframe = tk.Frame(dataframe)
grframe.pack()


# graph

matplotlib.rcParams.update({"figure.facecolor":grcolor,
                           "axes.facecolor":grcolor,
                           "axes.edgecolor":grcolor,
                           "text.color":msgcolor,
                           "grid.color":"0.8",
                           "grid.linestyle":"--",
                           "lines.markersize":9,
                           "lines.linewidth":3,
                           "lines.color":"orange",
                           "figure.edgecolor":"red",
                           "font.family":"Ubuntu",
                           "axes.labelcolor":msgcolor,
                           "xtick.color":msgcolor,
                           "ytick.color":msgcolor}) #
epsgraph = Figure(figsize=(10,7), dpi = 100) #create matlib figure for graph
graxes = epsgraph.add_subplot(111) #create axes to plot
graxes.grid(True) #adds gridlines on ticks

grcanvas = FigureCanvasTkAgg(epsgraph, master=grframe) #compatibility object for matlibplot and tkinter/assign frame
grcanvas.get_tk_widget().pack()

epsgui.mainloop()
