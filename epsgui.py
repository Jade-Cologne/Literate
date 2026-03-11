import tkinter as tk
import webbrowser
import tkinter.font as tkFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

bgcolor="grey"
msgcolor="white"
esguix=900
esguiy=600
graphx=600
graphy=300
chcount=8
maxwords=5000

epsgui = tk.Tk(className="E-Pub Stats") #window widget
epsgui.geometry(f"{esguix}x{esguiy}")
epsgui.configure(bg=bgcolor)

msgfont = tkFont.Font(family="Calibre", size=16, weight="bold")
btnfont = tkFont.Font(family="Calibre", size=14)

#top-packed widgets

wpmframe = tk.Frame(bg=bgcolor, padx=5, pady=20) 
wpmframe.pack(side="top")

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

wpmlink = tk.Button(epsgui, text="Don't know your WPM? Click here to test!", width =40, font=btnfont, command=lambda: webbrowser.open("https://swiftread.com/reading-speed-test"))
wpmlink.pack()

#bottom-packed widgets
closebutton = tk.Button(epsgui, text="Close", width =20, font=btnfont, command=epsgui.destroy)
closebutton.pack(side="bottom", pady=20)

graphframe = tk.Frame(epsgui, bg="lightgrey", width=graphx, height=graphy)
graphframe.pack(side="bottom", padx=20, pady=20)

espgraph = Figure(figsize=(4,4), dpi = 100)

epsgui.mainloop()

