import tkinter as tk
from tkinter import filedialog
import webbrowser
import tkinter.font as tkFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors    #Work on this next
import epsread

bgcolor="grey"
msgcolor="white"
esguix=1200
esguiy=800
graphx=950
graphy=600
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
    
    graxes.plot(range(1, len(chwc)+1), chwc, marker='o') #these have to be set here due to data access
    graxes.set_xticks(range(1, len(chwc)+1))
    graxes.axhline(y=avgwords)
    graxes.set_title(bookname)
    graxes.set_xlabel("Chapters")
    graxes.set_ylabel("Word count")
    
    grcanvas.draw() #render graph
    
    landframe.pack_forget()
    dataframe.pack(side="top")

epsgui = tk.Tk(className="E-Pub Stats") #window widget
epsgui.geometry(f"{esguix}x{esguiy}")
epsgui.configure(bg=bgcolor)

msgfont = tkFont.Font(family="Calibre", size=16, weight="bold") #font settings
btnfont = tkFont.Font(family="Calibre", size=14)

landframe = tk.Frame(bg=bgcolor) #file selection frame
landframe.pack()

uploadbtn = tk.Button(landframe, text="Open EPub", width=20, padx=10, pady=10, command=getfile)
uploadbtn.pack(pady=50)

dataframe = tk.Frame(bg=bgcolor) #graph page frame
#dataframe.pack(side="top")

wpmframe = tk.Frame(dataframe, bg=bgcolor, padx=5, pady=20) #frame for wpm entry
wpmframe.pack(side="top")

#top-packed widgets

wpmlabelleft = tk.Label(wpmframe, text="For reading time estimates, enter your reading speed: ", fg=msgcolor, font=msgfont)
wpmlabelleft.grid(row=0, column=0)
wpmlabelleft.configure(bg=bgcolor)

userwpm=tk.StringVar() #stringvar for WPM output

wpminput = tk.Entry(wpmframe, textvariable=userwpm, justify="right", width=3, fg=msgcolor, font=msgfont, bd=0, relief="sunken")
wpminput.grid(row=0, column=1)
wpminput.configure(bg="gray30")

wpmlabelright = tk.Label(wpmframe, text=" words per minute", fg=msgcolor, font=msgfont)
wpmlabelright.grid(row=0, column=2)
wpmlabelright.configure(bg=bgcolor)

wpmlink = tk.Button(dataframe, text="Don't know your WPM? Click here to test!", width =40, font=btnfont, command=lambda: webbrowser.open("https://swiftread.com/reading-speed-test"))
wpmlink.pack()

#bottom-packed widgets
closebutton = tk.Button(dataframe, text="Close", width =20, font=btnfont, command=epsgui.destroy)
closebutton.pack(side="bottom", pady=20)

grframe = tk.Frame(dataframe, bg="lightgrey", width=graphx, height=graphy)
grframe.pack(side="bottom", padx=20, pady=20)

#graph creation

epsgraph = Figure(figsize=(9.5,6), dpi = 100) #create matlib figure for graph
graxes = epsgraph.add_subplot(111) #create axes to plot
graxes.grid(True)

grcanvas = FigureCanvasTkAgg(epsgraph, master=grframe) #compatibility class for matlibplot and tkinter/assign frame
grcanvas.get_tk_widget().pack()

epsgui.mainloop()
