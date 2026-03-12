import tkinter as tk
from tkinter import filedialog
import webbrowser
import tkinter.font as tkFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import epsread

bgcolor="grey"
msgcolor="white"
esguix=900
esguiy=600
graphx=600
graphy=300
chcount=8
chapters=[1, 2, 3, 4, 5, 6, 7, 8, 9]
chwords=[1204, 750, 251, 2145, 3125, 800, 1902, 750, 2400] #sample data
maxwords=3500

def getfile():
    filepath = filedialog.askopenfilename(filetypes=[("Epub filetype", "*.epub")])
    if not filepath:
        return
    epsread.getdata(filepath)
    landframe.pack_forget()
    dataframe.pack(side="top")

epsgui = tk.Tk(className="E-Pub Stats") #window widget
epsgui.geometry(f"{esguix}x{esguiy}")
epsgui.configure(bg=bgcolor)

msgfont = tkFont.Font(family="Calibre", size=16, weight="bold") #font settings
btnfont = tkFont.Font(family="Calibre", size=14)

landframe = tk.Frame(bg=bgcolor) #file selection frame
landframe.pack()

uploadbtn = tk.Button(landframe, text="Open EPub", width=20, command=getfile)
uploadbtn.pack()

dataframe = tk.Frame(bg=bgcolor) #graph page frame
#dataframe.pack(side="top")

wpmframe = tk.Frame(dataframe, bg=bgcolor, padx=5, pady=20) #frame for wpm entry
wpmframe.pack(side="top")

#top-packed widgets

wpmlabelleft = tk.Label(wpmframe, text="Enter your reading speed: ", fg=msgcolor, font=msgfont)
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

#graph
epsgraph = Figure(figsize=(4,4), dpi = 100) #create figure for graph
graxes = epsgraph.add_subplot(111)
graxes.plot(chapters, chwords)

grcanvas = FigureCanvasTkAgg(epsgraph, master=grframe)
grcanvas.draw()
grcanvas.get_tk_widget().pack()

epsgui.mainloop()
