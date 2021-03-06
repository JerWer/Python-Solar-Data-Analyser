#! python3

import os,datetime
import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg

import tkinter as tk
from tkinter import *
from tkinter.ttk import Treeview
from tkinter import messagebox, Button, Label, Frame, Entry, Checkbutton, IntVar, Toplevel, Scrollbar, Canvas, OptionMenu, StringVar

from tkinter import filedialog
from pathlib import Path
import numpy as np
import copy
import xlsxwriter
import xlrd
from scipy.interpolate import interp1d
from scipy import integrate
from operator import itemgetter
from itertools import groupby, chain
#import PIL
from PIL import Image as ImageTk
from matplotlib.ticker import MaxNLocator
from tkinter import font as tkFont
from matplotlib.transforms import Bbox
import pickle
import six
from tkinter import colorchooser
from functools import partial
import darktolight as DtoL
import os.path
import shutil
import sqlite3
from dateutil import parser
from scipy import stats
from statistics import mean

"""
TODOLIST

- low illumination: mirrored curves, chech automatically and mirror the curve
- illumination intensity given in legend
=> place dark data analysis in a pop-up window
 
- make it compatible with HIT files: how to select the batch, wafer, cell names? check with Mario&Co if they agreed on something


- when finish autoanalysis, it doesn't plot back the same as before for the mpp

- low-intensity meas: if several intensities for a single cell
    get automatic graph of Voc&Jsc&FF as function of intensity
    fits ? something to extract?

- group: modify the name of an existing group => automatically change in all samples


- database adaptation

- Vmpp is rounded somewhere... ??

- bring back DtoL and changeArea

- exception with the default group empty => just remove the default group, annoying to fix...

- add HI group plot to autoanalysis


Plottime graph:
- change legend
- best of rev and forw at every date

histogram graph: relative number of device (%)
    

mpp graph:
    problem with legend mod if after importing on loaded session: invalid command name toplevel3.!canvas.!frame.!entry2
    problem is solved if save session again and reload


- for CIGS station: dark file makes some errors...




"""
#%%############# Global variable definition
testdata = []
DATA = [] #[{"SampleName":, "CellNumber": , "MeasDayTime":, "CellSurface":, "Voc":, "Jsc":, "FF":, "Eff":, "Pmpp":, "Vmpp":, "Jmpp":, "Roc":, "Rsc":, "VocFF":, "RscJsc":, "NbPoints":, "Delay":, "IntegTime":, "Vstart":, "Vend":, "Illumination":, "ScanDirection":, "ImaxComp":, "Isenserange":,"AreaJV":, "Operator":, "MeasComment":, "IVData":}]
DATAJVforexport=[]
DATAJVtabforexport=[]
DATAmppforexport=[]
DATAgroupforexport=[]
DATAHistforexport=[]
DATAcompforexport=[]
DATAtimeevolforexport={}#key: [[realtimeF, relativetimeF, valueF, normalizedvaluetot0F, realtimeR, relativetimeR, valueR, normalizedvaluetot0R]]
takenforplot=[]
takenforplotmpp=[]
takenforplotTime=[]

DATAMPP = []
DATAdark = []
DATAFV=[]

numbLightfiles=0
numbDarkfiles=0

IVlegendMod = []
IVlinestyle = []
colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']

MPPlegendMod = []
MPPlinestyle = []

titIV =0
titmpp=0
titStat=0
samplesgroups=["Default group"]
groupstoplot=["Default group"]
groupstoplotcomp=["Default group"]

listofanswer=[]
listoflinestyle=[]
listofcolorstyle=[]
listoflinewidthstyle=[]

#%%#############
def modification_date(path_to_file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(path_to_file)).strftime("%Y-%m-%d %H:%M:%S")

def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

   
#%%#############             
    
class IVApp(Toplevel):

    def __init__(self, *args, **kwargs): 
        """
        initialize the graphical user interface with all buttons, graphs and tables, calling the functions defined below
        """
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "IVApp")
        Toplevel.config(self,background="white")
        self.wm_geometry("1250x700")
        self.wm_resizable(True,True)
        center(self)
        #self.iconbitmap('icon1.ico') #gives an error when calling self.__init__() : TclError: bitmap "icon1.ico" not defined
        
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="white")
        self.superframe=Frame(self.canvas0,background="white")
        
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas0.yview)
        self.canvas0.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas0.xview)
        self.canvas0.configure(xscrollcommand=self.hsb.set)
        self.hsb.pack(side="bottom", fill="x")
        
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        self.canvas0.create_window((1,4), window=self.superframe, anchor="nw", 
                                  tags="self.superframe")
        self.superframe.bind("<Configure>", self.onFrameConfigure)
        
        ############ the figures #################
        self.fig = plt.figure(figsize=(35, 30))
        self.fig.patch.set_facecolor('white')
        canvas = FigureCanvasTkAgg(self.fig, self.superframe)
        canvas.get_tk_widget().grid(row=0,column=0,rowspan=80,columnspan=130)
        
        
        self.IVsubfig = self.fig.add_subplot(551)        
        self.mppsubfig = self.fig.add_subplot(553) 
        self.GroupStatfig = self.fig.add_subplot(5,5,11)  
        self.TimeEvolfig = self.fig.add_subplot(5,5,21) 
        self.CompParamGroupfig = self.fig.add_subplot(5,5,23) 
        self.Histofig = self.fig.add_subplot(5,5,25)
         
        label = tk.Label(self.superframe, text="Solar Simulator DATA Analyzer", bg="black",fg="white")
        label.grid(row = 0, column = 0, rowspan = 2, columnspan = 130, sticky = "wens")
              
        self.Frame2 = Frame(self.superframe, bg="white")
        self.Frame2.grid(row = 22, column = 0, rowspan = 10, columnspan = 130, sticky = "wens") 

        for r in range(10):
            self.Frame2.rowconfigure(r, weight=1)    
        for c in range(130):
            self.Frame2.columnconfigure(c, weight=1)
        
        #### Comparison of parameters ####
        
        self.Frame31 = Frame(self.superframe, bg="white")
        self.Frame31.grid(row = 55, column = 50, rowspan = 5, columnspan = 30)
        
        self.saveCompgraph = Button(self.Frame31, text="Save graph",
                            command = self.GraphCompsave_as)
        self.saveCompgraph.grid(row=0, column=0, columnspan=6)

        CompChoiceList = ["Voc","Jsc","FF", "Eff", "Roc", "Rsc","Vmpp","Jmpp"]
        self.CompXChoice=StringVar()
        self.CompXChoice.set("Eff") # default choice
        self.dropMenuComp = OptionMenu(self.Frame31, self.CompXChoice, *CompChoiceList, command=self.UpdateCompGraph)
        self.dropMenuComp.grid(row=0, column=7, columnspan=5)
        self.CompYChoice=StringVar()
        self.CompYChoice.set("Eff") # default choice
        self.dropMenuComp = OptionMenu(self.Frame31, self.CompYChoice, *CompChoiceList, command=self.UpdateCompGraph)
        self.dropMenuComp.grid(row=0, column=12, columnspan=5)
        
        self.Compgrouptoplotbutton = tk.Menubutton(self.Frame31, text="grouptoplot", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.Compgrouptoplotmenu = tk.Menu(self.Compgrouptoplotbutton, tearoff=False)
        self.Compgrouptoplotbutton.configure(menu=self.Compgrouptoplotmenu)
        self.Compgrouptoplotbutton.grid(row=0, column=17, columnspan=6)
        
        self.updateCompgrouptoplotdropbutton()
        
        self.minYCompgraph = tk.DoubleVar()
        entry=Entry(self.Frame31, textvariable=self.minYCompgraph,width=3)
        entry.grid(row=1,column=0,columnspan=2)
        self.minYCompgraph.set(0)
        self.maxYCompgraph = tk.DoubleVar()
        entry=Entry(self.Frame31, textvariable=self.maxYCompgraph,width=3)
        entry.grid(row=1,column=2,columnspan=2)
        self.maxYCompgraph.set(1)
        self.minXCompgraph = tk.DoubleVar()
        entry=Entry(self.Frame31, textvariable=self.minXCompgraph,width=3)
        entry.grid(row=1,column=4,columnspan=2)
        self.minXCompgraph.set(0)
        self.maxXCompgraph = tk.DoubleVar()
        entry=Entry(self.Frame31, textvariable=self.maxXCompgraph,width=3)
        entry.grid(row=1,column=6,columnspan=2)
        self.maxXCompgraph.set(1)
        self.minmaxCompgraphcheck = IntVar()
        Checkbutton(self.Frame31,text="rescale?",variable=self.minmaxCompgraphcheck, 
                           onvalue=1,offvalue=0,height=1, width=6, command = lambda: self.UpdateCompGraph(1),fg='black',background='white').grid(row=1, column=8, columnspan=5)
#        aftermppcheck=Checkbutton(self.Frame31,text="onlyDark?",variable=self.minmaxCompgraphcheck, 
#                           onvalue=1,offvalue=0,height=1, width=6, command = lambda: self.UpdateCompGraph(1),fg='black',background='white')
#        aftermppcheck.grid(row=1, column=13, columnspan=5)
#        aftermppcheck=Checkbutton(self.Frame31,text="onlyLight?",variable=self.minmaxCompgraphcheck, 
#                           onvalue=1,offvalue=0,height=1, width=6, command = lambda: self.UpdateCompGraph(1),fg='black',background='white')
#        aftermppcheck.grid(row=1, column=18, columnspan=6)
        
        
        #### TimeEvol ####
        
        self.Frame3 = Frame(self.superframe, bg="white")
        self.Frame3.grid(row = 54, column = 11, rowspan = 5, columnspan = 30)
        
        self.saveTimegraph = Button(self.Frame3, text="Save graph",
                            command = self.GraphTimesave_as)
        self.saveTimegraph.grid(row=0, column=0, columnspan=6)

        TimeChoiceList = ["Voc","Jsc","FF", "Eff", "Roc", "Rsc","Vmpp","Jmpp","HI"]
        self.TimeChoice=StringVar()
        self.TimeChoice.set("Eff") # default choice
        self.dropMenuTime = OptionMenu(self.Frame3, self.TimeChoice, *TimeChoiceList, command=self.UpdateTimeGraph)
        self.dropMenuTime.grid(row=0, column=7, columnspan=5)
        
        self.updateTimegraph = Button(self.Frame3, text="Update graph",command = lambda: self.UpdateTimeGraph(1))
        self.updateTimegraph.grid(row=1, column=0, columnspan=6)
        
        self.changeTimelegend = Button(self.Frame3, text="change legend",command = self.ChangeLegendTimegraph)
        self.changeTimelegend.grid(row=1, column=7, columnspan=5)
        
#        self.timeminx = tk.DoubleVar()
#        entry=Entry(self.Frame3, textvariable=self.timeminx,width=5).grid(row=0,column=13,columnspan=1)
#        tk.Label(self.Frame3, text="Min X",fg='black',background='white').grid(row=1,column=13,columnspan=1)
#        self.timeminx.set(0)
#        self.timemaxx = tk.DoubleVar()
#        Entry(self.Frame3, textvariable=self.timemaxx,width=5).grid(row=0,column=14,columnspan=1)
#        tk.Label(self.Frame3, text="Max X",fg='black',background='white').grid(row=1,column=14,columnspan=1)
#        self.timemaxx.set(1) 
#        self.timeminy = tk.DoubleVar()
#        Entry(self.Frame3, textvariable=self.timeminy,width=5).grid(row=0,column=15,columnspan=1)
#        tk.Label(self.Frame3, text="Min Y",fg='black',background='white').grid(row=1,column=15,columnspan=1)
#        self.timeminy.set(0)
#        self.timemaxy = tk.DoubleVar()
#        Entry(self.Frame3, textvariable=self.timemaxy,width=5).grid(row=0,column=16,columnspan=1)
#        tk.Label(self.Frame3, text="Max Y",fg='black',background='white').grid(row=1,column=16,columnspan=1)
#        self.timemaxy.set(1)
        
        self.LineornolineTimegraph = IntVar()
        lineTime=Checkbutton(self.Frame3,text="Line?",variable=self.LineornolineTimegraph, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.UpdateTimeGraph(1),fg='black',background='white')
        lineTime.grid(row=2, column=0, columnspan=6)
        self.LineornolineTimegraph.set(1)
        
        self.big4Timegraph = IntVar()
        lineTime=Checkbutton(self.Frame3,text="big4?",variable=self.big4Timegraph, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.UpdateTimeGraph(1),fg='black',background='white')
        lineTime.grid(row=2, column=13, columnspan=5)
        self.big4Timegraph.set(1)
        
        self.timerelativeTimegraph = IntVar()
        lineTime=Checkbutton(self.Frame3,text="RelativeTime?",variable=self.timerelativeTimegraph, 
                           onvalue=1,offvalue=0,height=1, width=10, command = lambda: self.UpdateTimeGraph(1),fg='black',background='white')
        lineTime.grid(row=2, column=7, columnspan=5)
        self.timerelativeTimegraph.set(0)
        self.normalTimegraph = IntVar()
        lineTime=Checkbutton(self.Frame3,text="Normal.?",variable=self.normalTimegraph, 
                           onvalue=1,offvalue=0,height=1, width=10, command = lambda: self.UpdateTimeGraph(1),fg='black',background='white')
        lineTime.grid(row=1, column=13, columnspan=5)
        self.normalTimegraph.set(0)
        self.normalsettimegraph = tk.DoubleVar()
        entry=Entry(self.Frame3, textvariable=self.normalsettimegraph,width=3)
        entry.grid(row=1,column=18,columnspan=2)
        self.normalsettimegraph.set(-1)
        
        self.minYtimegraph = tk.DoubleVar()
        entry=Entry(self.Frame3, textvariable=self.minYtimegraph,width=3)
        entry.grid(row=2,column=18,columnspan=2)
        self.minYtimegraph.set(0)
        self.maxYtimegraph = tk.DoubleVar()
        entry=Entry(self.Frame3, textvariable=self.maxYtimegraph,width=3)
        entry.grid(row=2,column=20,columnspan=2)
        self.maxYtimegraph.set(1)
        self.minmaxtimegraphcheck = IntVar()
        aftermppcheck=Checkbutton(self.Frame3,text="Yscale",variable=self.minmaxtimegraphcheck, 
                           onvalue=1,offvalue=0,height=1, width=6, command = lambda: self.UpdateTimeGraph(1),fg='black',background='white')
        aftermppcheck.grid(row=2, column=22, columnspan=3)
        
        self.BestofRevForTimegraph = IntVar()
        lineTime=Checkbutton(self.Frame3,text="bestofRevFor",variable=self.BestofRevForTimegraph, 
                           onvalue=1,offvalue=0,height=1, width=9, command = lambda: self.UpdateTimeGraph(1),fg='black',background='white')
        lineTime.grid(row=3, column=0, columnspan=8)
        self.BestofRevForTimegraph.set(0)
        
        self.BestPixofDayTimegraph = IntVar()
        lineTime=Checkbutton(self.Frame3,text="BestEffPixDay",variable=self.BestPixofDayTimegraph, 
                           onvalue=1,offvalue=0,height=1, width=9, command = lambda: self.UpdateTimeGraph(1),fg='black',background='white')
        lineTime.grid(row=3, column=7, columnspan=8)
        self.BestPixofDayTimegraph.set(0)
        
        
        #### Histogram ####
        self.Frame5 = Frame(self.superframe, bg="white")
        self.Frame5.grid(row = 54, column = 90, rowspan = 5, columnspan = 30)
        
        self.saveHistgraph = Button(self.Frame5, text="Save graph",
                            command = self.GraphHistsave_as)
        self.saveHistgraph.grid(row=0, column=0, columnspan=5)
        
        HistparamChoiceList = ["Voc","Jsc","FF", "Eff", "Roc", "Rsc","Vmpp","Jmpp"]
        self.HistparamChoice=StringVar()
        self.HistparamChoice.set("Eff") # default choice
        self.dropMenuHist = OptionMenu(self.Frame5, self.HistparamChoice, *HistparamChoiceList, command=self.UpdateHistGraph)
        self.dropMenuHist.grid(row=0, column=6, columnspan=5)
        
        self.Histgrouptoplotbutton = tk.Menubutton(self.Frame5, text="grouptoplot", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.Histgrouptoplotmenu = tk.Menu(self.Histgrouptoplotbutton, tearoff=False)
        self.Histgrouptoplotbutton.configure(menu=self.Histgrouptoplotmenu)
        self.Histgrouptoplotbutton.grid(row=0, column=12, columnspan=6)
        
        self.updateHistgrouptoplotdropbutton()
        
        HistWhichMeasList = ["OnlyRev","OnlyForw","Bestof/pix", "Bestof/subst", "Allmeas"]
        self.HistWhichMeasChoice=StringVar()
        self.HistWhichMeasChoice.set("Bestof/pix") # default choice
        self.dropMenuHistWhichMeas = OptionMenu(self.Frame5, self.HistWhichMeasChoice, *HistWhichMeasList, command=self.UpdateHistGraph)
        self.dropMenuHistWhichMeas.grid(row=1, column=0, columnspan=5)
        
        self.HistFitGaussian = IntVar()
        Big4=Checkbutton(self.Frame5,text="Fit",variable=self.HistFitGaussian, 
                           onvalue=1,offvalue=0,height=1, width=3, command = (),fg='black',background='white')
        Big4.grid(row=1, column=6, columnspan=3)
        
        self.NumbBinsHist = tk.DoubleVar()
        entry=Entry(self.Frame5, textvariable=self.NumbBinsHist,width=3)
        entry.grid(row=1,column=10,columnspan=3)
        tk.Label(self.Frame5, text="#bins",fg='black',background='white').grid(row=1,column=13,columnspan=2)
        self.NumbBinsHist.set(2)
        
        HistTypeList = ['bar', 'barstacked', 'step', 'stepfilled']
        self.HistTypeChoice=StringVar()
        self.HistTypeChoice.set("bar") # default choice
        self.dropMenuHistType = OptionMenu(self.Frame5, self.HistTypeChoice, *HistTypeList, command=self.UpdateHistGraph)
        self.dropMenuHistType.grid(row=1, column=15, columnspan=5)
        
        self.minXHistgraph = tk.DoubleVar()
        entry=Entry(self.Frame5, textvariable=self.minXHistgraph,width=3)
        entry.grid(row=2,column=0,columnspan=2)
        self.minXHistgraph.set(0)
        self.maxXHistgraph = tk.DoubleVar()
        entry=Entry(self.Frame5, textvariable=self.maxXHistgraph,width=3)
        entry.grid(row=2,column=3,columnspan=2)
        self.maxXHistgraph.set(1)
        self.minmaxHistgraphcheck = IntVar()
        Checkbutton(self.Frame5,text="Xscale",variable=self.minmaxHistgraphcheck, 
                           onvalue=1,offvalue=0,height=1, width=6, command = lambda: self.UpdateHistGraph(1)
                           ,fg='black',background='white').grid(row=2, column=6, columnspan=3)
        
        
        #### Group ####
        
        self.Frame4 = Frame(self.superframe, bg="white")
        self.Frame4.grid(row = 47, column = 10, rowspan = 5, columnspan = 30)
        
        self.saveGroupgraph = Button(self.Frame4, text="Save graph",
                            command = self.GraphGroupsave_as)
        self.saveGroupgraph.grid(row=0, column=0, columnspan=5)
        
        GroupChoiceList = ["Voc","Jsc","FF", "Eff", "Roc", "Rsc","Vmpp","Jmpp","HI"]
        self.GroupChoice=StringVar()
        self.GroupChoice.set("Eff") # default choice
        self.dropMenuGroup = OptionMenu(self.Frame4, self.GroupChoice, *GroupChoiceList, command=self.UpdateGroupGraph)
        self.dropMenuGroup.grid(row=0, column=6, columnspan=5)
        
        self.Big4 = IntVar()
        Big4=Checkbutton(self.Frame4,text="Big4",variable=self.Big4, 
                           onvalue=1,offvalue=0,height=1, width=3, command = (),fg='black',background='white')
        Big4.grid(row=0, column=12, columnspan=3)
        
        self.RF = IntVar()
        RF=Checkbutton(self.Frame4,text="RF",variable=self.RF, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.UpdateGroupGraph(1),fg='black',background='white')
        RF.grid(row=0, column=15, columnspan=3)
        self.boxplot = IntVar()
        boxplot=Checkbutton(self.Frame4,text="box",variable=self.boxplot, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.UpdateGroupGraph(1),fg='black',background='white')
        boxplot.grid(row=0, column=18, columnspan=4)
        self.boxplot.set(0)
        
        self.fontsizeGroupGraph = tk.DoubleVar()
        entry=Entry(self.Frame4, textvariable=self.fontsizeGroupGraph,width=3)
        entry.grid(row=0,column=24,columnspan=1)
        tk.Label(self.Frame4, text="Fontsize",fg='black',background='white').grid(row=0,column=22,columnspan=2)
        self.fontsizeGroupGraph.set(8)
        
        self.rotationGroupGraph = tk.DoubleVar()
        entry=Entry(self.Frame4, textvariable=self.rotationGroupGraph,width=3)
        entry.grid(row=1,column=3,columnspan=3)
        tk.Label(self.Frame4, text="RotLab",fg='black',background='white').grid(row=1,column=0,columnspan=2)
        self.rotationGroupGraph.set(0)
        
        self.aftermppcheck = IntVar()
        aftermppcheck=Checkbutton(self.Frame4,text="aftermpp",variable=self.aftermppcheck, 
                           onvalue=1,offvalue=0,height=1, width=6, command = lambda: self.UpdateGroupGraph(1),fg='black',background='white')
        aftermppcheck.grid(row=1, column=6, columnspan=5)
#        tk.Label(self.superframe, text="RotLab",fg='black',background='white').grid(row=rowpos+1,column=8,columnspan=2)

        self.grouptoplotbutton = tk.Menubutton(self.Frame4, text="grouptoplot", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.grouptoplotmenu = tk.Menu(self.grouptoplotbutton, tearoff=False)
        self.grouptoplotbutton.configure(menu=self.grouptoplotmenu)
        self.grouptoplotbutton.grid(row=1, column=12, columnspan=6)
        
        self.updategrouptoplotdropbutton()
        
        self.minYgroupgraph = tk.DoubleVar()
        entry=Entry(self.Frame4, textvariable=self.minYgroupgraph,width=3)
        entry.grid(row=1,column=18,columnspan=2)
        self.minYgroupgraph.set(0)
        self.maxYgroupgraph = tk.DoubleVar()
        entry=Entry(self.Frame4, textvariable=self.maxYgroupgraph,width=3)
        entry.grid(row=1,column=20,columnspan=2)
        self.maxYgroupgraph.set(1)
        self.minmaxgroupgraphcheck = IntVar()
        aftermppcheck=Checkbutton(self.Frame4,text="Yscale",variable=self.minmaxgroupgraphcheck, 
                           onvalue=1,offvalue=0,height=1, width=6, command = lambda: self.UpdateGroupGraph(1),fg='black',background='white')
        aftermppcheck.grid(row=1, column=22, columnspan=3)
        
        self.transparentbkg = IntVar()
        transparentbkgcheck=Checkbutton(self.Frame4,text="transparentbkg",variable=self.transparentbkg, 
                           onvalue=1,offvalue=0,height=1, width=10, command = lambda: self.UpdateGroupGraph(1),fg='black',background='white')
        transparentbkgcheck.grid(row=2, column=0, columnspan=10)
        self.transparentbkg.set(1)
        
        #### JV ####

        columnpos = 20
        rowpos = 0
        
        self.saveIVgraph = Button(self.Frame2, text="Save graph",
                            command = self.GraphJVsave_as)
        self.saveIVgraph.grid(row=rowpos+1, column=columnpos, columnspan=3)
                
        self.updateIVgraph = Button(self.Frame2, text="Update graph",
                            command = self.UpdateIVGraph)
        self.updateIVgraph.grid(row=rowpos+2, column=columnpos, columnspan=3)
        
        self.changeIVlegend = Button(self.Frame2, text="change legend",
                            command = self.ChangeLegendIVgraph)
        self.changeIVlegend.grid(row=rowpos+3, column=columnpos, columnspan=3)
        
        self.CheckIVLegend = IntVar()
        legend=Checkbutton(self.Frame2,text='Legend',variable=self.CheckIVLegend, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateIVGraph,fg='black',background='white')
        legend.grid(row=rowpos+1, column=columnpos+3, columnspan=3)
        
        self.CheckIVLog = IntVar()
        logJV=Checkbutton(self.Frame2,text='Log',variable=self.CheckIVLog, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateIVGraph,fg='black',background='white')
        logJV.grid(row=rowpos+1, column=columnpos+5, columnspan=3)
        
        self.fontsizeJVGraph = tk.DoubleVar()
        entry=Entry(self.Frame2, textvariable=self.fontsizeJVGraph,width=3)
        entry.grid(row=rowpos+2, column=columnpos+5, columnspan=1)
        tk.Label(self.Frame2, text="Fontsize",fg='black',background='white').grid(row=rowpos+2, column=columnpos+6, columnspan=1)
        self.fontsizeJVGraph.set(8)
        
        self.IVtitle = Button(self.Frame2, text="Title",
                            command = self.GiveIVatitle)
        self.IVtitle.grid(row=rowpos, column=columnpos+3, columnspan=3)
        
        self.IVminx = tk.DoubleVar()
        entry=Entry(self.Frame2, textvariable=self.IVminx,width=5)
        entry.grid(row=rowpos+4,column=columnpos,columnspan=1)
        tk.Label(self.Frame2, text="Min X",fg='black',background='white').grid(row=rowpos+5,column=columnpos,columnspan=1)
        self.IVminx.set(-0.2)
        self.IVmaxx = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.IVmaxx,width=5).grid(row=rowpos+4,column=columnpos+1,columnspan=1)
        tk.Label(self.Frame2, text="Max X",fg='black',background='white').grid(row=rowpos+5,column=columnpos+1,columnspan=1)
        self.IVmaxx.set(1) 
        self.IVminy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.IVminy,width=5).grid(row=rowpos+4,column=columnpos+2,columnspan=1)
        tk.Label(self.Frame2, text="Min Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+2,columnspan=1)
        self.IVminy.set(-35)
        self.IVmaxy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.IVmaxy,width=5).grid(row=rowpos+4,column=columnpos+3,columnspan=1)
        tk.Label(self.Frame2, text="Max Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+3,columnspan=1)
        self.IVmaxy.set(10)
        
        self.IVlegpos1 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=1,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+4, columnspan=1)
        self.pos2 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=2,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+3, columnspan=1)
        self.pos3 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=3,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+3, columnspan=1)
        self.pos4 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=4,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+4, columnspan=1)
        self.pos5 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.IVlegpos1, 
                           onvalue=5,offvalue=0,height=1, width=1, command = self.UpdateIVGraph,fg='black',background='white')
        pos.grid(row=rowpos+4, column=columnpos+4, columnspan=1)
        
        
        #### MPP ###
        
        columnpos = 55
        rowpos = 0
        
        self.mppmenubutton = tk.Menubutton(self.Frame2, text="Choose mpp data", 
                                   indicatoron=True, borderwidth=1, relief="raised")
        self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
        self.mppmenubutton.configure(menu=self.mppmenu)
        self.mppmenubutton.grid(row=rowpos, column=columnpos, columnspan=3)

        self.savemppgraph = Button(self.Frame2, text="Save graph",
                            command = self.GraphMPPsave_as)
        self.savemppgraph.grid(row=rowpos+1, column=columnpos, columnspan=3)
        
        self.updatemppgraph = Button(self.Frame2, text="Update graph",
                           command = self.UpdateMppGraph)
        self.updatemppgraph.grid(row=rowpos+2, column=columnpos, columnspan=3)
        
        self.changempplegend = Button(self.Frame2, text="change legend",
                            command = self.ChangeLegendMPPgraph)
        self.changempplegend.grid(row=rowpos+3, column=columnpos, columnspan=3)
        
        self.CheckmppLegend = IntVar()
        legend=Checkbutton(self.Frame2,text='Legend',variable=self.CheckmppLegend, 
                           onvalue=1,offvalue=0,height=1, width=10, command = self.UpdateMppGraph,fg='black',background='white')
        legend.grid(row=rowpos+1, column=columnpos+3, columnspan=3)
        
        self.mpptitle = Button(self.Frame2, text="Title",
                            command = self.GiveMPPatitle)
        self.mpptitle.grid(row=rowpos, column=columnpos+3, columnspan=3)

        self.fontsizeMppGraph = tk.DoubleVar()
        entry=Entry(self.Frame2, textvariable=self.fontsizeMppGraph,width=3)
        entry.grid(row=rowpos+1, column=columnpos+5, columnspan=1)
        tk.Label(self.Frame2, text="Fontsize",fg='black',background='white').grid(row=rowpos+1, column=columnpos+6, columnspan=1)
        self.fontsizeMppGraph.set(8)
        
        self.mppminx = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppminx,width=5).grid(row=rowpos+4,column=columnpos,columnspan=1)
        tk.Label(self.Frame2, text="Min X",fg='black',background='white').grid(row=rowpos+5,column=columnpos,columnspan=1)
        self.mppminx.set(0)
        self.mppmaxx = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppmaxx,width=5).grid(row=rowpos+4,column=columnpos+1,columnspan=1)
        tk.Label(self.Frame2, text="Max X",fg='black',background='white').grid(row=rowpos+5,column=columnpos+1,columnspan=1)
        self.mppmaxx.set(500)
        self.mppminy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppminy,width=5).grid(row=rowpos+4,column=columnpos+2,columnspan=1)
        tk.Label(self.Frame2, text="Min Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+2,columnspan=1)
        self.mppminy.set(0)
        self.mppmaxy = tk.DoubleVar()
        Entry(self.Frame2, textvariable=self.mppmaxy,width=5).grid(row=rowpos+4,column=columnpos+3,columnspan=1)
        tk.Label(self.Frame2, text="Max Y",fg='black',background='white').grid(row=rowpos+5,column=columnpos+3,columnspan=1)
        self.mppmaxy.set(20)
        
        self.mpplegpos1 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=1,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+4, columnspan=1)
        self.pos2 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=2,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+2, column=columnpos+3, columnspan=1)
        self.pos3 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=3,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+3, columnspan=1)
        self.pos4 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=4,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+3, column=columnpos+4, columnspan=1)
        self.pos5 = IntVar()
        pos=Checkbutton(self.Frame2,text=None,variable=self.mpplegpos1, 
                           onvalue=5,offvalue=0,height=1, width=1, command = self.UpdateMppGraph,fg='black',background='white')
        pos.grid(row=rowpos+4, column=columnpos+4, columnspan=1)
        
        
        
        ############ the table ###################
        global testdata
        global DATA
        
        rowspantable=30
        columnspantable=70
        
        self.frame0 = Frame(self.superframe,bg='white')
        self.frame0.grid(row=26,column=37,rowspan=rowspantable,columnspan=columnspantable) #,sticky='wens'
        for r in range(rowspantable):
            self.frame0.rowconfigure(r, weight=1)    
        for c in range(columnspantable):
            self.frame0.columnconfigure(c, weight=1)
        
        self.import_button = Button(self.frame0, text = "Import Data", command = self.importdata)
        self.import_button.grid(row = 0, column = 0,columnspan=1)
        self.loadsession_button = Button(self.frame0, text = "Load session", command = self.LoadSession)
        self.loadsession_button.grid(row = 0, column = 4, columnspan=1)
        self.savesession_button = Button(self.frame0, text = "Save session", command = self.SaveSession)
        self.savesession_button.grid(row = 0, column = 5, columnspan=1)
        self.ExportAll = Button(self.frame0, text="DB & AutoAnalysis", command = self.AskforRefcells)
        self.ExportAll.grid(row=0, column=6, columnspan=1,rowspan=1)
#        self.Darktolight = Button(self.frame0, text="DtoL.",command = self.darktolightchange,fg='black')
#        self.Darktolight.grid(row=0, column=8, columnspan=1,rowspan=1)
#        self.changeArea = Button(self.frame0, text="ChangeArea",command = self.changecellarea,fg='black')
#        self.changeArea.grid(row=0, column=11, columnspan=1,rowspan=1)
        self.deletetabelem = Button(self.frame0, text = "Delete table elements", command = self.deletedatatreeview)
        self.deletetabelem.grid(row = 0, column = 1, columnspan=1)
        self.plotfromtable = Button(self.frame0, text="Plot",command = self.plottingfromTable,fg='black')
        self.plotfromtable.grid(row=0, column=9, columnspan=1,rowspan=1)
        self.groupbutton = Button(self.frame0, text="Group",command = self.groupfromTable,fg='black')
        self.groupbutton.grid(row=0, column=10, columnspan=1,rowspan=1)
        self.plotTimefromtable = Button(self.frame0, text="PlotTime",command = self.plottingTimefromTable,fg='black')
        self.plotTimefromtable.grid(row=0, column=11, columnspan=1,rowspan=1)

        self.frame01 = Frame(self.frame0,bg='black')
        self.frame01.grid(row=1,column=0,rowspan=rowspantable-1,columnspan=columnspantable)
        
        
        self.TableBuilder()
        
        self.workongoing = tk.Label(self.superframe, text='ready', font=5, relief=tk.RIDGE, width=10)
        self.workongoing.grid(row=32, column=0,columnspan=8,rowspan=10)
    

#%%######################################################################
        
    def on_closing(self):
        """
        what happens when user clicks on the red cross to exit the window.
        reinitializes all lists and destroys the window
        """
        global testdata, DATA, DATAJVforexport, DATAJVtabforexport
        global DATAmppforexport, DATAgroupforexport, takenforplot
        global takenforplotmpp, DATAMPP, DATAdark, DATAFV, IVlegendMod,groupstoplot
        global IVlinestyle, colorstylelist, MPPlegendMod, MPPlinestyle
        global titIV, titmpp, titStat, samplesgroups, listofanswer, listoflinestyle, listofcolorstyle,listoflinewidthstyle
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            testdata = []
            DATA = [] #[{"SampleName":, "CellNumber": , "MeasDayTime":, "CellSurface":, "Voc":, "Jsc":, "FF":, "Eff":, "Pmpp":, "Vmpp":, "Jmpp":, "Roc":, "Rsc":, "VocFF":, "RscJsc":, "NbPoints":, "Delay":, "IntegTime":, "Vstart":, "Vend":, "Illumination":, "ScanDirection":, "ImaxComp":, "Isenserange":,"AreaJV":, "Operator":, "MeasComment":, "IVData":}]
            DATAJVforexport=[]
            DATAJVtabforexport=[]
            DATAmppforexport=[]
            DATAgroupforexport=[]
            takenforplot=[]
            takenforplotmpp=[]
            plt.close()
            DATAMPP = []
            DATAdark = []
            DATAFV=[]
            
            IVlegendMod = []
            IVlinestyle = []
            colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
            
            MPPlegendMod = []
            MPPlinestyle = []
            
            titIV =0
            titmpp=0
            titStat=0
            samplesgroups=["Default group"]
            groupstoplot=["Default group"]
            
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]   
            listoflinewidthstyle=[]

            self.destroy()
            self.master.deiconify()

    
    def darktolightchange(self):
        DtoL.DarkToLight()
        
    def onFrameConfigure(self, event):
        self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        #self.canvas0.configure(scrollregion=(0,0,500,500))
    def start(self):
        self.progress["value"] = 0
        self.maxbytes = 100000
        self.progress["maximum"] = 100000
        self.read_bytes()
        
    def updateTable(self):
        self.TableBuilder()

#%%######################################################################
        
    def importdata(self):
        global DATA 
        global DATAFV
        global DATAMPP
        global DATAdark, numbLightfiles, numbDarkfiles
               
        self.workongoing.configure(text="Importation\nstarted...\nPatience\nis a great\nvirtue")
        
        finished=0
        j=0
        while j<2:
            #try: 
            file_pathnew=[]
            file_path =filedialog.askopenfilenames(title="Please select the JV files")
            if file_path!='':
                filetypes=[os.path.splitext(item)[1] for item in file_path]
#                print(list(set(filetypes)))
                if len(list(set(filetypes)))==1 or (''in list(set(filetypes)) and '.txt'in list(set(filetypes))) or (".itx" in list(set(filetypes)) and '.txt'in list(set(filetypes))):
                    directory = os.path.join(str(Path(file_path[0]).parent.parent),'resultFilesIV')
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                        os.chdir(directory)
                    else :
                        os.chdir(directory)
                    filetype=list(set(filetypes))[0]
                    if filetype==".iv":
                        file_pathnew=file_path
                        print("these are rawdata files")
                        self.getdatalistsfromIVTFfiles(file_pathnew)
                        finished=1
                        break
                    elif filetype==".itx" or (".itx" in list(set(filetypes)) and '.txt'in list(set(filetypes))):
                        print("cigs igor text data")
                        self.getdatalistsfromNRELcigssetup(file_path)
                        finished=1
                        break
                    elif filetype==".txt" or filetype=='':
                        filetoread = open(file_path[0],"r", encoding='ISO-8859-1')
                        filerawdata = filetoread.readlines()
                        print(filerawdata[0])
                        if '***' in filerawdata[0]:
                            print("NREL files")
                            self.getdatalistsfromNRELfiles(file_path)
                            finished=1
                        elif 'Notes' in filerawdata[1]:
                            print("CUB files")
                            self.getdatalistsfromCUBfiles(file_path)
                            finished=1
                        else:
                            print("NREL files")
                            self.getdatalistsfromNRELfiles(file_path)
                            finished=1
                        break
                    elif filetype==".xls":
                        celltest=[]
                        for k in range(len(file_path)):
                            wb = xlrd.open_workbook(file_path[k])
                            xlsheet = wb.sheet_by_index(0)
                            celltest.append(str(xlsheet.cell(3,0).value))
                        if len(list(set(celltest)))==1:
                            if celltest[0]=="User name:             ":#HIT excel files
                                print("HITfiles")
                                self.getdatalistsfromIVHITfiles(file_path)
                                finished=1
                                break
                            elif str(xlsheet.cell(3,1).value)=="Cell number":
                                print("thin film files")
                                for k in range(len(file_path)):
                                    wb = xlrd.open_workbook(file_path[k])
                                    sheet_names = wb.sheet_names()
                                    for j in range(len(sheet_names)):
                                        if 'Sheet' not in sheet_names[j]:
                                            xlsheet = wb.sheet_by_index(j)
                                            #print(sheet_names[j])
                                            item=0
                                            while(True):
                                                try:
                                                    #print(item)
                                                    cell1 = xlsheet.cell(68+item,17).value 
                                                    #print(cell1)
                                                    if cell1!="":
                                                        file_pathnew.append(cell1)
                                                        item+=1
                                                    else:
                                                        break
                                                except:
                                                    print("except")
                                                    break
                                self.getdatalistsfromIVTFfiles(file_pathnew)
                                finished=1
                                break
                            else:
                                messagebox.showinfo("Information","these are not IV related .xls files... try again")
#                                print("these are not IV related .xls files... try again")
                                j+=1
                        else:
                            messagebox.showinfo("Information","several types of .xls files... try again")
#                            print("several types of .xls files... try again")
                            j+=1
                    else:
                        messagebox.showinfo("Information","neither .iv or .xls IV files... try again")
#                        print("neither .iv or .xls IV files... try again")
                        j+=1
                else:
                    messagebox.showinfo("Information","Multiple types of files... please choose one!")
#                    print("Multiple types of files... please choose one!")
                    j+=1
            else:
                messagebox.showinfo("Information","Please select IV files")
#                print("Please select IV files")
                j+=1
            #except:
            #    print("no file selected")
            #    j+=1
        
        if finished:
            print("getdata done")
            print(len(DATA))
            print(len(DATAMPP))
            print(len(DATAdark))
            print(len(DATAFV))
            self.workongoing.configure(text="Imported:\n%d JV files\n%d MPP files\n%d Dark files " % (numbLightfiles,len(DATAMPP),numbDarkfiles))
            
            if DATAMPP!=[]:
                self.mppnames = ()
                self.mppnames=self.SampleMppNames(DATAMPP)
                self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
                self.mppmenubutton.configure(menu=self.mppmenu)
                self.choicesmpp = {}
                for choice in range(len(self.mppnames)):
                    self.choicesmpp[choice] = tk.IntVar(value=0)
                    self.mppmenu.add_checkbutton(label=self.mppnames[choice], variable=self.choicesmpp[choice], 
                                         onvalue=1, offvalue=0, command = self.UpdateMppGraph0)
            
            self.updateTable()
            
#%%######################################################################
     
    def UpdateHistGraph(self, a):
        global DATA
        global DATAHistforexport, groupstoplot

        
        DATAHistforexport=[]
        numbbins=int(self.NumbBinsHist.get())
        DATAx=copy.deepcopy(DATA)
        
        samplesgroups=[]
        for name, var in self.choicesgroupHisttoplot.items():
            samplesgroups.append(var.get())
        m=[]
        for i in range(len(samplesgroups)):
            if samplesgroups[i]==1:
                m.append(groupstoplot[i])
        samplesgroups=m
        groupnames=[]
        #sorting data
        if samplesgroups==[]:
            self.Histofig.clear()
        else:
            grouplistdict=[]
            if self.HistWhichMeasChoice.get()=="Allmeas":    #select all data points
                for item in range(len(samplesgroups)):
                    listdata=[]
                    for item1 in range(len(DATAx)):
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light':
                            listdata.append(DATAx[item1][self.HistparamChoice.get()])
                    groupnames.append(samplesgroups[item])        
                    grouplistdict.append(listdata)
            
            elif self.HistWhichMeasChoice.get()=="OnlyRev":
                for item in range(len(samplesgroups)):
                    listdata=[]
                    for item1 in range(len(DATAx)):
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["ScanDirection"]=="Reverse":
                            listdata.append(DATAx[item1][self.HistparamChoice.get()])
                    groupnames.append(samplesgroups[item])        
                    grouplistdict.append(listdata)
                    
            elif self.HistWhichMeasChoice.get()=="OnlyForw":
                for item in range(len(samplesgroups)):
                    listdata=[]
                    for item1 in range(len(DATAx)):
                        if DATAx[item1]["Group"]==samplesgroups[item] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["ScanDirection"]=="Forward":
                            listdata.append(DATAx[item1][self.HistparamChoice.get()])
                    groupnames.append(samplesgroups[item])        
                    grouplistdict.append(listdata)
                    
            elif self.HistWhichMeasChoice.get()=="Bestof/pix":  
                for item in range(len(samplesgroups)):
                    groupdict={}
                    groupdict["Group"]=samplesgroups[item]
                    listofthegroup=[]
                    for item1 in range(len(DATAx)):
                        if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                            listofthegroup.append(DATAx[item1])
                    if len(listofthegroup)!=0:
                        grouper = itemgetter("DepID", "Cellletter")
                        result = []
                        keylist=[]
                        for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                            result.append(list(grp))
                            keylist.append(key)
                        print(result)
                        print(keylist)
                        listdata=[]
                        for item1 in range(len(keylist)):
                            listdata1=[]
                            for item2 in range(len(result[item1])):
                                listdata1.append(result[item1][item2][self.HistparamChoice.get()])
                            listdata.append(max(listdata1))
                            
                        groupnames.append(samplesgroups[item])        
                        grouplistdict.append(listdata)
                    
                    
            elif self.HistWhichMeasChoice.get()=="Bestof/subst":  
                for item in range(len(samplesgroups)):
                    groupdict={}
                    groupdict["Group"]=samplesgroups[item]
                    listofthegroup=[]
                    for item1 in range(len(DATAx)):
                        if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                            listofthegroup.append(DATAx[item1])
                    if len(listofthegroup)!=0:
                        grouper = itemgetter("DepID")
                        result = []
                        keylist=[]
                        for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                            result.append(list(grp))
#                            print(len(result))
                            keylist.append(key)
                        
                        listdata=[]
                        for item1 in range(len(keylist)):
                            listdata1=[]
                            for item2 in range(len(result[item1])):
                                listdata1.append(result[item1][item2][self.HistparamChoice.get()])
                            listdata.append(max(listdata1))
                            
                        groupnames.append(samplesgroups[item])        
                        grouplistdict.append(listdata)
        
        #ploting data   "Bestof/pix", "Bestof/subst"
        
        
            self.Histofig.clear()
            if self.minmaxHistgraphcheck.get():
                self.Histofig.hist(grouplistdict,bins=numbbins,range=[self.minXHistgraph.get(), self.maxXHistgraph.get()],histtype= self.HistTypeChoice.get(), density=False, cumulative=False, alpha=0.6, edgecolor='black', linewidth=1.2, label=groupnames)
            else:
                self.Histofig.hist(grouplistdict,bins=numbbins,histtype= self.HistTypeChoice.get(), density=False, cumulative=False, alpha=0.6, edgecolor='black', linewidth=1.2, label=groupnames)
                
            self.Histofig.set_xlabel(self.HistparamChoice.get())
            self.Histofig.set_ylabel('counts')
            self.Histofig.legend()
        
            DATAHistforexport=list(map(list, six.moves.zip_longest(*grouplistdict, fillvalue=' ')))
            DATAHistforexport=[groupnames]+DATAHistforexport

        
        plt.gcf().canvas.draw()
        
        
        
    def GraphHistsave_as(self):
        global DATA, DATAHistforexport
        
        try:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
            extent = self.Histofig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
            self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.3, 1.3))#, transparent=True)
                           
            DATAHistforexport1=[]            
            for item in DATAHistforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAHistforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAHistforexport1)
            file.close()
        
        except:
            print("there is an exception") 
        
        
        
    def UpdateGroupGraph(self,a):
        global DATA
        global DATAdark
        global DATAFV
        global DATAMPP
        global groupstoplot
        global DATAgroupforexport
        
#        print(samplesgroups)
        
        DATAgroupforexport=[]
        fontsizegroup=self.fontsizeGroupGraph.get()
        DATAx=copy.deepcopy(DATA)
        
#        print(groupstoplot)
        
        samplesgroups=[]
        for name, var in self.choicesgrouptoplot.items():
            samplesgroups.append(var.get())
        m=[]
        for i in range(len(samplesgroups)):
            if samplesgroups[i]==1:
                m.append(groupstoplot[i])
        samplesgroups=m
        
#        print(samplesgroups)
        
#        samplesgroups=copy.deepcopy(groupstoplot)
#        try:
        if len(samplesgroups)>0:    #if user defined group names different than "Default group"        
            grouplistdict=[]
            if self.RF.get()==0:    #select all data points
                if self.aftermppcheck.get()==0:#all points without separation
                    for item in range(len(samplesgroups)):
#                        print(samplesgroups[item])
                        groupdict={}
                        groupdict["Group"]=samplesgroups[item]
                        listofthegroup=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                                listofthegroup.append(DATAx[item1])
                       
                        if len(listofthegroup)!=0:
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            for item1 in range(len(listofthegroup)):
#                                print(listofthegroup[item1]["ScanDirection"])
                                if listofthegroup[item1]["ScanDirection"]=="Reverse":
                                    listofthegroupRev.append(listofthegroup[item1])
                                else:
                                    listofthegroupFor.append(listofthegroup[item1])
                            
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
                            grouplistdict.append(groupdict)
                else:#for separation before/after mpp
                    for item in range(len(samplesgroups)):
                        groupdict={}
                        groupdict["Group"]=samplesgroups[item]
                        listofthegroup=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==0:
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            for item1 in range(len(listofthegroup)):
                                if listofthegroup[item1]["ScanDirection"]=="Reverse":
                                    listofthegroupRev.append(listofthegroup[item1])
                                else:
                                    listofthegroupFor.append(listofthegroup[item1])
                            
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
#                            grouplistdict.append(groupdict)
                        listofthegroup2=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==1:
                                listofthegroup2.append(DATAx[item1])
                        if len(listofthegroup2)!=0:
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            for item1 in range(len(listofthegroup2)):
                                if listofthegroup2[item1]["ScanDirection"]=="Reverse":
                                    listofthegroupRev.append(listofthegroup2[item1])
                                else:
                                    listofthegroupFor.append(listofthegroup2[item1])
                            
                            groupdict["RevVocAMPP"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVocAMPP"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJscAMPP"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJscAMPP"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFFAMPP"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFFAMPP"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEffAMPP"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEffAMPP"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRocAMPP"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRocAMPP"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRscAMPP"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRscAMPP"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmppAMPP"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmppAMPP"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmppAMPP"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmppAMPP"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                        else:
                            groupdict["RevVocAMPP"]=[]
                            groupdict["ForVocAMPP"]=[]
                            groupdict["RevJscAMPP"]=[]
                            groupdict["ForJscAMPP"]=[]
                            groupdict["RevFFAMPP"]=[]
                            groupdict["ForFFAMPP"]=[]
                            groupdict["RevEffAMPP"]=[]
                            groupdict["ForEffAMPP"]=[]
                            groupdict["RevRocAMPP"]=[]
                            groupdict["ForRocAMPP"]=[]
                            groupdict["RevRscAMPP"]=[]
                            groupdict["ForRscAMPP"]=[]
                            groupdict["RevVmppAMPP"]=[]
                            groupdict["ForVmppAMPP"]=[]
                            groupdict["RevJmppAMPP"]=[]
                            groupdict["ForJmppAMPP"]=[]                            
                        grouplistdict.append(groupdict)
                    
                    
            elif self.RF.get()==1:      #select only the best RevFor of each cell
                if self.aftermppcheck.get()==0:
                    for item in range(len(samplesgroups)):
                        groupdict={}
                        groupdict["Group"]=samplesgroups[item]
                        listofthegroup=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
                            grouper = itemgetter("DepID", "Cellletter",'ScanDirection')
                            result = []
                            for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                                result.append(list(grp))
                            
                            result1=[]
                            
                            for item in result:
                                result1.append(sorted(item,key=itemgetter('Eff'),reverse=True)[0])
                            
                            grouper = itemgetter('ScanDirection')
                            result2 = []
                            for key, grp in groupby(sorted(result1, key = grouper), grouper):
                                result2.append(list(grp))
                            
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            
                            if result2[0][0]['ScanDirection']=='Forward':
                                listofthegroupFor=result2[0]
                                if len(result2)>1:
                                    listofthegroupRev=result2[1]
                            else:
                                listofthegroupRev=result2[0]
                                if len(result2)>1:
                                    listofthegroupFor=result2[1]
        
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
                            grouplistdict.append(groupdict)
                else: #if aftermppchecked
#                    print("aftermpp is checked")
#                    print(samplesgroups)
                    for item in range(len(samplesgroups)):
                        groupdict={}
                        groupdict["Group"]=samplesgroups[item]
                        listofthegroup=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==0:
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
#                            print("listofthegroup1nonzero")
                            grouper = itemgetter("DepID", "Cellletter",'ScanDirection')
                            result = []
                            for key, grp in groupby(sorted(listofthegroup, key = grouper), grouper):
                                result.append(list(grp))
                            
                            result1=[]
                            
                            for item in result:
                                result1.append(sorted(item,key=itemgetter('Eff'),reverse=True)[0])
                            
                            grouper = itemgetter('ScanDirection')
                            result2 = []
                            for key, grp in groupby(sorted(result1, key = grouper), grouper):
                                result2.append(list(grp))
                            
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            
                            if result2[0][0]['ScanDirection']=='Forward':
                                listofthegroupFor=result2[0]
                                if len(result2)>1:
                                    listofthegroupRev=result2[1]
                            else:
                                listofthegroupRev=result2[0]
                                if len(result2)>1:
                                    listofthegroupFor=result2[1]
        
                            groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRoc"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRoc"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRsc"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRsc"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmpp"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmpp"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmpp"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmpp"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                            
#                            grouplistdict.append(groupdict)
                        listofthegroup2=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light' and DATAx[item1]["aftermpp"]==1:
                                listofthegroup2.append(DATAx[item1])
                        if len(listofthegroup2)!=0:
#                            print("listofthegroup2nonzero")
                            grouper = itemgetter("DepID", "Cellletter",'ScanDirection')
                            result = []
                            for key, grp in groupby(sorted(listofthegroup2, key = grouper), grouper):
                                result.append(list(grp))
                            
                            result1=[]
                            
                            for item in result:
                                result1.append(sorted(item,key=itemgetter('Eff'),reverse=True)[0])
                            
                            grouper = itemgetter('ScanDirection')
                            result2 = []
                            for key, grp in groupby(sorted(result1, key = grouper), grouper):
                                result2.append(list(grp))
                            
                            listofthegroupRev=[]
                            listofthegroupFor=[]
                            
                            if result2[0][0]['ScanDirection']=='Forward':
                                listofthegroupFor=result2[0]
                                if len(result2)>1:
                                    listofthegroupRev=result2[1]
                            else:
                                listofthegroupRev=result2[0]
                                if len(result2)>1:
                                    listofthegroupFor=result2[1]
        
                            groupdict["RevVocAMPP"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                            groupdict["ForVocAMPP"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                            groupdict["RevJscAMPP"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                            groupdict["ForJscAMPP"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                            groupdict["RevFFAMPP"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                            groupdict["ForFFAMPP"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                            groupdict["RevEffAMPP"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                            groupdict["ForEffAMPP"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                            groupdict["RevRocAMPP"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                            groupdict["ForRocAMPP"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                            groupdict["RevRscAMPP"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                            groupdict["ForRscAMPP"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                            groupdict["RevVmppAMPP"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                            groupdict["ForVmppAMPP"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                            groupdict["RevJmppAMPP"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                            groupdict["ForJmppAMPP"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                        else:
                            groupdict["RevVocAMPP"]=[]
                            groupdict["ForVocAMPP"]=[]
                            groupdict["RevJscAMPP"]=[]
                            groupdict["ForJscAMPP"]=[]
                            groupdict["RevFFAMPP"]=[]
                            groupdict["ForFFAMPP"]=[]
                            groupdict["RevEffAMPP"]=[]
                            groupdict["ForEffAMPP"]=[]
                            groupdict["RevRocAMPP"]=[]
                            groupdict["ForRocAMPP"]=[]
                            groupdict["RevRscAMPP"]=[]
                            groupdict["ForRscAMPP"]=[]
                            groupdict["RevVmppAMPP"]=[]
                            groupdict["ForVmppAMPP"]=[]
                            groupdict["RevJmppAMPP"]=[]
                            groupdict["ForJmppAMPP"]=[]    
                        grouplistdict.append(groupdict)
#                        listofthegroup=listofthegroup1+listofthegroup2
#            print("aftermpp0") 
#            print(listofthegroup)
#            print(len(listofthegroup))
#            print(len(grouplistdict))
            if 1:#grouplistdict!=[]:  
#                print("is grouplistdict non zero length")
#                print(len(grouplistdict))
                self.GroupStatfig.clear()
                names=samplesgroups
                #                print("aftermpp1")
                if self.GroupChoice.get()=="Eff":
                    if self.aftermppcheck.get()==0:
                        Effsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i])
                        valstot=[]
                        
                        for item in names:
                            d=[item,"RevEff"]+[i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i]
                            if d!=[]:
                                DATAgroupforexport.append(d[0])
                            d=[item,"ForEff"]+[i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i]
                            if d!=[]:
                                DATAgroupforexport.append(d[0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
        
                        Rev=[]
                        Forw=[]
                        namelist=[]
#                        print(names)
                        for i in range(len(names)):
                             if valsRev!=[]:
                                 if valsRev[i]!=[]:
                                     if valsRev[i][0]!=[]:
                                         Rev.append(valsRev[i][0])
                                     else:
                                         Rev.append([])
                             if valsFor!=[]:
                                 if valsFor[i]!=[]:
                                     if valsFor[i][0]!=[]:
                                         Forw.append(valsFor[i][0])
                                     else:
                                         Forw.append([])
                             if valsRev!=[] or valsFor!=[]: 
                                 if valsRev[i]!=[] or valsFor[i]!=[]: 
                                     if valsRev[i][0]!=[] or valsFor[i][0]!=[]:
                                         valstot.append(valsRev[i][0]+valsFor[i][0])
                                         namelist.append(names[i])
#                        print(namelist)  
                        
                        if self.boxplot.get()==1:
                            Effsubfig.boxplot(valstot,0,'',labels=namelist)
                    
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Effsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Effsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                            
                    else:
#                        print("aftermpp")
                        Effsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i])
                        valsRevAMPP=[]
                        for item in names:
#                            v=[i["RevEffAMPP"] for i in grouplistdict if i["Group"]==item and "RevEffAMPP" in i]
                            valsRevAMPP.append([i["RevEffAMPP"] for i in grouplistdict if i["Group"]==item and "RevEffAMPP" in i])
#                        print(len(valsRevAMPP))
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForEffAMPP"] for i in grouplistdict if i["Group"]==item and "ForEffAMPP" in i])
#                        print(len(valsForAMPP))
                        
                        
                        
                        for item in names:
                            try:
                                DATAgroupforexport.append([item,"RevEff"]+[i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i][0])
                            except IndexError:
#                                print("indexError1")
                                DATAgroupforexport.append([item,"RevEff"]+[])
                            try:
                                DATAgroupforexport.append([item,"ForEff"]+[i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i][0])
                            except IndexError:
#                                print("indexError1")
                                DATAgroupforexport.append([item,"ForEff"]+[])
                            try:
                                DATAgroupforexport.append([item,"RevEffAMPP"]+[i["RevEffAMPP"] for i in grouplistdict if i["Group"]==item and "RevEffAMPP" in i][0])
                            except IndexError:
#                                print("indexError1")
                                DATAgroupforexport.append([item,"RevEffAMPP"]+[])
                            try:
                                DATAgroupforexport.append([item,"ForEffAMPP"]+[i["ForEffAMPP"] for i in grouplistdict if i["Group"]==item and "ForEffAMPP" in i][0])
                            except IndexError:
#                                print("indexError2")
                                DATAgroupforexport.append([item,"ForEffAMPP"]+[])

                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i]!=[]:
                                if valsRev[i][0]!=[]:
                                     Rev.append(valsRev[i][0])
                                else:
                                     Rev.append([])
                            else:
                                Rev.append([])
                            if valsFor[i]!=[]:
                                if valsFor[i][0]!=[]:
                                     Forw.append(valsFor[i][0])
                                else:
                                     Forw.append([])
                            else:
                                Forw.append([])
                            if valsRevAMPP[i]!=[]:
                                if valsRevAMPP[i][0]!=[]:
                                     RevAMPP.append(valsRevAMPP[i][0])
                                else:
                                     RevAMPP.append([])
                            else:
                                RevAMPP.append([])
                            if valsForAMPP[i]!=[]:    
                                if valsForAMPP[i][0]!=[]:
                                     ForwAMPP.append(valsForAMPP[i][0])
                                else:
                                     ForwAMPP.append([])  
                            else:
                                ForwAMPP.append([])
                            try:    
                                if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                     valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                     namelist.append(names[i])
                            except IndexError:
                                toaddtovalstot=[]
                                try:
                                    toaddtovalstot+=valsRev[i][0]
                                except:
                                    pass
                                try:
                                    toaddtovalstot+=valsFor[i][0]
                                except:
                                    pass
                                try:
                                    toaddtovalstot+=valsRevAMPP[i][0]
                                except:
                                    pass
                                try:
                                    toaddtovalstot+=valsForAMPP[i][0]
                                except:
                                    pass
                                    
                                    
#                        if len(listofthegroup)!=0:
#                            for i in range(len(names)):
#                                found1=0
#                                found2=0
#                                try:
#                                    if valsRev[i]!=[]:
#                                         if valsRev[i][0]!=[]:
#                                             Rev.append(valsRev[i][0])
#                                             found1=1
#                                         else:
#                                             Rev.append([])
#                                    else:
#                                         Rev.append([])
#                                except:
#                                    print("indexError3")
#                                    Rev.append([])
#                                try:
#                                    if valsFor[i]!=[]:    
#                                         if valsFor[i][0]!=[]:
#                                             Forw.append(valsFor[i][0])
#                                             found2=1
#                                         else:
#                                             Forw.append([])
#                                    else:
#                                         Forw.append([])
#                                except:
#                                    print("indexError4")
#                                    Forw.append([])
#                                try:    
#                                    if found1 and found2 :
#                                         valstot.append(valsRev[i][0]+valsFor[i][0])
#                                         namelist.append(names[i])
#                                    elif found1 and not found2:
#                                         valstot.append(valsRev[i][0])
#                                         namelist.append(names[i])
#                                    elif not found1 and found2:
#                                         valstot.append(valsFor[i][0])
#                                         namelist.append(names[i])
#                                except:
#                                    print("indexError5")
                                    
                                     
#                        if len(listofthegroup2)!=0:   
#                            for i in range(len(names)):
#                                found1=0
#                                found2=0
#                                try:
#                                    if valsRevAMPP[i]!=[]:
#                                         if valsRevAMPP[i][0]!=[]:
#                                             RevAMPP.append(valsRevAMPP[i][0])
#                                             found1=0
#                                         else:
#                                             RevAMPP.append([]) 
#                                    else:
#                                         RevAMPP.append([])
#                                except:
#                                    print("indexError6")
#                                    RevAMPP.append([])
#                                try:    
#                                    if valsForAMPP[i][0]!=[]:    
#                                         if valsForAMPP[i][0]!=[]:
#                                             ForwAMPP.append(valsForAMPP[i][0])
#                                         else:
#                                             ForwAMPP.append([])
#                                    else:
#                                         ForwAMPP.append([]) 
#                                except:
#                                    print("indexError7")
#                                    ForwAMPP.append([]) 
#                                try:
#                                    if found1 and found2 :
#                                         valstot.append(valsRevAMPP[i][0]+valsForAMPP[i][0])
#                                         namelist.append(names[i])
#                                    elif found1 and not found2:
#                                         valstot.append(valsRevAMPP[i][0])
#                                         namelist.append(names[i])
#                                    elif not found1 and found2:
#                                         valstot.append(valsForAMPP[i][0])
#                                         namelist.append(names[i])
#                                except:
#                                    print("indexError8")
                        if namelist!=[]:            
                            if self.boxplot.get()==1:
                                Effsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                            for i in range(len(namelist)):
    #                            if len(listofthegroup)!=0:
                                y=Rev[i]
                                if len(y)>0:
                                    x=np.random.normal(i+0.9,0.04,size=len(y))
                                    Effsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                                y=Forw[i]
                                if len(y)>0:
                                    x=np.random.normal(i+0.9,0.04,size=len(y))
                                    Effsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
    #                            if len(listofthegroup2)!=0:   
                                    y=RevAMPP[i]
                                if len(y)>0:
                                    x=np.random.normal(i+1.1,0.04,size=len(y))
                                    Effsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                                y=ForwAMPP[i]
                                if len(y)>0:
                                    x=np.random.normal(i+1.1,0.04,size=len(y))
                                    Effsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5) 
                                
                    if self.boxplot.get()==0:
                        if namelist!=[]:
                            span=range(1,len(namelist)+1)
#                            print(namelist)
#                            print(span)
    #                        plt.xticks(span,namelist)
                            Effsubfig.set_xticks(span)
                            Effsubfig.set_xticklabels(namelist)
                            Effsubfig.set_xlim([0.5,span[-1]+0.5])
                    
                    if self.minmaxgroupgraphcheck.get()==1:
                        Effsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])
                        
                    Effsubfig.set_ylabel('Efficiency (%)')
                    for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                                 Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    
                    for tick in Effsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Voc":
                    if self.aftermppcheck.get()==0:
                        Vocsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i])
                         
                        for item in names:
                            DATAgroupforexport.append([item,"RevVoc"]+[i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i][0])
                            DATAgroupforexport.append([item,"ForVoc"]+[i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        namelist=[]
#                        for i in range(len(names)):
#                            if valsRev[i][0]==[] and valsFor[i][0]==[]:
#                                print(" ")
#                            else:
#                                Rev.append(valsRev[i][0])
#                                Forw.append(valsFor[i][0])
#                                valstot.append(valsRev[i][0]+valsFor[i][0])
#                                namelist.append(names[i])
                        for i in range(len(names)):
                             if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                             else:
                                 Rev.append([])
                             if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                             else:
                                 Forw.append([])
                             if valsRev[i][0]!=[] or valsFor[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0])
                                 namelist.append(names[i])
                                 
                        if self.boxplot.get()==1:
                            Vocsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Vocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Vocsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    else:
                        Vocsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i])
                        valsRevAMPP=[]
                        for item in names:
                            valsRevAMPP.append([i["RevVocAMPP"] for i in grouplistdict if i["Group"]==item and "RevVocAMPP" in i])
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForVocAMPP"] for i in grouplistdict if i["Group"]==item and "ForVocAMPP" in i])

                        
                        for item in names:
                            DATAgroupforexport.append([item,"RevVoc"]+[i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i][0])
                            DATAgroupforexport.append([item,"ForVoc"]+[i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i][0])
                            DATAgroupforexport.append([item,"RevVocAMPP"]+[i["RevVocAMPP"] for i in grouplistdict if i["Group"]==item and "RevVocAMPP" in i][0])
                            DATAgroupforexport.append([item,"ForVocAMPP"]+[i["ForVocAMPP"] for i in grouplistdict if i["Group"]==item and "ForVocAMPP" in i][0])
         
                        
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                            else:
                                 Rev.append([])
                            if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                            else:
                                 Forw.append([])
                            if valsRevAMPP[i][0]!=[]:
                                 RevAMPP.append(valsRevAMPP[i][0])
                            else:
                                 RevAMPP.append([])
                            if valsForAMPP[i][0]!=[]:
                                 ForwAMPP.append(valsForAMPP[i][0])
                            else:
                                 ForwAMPP.append([])    
                            if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                 namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Vocsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Vocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Vocsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                            y=RevAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Vocsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                            y=ForwAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Vocsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5)  
                                
                                
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        Vocsubfig.set_xticks(span)
                        Vocsubfig.set_xticklabels(namelist)
                        Vocsubfig.set_xlim([0.5,span[-1]+0.5])
                        
                    if self.minmaxgroupgraphcheck.get()==1:
                        Vocsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    Vocsubfig.set_ylabel('Voc (mV)')
                    for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                                 Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Vocsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                        
                elif self.GroupChoice.get()=="Jsc":  
                    if self.aftermppcheck.get()==0:
                        Jscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i])
                         
                        for item in names:
                            DATAgroupforexport.append([item,"RevJsc"]+[i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i][0])
                            DATAgroupforexport.append([item,"ForJsc"]+[i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]==[] and valsFor[i][0]==[]:
                                print(" ")
                            else:
                                Rev.append(valsRev[i][0])
                                Forw.append(valsFor[i][0])
                                valstot.append(valsRev[i][0]+valsFor[i][0])
                                namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Jscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Jscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Jscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    else:
                        Jscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i])
                        valsRevAMPP=[]
                        for item in names:
                            valsRevAMPP.append([i["RevJscAMPP"] for i in grouplistdict if i["Group"]==item and "RevJscAMPP" in i])
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForJscAMPP"] for i in grouplistdict if i["Group"]==item and "ForJscAMPP" in i])
 
                        for item in names:
                            DATAgroupforexport.append([item,"RevJsc"]+[i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i][0])
                            DATAgroupforexport.append([item,"ForJsc"]+[i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i][0])
                            DATAgroupforexport.append([item,"RevJscAMPP"]+[i["RevJscAMPP"] for i in grouplistdict if i["Group"]==item and "RevJscAMPP" in i][0])
                            DATAgroupforexport.append([item,"ForJscAMPP"]+[i["ForJscAMPP"] for i in grouplistdict if i["Group"]==item and "ForJscAMPP" in i][0])

                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                            else:
                                 Rev.append([])
                            if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                            else:
                                 Forw.append([])
                            if valsRevAMPP[i][0]!=[]:
                                 RevAMPP.append(valsRevAMPP[i][0])
                            else:
                                 RevAMPP.append([])
                            if valsForAMPP[i][0]!=[]:
                                 ForwAMPP.append(valsForAMPP[i][0])
                            else:
                                 ForwAMPP.append([])    
                            if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                 namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Jscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Jscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Jscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                            y=RevAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Jscsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                            y=ForwAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Jscsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5) 
                        
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        Jscsubfig.set_xticks(span)
                        Jscsubfig.set_xticklabels(namelist)
                        Jscsubfig.set_xlim([0.5,span[-1]+0.5])
                        
                    if self.minmaxgroupgraphcheck.get()==1:
                        Jscsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                    for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                                 Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Jscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="FF":
                    if self.aftermppcheck.get()==0:
                        FFsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i])
                        
                        for item in names:
                            DATAgroupforexport.append([item,"RevFF"]+[i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i][0])
                            DATAgroupforexport.append([item,"ForFF"]+[i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]==[] and valsFor[i][0]==[]:
                                print(" ")
                            else:
                                Rev.append(valsRev[i][0])
                                Forw.append(valsFor[i][0])
                                valstot.append(valsRev[i][0]+valsFor[i][0])
                                namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            FFsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                FFsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                FFsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    else:
                        FFsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i])
                        valsRevAMPP=[]
                        for item in names:
                            valsRevAMPP.append([i["RevFFAMPP"] for i in grouplistdict if i["Group"]==item and "RevFFAMPP" in i])
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForFFAMPP"] for i in grouplistdict if i["Group"]==item and "ForFFAMPP" in i])

                        for item in names:
                            DATAgroupforexport.append([item,"RevFF"]+[i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i][0])
                            DATAgroupforexport.append([item,"ForFF"]+[i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i][0])
                            DATAgroupforexport.append([item,"RevFFAMPP"]+[i["RevFFAMPP"] for i in grouplistdict if i["Group"]==item and "RevFFAMPP" in i][0])
                            DATAgroupforexport.append([item,"ForFFAMPP"]+[i["ForFFAMPP"] for i in grouplistdict if i["Group"]==item and "ForFFAMPP" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                            else:
                                 Rev.append([])
                            if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                            else:
                                 Forw.append([])
                            if valsRevAMPP[i][0]!=[]:
                                 RevAMPP.append(valsRevAMPP[i][0])
                            else:
                                 RevAMPP.append([])
                            if valsForAMPP[i][0]!=[]:
                                 ForwAMPP.append(valsForAMPP[i][0])
                            else:
                                 ForwAMPP.append([])    
                            if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                 namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            FFsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                FFsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                FFsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                            y=RevAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                FFsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                            y=ForwAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                FFsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5)  
                                
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        FFsubfig.set_xticks(span)
                        FFsubfig.set_xticklabels(namelist)
                        FFsubfig.set_xlim([0.5,span[-1]+0.5])
                        
                    if self.minmaxgroupgraphcheck.get()==1:
                        FFsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    FFsubfig.set_ylabel('FF (%)')
                    for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                                 FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in FFsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Roc":
                    if self.aftermppcheck.get()==0:
                        Rocsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevRoc"] for i in grouplistdict if i["Group"]==item and "RevRoc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForRoc"] for i in grouplistdict if i["Group"]==item and "ForRoc" in i])
                         
                        for item in names:
                            DATAgroupforexport.append([item,"RevRoc"]+[i["RevRoc"] for i in grouplistdict if i["Group"]==item and "RevRoc" in i][0])
                            DATAgroupforexport.append([item,"ForRoc"]+[i["ForRoc"] for i in grouplistdict if i["Group"]==item and "ForRoc" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]==[] and valsFor[i][0]==[]:
                                print(" ")
                            else:
                                Rev.append(valsRev[i][0])
                                Forw.append(valsFor[i][0])
                                valstot.append(valsRev[i][0]+valsFor[i][0])
                                namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rocsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rocsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                    else:
                        Rocsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevRoc"] for i in grouplistdict if i["Group"]==item and "RevRoc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForRoc"] for i in grouplistdict if i["Group"]==item and "ForRoc" in i])
                        valsRevAMPP=[]
                        for item in names:
                            valsRevAMPP.append([i["RevRocAMPP"] for i in grouplistdict if i["Group"]==item and "RevRocAMPP" in i])
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForRocAMPP"] for i in grouplistdict if i["Group"]==item and "ForRocAMPP" in i])
 
                        for item in names:
                            DATAgroupforexport.append([item,"RevRoc"]+[i["RevRoc"] for i in grouplistdict if i["Group"]==item and "RevRoc" in i][0])
                            DATAgroupforexport.append([item,"ForRoc"]+[i["ForRoc"] for i in grouplistdict if i["Group"]==item and "ForRoc" in i][0])
                            DATAgroupforexport.append([item,"RevRocAMPP"]+[i["RevRocAMPP"] for i in grouplistdict if i["Group"]==item and "RevRocAMPP" in i][0])
                            DATAgroupforexport.append([item,"ForRocAMPP"]+[i["ForRocAMPP"] for i in grouplistdict if i["Group"]==item and "ForRocAMPP" in i][0])

                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                            else:
                                 Rev.append([])
                            if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                            else:
                                 Forw.append([])
                            if valsRevAMPP[i][0]!=[]:
                                 RevAMPP.append(valsRevAMPP[i][0])
                            else:
                                 RevAMPP.append([])
                            if valsForAMPP[i][0]!=[]:
                                 ForwAMPP.append(valsForAMPP[i][0])
                            else:
                                 ForwAMPP.append([])    
                            if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                 namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rocsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rocsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                            y=RevAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rocsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                            y=ForwAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rocsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        Rocsubfig.set_xticks(span)
                        Rocsubfig.set_xticklabels(namelist)
                        Rocsubfig.set_xlim([0.5,span[-1]+0.5])
                    
                    if self.minmaxgroupgraphcheck.get()==1:
                        Rocsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    Rocsubfig.set_ylabel('Roc')
                    for item in ([Rocsubfig.title, Rocsubfig.xaxis.label, Rocsubfig.yaxis.label] +
                                 Rocsubfig.get_xticklabels() + Rocsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Rocsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Rsc":
                    if self.aftermppcheck.get()==0:
                        Rscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevRsc"] for i in grouplistdict if i["Group"]==item and "RevRsc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForRsc"] for i in grouplistdict if i["Group"]==item and "ForRsc" in i])
                        
                        for item in names:
                            DATAgroupforexport.append([item,"RevRsc"]+[i["RevRsc"] for i in grouplistdict if i["Group"]==item and "RevRsc" in i][0])
                            DATAgroupforexport.append([item,"ForRsc"]+[i["ForRsc"] for i in grouplistdict if i["Group"]==item and "ForRsc" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]==[] and valsFor[i][0]==[]:
                                print(" ")
                            else:
                                Rev.append(valsRev[i][0])
                                Forw.append(valsFor[i][0])
                                valstot.append(valsRev[i][0]+valsFor[i][0])
                                namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    else:
                        Rscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevRsc"] for i in grouplistdict if i["Group"]==item and "RevRsc" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForRsc"] for i in grouplistdict if i["Group"]==item and "ForRsc" in i])
                        valsRevAMPP=[]
                        for item in names:
                            valsRevAMPP.append([i["RevRscAMPP"] for i in grouplistdict if i["Group"]==item and "RevRscAMPP" in i])
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForRscAMPP"] for i in grouplistdict if i["Group"]==item and "ForRscAMPP" in i])

                        for item in names:
                            DATAgroupforexport.append([item,"RevRsc"]+[i["RevRsc"] for i in grouplistdict if i["Group"]==item and "RevRsc" in i][0])
                            DATAgroupforexport.append([item,"ForRsc"]+[i["ForRsc"] for i in grouplistdict if i["Group"]==item and "ForRsc" in i][0])
                            DATAgroupforexport.append([item,"RevRscAMPP"]+[i["RevRscAMPP"] for i in grouplistdict if i["Group"]==item and "RevRscAMPP" in i][0])
                            DATAgroupforexport.append([item,"ForRscAMPP"]+[i["ForRscAMPP"] for i in grouplistdict if i["Group"]==item and "ForRscAMPP" in i][0])

                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                            else:
                                 Rev.append([])
                            if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                            else:
                                 Forw.append([])
                            if valsRevAMPP[i][0]!=[]:
                                 RevAMPP.append(valsRevAMPP[i][0])
                            else:
                                 RevAMPP.append([])
                            if valsForAMPP[i][0]!=[]:
                                 ForwAMPP.append(valsForAMPP[i][0])
                            else:
                                 ForwAMPP.append([])    
                            if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                 namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                            y=RevAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                            y=ForwAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5) 
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        Rscsubfig.set_xticks(span)
                        Rscsubfig.set_xticklabels(namelist)
                        Rscsubfig.set_xlim([0.5,span[-1]+0.5])
                    
                    if self.minmaxgroupgraphcheck.get()==1:
                        Rscsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    Rscsubfig.set_ylabel('Rsc')
                    for item in ([Rscsubfig.title, Rscsubfig.xaxis.label, Rscsubfig.yaxis.label] +
                                 Rscsubfig.get_xticklabels() + Rscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)
                    for tick in Rscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Vmpp":
                    if self.aftermppcheck.get()==0:
                        Rscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevVmpp"] for i in grouplistdict if i["Group"]==item and "RevVmpp" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForVmpp"] for i in grouplistdict if i["Group"]==item and "ForVmpp" in i])
                         
                        for item in names:
                            DATAgroupforexport.append([item,"RevVmpp"]+[i["RevVmpp"] for i in grouplistdict if i["Group"]==item and "RevVmpp" in i][0])
                            DATAgroupforexport.append([item,"ForVmpp"]+[i["ForVmpp"] for i in grouplistdict if i["Group"]==item and "ForVmpp" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]==[] and valsFor[i][0]==[]:
                                print(" ")
                            else:
                                Rev.append(valsRev[i][0])
                                Forw.append(valsFor[i][0])
                                valstot.append(valsRev[i][0]+valsFor[i][0])
                                namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                    else:
                        Rscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevVmpp"] for i in grouplistdict if i["Group"]==item and "RevVmpp" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForVmpp"] for i in grouplistdict if i["Group"]==item and "ForVmpp" in i])
                        valsRevAMPP=[]
                        for item in names:
                            valsRevAMPP.append([i["RevVmppAMPP"] for i in grouplistdict if i["Group"]==item and "RevVmppAMPP" in i])
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForVmppAMPP"] for i in grouplistdict if i["Group"]==item and "ForVmppAMPP" in i])
                            
                        for item in names:
                            DATAgroupforexport.append([item,"RevVmpp"]+[i["RevVmpp"] for i in grouplistdict if i["Group"]==item and "RevVmpp" in i][0])
                            DATAgroupforexport.append([item,"ForVmpp"]+[i["ForVmpp"] for i in grouplistdict if i["Group"]==item and "ForVmpp" in i][0])
                            DATAgroupforexport.append([item,"RevVmppAMPP"]+[i["RevVmppAMPP"] for i in grouplistdict if i["Group"]==item and "RevVmppAMPP" in i][0])
                            DATAgroupforexport.append([item,"ForVmppAMPP"]+[i["ForVmppAMPP"] for i in grouplistdict if i["Group"]==item and "ForVmppAMPP" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                            else:
                                 Rev.append([])
                            if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                            else:
                                 Forw.append([])
                            if valsRevAMPP[i][0]!=[]:
                                 RevAMPP.append(valsRevAMPP[i][0])
                            else:
                                 RevAMPP.append([])
                            if valsForAMPP[i][0]!=[]:
                                 ForwAMPP.append(valsForAMPP[i][0])
                            else:
                                 ForwAMPP.append([])    
                            if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                 namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                            y=RevAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                            y=ForwAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5)  
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        Rscsubfig.set_xticks(span)
                        Rscsubfig.set_xticklabels(namelist)
                        Rscsubfig.set_xlim([0.5,span[-1]+0.5])
                    if self.minmaxgroupgraphcheck.get()==1:
                        Rscsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    Rscsubfig.set_ylabel('Vmpp (mV)')
                    for item in ([Rscsubfig.title, Rscsubfig.xaxis.label, Rscsubfig.yaxis.label] +
                                 Rscsubfig.get_xticklabels() + Rscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup) 
                    for tick in Rscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                        
                elif self.GroupChoice.get()=="Jmpp":
                    if self.aftermppcheck.get()==0:
                        Rscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevJmpp"] for i in grouplistdict if i["Group"]==item and "RevJmpp" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForJmpp"] for i in grouplistdict if i["Group"]==item and "ForJmpp" in i])
                         
                        for item in names:
                            DATAgroupforexport.append([item,"RevJmpp"]+[i["RevJmpp"] for i in grouplistdict if i["Group"]==item and "RevJmpp" in i][0])
                            DATAgroupforexport.append([item,"ForJmpp"]+[i["ForJmpp"] for i in grouplistdict if i["Group"]==item and "ForJmpp" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]==[] and valsFor[i][0]==[]:
                                print(" ")
                            else:
                                Rev.append(valsRev[i][0])
                                Forw.append(valsFor[i][0])
                                valstot.append(valsRev[i][0]+valsFor[i][0])
                                namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5)  
                    else:
                        Rscsubfig = self.GroupStatfig 
                        #names=samplesgroups
                        valsRev=[]
                        for item in names:
                            valsRev.append([i["RevJmpp"] for i in grouplistdict if i["Group"]==item and "RevJmpp" in i])
                        valsFor=[]
                        for item in names:
                            valsFor.append([i["ForJmpp"] for i in grouplistdict if i["Group"]==item and "ForJmpp" in i])
                        valsRevAMPP=[]
                        for item in names:
                            valsRevAMPP.append([i["RevJmppAMPP"] for i in grouplistdict if i["Group"]==item and "RevJmppAMPP" in i])
                        valsForAMPP=[]
                        for item in names:
                            valsForAMPP.append([i["ForJmppAMPP"] for i in grouplistdict if i["Group"]==item and "ForJmppAMPP" in i])
                         
                        for item in names:
                            DATAgroupforexport.append([item,"RevJmpp"]+[i["RevJmpp"] for i in grouplistdict if i["Group"]==item and "RevJmpp" in i][0])
                            DATAgroupforexport.append([item,"ForJmpp"]+[i["ForJmpp"] for i in grouplistdict if i["Group"]==item and "ForJmpp" in i][0])
                            DATAgroupforexport.append([item,"RevJmppAMPP"]+[i["RevJmppAMPP"] for i in grouplistdict if i["Group"]==item and "RevJmppAMPP" in i][0])
                            DATAgroupforexport.append([item,"ForJmppAMPP"]+[i["ForJmppAMPP"] for i in grouplistdict if i["Group"]==item and "ForJmppAMPP" in i][0])
                        DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                        
                        valstot=[]
                        Rev=[]
                        Forw=[]
                        RevAMPP=[]
                        ForwAMPP=[]
                        namelist=[]
                        for i in range(len(names)):
                            if valsRev[i][0]!=[]:
                                 Rev.append(valsRev[i][0])
                            else:
                                 Rev.append([])
                            if valsFor[i][0]!=[]:
                                 Forw.append(valsFor[i][0])
                            else:
                                 Forw.append([])
                            if valsRevAMPP[i][0]!=[]:
                                 RevAMPP.append(valsRevAMPP[i][0])
                            else:
                                 RevAMPP.append([])
                            if valsForAMPP[i][0]!=[]:
                                 ForwAMPP.append(valsForAMPP[i][0])
                            else:
                                 ForwAMPP.append([])    
                            if valsRev[i][0]!=[] or valsFor[i][0]!=[] or valsRevAMPP[i][0]!=[] or valsForAMPP[i][0]!=[]:
                                 valstot.append(valsRev[i][0]+valsFor[i][0]+valsRevAMPP[i][0]+valsForAMPP[i][0])
                                 namelist.append(names[i])
                        
                        if self.boxplot.get()==1:
                            Rscsubfig.boxplot(valstot,0,'',labels=namelist)
                        
                        for i in range(len(namelist)):
                            y=Rev[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                            y=Forw[i]
                            if len(y)>0:
                                x=np.random.normal(i+0.9,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='blue', alpha=0.5) 
                            y=RevAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='orange', alpha=0.5)
                            y=ForwAMPP[i]
                            if len(y)>0:
                                x=np.random.normal(i+1.1,0.04,size=len(y))
                                Rscsubfig.scatter(x,y,s=15,color='lightblue', alpha=0.5) 
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        Rscsubfig.set_xticks(span)
                        Rscsubfig.set_xticklabels(namelist)
                        Rscsubfig.set_xlim([0.5,span[-1]+0.5])
                    if self.minmaxgroupgraphcheck.get()==1:
                        Rscsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    Rscsubfig.set_ylabel('Jmpp (mA/cm'+'\xb2'+')')
                    for item in ([Rscsubfig.title, Rscsubfig.xaxis.label, Rscsubfig.yaxis.label] +
                                 Rscsubfig.get_xticklabels() + Rscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)    
                    for tick in Rscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                elif self.GroupChoice.get()=="HI":
#                    print("HI")
                    grouplistdict=[]
                    for item in range(len(samplesgroups)):
                        groupdict={}
                        groupdict["Group"]=samplesgroups[item]
                        listofthegroup=[]
                        for item1 in range(len(DATAx)):
                            if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                                listofthegroup.append(DATAx[item1])
                        if len(listofthegroup)!=0:
                                
                            listofthegroupFor=[]
                            for item1 in range(len(listofthegroup)):
                                listofthegroupFor.append(listofthegroup[item1])
                            groupdict["HI"]=[x['HI'] for x in listofthegroupFor if 'HI' in x]
#                            print(len(groupdict["HI"]))
                            grouplistdict.append(groupdict)
                    
                    
                    
                    Rscsubfig = self.GroupStatfig 
                    #names=samplesgroups
                    valsRev=[]
                    for item in names:
                        valsRev.append([i["HI"] for i in grouplistdict if i["Group"]==item and "HI" in i])
#                    print(valsRev)
                    for item in names:
                        DATAgroupforexport.append([item,"HI"]+[i["HI"] for i in grouplistdict if i["Group"]==item and "HI" in i][0])
                    DATAgroupforexport=map(list, six.moves.zip_longest(*DATAgroupforexport, fillvalue=' '))
                    
                    valstot=[]
                    Rev=[]
                    namelist=[]
                    for i in range(len(names)):
                        if valsRev[i][0]==[]:
                            print(" ")
                        else:
                            Rev.append(valsRev[i][0])
                            valstot.append(valsRev[i][0])
                            namelist.append(names[i])
                    
                    if self.boxplot.get()==1:
                        Rscsubfig.boxplot(valstot,0,'',labels=namelist)
#                    print(namelist)
                    for i in range(len(namelist)):
                        y=Rev[i]
                        if len(y)>0:
                            x=np.random.normal(i+1,0.04,size=len(y))
                            Rscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                    
                    if self.boxplot.get()==0:
                        span=range(1,len(namelist)+1)
                        Rscsubfig.set_xticks(span)
                        Rscsubfig.set_xticklabels(namelist)
                        Rscsubfig.set_xlim([0.5,span[-1]+0.5])
                    if self.minmaxgroupgraphcheck.get()==1:
                        Rscsubfig.set_ylim([self.minYgroupgraph.get(),self.maxYgroupgraph.get()])

                    Rscsubfig.set_ylabel('Hysteresis Index 100(R-F)/R (%)')
                    for item in ([Rscsubfig.title, Rscsubfig.xaxis.label, Rscsubfig.yaxis.label] +
                                 Rscsubfig.get_xticklabels() + Rscsubfig.get_yticklabels()):
                        item.set_fontsize(fontsizegroup)    
                    for tick in Rscsubfig.get_xticklabels():
                        tick.set_rotation(self.rotationGroupGraph.get())
                
                if self.GroupChoice.get()!="Voc" and self.GroupChoice.get()!="FF":    
                    self.GroupStatfig.annotate('Red/Orange=reverse; Blue/Lightblue=forward', xy=(0.7,1.05), xycoords='axes fraction', fontsize=7,
                                horizontalalignment='right', verticalalignment='bottom')
    
                plt.gcf().canvas.draw()
#        except:
#            pass
#    def UpdateTimeGraph(self,a):
#        global DATA, takenforplotTime, colorstylelist, DATAtimeevolforexport
##        print("")
##        print(takenforplotTime)
#        #"MeasDayTime2"
#        if takenforplotTime!=[]:
#            TimeDatDict={}
#            self.TimeEvolfig.clear()
#            for item in takenforplotTime:
#                newkey=item.split('_')[0]+'_'+item.split('_')[1]+'_'+item.split('_')[2]
#                if newkey not in TimeDatDict.keys():
#                    TimeDatDict[newkey]={'reverse':{'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]},'forward':{'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]}}
#                for item1 in DATA:
#                    if item1["SampleName"]==item:
#                        if item1["ScanDirection"]=="Reverse" and item1["Illumination"]=="Light":
#                            TimeDatDict[newkey]['reverse']['Voc'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['reverse']['Voc'][1].append(item1["Voc"])
#                            TimeDatDict[newkey]['reverse']['Jsc'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['reverse']['Jsc'][1].append(item1["Jsc"])
#                            TimeDatDict[newkey]['reverse']['FF'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['reverse']['FF'][1].append(item1["FF"])
#                            TimeDatDict[newkey]['reverse']['Eff'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['reverse']['Eff'][1].append(item1["Eff"])
#                        elif item1["ScanDirection"]=="Forward" and item1["Illumination"]=="Light":
#                            TimeDatDict[newkey]['forward']['Voc'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['forward']['Voc'][1].append(item1["Voc"])
#                            TimeDatDict[newkey]['forward']['Jsc'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['forward']['Jsc'][1].append(item1["Jsc"])
#                            TimeDatDict[newkey]['forward']['FF'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['forward']['FF'][1].append(item1["FF"])
#                            TimeDatDict[newkey]['forward']['Eff'][0].append(item1["MeasDayTime2"])
#                            TimeDatDict[newkey]['forward']['Eff'][1].append(item1["Eff"])
#    #        num_plots = len(TimeDatDict.keys())          
#    #        plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.Spectral(np.linspace(0, 1, num_plots))))
#            color1=0    
#    #        print(list(TimeDatDict.keys())) 
#            minx=min(TimeDatDict[newkey]['forward'][self.TimeChoice.get()][0]+TimeDatDict[newkey]['reverse'][self.TimeChoice.get()][0])
#            maxx=max(TimeDatDict[newkey]['forward'][self.TimeChoice.get()][0]+TimeDatDict[newkey]['reverse'][self.TimeChoice.get()][0])
#            
#            for key in list(TimeDatDict.keys()):
#                if minx>min(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0]):
#                    minx=min(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0])
#                if maxx<max(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0]):
#                    maxx=max(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0])
#                try:
#                    xfor, yfor=zip(*sorted(zip(TimeDatDict[key]['forward'][self.TimeChoice.get()][0],TimeDatDict[key]['forward'][self.TimeChoice.get()][1]), key = lambda x: x[1]))
#                    xfor=list(xfor)
#                    yfor=list(yfor)
#                    yfor.sort(key=dict(zip(yfor, xfor)).get)
#                    xfor=sorted(xfor)
#                    if self.LineornolineTimegraph.get():
#                        self.TimeEvolfig.plot(xfor, yfor, linestyle='--', marker='o',color=colorstylelist[color1],label=key+'_For')
#                    else:
#                        self.TimeEvolfig.plot(xfor, yfor, linestyle='', marker='o',color=colorstylelist[color1],label=key+'_For')                       
#                except ValueError:
#                    pass
#                try:
#                    xrev, yrev=zip(*sorted(zip(TimeDatDict[key]['reverse'][self.TimeChoice.get()][0],TimeDatDict[key]['reverse'][self.TimeChoice.get()][1]), key = lambda x: x[1]))                
#                    xrev=list(xrev)
#                    yrev=list(yrev)
#                    yrev.sort(key=dict(zip(yrev, xrev)).get)
#                    xrev=sorted(xrev)
#                    if self.LineornolineTimegraph.get():
#                        self.TimeEvolfig.plot(xrev, yrev, linestyle='-', marker='o', color=colorstylelist[color1], alpha=0.5,label=key+'_Rev')
#                    else:
#                        self.TimeEvolfig.plot(xrev, yrev, linestyle='', marker='o', color=colorstylelist[color1], alpha=0.5,label=key+'_Rev')                        
#                except ValueError:
#                    pass
#                color1=color1+1
#                
#            self.TimeEvolfig.set_xlim(minx-0.05*(maxx-minx),maxx+0.05*(maxx-minx))    
#            self.TimeEvolfig.set_xlabel('Time')
#            self.TimeEvolfig.set_ylabel(self.TimeChoice.get())
#            for tick in self.TimeEvolfig.get_xticklabels():
#                tick.set_rotation(20)
#            self.TimeEvolfigleg=self.TimeEvolfig.legend(loc='lower left', bbox_to_anchor=(1, 0))
#            plt.gcf().canvas.draw()
#        
#        #order by time, and substract the oldest measurement from the other, then transform all in hours
#        
#        #normalization of y axis
    def UpdateTimeGraph(self,a):
        global DATA, takenforplotTime, colorstylelist, DATAtimeevolforexport
#        print("")
#        print(takenforplotTime)
        #"MeasDayTime2"
        DATAtimeevolforexport={}
        print(takenforplotTime)
        if takenforplotTime!=[]:
            if self.BestPixofDayTimegraph.get()==0 and self.BestofRevForTimegraph.get()==0:
                TimeDatDict={}
                self.TimeEvolfig.clear()
                for item in takenforplotTime:
                    newkey=item.split('_')[0]+'_'+item.split('_')[1]+'_'+item.split('_')[2]
                    if newkey not in TimeDatDict.keys():
                        TimeDatDict[newkey]={'reverse':{'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]},'forward':{'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]}}
                    for item1 in DATA:
                        if item1["SampleName"]==item:
                            if item1["ScanDirection"]=="Reverse" and item1["Illumination"]=="Light":
                                TimeDatDict[newkey]['reverse']['Voc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['Voc'][1].append(item1["Voc"])
                                TimeDatDict[newkey]['reverse']['Jsc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['Jsc'][1].append(item1["Jsc"])
                                TimeDatDict[newkey]['reverse']['FF'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['FF'][1].append(item1["FF"])
                                TimeDatDict[newkey]['reverse']['Eff'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['reverse']['Eff'][1].append(item1["Eff"])
                            elif item1["ScanDirection"]=="Forward" and item1["Illumination"]=="Light":
                                TimeDatDict[newkey]['forward']['Voc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['Voc'][1].append(item1["Voc"])
                                TimeDatDict[newkey]['forward']['Jsc'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['Jsc'][1].append(item1["Jsc"])
                                TimeDatDict[newkey]['forward']['FF'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['FF'][1].append(item1["FF"])
                                TimeDatDict[newkey]['forward']['Eff'][0].append(item1["MeasDayTime2"])
                                TimeDatDict[newkey]['forward']['Eff'][1].append(item1["Eff"])
        #        num_plots = len(TimeDatDict.keys())          
        #        plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.Spectral(np.linspace(0, 1, num_plots))))
                   
        #        print(list(TimeDatDict.keys())) 
                minx=min(TimeDatDict[newkey]['forward'][self.TimeChoice.get()][0]+TimeDatDict[newkey]['reverse'][self.TimeChoice.get()][0])
                maxx=max(TimeDatDict[newkey]['forward'][self.TimeChoice.get()][0]+TimeDatDict[newkey]['reverse'][self.TimeChoice.get()][0])
                
                for key in list(TimeDatDict.keys()):
                    partdatatime=[[],[],[],[],[],[],[],[]]
                    if minx>min(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0]):
                        minx=min(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0])
                    if maxx<max(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0]):
                        maxx=max(TimeDatDict[key]['forward'][self.TimeChoice.get()][0]+TimeDatDict[key]['reverse'][self.TimeChoice.get()][0])
                    try:
                        xfor, yfor=zip(*sorted(zip(TimeDatDict[key]['forward'][self.TimeChoice.get()][0],TimeDatDict[key]['forward'][self.TimeChoice.get()][1]), key = lambda x: x[1]))
                        xfor=list(xfor)
                        yfor=list(yfor)
                        yfor.sort(key=dict(zip(yfor, xfor)).get)
                        xfor=sorted(xfor)
                        partdatatime[0]=xfor
                        partdatatime[1]=[(m-xfor[0]).total_seconds()/3600 for m in xfor]
                        partdatatime[2]=yfor
                        if self.normalsettimegraph.get()==-1:
                            partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                        else:
                            foundnormalsetpt=0
                            for item in range(len(partdatatime[1])):
                                if partdatatime[1][item]>=self.normalsettimegraph.get():
                                    partdatatime[3]=[(m)/(partdatatime[2][item]) for m in yfor]
                                    foundnormalsetpt=1
                                    break
                            if foundnormalsetpt==0:
                                partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                    except ValueError:
                        pass
                    try:
                        xrev, yrev=zip(*sorted(zip(TimeDatDict[key]['reverse'][self.TimeChoice.get()][0],TimeDatDict[key]['reverse'][self.TimeChoice.get()][1]), key = lambda x: x[1]))                
                        xrev=list(xrev)
                        yrev=list(yrev)
                        yrev.sort(key=dict(zip(yrev, xrev)).get)
                        xrev=sorted(xrev)
                        partdatatime[4]=xrev
                        partdatatime[5]=[(m-xrev[0]).total_seconds()/3600 for m in xrev]
                        partdatatime[6]=yrev
                        
                        if self.normalsettimegraph.get()==-1:
                            partdatatime[7]=[(m)/(yrev[0]) for m in yrev]
                        else:
                            foundnormalsetpt=0
                            for item in range(len(partdatatime[5])):
                                if partdatatime[5][item]>=self.normalsettimegraph.get():
                                    partdatatime[7]=[(m)/(partdatatime[6][item]) for m in yrev]
                                    foundnormalsetpt=1
                                    break
                            if foundnormalsetpt==0:
                                partdatatime[7]=[(m)/(yrev[0]) for m in yrev]
                        
                    except ValueError:
                        pass
                    DATAtimeevolforexport[key]=partdatatime
                 
                color1=0 
                for key in list(DATAtimeevolforexport.keys()):
                    xfor=DATAtimeevolforexport[key][0]
                    yfor=DATAtimeevolforexport[key][2]
                    xrev=DATAtimeevolforexport[key][4]
                    yrev=DATAtimeevolforexport[key][6]
                    if self.timerelativeTimegraph.get():
                        xfor=DATAtimeevolforexport[key][1]
                        xrev=DATAtimeevolforexport[key][5]
                    if self.normalTimegraph.get():
                        yfor=DATAtimeevolforexport[key][3]
                        yrev=DATAtimeevolforexport[key][7]
                
                    if self.LineornolineTimegraph.get():
                        self.TimeEvolfig.plot(xfor, yfor, linestyle='--', marker='o',color=colorstylelist[color1],label=key+'_For')
                        self.TimeEvolfig.plot(xrev, yrev, linestyle='-', marker='o', color=colorstylelist[color1], alpha=0.5,label=key+'_Rev')
                    else:
                        self.TimeEvolfig.plot(xfor, yfor, linestyle='', marker='o',color=colorstylelist[color1],label=key+'_For')
                        self.TimeEvolfig.plot(xrev, yrev, linestyle='', marker='o', color=colorstylelist[color1], alpha=0.5,label=key+'_Rev')  
                    color1=color1+1
                    
                
                if self.timerelativeTimegraph.get():
                    self.TimeEvolfig.set_xlabel('Time (hours)')
                else:
                    self.TimeEvolfig.set_xlim(minx-0.05*(maxx-minx),maxx+0.05*(maxx-minx))    
                    self.TimeEvolfig.set_xlabel('Time')
                
                if self.minmaxtimegraphcheck.get():
                    self.TimeEvolfig.set_ylim(self.minYtimegraph.get(),self.maxYtimegraph.get())
                
                self.TimeEvolfig.set_ylabel(self.TimeChoice.get())
                for tick in self.TimeEvolfig.get_xticklabels():
                    tick.set_rotation(20)
                self.TimeEvolfigleg=self.TimeEvolfig.legend(loc='lower left', bbox_to_anchor=(1, 0))
                plt.gcf().canvas.draw()
                
            elif self.BestofRevForTimegraph.get()==1 and self.BestPixofDayTimegraph.get()==0:
                print("bestrevfor")
                
                
            elif self.BestofRevForTimegraph.get()==0 and self.BestPixofDayTimegraph.get()==1:   
#                print("bestoftheday")
                TimeDatDict={}
                self.TimeEvolfig.clear()
                for item in takenforplotTime:
                    newkey=item.split('_')[0]+'_'+item.split('_')[1]#per substrate e.g. 41_10
                    if newkey not in TimeDatDict.keys():
                        TimeDatDict[newkey]={}
                    for item1 in DATA:
                        if item1["SampleName"]==item:
                            newdatekey=str(item1["MeasDayTime2"].date())
                            if newdatekey not in TimeDatDict[newkey].keys():
                                TimeDatDict[newkey][newdatekey]={'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]}
                            
                            TimeDatDict[newkey][newdatekey]['Voc'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['Voc'][1].append(item1["Voc"])
                            TimeDatDict[newkey][newdatekey]['Jsc'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['Jsc'][1].append(item1["Jsc"])
                            TimeDatDict[newkey][newdatekey]['FF'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['FF'][1].append(item1["FF"])
                            TimeDatDict[newkey][newdatekey]['Eff'][0].append(item1["MeasDayTime2"])
                            TimeDatDict[newkey][newdatekey]['Eff'][1].append(item1["Eff"])
                
                for key0 in list(TimeDatDict.keys()):
#                    print(key0)
                    TimeDatDict[key0]['bestEffofday']={'Voc':[[],[]],'Jsc':[[],[]],'FF':[[],[]],'Eff':[[],[]]}
                    for key in list(TimeDatDict[key0].keys()):
#                        print(key)
#                        print(max(TimeDatDict[key0][key]['Eff'][1]))
                        
                        ind=TimeDatDict[key0][key]['Eff'][1].index(max(TimeDatDict[key0][key]['Eff'][1]))
                        
                        TimeDatDict[key0]['bestEffofday']['Voc'][0].append(TimeDatDict[key0][key]['Voc'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['Voc'][1].append(TimeDatDict[key0][key]['Voc'][1][ind])
                        TimeDatDict[key0]['bestEffofday']['Jsc'][0].append(TimeDatDict[key0][key]['Jsc'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['Jsc'][1].append(TimeDatDict[key0][key]['Jsc'][1][ind])
                        TimeDatDict[key0]['bestEffofday']['FF'][0].append(TimeDatDict[key0][key]['FF'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['FF'][1].append(TimeDatDict[key0][key]['FF'][1][ind])
                        TimeDatDict[key0]['bestEffofday']['Eff'][0].append(TimeDatDict[key0][key]['Eff'][0][ind])
                        TimeDatDict[key0]['bestEffofday']['Eff'][1].append(TimeDatDict[key0][key]['Eff'][1][ind])
                
                minx=min(TimeDatDict[newkey]['bestEffofday'][self.TimeChoice.get()][0])
                maxx=max(TimeDatDict[newkey]['bestEffofday'][self.TimeChoice.get()][0])
                
                for key in list(TimeDatDict.keys()):
                    partdatatime=[[],[],[],[]]
                    if minx>min(TimeDatDict[key]['bestEffofday'][self.TimeChoice.get()][0]):
                        minx=min(TimeDatDict[key]['bestEffofday'][self.TimeChoice.get()][0])
                    if maxx<max(TimeDatDict[key]['bestEffofday'][self.TimeChoice.get()][0]):
                        maxx=max(TimeDatDict[key]['bestEffofday'][self.TimeChoice.get()][0])
                    try:
                        xfor, yfor=zip(*sorted(zip(TimeDatDict[key]['bestEffofday'][self.TimeChoice.get()][0],TimeDatDict[key]['bestEffofday'][self.TimeChoice.get()][1]), key = lambda x: x[1]))
                        xfor=list(xfor)
                        yfor=list(yfor)
                        yfor.sort(key=dict(zip(yfor, xfor)).get)
                        xfor=sorted(xfor)
                        partdatatime[0]=xfor
                        partdatatime[1]=[(m-xfor[0]).total_seconds()/3600 for m in xfor]
                        partdatatime[2]=yfor
                        if self.normalsettimegraph.get()==-1:
                            partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                        else:
                            foundnormalsetpt=0
                            for item in range(len(partdatatime[1])):
                                if partdatatime[1][item]>=self.normalsettimegraph.get():
                                    partdatatime[3]=[(m)/(partdatatime[2][item]) for m in yfor]
                                    foundnormalsetpt=1
                                    break
                            if foundnormalsetpt==0:
                                partdatatime[3]=[(m)/(yfor[0]) for m in yfor]
                    except ValueError:
                        pass
                    
                    DATAtimeevolforexport[key]=partdatatime
                 
                color1=0 
                for key in list(DATAtimeevolforexport.keys()):
                    xfor=DATAtimeevolforexport[key][0]
                    yfor=DATAtimeevolforexport[key][2]
                    
                    if self.timerelativeTimegraph.get():
                        xfor=DATAtimeevolforexport[key][1]
                    if self.normalTimegraph.get():
                        yfor=DATAtimeevolforexport[key][3]
                
                    if self.LineornolineTimegraph.get():
                        self.TimeEvolfig.plot(xfor, yfor, linestyle='-', marker='o',color=colorstylelist[color1],label=key+'_Best')
                    else:
                        self.TimeEvolfig.plot(xfor, yfor, linestyle='', marker='o',color=colorstylelist[color1],label=key+'_Best')
                    color1=color1+1
                    
                
                if self.timerelativeTimegraph.get():
                    self.TimeEvolfig.set_xlabel('Time (hours)')
                else:
                    self.TimeEvolfig.set_xlim(minx-0.05*(maxx-minx),maxx+0.05*(maxx-minx))    
                    self.TimeEvolfig.set_xlabel('Time')
                
                if self.minmaxtimegraphcheck.get():
                    self.TimeEvolfig.set_ylim(self.minYtimegraph.get(),self.maxYtimegraph.get())
                
                self.TimeEvolfig.set_ylabel(self.TimeChoice.get())
                for tick in self.TimeEvolfig.get_xticklabels():
                    tick.set_rotation(20)
                self.TimeEvolfigleg=self.TimeEvolfig.legend(loc='lower left', bbox_to_anchor=(1, 0))
                plt.gcf().canvas.draw()

                
        
    def UpdateCompGraph(self,a):
        global DATA
        global DATAdark
        global DATAFV
        global DATAMPP
        global groupstoplot
        global DATAcompforexport
        
        DATAcompforexport=[]
        DATAx=copy.deepcopy(DATA)
        
        samplesgroups=[]
        for name, var in self.choicesgroupcomptoplot.items():
            samplesgroups.append(var.get())
        m=[]
        for i in range(len(samplesgroups)):
            if samplesgroups[i]==1:
                m.append(groupstoplot[i])
        samplesgroups=m
        
#        print(samplesgroups)
        
        if samplesgroups==[]:
            self.CompParamGroupfig.clear()
        else:
            grouplistdict={}
            for item in range(len(samplesgroups)):
                groupdict={}
                groupdict["Group"]=samplesgroups[item]
                listofthegroup=[]
                for item1 in range(len(DATAx)):
                    if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=='Light':
                        listofthegroup.append(DATAx[item1])
               
                if len(listofthegroup)!=0:
                    listofthegroupRev=[]
                    listofthegroupFor=[]
                    for item1 in range(len(listofthegroup)):
                        if listofthegroup[item1]["ScanDirection"]=="Reverse":
                            listofthegroupRev.append(listofthegroup[item1])
                        else:
                            listofthegroupFor.append(listofthegroup[item1])
                    
                    groupdict["Voc"]={}
                    groupdict["Jsc"]={}
                    groupdict["FF"]={}
                    groupdict["Eff"]={}
                    groupdict["Roc"]={}
                    groupdict["Rsc"]={}
                    groupdict["Vmpp"]={}
                    groupdict["Jmpp"]={}
                    
                    
                    groupdict["Voc"]["Rev"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                    groupdict["Voc"]["For"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                    groupdict["Jsc"]["Rev"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                    groupdict["Jsc"]["For"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                    groupdict["FF"]["Rev"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                    groupdict["FF"]["For"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                    groupdict["Eff"]["Rev"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                    groupdict["Eff"]["For"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                    groupdict["Roc"]["Rev"]=[x['Roc'] for x in listofthegroupRev if 'Roc' in x]
                    groupdict["Roc"]["For"]=[x['Roc'] for x in listofthegroupFor if 'Roc' in x]
                    groupdict["Rsc"]["Rev"]=[x['Rsc'] for x in listofthegroupRev if 'Rsc' in x]
                    groupdict["Rsc"]["For"]=[x['Rsc'] for x in listofthegroupFor if 'Rsc' in x]
                    groupdict["Vmpp"]["Rev"]=[x['Vmpp'] for x in listofthegroupRev if 'Vmpp' in x]
                    groupdict["Vmpp"]["For"]=[x['Vmpp'] for x in listofthegroupFor if 'Vmpp' in x]
                    groupdict["Jmpp"]["Rev"]=[x['Jmpp'] for x in listofthegroupRev if 'Jmpp' in x]
                    groupdict["Jmpp"]["For"]=[x['Jmpp'] for x in listofthegroupFor if 'Jmpp' in x]
                    
#                    grouplistdict.append(groupdict)
                    grouplistdict[samplesgroups[item]]=groupdict
            colormapname="jet"
            cmap = plt.get_cmap(colormapname)
            colors = cmap(np.linspace(0, 1.0, len(list(grouplistdict.keys()))))
            colors=[tuple(item) for item in colors]  
             
            self.CompParamGroupfig.clear()
            indexcolor=0
            for group in list(grouplistdict.keys()):
                DATAcompforexport.append([self.CompXChoice.get(),'']+grouplistdict[group][self.CompXChoice.get()]['Rev'])
                DATAcompforexport.append([self.CompYChoice.get(),group+'_Rev']+grouplistdict[group][self.CompYChoice.get()]['Rev'])
                self.CompParamGroupfig.scatter(grouplistdict[group][self.CompXChoice.get()]['Rev'],grouplistdict[group][self.CompYChoice.get()]['Rev']
                                            ,label=group+'_Rev',color=colors[indexcolor],marker="o")
                DATAcompforexport.append([self.CompXChoice.get(),'']+grouplistdict[group][self.CompXChoice.get()]['For'])
                DATAcompforexport.append([self.CompYChoice.get(),group+'For']+grouplistdict[group][self.CompYChoice.get()]['For'])
                self.CompParamGroupfig.scatter(grouplistdict[group][self.CompXChoice.get()]['For'],grouplistdict[group][self.CompYChoice.get()]['For']
                                            ,label=group+'_For',color=colors[indexcolor],marker="s")
                indexcolor+=1
            
            DATAcompforexport=map(list, six.moves.zip_longest(*DATAcompforexport, fillvalue=' '))
    
            if self.minmaxCompgraphcheck.get():
                self.CompParamGroupfig.set_ylim([self.minYCompgraph.get(),self.maxYCompgraph.get()])
                self.CompParamGroupfig.set_xlim([self.minXCompgraph.get(),self.maxXCompgraph.get()])
            
            self.CompParamGroupfig.set_ylabel(self.CompYChoice.get())    
            self.CompParamGroupfig.set_xlabel(self.CompXChoice.get()) 
#            self.CompParamGroupfig.legend()
            self.leg=self.CompParamGroupfig.legend(loc='lower left', bbox_to_anchor=(1, 0))
            
        plt.gcf().canvas.draw()
            
        
    def UpdateIVGraph(self):
        global DATA
        global IVlegendMod
        global titIV
        global DATAJVforexport
        global DATAJVtabforexport
        global takenforplot
        global IVlinestyle
        global colorstylelist
        #csfont = {'fontname':'Helvetica'}
        
        DATAJVforexport=[]
        DATAJVtabforexport=[]
        
        DATAx=copy.deepcopy(DATA)
        sampletotake=[]
        if takenforplot!=[]:
            for item in takenforplot:
                for item1 in range(len(DATAx)):
                    if item ==DATAx[item1]["SampleName"]:
                        sampletotake.append(item1)
                        break
        if self.CheckIVLog.get()!=1:
            if IVlegendMod!=[]:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    if self.CheckIVLegend.get()==1:
                        newlegend=1
                        for item1 in range(len(IVlegendMod)):
                            if IVlegendMod[item1][0]==DATAx[item]["SampleName"]:
                                try:
                                    IVfig.plot(x,y,label=IVlegendMod[item1][1],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2],linewidth=IVlinestyle[item1][3])
                                except IndexError:
                                    print("some indexerror... but just continue...")
                                newlegend=0
                                break
                        if newlegend:
                            try:
                                IVfig.plot(x,y,label=DATAx[item]["SampleName"],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2],linewidth=IVlinestyle[item1][3])
                                IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                                IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1],2])
                            except IndexError:
                                print("some indexerror... but just continue...")
                    else:
                        IVfig.plot(x,y,color=colorstylelist[color1])
                    color1=color1+1
            else:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm^2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    
                    if self.CheckIVLegend.get()==1:
                        try:
                            IVfig.plot(x,y,label=DATAx[item]["SampleName"],color=colorstylelist[color1])
                            IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                            IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1],2])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    else:
                        try:
                            IVfig.plot(x,y,color=colorstylelist[color1])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    color1=color1+1
            
            self.IVsubfig.set_xlabel('Voltage (V)')#,**csfont)
            self.IVsubfig.set_ylabel('Current density (mA/cm'+'\xb2'+')')#,**csfont)
            self.IVsubfig.axhline(y=0, color='k')
            self.IVsubfig.axvline(x=0, color='k')
            self.IVsubfig.axis([self.IVminx.get(),self.IVmaxx.get(),self.IVminy.get(),self.IVmaxy.get()])
            
        else:
            if IVlegendMod!=[]:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    y=[abs(item) for item in y]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    if self.CheckIVLegend.get()==1:
                        newlegend=1
                        for item1 in range(len(IVlegendMod)):
                            if IVlegendMod[item1][0]==DATAx[item]["SampleName"]:
                                try:
                                    IVfig.semilogy(x,y,label=IVlegendMod[item1][1],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2],linewidth=IVlinestyle[item1][3])
                                except IndexError:
                                    print("some indexerror... but just continue...")
                                newlegend=0
                                break
                        if newlegend:
                            try:
                                IVfig.semilogy(x,y,label=DATAx[item]["SampleName"],linestyle=IVlinestyle[item1][1],color=IVlinestyle[item1][2],linewidth=IVlinestyle[item1][3])
                                IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                                IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1],2])
                            except IndexError:
                                print("some indexerror... but just continue...")
                    else:
                        IVfig.semilogy(x,y,color=colorstylelist[color1])
                    color1=color1+1
            else:
                self.IVsubfig.clear()
                IVfig=self.IVsubfig
                color1=0
                for item in sampletotake:
                    x = DATAx[item]["IVData"][0]
                    y = DATAx[item]["IVData"][1]
                    y=[abs(item2) for item2 in y]
                    
                    colx=["Voltage","mV",""]+x
                    coly=["Current density","ma/cm^2",DATAx[item]["SampleName"]]+y
                    DATAJVforexport.append(colx)
                    DATAJVforexport.append(coly)
                    DATAJVtabforexport.append([DATAx[item]["SampleName"],'%.f' % float(DATAx[item]["Voc"]),'%.2f' % float(DATAx[item]["Jsc"]),'%.2f' % float(DATAx[item]["FF"]),'%.2f' % float(DATAx[item]["Eff"]),'%.2f' % float(DATAx[item]["Roc"]),'%.2f' % float(DATAx[item]["Rsc"]),'%.2f' % float(DATAx[item]["Vstart"]),'%.2f' % float(DATAx[item]["Vend"]),'%.2f' % float(DATAx[item]["CellSurface"])])
    
                    
                    if self.CheckIVLegend.get()==1:
                        try:
                            IVfig.semilogy(x,y,label=DATAx[item]["SampleName"],color=colorstylelist[color1])
                            IVlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                            IVlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color1],2])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    else:
                        try:
                            IVfig.semilogy(x,y,color=colorstylelist[color1])
                        except IndexError:
                            print("some indexerror... but just continue...")
                    color1=color1+1
            
            self.IVsubfig.set_xlabel('Voltage (V)')#,**csfont)
            self.IVsubfig.set_ylabel('Current density (mA/cm'+'\xb2'+')')#,**csfont)
            self.IVsubfig.axhline(y=0, color='k')
            self.IVsubfig.axvline(x=0, color='k')  
            self.IVsubfig.axis([self.IVminx.get(),self.IVmaxx.get(),0,self.IVmaxy.get()])
        
        for item in ([self.IVsubfig.title, self.IVsubfig.xaxis.label, self.IVsubfig.yaxis.label] +
                             self.IVsubfig.get_xticklabels() + self.IVsubfig.get_yticklabels()):
            item.set_fontsize(self.fontsizeJVGraph.get())
            
        DATAJVforexport=map(list, six.moves.zip_longest(*DATAJVforexport, fillvalue=' '))
        DATAJVtabforexport.insert(0,[" ","Voc", "Jsc", "FF","Eff","Roc","Rsc","Vstart","Vend","Cellsurface"])

        if titIV:
            self.IVsubfig.set_title(self.titleIV.get())#,**csfont)
        
        if self.CheckIVLegend.get()==1:
            if self.IVlegpos1.get()==1:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==2:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==3:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==4:
                self.leg=IVfig.legend(loc=self.IVlegpos1.get())
            elif self.IVlegpos1.get()==5:
                self.leg=IVfig.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
            else:
                self.leg=IVfig.legend(loc=0)
        
        plt.gcf().canvas.draw()
    
    def UpdateMppGraph0(self):
        global takenforplotmpp
        global MPPlinestyle
        global MPPlegendMod
        global colorstylelist
        
        takenforplotmpp=[]
        for name, var in self.choicesmpp.items():
            takenforplotmpp.append(var.get())
        m=[]
        for i in range(len(takenforplotmpp)):
            if takenforplotmpp[i]==1:
                m.append(self.mppnames[i])
        takenforplotmpp=m
        if MPPlegendMod!=[]:
            for item in takenforplotmpp:
                founded=0
                for item1 in MPPlegendMod:
                    if item1[0]==item:
                        founded=1
                if founded==0:
                    MPPlegendMod.append([item,item])
                    MPPlinestyle.append([item,"-",colorstylelist[len(MPPlegendMod)],1])
            
        self.UpdateMppGraph()
        
    def UpdateMppGraph(self):
        global DATAMPP
        global MPPlegendMod
        global titmpp
        global MPPlinestyle
        global colorstylelist
        global DATAmppforexport
        global takenforplotmpp
        
        DATAmppforexport=[]
        
        DATAx=copy.deepcopy(DATAMPP)
        
        
        sampletotake=[]
        if takenforplotmpp!=[]:
            for item in takenforplotmpp:
                for item1 in range(len(DATAx)):
                    if item ==DATAx[item1]["SampleName"]:
                        sampletotake.append(item1)
                        break
        
        if MPPlegendMod!=[]:
            self.mppsubfig.clear()
            mppfig=self.mppsubfig
            color=0
            for item in sampletotake:
                x = DATAx[item]["MppData"][2]
                y = DATAx[item]["MppData"][3]
                
                colx=["Time","s",""]+x
                coly=["Power","mW/cm2",DATAx[item]["SampleName"]]+y
                DATAmppforexport.append(colx)
                DATAmppforexport.append(coly)
                
                if self.CheckmppLegend.get()==1:
                    newlegend=1
                    for item1 in range(len(MPPlegendMod)):
                        if MPPlegendMod[item1][0]==DATAx[item]["SampleName"]:
                            mppfig.plot(x,y,label=MPPlegendMod[item1][1],linestyle=MPPlinestyle[item1][1],color=MPPlinestyle[item1][2],linewidth=MPPlinestyle[item1][3])
                            newlegend=0
                            break
                    if newlegend:
                        mppfig.plot(x,y,label=DATAx[item]["SampleName"],linestyle=MPPlinestyle[item][1],color=MPPlinestyle[item][2],linewidth=MPPlinestyle[item1][3])
                        MPPlegendMod.append([DATAx[item]["SampleName"],DATAx[item]["SampleName"]])
                        MPPlinestyle.append([DATAx[item]["SampleName"],"-",colorstylelist[color],2])
                else:
                    mppfig.plot(x,y)
                color=color+1
        else:
            self.mppsubfig.clear()
            mppfig=self.mppsubfig
            color=0
            for i in range(len(sampletotake)):
                x = DATAx[sampletotake[i]]["MppData"][2]
                y = DATAx[sampletotake[i]]["MppData"][3]
                if self.CheckmppLegend.get()==1:
                    mppfig.plot(x,y,label=DATAx[sampletotake[i]]["SampleName"],color=colorstylelist[color])
                    MPPlegendMod.append([DATAx[sampletotake[i]]["SampleName"],DATAx[sampletotake[i]]["SampleName"]])
                    MPPlinestyle.append([DATAx[sampletotake[i]]["SampleName"],"-",colorstylelist[color],2])
                else:
                    mppfig.plot(x,y,color=colorstylelist[color])
                color=color+1
        
        self.mppsubfig.set_ylabel('Power (mW/cm'+'\xb2'+')')
        self.mppsubfig.set_xlabel('Time (s)')
        
        for item in ([self.mppsubfig.title, self.mppsubfig.xaxis.label, self.mppsubfig.yaxis.label] +
                             self.mppsubfig.get_xticklabels() + self.mppsubfig.get_yticklabels()):
            item.set_fontsize(self.fontsizeMppGraph.get())
            
        if titmpp:
            self.mppsubfig.set_title(self.titlempp.get())
        
        if self.CheckmppLegend.get()==1:
            if self.mpplegpos1.get()==1:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==2:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==3:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==4:
                self.leg=mppfig.legend(loc=self.mpplegpos1.get())
            elif self.mpplegpos1.get()==5:
                self.leg=mppfig.legend(bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
            else:
                self.leg=mppfig.legend(loc=0)
        
        DATAmppforexport=map(list, six.moves.zip_longest(*DATAmppforexport, fillvalue=' '))

        self.mppsubfig.axis([self.mppminx.get(),self.mppmaxx.get(),self.mppminy.get(),self.mppmaxy.get()])
        plt.gcf().canvas.draw()

#%%######################################################################
        
    def getdatalistsfromIVHITfiles(self, file_path):
        print("importing HIT iv files")
        global DATA
        for k in range(len(file_path)):
            print(k)
            wb = xlrd.open_workbook(file_path[k])
            sheet_names = wb.sheet_names()
            for j in range(len(sheet_names)):
                partdict={}
                if 'Sheet' not in sheet_names[j]:
                    xlsheet = wb.sheet_by_index(j)
                    if xlsheet.cell(13,0).value=="Number of points":#epfl hit iv files
                        #AllNames.append(sheet_names[j])
                        partdict["SampleName"]=sheet_names[j]
#                        print(partdict["SampleName"])
                        partdict["SampleName"]=partdict["SampleName"].replace("-","_")
                        partdict["DepID"]=partdict["SampleName"]
                        partdict["Cellletter"]='SingleEPFL'
                        partdict["CellNumber"]=4
                        
                        partdict["MeasDayTime"] = xlsheet.cell(0,0).value
                        partdict["CellSurface"]=xlsheet.cell(5,1).value
                        partdict["MeasComment"]=str(xlsheet.cell(6,1).value)
                          
                        partdict["ImaxComp"]=float(xlsheet.cell(9,1).value)
                        partdict["Isenserange"]=str(xlsheet.cell(10,1).value)
                        partdict["Vstart"]=float(xlsheet.cell(11,1).value)
                        partdict["Vend"]=float(xlsheet.cell(12,1).value)
                        partdict["NbPoints"]=float(xlsheet.cell(13,1).value)
                        partdict["Delay"]=float(xlsheet.cell(14,1).value)
                        partdict["IntegTime"]=float(xlsheet.cell(15,1).value)
                        
                        partdict["Operator"]=str(xlsheet.cell(3,1).value)
                        
                        partdict["RefNomCurr"]=float(xlsheet.cell(22,1).value)
                        partdict["RefMeasCurr"]=float(xlsheet.cell(23,1).value)
                        partdict["AirTemp"]=float(xlsheet.cell(26,1).value)
                        partdict["ChuckTemp"]=str(xlsheet.cell(27,1).value)
                        partdict["Illumination"]="Light"
                        partdict["Setup"]="HIT"
                        corrlign=0
                        partdict["Eff"]=float(xlsheet.cell(35-corrlign,1).value)
                        partdict["Voc"]=float(xlsheet.cell(35-corrlign,2).value)
                        partdict["Jsc"]=float(xlsheet.cell(35-corrlign,3).value)
                        partdict["FF"]=float(xlsheet.cell(35-corrlign,4).value)
                        partdict["Vmpp"]=float(xlsheet.cell(35-corrlign,5).value)
                        partdict["Jmpp"]=float(xlsheet.cell(35-corrlign,6).value)
                        partdict["Pmpp"]=float(xlsheet.cell(35-corrlign,7).value)
                        partdict["Rsc"]=float(xlsheet.cell(35-corrlign,8).value)
                        partdict["Roc"]=float(xlsheet.cell(35-corrlign,9).value)
                        partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                        partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                        
                        if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                            partdict["ScanDirection"]="Reverse"
                        else:
                            partdict["ScanDirection"]="Forward"
                        partdict["Group"]="Default group"
                        ivpartdat = [[],[]]#[voltage,current]
                        for item in range(37-corrlign,36-corrlign+int(partdict["NbPoints"]),1):
                            ivpartdat[0].append(float(xlsheet.cell(item,3).value))
                            ivpartdat[1].append(1000*float(xlsheet.cell(item,4).value)/partdict["CellSurface"])
                        partdict["IVData"]=ivpartdat
                        try:
                            if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                                f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                                x2 = lambda x: f(x)
                                partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                            else:
                                partdict["AreaJV"] =""
                        except ValueError:
                            print("there is a ValueError on sample ",k)
                        
                        DATA.append(partdict)
                    elif xlsheet.cell(13,0).value=="Vend:":#CSEM iv files
                        #AllNames.append(sheet_names[j])
                        partdict["SampleName"]=sheet_names[j]
#                        print(partdict["SampleName"])
                        partdict["SampleName"]=partdict["SampleName"].replace("-","_")
                        partdict["DepID"]=partdict["SampleName"]
                        partdict["Cellletter"]='SingleCSEM'
                        partdict["CellNumber"]=4
                        
                        partdict["MeasDayTime"] = xlsheet.cell(0,0).value
                        partdict["CellSurface"]=xlsheet.cell(5,1).value
                        partdict["MeasComment"]=str(xlsheet.cell(6,1).value)
                          
                        partdict["ImaxComp"]=""
                        partdict["Isenserange"]=str(xlsheet.cell(9,1).value)
                        partdict["Vstart"]=float(xlsheet.cell(12,1).value)
                        partdict["Vend"]=float(xlsheet.cell(13,1).value)
                        partdict["NbPoints"]=abs(partdict["Vend"]-partdict["Vstart"])/float(xlsheet.cell(10,1).value)
                        partdict["Delay"]=float(xlsheet.cell(14,1).value)
                        partdict["IntegTime"]=float(xlsheet.cell(15,1).value)
                        
                        partdict["Operator"]=str(xlsheet.cell(3,1).value)
                        
                        partdict["RefNomCurr"]=float(xlsheet.cell(22,1).value)
                        partdict["RefMeasCurr"]=float(xlsheet.cell(23,1).value)
                        partdict["AirTemp"]=float(xlsheet.cell(26,1).value)
                        partdict["ChuckTemp"]=str(xlsheet.cell(27,1).value)
                        partdict["Illumination"]="Light"
                        partdict["Setup"]="HIT"
                        corrlign=1    
                        partdict["Eff"]=float(xlsheet.cell(35-corrlign,1).value)
                        partdict["Voc"]=float(xlsheet.cell(35-corrlign,2).value)
                        partdict["Jsc"]=float(xlsheet.cell(35-corrlign,3).value)
                        partdict["FF"]=float(xlsheet.cell(35-corrlign,4).value)
                        partdict["Vmpp"]=float(xlsheet.cell(35-corrlign,5).value)
                        partdict["Jmpp"]=float(xlsheet.cell(35-corrlign,6).value)
                        partdict["Pmpp"]=float(xlsheet.cell(35-corrlign,7).value)
                        partdict["Rsc"]=float(xlsheet.cell(35-corrlign,8).value)
                        partdict["Roc"]=float(xlsheet.cell(35-corrlign,9).value)
                        partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                        partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                        
                        if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                            partdict["ScanDirection"]="Reverse"
                        else:
                            partdict["ScanDirection"]="Forward"
                        partdict["Group"]="Default group"
                        ivpartdat = [[],[]]#[voltage,current]
                        for item in range(37,36+int(partdict["NbPoints"]),1):
                            ivpartdat[0].append(float(xlsheet.cell(item,3).value))
                            ivpartdat[1].append(1000*float(xlsheet.cell(item,4).value)/partdict["CellSurface"])
                        partdict["IVData"]=ivpartdat
                        try:
                            if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                                f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                                x2 = lambda x: f(x)
                                partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                            else:
                                partdict["AreaJV"] =""
                        except ValueError:
                            print("there is a ValueError on sample ",k)
                        
                        DATA.append(partdict)
                    
        DATA = sorted(DATA, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATA if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATA)):
            DATA[item]['SampleName']=groupednames[item]
    
    def extract_jv_params(self, jv):#function originally written by Rohit Prasana (adapted by JW)
        '''
        Extract Voc, Jsc, FF, Pmax from a given JV curve
            * Assume given JV curve is in volts and mA/cm2
        '''
        resample_step_size = 0.00001 # Voltage step size to use while resampling JV curve to find Pmax
    
        from scipy.interpolate import interp1d, UnivariateSpline
    
        # Create a dict to store the parameters. Default values are -1 indicating failure to extract parameter
        params = {'Voc': -1., 'Jsc': -1., 'FF': -1., 'Pmax': -1., 'Roc':-1., 'Rsc':-1., 'Jmpp':-1, 'Vmpp':-1, 'Rshunt':-1, 'Rseries':-1}
        
        try:
            # Extract Jsc by interpolating wrt V
            jv_interp_V = interp1d(jv[0], jv[1], bounds_error=False, fill_value=0.)
            Jsc = jv_interp_V(0.)
            params['Jsc'] = abs(np.around(Jsc, decimals=8))
#            print(Jsc)
#            print(params['Jsc'])
        
            # Extract Voc by interpolating wrt J
            jv_interp_J = interp1d(jv[1], jv[0], bounds_error=False, fill_value=0.)
            Voc = jv_interp_J(0.)
    #            print(Voc)
            params['Voc'] = np.around(Voc, decimals=4)
        
            # Resample JV curve over standard interval and find Pmax
            Vrange_new = np.arange(0., Voc, resample_step_size)
    #            print(Vrange_new)
            jv_resampled = np.zeros((len(Vrange_new), 3))
            jv_resampled[:,0] = np.copy(Vrange_new)
            jv_resampled[:,1] = jv_interp_V(jv_resampled[:,0])
            jv_resampled[:,2] = np.abs(np.multiply(jv_resampled[:,0], jv_resampled[:,1]))
    #            print(jv_resampled)
            pmax=np.max(np.abs(np.multiply(jv_resampled[:,0], jv_resampled[:,1])))
            params['Pmax'] = np.around(np.max(np.abs(np.multiply(jv_resampled[:,0], jv_resampled[:,1]))), decimals=4)
            indPmax=list(jv_resampled[:,2]).index(pmax)
            params['Jmpp']=abs(list(jv_resampled[:,1])[indPmax])
    #            print(list(jv_resampled[:,1])[indPmax])
    #            print(indPmax)
    #            print(jv_interp_J(list(jv_resampled[:,1])[indPmax]))
            params['Vmpp']=1000*abs(list(jv_resampled[:,0])[indPmax])
    #            print(params['Vmpp'])
        
            # Calculate fill factor
            params['FF'] = abs(100*np.around(pmax/(Jsc*Voc), decimals=4))
            
            # Calculate Rsc&Roc 
            x= [x0 for x0,y0 in sorted(zip(params['Voltage'],params['CurrentDensity']))]
            y= [0.001*y0 for x0,y0 in sorted(zip(params['Voltage'],params['CurrentDensity']))]
            
            xSC=[]
            ySC=[]
            for i in range(len(x)):
                if x[i]>=0:
                    xSC.append(x[i-3])
                    xSC.append(x[i-2])
                    xSC.append(x[i-1])
                    xSC.append(x[i])
                    xSC.append(x[i+1])
                    xSC.append(x[i+2])
                    ySC.append(y[i-3])
                    ySC.append(y[i-2])
                    ySC.append(y[i-2])
                    ySC.append(y[i])
                    ySC.append(y[i+1])
                    ySC.append(y[i+2])
                    break

            xSC=np.array(xSC)
            ySC=np.array(ySC)    
                  
            xy=[xi*yi for xi, yi in zip(xSC,ySC)]
            xSC2=[xi**2 for xi in xSC]
            
            params['Rsc'] =abs( 1/(((sum(xSC)*sum(ySC)) - len(xSC)*sum(xy)) / ((sum(xSC)*sum(xSC)) - len(xSC)*sum(xSC2))))  
            # print(AllDATA[sample]['Rsc'])
            
            if params['Jsc']>1:
                xSC=[]
                ySC=[]
                for i in range(len(x)):
                    if x[i]>=params['Voc']:
                        xSC.append(x[i-2])
                        xSC.append(x[i-1])
                        xSC.append(x[i])
                        xSC.append(x[i+1])
                        
                        ySC.append(y[i-2])
                        ySC.append(y[i-1])
                        ySC.append(y[i])
                        ySC.append(y[i+1])
                        break
    #                plt.plot(xSC,ySC,'bo')
                xSC=np.array(xSC)
                ySC=np.array(ySC)
                
                xy=[xi*yi for xi, yi in zip(xSC,ySC)]
                xSC2=[xi**2 for xi in xSC]
                params['Roc'] =abs( 1/(((sum(xSC)*sum(ySC)) - len(xSC)*sum(xy)) / ((sum(xSC)*sum(xSC)) - len(xSC)*sum(xSC2))))
            else:
                xSC=x[-3:]
                ySC=y[-3:]
                xSC=np.array(xSC)
                ySC=np.array(ySC)      
                xy=[xi*yi for xi, yi in zip(xSC,ySC)]
                xSC2=[xi**2 for xi in xSC]
                
                params['Roc'] = abs( 1/(((sum(xSC)*sum(ySC)) - len(xSC)*sum(xy)) / ((sum(xSC)*sum(xSC)) - len(xSC)*sum(xSC2))))   
            # print(AllDATA[sample]['Roc'])
#             x= [x0 for x0,y0 in sorted(zip(jv[0],jv[1]))]
#             y= [0.001*y0 for x0,y0 in sorted(zip(jv[0],jv[1]))]
    

#             xSC=[]
#             ySC=[]
#             for i in range(len(x)):
#                 if x[i]>=0:
#                     xSC.append(x[i-3])
#                     xSC.append(x[i-2])
#                     xSC.append(x[i-1])
#                     xSC.append(x[i])
#                     xSC.append(x[i+1])
#                     xSC.append(x[i+2])
#                     ySC.append(y[i-3])
#                     ySC.append(y[i-2])
#                     ySC.append(y[i-2])
#                     ySC.append(y[i])
#                     ySC.append(y[i+1])
#                     ySC.append(y[i+2])
#                     break
#     #        print(xSC)
#     #        print(ySC)
#     #        plt.plot(xSC,ySC,'bo')
#             xSC=np.array(xSC)
#             ySC=np.array(ySC)    
                
#     #        slope = stats.linregress(xSC,ySC)   
            
#             params['Rsc'] =abs( 1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))))    
            
#             if params['Jsc']>1:
#                 xSC=[]
#                 ySC=[]
#                 for i in range(len(x)):
#                     if x[i]>=params['Voc']:
#                         xSC.append(x[i-2])
#                         xSC.append(x[i-1])
#                         xSC.append(x[i])
#                         xSC.append(x[i+1])
                        
#                         ySC.append(y[i-2])
#                         ySC.append(y[i-1])
#                         ySC.append(y[i])
#                         ySC.append(y[i+1])
#                         break
# #                plt.plot(xSC,ySC,'bo')
#                 xSC=np.array(xSC)
#                 ySC=np.array(ySC)      
                
#                 params['Roc'] =abs( 1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))))
#             else:
#                 xSC=x[-3:]
#                 ySC=y[-3:]
# #                plt.plot(xSC,ySC,'bo')
#                 xSC=np.array(xSC)
#                 ySC=np.array(ySC)      
                
#                 params['Roc'] = abs(1/(((mean(xSC)*mean(ySC)) - mean(xSC*ySC)) / ((mean(xSC)**2) - mean(xSC**2))) )   
            
            
            
            
#        plt.show()
#        print(params['Rsc'])
#        print(params['Roc'])
#        print(params['Jsc'])
        
        
        except:
            print("error with fits, probably a dark curve...")
    
        return  params
    
    def getdatalistsfromNRELcigssetup(self, file_path): #reads JV and mpp files from NREL cigs substrate config setup in S&TF 136
        global DATA, DATAdark
        global DATAMPP, numbLightfiles, numbDarkfiles
        
        for i in range(len(file_path)):
            filetoread = open(file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            if os.path.splitext(file_path[i])[1]=='.txt':
#                print("txt mpp file")
                partdict = {}
                partdict["filepath"]=file_path[i]
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
                partdict["DepID"]=filename.split('.')[0]+'_'+filename.split('.')[1]
                partdict["SampleName"]=filename.split('.')[0]+'_'+filename.split('.')[1]+'_'+filename.split('.')[2]
                partdict["Cellletter"]='Single'
                partdict["batchname"]=filename.split('.')[0]
                partdict["MeasComment"]=filerawdata[0].split('\t')[-1]

                partdict["MeasDayTime"]=modification_date(file_path[i])

                partdict["CellSurface"]= 1

                partdict["Delay"]=0
                partdict["IntegTime"]=0
                partdict["Vstep"]=0
                partdict["Vstart"]=0
                partdict["Vend"]=0
                partdict["ExecTime"]=0
                partdict["Operator"]='unknown'
                partdict["Group"]="Default group"
                
                mpppartdat = [[],[],[],[],[]]#[voltage,current,time,power,vstep,delay]
                for item in range(2,len(filerawdata),1):
                    mpppartdat[0].append(float(filerawdata[item].split("\t")[0]))
                    mpppartdat[1].append(float(filerawdata[item].split("\t")[1]))
                    mpppartdat[2].append(float(filerawdata[item].split("\t")[2]))
                    mpppartdat[3].append(float(filerawdata[item].split("\t")[3]))
                    mpppartdat[4].append(float(filerawdata[item].split("\t")[4]))
                partdict["PowerEnd"]=mpppartdat[3][-1]
                partdict["PowerAvg"]=sum(mpppartdat[3])/float(len(mpppartdat[3]))
                partdict["trackingduration"]=mpppartdat[2][-1]
                partdict["MppData"]=mpppartdat
                DATAMPP.append(partdict)   
                
                
            elif os.path.splitext(file_path[i])[1]=='.itx':
#                print("cigs iv file")
                partdict = {}
                partdict["filepath"]=file_path[i]
                
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
#                print(filename)
                if 'Reverse' in filename:
                    partdict["DepID"]=filename[:filename.index('Reverse')-1]
                    aftername=filename[filename.index('Reverse'):]
                    partdict["ScanDirection"]="Reverse"
                elif 'Forward' in filename:
                    partdict["DepID"]=filename[:filename.index('Forward')-1]
                    aftername=filename[filename.index('Forward'):]
                    partdict["ScanDirection"]="Forward" 
                
                partdict["Cellletter"]='Single'
                partdict["batchname"]=partdict["DepID"].split('.')[0]
                partdict["SampleName"]=partdict["DepID"]+"_"+aftername.split('.')[1]+"_"+aftername.split('.')[2]
                
#                print(partdict["SampleName"])
                
                if 'LIV' in aftername:
                    partdict["Illumination"]="Light"
                elif 'DIV' in aftername:
                    partdict["Illumination"]="Dark"
                    
                    
                partdict["MeasDayTime2"]=modification_date(file_path[i])#'2020-01-29 12:55:00'
                partdict["MeasDayTime"]='Mon, Jan 01, 0000 0:00:00'
                
                for item in range(len(filerawdata)):
                    if "X Note" in filerawdata[item]:
#                        print(filerawdata[item].index('\\r'))
#                        print(filerawdata[item][filerawdata[item].index('\\r')+2:filerawdata[item].index('\\rArea')-1])
                        partdict["MeasDayTime2"]=parser.parse(filerawdata[item][filerawdata[item].index('\\r')+2:filerawdata[item].index('\\rArea')-1])
                        partdict["MeasDayTime"]=filerawdata[item][filerawdata[item].index('\\r')+2:filerawdata[item].index('\\rArea')-1]
#                        print(partdict["MeasDayTime2"])
                        break
                
#                partdict["MeasComment"]=filerawdata[-1][filerawdata[-1].index('"')+1:-3]
                partdict["MeasComment"]=''
#                if "aftermpp" in partdict["MeasComment"]:
#                    partdict["aftermpp"]=1
#                else:
#                    partdict["aftermpp"]=0
                
                for item in range(len(filerawdata)):
                    if "X SetScale" in filerawdata[item]:
                        partdict["Vstart"]=float(filerawdata[item][15:filerawdata[item].index(',')])
                        break
                #vstep
                for item in range(len(filerawdata)):
                    if "X SetScale" in filerawdata[item]:
                        partdict["Vstep"]=float(filerawdata[item].split(',')[1])
                        break
#                print(partdict["Vstart"])
#                print(partdict["Vstep"])
                ivpartdat = [[],[]]#[voltage,current]
                increm=0
                for item in range(3,len(filerawdata),1):
                    if 'END' not in filerawdata[item]:
                        ivpartdat[0].append(partdict["Vstart"]+increm*partdict["Vstep"])
#                        print(item)
#                        if partdict["ScanDirection"]=="Forward":
#                            ivpartdat[0].append(partdict["Vstart"]+increm*partdict["Vstep"])
#                        else:
#                            ivpartdat[0].append(partdict["Vstart"]+increm*partdict["Vstep"])
                        ivpartdat[1].append(float(filerawdata[item].split('\t')[2][:-2])) 
                        increm+=1
                    else:
                        break
                partdict["IVData"]=ivpartdat
                
                partdict["Vend"]=ivpartdat[0][-1]
                
#                if partdict["ScanDirection"]=="Reverse":
#                    if partdict["Vstart"]<partdict["Vend"]:
#                        vend=partdict["Vend"]
#                        partdict["Vend"]=partdict["Vstart"]
#                        partdict["Vstart"]=vend
#                else:
#                    if partdict["Vstart"]>partdict["Vend"]:
#                        vend=partdict["Vend"]
#                        partdict["Vend"]=partdict["Vstart"]
#                        partdict["Vstart"]=vend 
                        
                partdict["NbPoints"]=len(ivpartdat[0])
                partdict["CellSurface"]=999
                for item in range(len(filerawdata)):
                    if "X Note" in filerawdata[item]:
                        # print(filerawdata[item])
                        partdict["CellSurface"]=filerawdata[item][filerawdata[item].index('\\rArea')+18:filerawdata[item].index('\\rVoc')-1]
                        break
                
                partdict["Delay"]=-1
                partdict["IntegTime"]=-1                        

                params=self.extract_jv_params(partdict["IVData"])
                partdict["Voc"]=params['Voc']*1000 #mV
                partdict["Jsc"]=params['Jsc'] #mA/cm2
                partdict["FF"]=params['FF'] #%
                partdict["Eff"]=params['Pmax'] #%
                partdict["Pmpp"]=partdict["Eff"]*10 #W/cm2
                partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                partdict["Roc"]=params['Roc'] 
                partdict["Rsc"]=params['Rsc'] 
                partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                
                partdict["Vmpp"]=params['Vmpp']
                partdict["Jmpp"]=params['Jmpp']
                partdict["ImaxComp"]=-1
                partdict["Isenserange"]=-1
                
                partdict["Operator"]=-1
                              
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                
                partdict["Group"]="Default group"
                partdict["Setup"]="SSIgorC215"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
                    
#                DATA.append(partdict)

                if partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                    numbLightfiles+=1
                else:
                    partdict["SampleName"]=partdict["SampleName"]+'_D'
                    DATA.append(partdict)
                    DATAdark.append(partdict)
                    numbDarkfiles+=1
    
    def getdatalistsfromCUBfiles(self, file_path): #reads JV and mpp files from CUB
        global DATA, DATAdark
        global DATAMPP, numbLightfiles, numbDarkfiles
        
        for i in range(len(file_path)):
            filetoread = open(file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            print(i)
            filetype = 1
#            if "HEADER START" in filerawdata[0]:
#                filetype = 1 #JV file from solar simulator in SERF C215
#            elif "Power (mW/cm2)" in filerawdata[0]:
#                filetype = 2
#            elif "V\tI" in filerawdata[0]:
#                filetype = 3
#                print("JVT")
            
            
            if filetype ==1 : #J-V files of SERF C215
                              
                partdict = {}
                partdict["filepath"]=file_path[i]
                
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]                
                
                partdict["Cellletter"]=filename.split('_')[2][2:]
                partdict["batchname"]=filename.split('_')[0]
                partdict["DepID"]=partdict["batchname"]+"_"+filename.split('_')[1]
                partdict["SampleName"]=partdict["DepID"]+"_"+partdict["Cellletter"] #+"_"+aftername.split('_')[4]
                
                if "light" in filename:
                    partdict["Illumination"]="Light"
                else:
                    partdict["Illumination"]="Dark"
                    
                if "rev" in filename:
                    partdict["ScanDirection"]="Reverse"
                else:
                    partdict["ScanDirection"]="Forward" 
                
                
                partdict["MeasDayTime2"]=parser.parse(filerawdata[0])
                partdict["MeasDayTime"]=filerawdata[0]
#                print(partdict["MeasDayTime2"])
#                print(partdict["MeasDayTime"])
                        
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Notes = " in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][8:-1]
                        break
                if "aftermpp" in partdict["MeasComment"]:
                    partdict["aftermpp"]=1
                else:
                    partdict["aftermpp"]=0
                    
                for item in range(len(filerawdata)):
                    if "Device Area = " in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][14:-5])
#                        print(partdict["CellSurface"])
                        break
                for item in range(len(filerawdata)):
                    if "Delay = " in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][8:-3])
#                        print(partdict["Delay"])
                        break
                for item in range(len(filerawdata)):
                    if "NPLC = " in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][7:-1])
                        break     
                
                for item in range(len(filerawdata)):
                    if "Voltage" in filerawdata[item]:
                            pos=item+1
                            break
                        
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(pos,len(filerawdata),1):
                    try:
                        ivpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                        ivpartdat[1].append(float(filerawdata[item].split("\t")[1]))
                    except:
                        break
                partdict["IVData"]=ivpartdat
                partdict["NbPoints"]=len(ivpartdat[0])
                partdict["Vstart"]=ivpartdat[0][-1]
                partdict["Vend"]=ivpartdat[0][0]
                        
                params=self.extract_jv_params(partdict["IVData"])
                partdict["Voc"]=params['Voc']*1000 #mV
                partdict["Jsc"]=params['Jsc'] #mA/cm2
                partdict["FF"]=params['FF'] #%
                partdict["Eff"]=params['Pmax'] #%
                partdict["Pmpp"]=partdict["Eff"]*10 #W/cm2
                partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                partdict["Roc"]=params['Roc'] 
                partdict["Rsc"]=params['Rsc'] 
                partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                
                partdict["Vmpp"]=params['Vmpp']
                partdict["Jmpp"]=params['Jmpp']
                partdict["ImaxComp"]=-1
                partdict["Isenserange"]=-1
                
                partdict["Operator"]=-1
                              
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                
                partdict["Group"]="Default group"
                partdict["Setup"]="CUBoulder"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
                    
#                DATA.append(partdict)

                if partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                    numbLightfiles+=1
                else:
                    partdict["SampleName"]=partdict["SampleName"]+'_D'
                    DATA.append(partdict)
                    DATAdark.append(partdict)
                    numbDarkfiles+=1
            
        
        DATA = sorted(DATA, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATA if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
#        print(groupednames)
        for item in range(len(groupednames)):
            if len(groupednames[item])>1 and groupednames[item][0][-1]!='D':
                positions=[]
                effrev=0
                efffor=0
                for item2 in range(len(DATA)):
                    if DATA[item2]['SampleName']==groupednames[item][0]:
                        positions.append(item2)
                        if DATA[item2]["ScanDirection"]=="Reverse":
                            effrev=DATA[item2]['Eff']
                        else:
                            efffor=DATA[item2]['Eff']
                    if len(positions)==len(groupednames[item]):
                        break
                try:
                    hyste=100*(effrev-efffor)/effrev
                    for item2 in range(len(positions)):
                        DATA[positions[item2]]['HI']=hyste
#                        print(hyste)
                except:
                    print("except HI")
        
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                k=1
                for item0 in range(1,len(groupednames[item])):
                    
#                    groupednames2=copy.deepcopy(groupednames)
#                    groupednames[item][item0]+= "_"+str(k)
#                    print(groupednames[item][item0])
                    while(1):
                        groupednames2=list(chain.from_iterable(groupednames))
#                        print(groupednames2)
                        
                        if groupednames[item][item0]+"_"+str(k) in groupednames2:
                            k+=1
                            groupednames[item][item0]+= "_"+str(k)
#                            print(groupednames[item][item0])
#                            print('')
                        else:
                            groupednames[item][item0]+= "_"+str(k)
#                            print('notin')
                            break
                        
        groupednames=list(chain.from_iterable(groupednames))
#        print("")
#        print(groupednames)
        for item in range(len(DATA)):
            DATA[item]['SampleName']=groupednames[item]
        
        DATAMPP = sorted(DATAMPP, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATAMPP if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATAMPP)):
            DATAMPP[item]['SampleName']=groupednames[item]
        
        self.updategrouptoplotdropbutton()
        self.updateCompgrouptoplotdropbutton()
        self.updateHistgrouptoplotdropbutton()
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        
        
    def getdatalistsfromNRELfiles(self, file_path): #reads JV and mpp files from NREL
        global DATA, DATAdark
        global DATAMPP, numbLightfiles, numbDarkfiles
        
        
        for i in range(len(file_path)):
            filetoread = open(file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            print(i)
            filetype = 0
            if "HEADER START" in filerawdata[0]:
                filetype = 1 #JV file from solar simulator in SERF C215
            elif "Power (mW/cm2)" in filerawdata[0]:
                filetype = 2
            elif "V\tI" in filerawdata[0]:
                filetype = 3
                print("JVT")
            
            
            if filetype ==1 : #J-V files of SERF C215
                              
                partdict = {}
                partdict["filepath"]=file_path[i]
                
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
#                print(filename)
                if 'rev' in filename:
                    partdict["DepID"]=filename[:filename.index('rev')-1]
                    aftername=filename[filename.index('rev'):]
                elif 'fwd' in filename:
                    partdict["DepID"]=filename[:filename.index('fwd')-1]
                    aftername=filename[filename.index('fwd'):]
                
                partdict["Cellletter"]=aftername.split('_')[3][2:]
                partdict["batchname"]=partdict["DepID"].split('_')[0]
                partdict["SampleName"]=partdict["DepID"]+"_"+partdict["Cellletter"]+"_"+aftername.split('_')[4]
                
                if aftername.split('_')[1]=="lt":
                    partdict["Illumination"]="Light"
                else:
                    partdict["Illumination"]="Dark"
                    
                if aftername.split('_')[0]=="rev":
                    partdict["ScanDirection"]="Reverse"
                else:
                    partdict["ScanDirection"]="Forward" 
                
                for item in range(len(filerawdata)):
                    if "Date/Time:" in filerawdata[item]:
                        partdict["MeasDayTime2"]=parser.parse(filerawdata[item][11:-1])
                        partdict["MeasDayTime"]=filerawdata[item][11:-1]
#                        print(partdict["MeasDayTime2"])
#                        print(partdict["MeasDayTime"].split(' ')[-2])
                        break
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Comments: " in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][10:-1]
                        break
                if "aftermpp" in partdict["MeasComment"]:
                    partdict["aftermpp"]=1
                else:
                    partdict["aftermpp"]=0
                for item in range(len(filerawdata)):
                    if "Start V:" in filerawdata[item]:
                        partdict["Vstart"]=float(filerawdata[item][9:-1])
                        break
                for item in range(len(filerawdata)):
                    if "End V:" in filerawdata[item]:
                        partdict["Vend"]=float(filerawdata[item][7:-1])
                        break
                if partdict["ScanDirection"]=="Reverse":
                    if partdict["Vstart"]<partdict["Vend"]:
                        vend=partdict["Vend"]
                        partdict["Vend"]=partdict["Vstart"]
                        partdict["Vstart"]=vend
                else:
                    if partdict["Vstart"]>partdict["Vend"]:
                        vend=partdict["Vend"]
                        partdict["Vend"]=partdict["Vstart"]
                        partdict["Vstart"]=vend 
                for item in range(len(filerawdata)):
                    if "Number Points:" in filerawdata[item]:
                        partdict["NbPoints"]=float(filerawdata[item][15:-1])
                        break    
                for item in range(len(filerawdata)):
                    if "Pixel Size:" in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][12:-5])
                        #print(partdict["CellSurface"])
                        break
                for item in range(len(filerawdata)):
                    if "Source Delay:" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][14:-1])
                        break
                for item in range(len(filerawdata)):
                    if "NPLC:" in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][6:-1])
                        break
                for item in range(len(filerawdata)):
                    if "HEADER END" in filerawdata[item]:
                            pos=item+3
                            break
                        
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(pos,len(filerawdata),1):
                    try:
                        ivpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                        ivpartdat[1].append(-float(filerawdata[item].split("\t")[1]))
                    except:
                        break
                partdict["IVData"]=ivpartdat
                params=self.extract_jv_params(partdict["IVData"])
                partdict["Voc"]=params['Voc']*1000 #mV
                partdict["Jsc"]=params['Jsc'] #mA/cm2
                partdict["FF"]=params['FF'] #%
                partdict["Eff"]=params['Pmax'] #%
                partdict["Pmpp"]=partdict["Eff"]*10 #W/cm2
                partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                partdict["Roc"]=params['Roc'] 
                partdict["Rsc"]=params['Rsc'] 
                partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                
                partdict["Vmpp"]=params['Vmpp']
                partdict["Jmpp"]=params['Jmpp']
                partdict["ImaxComp"]=-1
                partdict["Isenserange"]=-1
                
                partdict["Operator"]=-1
                              
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                
                partdict["Group"]="Default group"
                partdict["Setup"]="SSIgorC215"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
                    
#                DATA.append(partdict)

                if partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                    numbLightfiles+=1
                else:
                    partdict["SampleName"]=partdict["SampleName"]+'_D'
                    DATA.append(partdict)
                    DATAdark.append(partdict)
                    numbDarkfiles+=1
            elif filetype ==3 : #JVT files from Taylor
                partdict = {}
                partdict["filepath"]=file_path[i]
                
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
#                print(filename)
                
                partdict["DepID"]=filename
                aftername=filename
    
                
                partdict["Cellletter"]='A'
                partdict["batchname"]='batch'
                partdict["SampleName"]=partdict["DepID"]
                
                partdict["Illumination"]="Light"
                    
                partdict["ScanDirection"]="Reverse"
                
                
                partdict["MeasDayTime2"]='2020-01-29 12:55:00'
                partdict["MeasDayTime"]='Wed, Jan 29, 2020 0:00:00'
                        
                partdict["MeasComment"]="-"
                partdict["aftermpp"]=1
                partdict["Vstart"]=0
                partdict["Vend"]=0
                partdict["NbPoints"]=0      
                partdict["CellSurface"]=0.1  
                partdict["Delay"]=0    
                partdict["IntegTime"]=0
                        
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(1,len(filerawdata),1):
                    try:
                        ivpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                        ivpartdat[1].append(1000*float(filerawdata[item].split("\t")[1])/partdict["CellSurface"])
                    except:
                        break
                partdict["IVData"]=ivpartdat
                params=self.extract_jv_params(partdict["IVData"])
                partdict["Voc"]=params['Voc']*1000 #mV
                partdict["Jsc"]=params['Jsc'] #mA/cm2
                partdict["FF"]=params['FF'] #%
                partdict["Eff"]=params['Pmax'] #%
                partdict["Pmpp"]=partdict["Eff"]*10 #W/cm2
                partdict["VocFF"]=partdict["Voc"]*partdict["FF"]
                partdict["Roc"]=params['Roc'] 
                partdict["Rsc"]=params['Rsc'] 
                partdict["RscJsc"]=partdict["Rsc"]*partdict["Jsc"]
                
                partdict["Vmpp"]=params['Vmpp']
                partdict["Jmpp"]=params['Jmpp']
                partdict["ImaxComp"]=-1
                partdict["Isenserange"]=-1
                
                partdict["Operator"]=-1
                              
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                
                partdict["Group"]="Default group"
                partdict["Setup"]="JVT"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
                    
#                DATA.append(partdict)
                DATA.append(partdict)
                numbLightfiles+=1
                
            elif filetype ==2 : #mpp files of SERF C215 labview program
                #assumes file name: batch_samplenumber_cellLetter_mpp
                partdict = {}
                partdict["filepath"]=file_path[i]
                filename=os.path.splitext(os.path.basename(partdict["filepath"]))[0]
                partdict["DepID"]=filename.split('_')[0]+'_'+filename.split('_')[1]
                partdict["SampleName"]=filename.split('_')[0]+'_'+filename.split('_')[1]+'_'+filename.split('_')[2]
                partdict["Cellletter"]=filename.split('_')[2]
                partdict["batchname"]=filename.split('_')[0]
                partdict["MeasComment"]=filename[filename.index('_')+1:]

                partdict["MeasDayTime"]=modification_date(file_path[i])

                partdict["CellSurface"]= float(filerawdata[0].split('\t')[-1])

                partdict["Delay"]=0
                partdict["IntegTime"]=0
                partdict["Vstep"]=0
                partdict["Vstart"]=0
                partdict["Vend"]=0
                partdict["ExecTime"]=0
                partdict["Operator"]='unknown'
                partdict["Group"]="Default group"
                
                mpppartdat = [[],[],[],[],[]]#[voltage,current,time,power,vstep]
                for item in range(1,len(filerawdata),1):
                    mpppartdat[0].append(float(filerawdata[item].split("\t")[2]))
                    mpppartdat[1].append(float(filerawdata[item].split("\t")[3]))
                    mpppartdat[2].append(float(filerawdata[item].split("\t")[0]))
                    mpppartdat[3].append(float(filerawdata[item].split("\t")[1]))
                    mpppartdat[4].append(-1)
                partdict["PowerEnd"]=mpppartdat[3][-1]
                partdict["PowerAvg"]=sum(mpppartdat[3])/float(len(mpppartdat[3]))
                partdict["trackingduration"]=mpppartdat[2][-1]
                partdict["MppData"]=mpppartdat
                partdict["SampleName"]=partdict["SampleName"]+'_'+str(partdict["MeasDayTime"]).replace(':','').replace(' ','-')
                DATAMPP.append(partdict)                
        
        DATA = sorted(DATA, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATA if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
#        print(groupednames)
        for item in range(len(groupednames)):
            if len(groupednames[item])>1 and groupednames[item][0][-1]!='D':
                positions=[]
                effrev=0
                efffor=0
                for item2 in range(len(DATA)):
                    if DATA[item2]['SampleName']==groupednames[item][0]:
                        positions.append(item2)
                        if DATA[item2]["ScanDirection"]=="Reverse":
                            effrev=DATA[item2]['Eff']
                        else:
                            efffor=DATA[item2]['Eff']
                    if len(positions)==len(groupednames[item]):
                        break
                try:
                    hyste=100*(effrev-efffor)/effrev
                    for item2 in range(len(positions)):
                        DATA[positions[item2]]['HI']=hyste
#                        print(hyste)
                except:
                    print("except HI")
        
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                k=1
                for item0 in range(1,len(groupednames[item])):
                    
#                    groupednames2=copy.deepcopy(groupednames)
#                    groupednames[item][item0]+= "_"+str(k)
#                    print(groupednames[item][item0])
                    while(1):
                        groupednames2=list(chain.from_iterable(groupednames))
#                        print(groupednames2)
                        
                        if groupednames[item][item0]+"_"+str(k) in groupednames2:
                            k+=1
                            groupednames[item][item0]+= "_"+str(k)
#                            print(groupednames[item][item0])
#                            print('')
                        else:
                            groupednames[item][item0]+= "_"+str(k)
#                            print('notin')
                            break
                        
        groupednames=list(chain.from_iterable(groupednames))
#        print("")
#        print(groupednames)
        for item in range(len(DATA)):
            DATA[item]['SampleName']=groupednames[item]
        
        DATAMPP = sorted(DATAMPP, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATAMPP if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATAMPP)):
            DATAMPP[item]['SampleName']=groupednames[item]
        
        self.updategrouptoplotdropbutton()
        self.updateCompgrouptoplotdropbutton()
        self.updateHistgrouptoplotdropbutton()
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        
    def getdatalistsfromIVTFfiles(self, file_path): #EPFL files
        global DATA
        global DATAdark
        global DATAMPP
        global DATAFV
        
        for i in range(len(file_path)):
            filetoread = open(file_path[i],"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            print(i)
            filetype = 0
            for item0 in range(len(filerawdata)):
                if "voltage/current" in filerawdata[item0]:
                    filetype = 1
                    break
                if "IV FRLOOP" in filerawdata[item0]:
                    filetype =2
                    break
                elif "Mpp tracker" in filerawdata[item0]:
#                    for item1 in range(len(filerawdata)):
#                        if "% MEASURED Pmpptracker" in filerawdata[item0]:
                    filetype = 3
                    break
                elif "Fixed voltage" in filerawdata[item0]:
                    filetype = 4
                    break
                elif "Keithley 238" in filerawdata[item0]:
                    filetype = 5
                    break
            
                                
            if filetype ==1 or filetype==2: #J-V files and FRLOOP
                partdict = {}
                partdict["filepath"]=file_path[i]
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Measurement comment:" in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][21:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell number:" in filerawdata[item]:
                        partdict["CellNumber"]=float(filerawdata[item][23:-1])
                        if partdict["CellNumber"]==1:
                            partdict["Cellletter"]='A'
                        elif partdict["CellNumber"]==2:
                            partdict["Cellletter"]='B'
                        elif partdict["CellNumber"]==3:
                            partdict["Cellletter"]='C'
                        else:
                            partdict["Cellletter"]='Single'
                        break
                for item in range(len(filerawdata)):
                    if "Deposition ID:" in filerawdata[item]:
                        if filerawdata[item-1][19:-1]=='':
                            partdict["SampleName"]=filerawdata[item][15:-1]+"_"+partdict["Cellletter"]
                        else:
                            partdict["SampleName"]=filerawdata[item][15:-1]+"_"+filerawdata[item-1][19:-1]+"_"+partdict["Cellletter"]
                        partdict["DepID"]=filerawdata[item][15:-1]
                        partdict["DepID"]=partdict["DepID"].replace("-","_")
                        partdict["SampleName"]=partdict["SampleName"].replace("-","_")
                        break
                for item in range(len(filerawdata)):
                    if "IV measurement time:" in filerawdata[item]:
                        partdict["MeasDayTime"]=filerawdata[item][22:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell size [m2]:" in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][17:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Voc [V]:" in filerawdata[item]:
                        partdict["Voc"]=float(filerawdata[item][19:-1])*1000
                        break            
                for item in range(len(filerawdata)):
                    if "Jsc [A/m2]:" in filerawdata[item]:
                        partdict["Jsc"]=float(filerawdata[item][19:-1])*0.1
                        break            
                for item in range(len(filerawdata)):
                    if "FF [.]:" in filerawdata[item]:
                        partdict["FF"]=float(filerawdata[item][18:-1])*100
                        break            
                for item in range(len(filerawdata)):
                    if "Efficiency [.]:" in filerawdata[item]:
                        partdict["Eff"]=float(filerawdata[item][19:-1])*100
                        break
                for item in range(len(filerawdata)):
                    if "Pmpp [W/m2]:" in filerawdata[item]:
                        partdict["Pmpp"]=float(filerawdata[item][19:-1])
                        break                
                for item in range(len(filerawdata)):
                    if "Vmpp [V]:" in filerawdata[item]:
                        partdict["Vmpp"]=float(filerawdata[item][10:-1])*1000
                        break                
                for item in range(len(filerawdata)):
                    if "Jmpp [A]:" in filerawdata[item]:
                        partdict["Jmpp"]=float(filerawdata[item][10:-1])*0.1
                        break   
                for item in range(len(filerawdata)):
                    if "Roc [Ohm.m2]:" in filerawdata[item]:
                        partdict["Roc"]=float(filerawdata[item][15:-1])*10000
                        break
                for item in range(len(filerawdata)):
                    if "Rsc [Ohm.m2]:" in filerawdata[item]:
                        partdict["Rsc"]=float(filerawdata[item][15:-1])*10000
                        break
                partdict["VocFF"]=float(partdict["Voc"])*float(partdict["FF"])*0.01
                partdict["RscJsc"]=float(partdict["Rsc"])*float(partdict["Jsc"])*0.001
                for item in range(len(filerawdata)):
                    if "Number of points:" in filerawdata[item]:
                        partdict["NbPoints"]=float(filerawdata[item][17:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Delay [s]:" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][10:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Integration time [s]:" in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][21:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Vstart:" in filerawdata[item]:
                        partdict["Vstart"]=float(filerawdata[item][7:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Vend:" in filerawdata[item]:
                        partdict["Vend"]=float(filerawdata[item][5:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Illumination:" in filerawdata[item]:
                        partdict["Illumination"]=filerawdata[item][14:-1]
                        break
                if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                    partdict["ScanDirection"]="Reverse"
                else:
                    partdict["ScanDirection"]="Forward"
                for item in range(len(filerawdata)):
                    if "Imax compliance [A]:" in filerawdata[item]:
                        partdict["ImaxComp"]=filerawdata[item][21:-1]
                        break
                for item in range(len(filerawdata)):
                    if "I sense range:" in filerawdata[item]:
                        partdict["Isenserange"]=filerawdata[item][15:-1]
                        break
                for item in range(len(filerawdata)):
                    if "User name:" in filerawdata[item]:
                        partdict["Operator"]=filerawdata[item][11:-1]
                        break
                for item in range(len(filerawdata)):
                    if "MEASURED IV DATA" in filerawdata[item]:
                            pos=item+2
                            break
                    elif "MEASURED IV FRLOOP DATA" in filerawdata[item]:
                            pos=item+2
                            break
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(pos,len(filerawdata),1):
                    ivpartdat[0].append(float(filerawdata[item].split("\t")[2]))
                    ivpartdat[1].append(0.1*float(filerawdata[item].split("\t")[3][:-1]))
                partdict["IVData"]=ivpartdat
                
                partdict["Group"]="Default group"
                partdict["Setup"]="TFIV"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
    
                #still missing: test for transposition, mirror
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                if partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                else:
                    DATAdark.append(partdict)
                        
            elif filetype==3: #Mpp files
                partdict = {}
                partdict["filepath"]=file_path[i]
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Measurement comment:" in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][21:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Deposition ID:" in filerawdata[item]:
                        partdict["SampleName"]=filerawdata[item][15:-1]+"_"+filerawdata[item-1][19:-1]
                        partdict["DepID"]=filerawdata[item][15:-1]
                        partdict["DepID"]=partdict["DepID"].replace("-","_")
                        break
                for item in range(len(filerawdata)):
                    if "Cell number:" in filerawdata[item]:
                        partdict["CellNumber"]=float(filerawdata[item][23:-1])
                        if partdict["CellNumber"]==1:
                            partdict["Cellletter"]='A'
                        elif partdict["CellNumber"]==2:
                            partdict["Cellletter"]='B'
                        elif partdict["CellNumber"]==3:
                            partdict["Cellletter"]='C'
                        else:
                            partdict["Cellletter"]='Single'
                        break
                for item in range(len(filerawdata)):
                    if "IV measurement time:" in filerawdata[item]:
                        partdict["MeasDayTime"]=filerawdata[item][22:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell size [m2]:" in filerawdata[item]:
                        partdict["CellSurface"]=filerawdata[item][17:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Delay [s]:" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][10:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Integration time [s]:" in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][21:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Vstep:" in filerawdata[item]:
                        partdict["Vstep"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vstart:" in filerawdata[item]:
                        partdict["Vstart"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vend:" in filerawdata[item]:
                        partdict["Vend"]=str(float(filerawdata[item][5:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Execution time:" in filerawdata[item]:
                        partdict["ExecTime"]=str(float(filerawdata[item][16:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "User name:" in filerawdata[item]:
                        partdict["Operator"]=filerawdata[item][11:-1]
                        break
                for item in range(len(filerawdata)):
                    if "MEASURED Pmpptracker" in filerawdata[item]:
                        pos=item+2
                        break
                partdict["Group"]="Default group"
                mpppartdat = [[],[],[],[],[]]#[voltage,current,time,power,vstep]
                for item in range(pos,len(filerawdata),1):
                    mpppartdat[0].append(float(filerawdata[item].split("\t")[0]))
                    mpppartdat[1].append(float(filerawdata[item].split("\t")[1]))
                    mpppartdat[2].append(float(filerawdata[item].split("\t")[2]))
                    mpppartdat[3].append(float(filerawdata[item].split("\t")[3]))
                    mpppartdat[4].append(float(filerawdata[item].split("\t")[4]))
                partdict["PowerEnd"]=mpppartdat[3][-1]
                partdict["PowerAvg"]=sum(mpppartdat[3])/float(len(mpppartdat[3]))
                partdict["trackingduration"]=mpppartdat[2][-1]
                partdict["MppData"]=mpppartdat
                DATAMPP.append(partdict)
        
        
            elif filetype==4: #FV files
                partdict = {}
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Measurement comment:" in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][21:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell number:" in filerawdata[item]:
                        partdict["CellNumber"]=float(filerawdata[item][23:-1])
                        if partdict["CellNumber"]==1:
                            partdict["Cellletter"]='A'
                        elif partdict["CellNumber"]==2:
                            partdict["Cellletter"]='B'
                        elif partdict["CellNumber"]==3:
                            partdict["Cellletter"]='C'
                        else:
                            partdict["Cellletter"]='Single'
                        break
                for item in range(len(filerawdata)):
                    if "Deposition ID:" in filerawdata[item]:
                        if filerawdata[item-1][19:-1]=='':
                            partdict["SampleName"]=filerawdata[item][15:-1]+"_"+partdict["Cellletter"]
                        else:
                            partdict["SampleName"]=filerawdata[item][15:-1]+"_"+filerawdata[item-1][19:-1]
                        partdict["DepID"]=filerawdata[item][15:-1]
                        break
                for item in range(len(filerawdata)):
                    if "IV measurement time:" in filerawdata[item]:
                        partdict["MeasDayTime"]=filerawdata[item][22:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell size [m2]:" in filerawdata[item]:
                        partdict["CellSurface"]=filerawdata[item][17:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Delay [s]:" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][10:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Integration time [s]:" in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][21:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Vstep:" in filerawdata[item]:
                        partdict["Vstep"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vstart:" in filerawdata[item]:
                        partdict["Vstart"]=str(float(filerawdata[item][7:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Vend:" in filerawdata[item]:
                        partdict["Vend"]=str(float(filerawdata[item][5:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Number of points:" in filerawdata[item]:
                        partdict["NbCycle"]=float(filerawdata[item][17:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Execution time:" in filerawdata[item]:
                        partdict["ExecTime"]=str(float(filerawdata[item][16:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "Time at V=0:" in filerawdata[item]:
                        partdict["TimeatZero"]=str(float(filerawdata[item][13:-1]))
                        break
                for item in range(len(filerawdata)):
                    if "User name:" in filerawdata[item]:
                        partdict["Operator"]=filerawdata[item][11:-1]
                        break
                for item in range(len(filerawdata)):
                    if "MEASURED Fixed Voltage" in filerawdata[item]:
                        pos=item+2
                        break 
                partdict["Group"]="Default group"
                fvpartdat = [[],[],[],[]]#[voltage,current,power,time]
                for item in range(pos,len(filerawdata),1):
                    fvpartdat[0].append(float(filerawdata[item].split("\t")[0]))
                    fvpartdat[1].append(float(filerawdata[item].split("\t")[1]))
                    fvpartdat[2].append(abs(10*float(filerawdata[item].split("\t")[2])))
                    fvpartdat[3].append(float(filerawdata[item].split("\t")[3]))
                partdict["FVData"]=fvpartdat
                DATAFV.append(partdict)
                
            elif filetype==5: #3sun files
                partdict = {}
                partdict["filepath"]=file_path[i]
                partdict["MeasComment"]="-"
                for item in range(len(filerawdata)):
                    if "Measurement comment:" in filerawdata[item]:
                        partdict["MeasComment"]=filerawdata[item][21:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell number:" in filerawdata[item]:
                        partdict["CellNumber"]=float(filerawdata[item][23:-1])
                        if partdict["CellNumber"]==1:
                            partdict["Cellletter"]='A'
                        elif partdict["CellNumber"]==2:
                            partdict["Cellletter"]='B'
                        elif partdict["CellNumber"]==3:
                            partdict["Cellletter"]='C'
                        else:
                            partdict["Cellletter"]='Single'
                        break
                for item in range(len(filerawdata)):
                    if "Deposition ID:" in filerawdata[item]:
                        if filerawdata[item-1][19:-1]=='':
                            partdict["SampleName"]=filerawdata[item][15:-1]+"_"+partdict["Cellletter"]
                        else:
                            partdict["SampleName"]=filerawdata[item][15:-1]+"_"+filerawdata[item-1][19:-1]+"_"+partdict["Cellletter"]
                        partdict["DepID"]=filerawdata[item][15:-1]
                        partdict["DepID"]=partdict["DepID"].replace("-","_")
                        partdict["SampleName"]=partdict["SampleName"].replace("-","_")
                        break
                for item in range(len(filerawdata)):
                    if "IV measurement time:" in filerawdata[item]:
                        partdict["MeasDayTime"]=filerawdata[item][22:-1]
                        break
                for item in range(len(filerawdata)):
                    if "Cell size [m2]:" in filerawdata[item]:
                        partdict["CellSurface"]=float(filerawdata[item][17:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Voc [V]:" in filerawdata[item]:
                        partdict["Voc"]=float(filerawdata[item][19:-1])*1000
                        break            
                for item in range(len(filerawdata)):
                    if "Jsc [A/m2]:" in filerawdata[item]:
                        partdict["Jsc"]=float(filerawdata[item][19:-1])*0.1
                        break            
                for item in range(len(filerawdata)):
                    if "FF [.]:" in filerawdata[item]:
                        partdict["FF"]=float(filerawdata[item][18:-1])*100
                        break            
                for item in range(len(filerawdata)):
                    if "Efficiency [.]:" in filerawdata[item]:
                        partdict["Eff"]=float(filerawdata[item][19:-1])*100
                        break
                for item in range(len(filerawdata)):
                    if "Pmpp [W/m2]:" in filerawdata[item]:
                        partdict["Pmpp"]=float(filerawdata[item][19:-1])
                        break                
                for item in range(len(filerawdata)):
                    if "Vmpp [V]:" in filerawdata[item]:
                        partdict["Vmpp"]=float(filerawdata[item][10:-1])*1000
                        break                
                for item in range(len(filerawdata)):
                    if "Jmpp [A]:" in filerawdata[item]:
                        partdict["Jmpp"]=float(filerawdata[item][10:-1])*0.1
                        break   
                for item in range(len(filerawdata)):
                    if "Roc [Ohm.m2]:" in filerawdata[item]:
                        partdict["Roc"]=float(filerawdata[item][15:-1])*10000
                        break
                for item in range(len(filerawdata)):
                    if "Rsc [Ohm.m2]:" in filerawdata[item]:
                        partdict["Rsc"]=float(filerawdata[item][15:-1])*10000
                        break
                partdict["VocFF"]=float(partdict["Voc"])*float(partdict["FF"])*0.01
                partdict["RscJsc"]=float(partdict["Rsc"])*float(partdict["Jsc"])*0.001
                for item in range(len(filerawdata)):
                    if "Number of points:" in filerawdata[item]:
                        partdict["NbPoints"]=float(filerawdata[item][17:-1])
                        break
                for item in range(len(filerawdata)):
                    if "delay_iv (ms):" in filerawdata[item]:
                        partdict["Delay"]=float(filerawdata[item][15:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Integration time [s]:" in filerawdata[item]:
                        partdict["IntegTime"]=float(filerawdata[item][21:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Vstart" in filerawdata[item]:
                        partdict["Vstart"]=float(filerawdata[item][15:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Vstop" in filerawdata[item]:
                        partdict["Vend"]=float(filerawdata[item][14:-1])
                        break
                for item in range(len(filerawdata)):
                    if "Illumination:" in filerawdata[item]:
                        partdict["Illumination"]=filerawdata[item][14:-1]
                        break
#                for item in range(len(filerawdata)):
#                    if "reverse/forward?" in filerawdata[item]:
#                        partdict["ScanDirection"]=filerawdata[item][21:-1]
#                        break
#                if partdict["ScanDirection"] =="":
#                    print(partdict["filepath"])
#                    print(partdict["Vstart"])
#                print(partdict["filepath"])
#                except:
#                    print(partdict["filepath"])
                if abs(float(partdict["Vstart"]))>abs(float(partdict["Vend"])):
                    partdict["ScanDirection"]="Reverse"
                else:
                    partdict["ScanDirection"]="Forward"
#                for item in range(len(filerawdata)):
#                    if "Imax compliance [A]:" in filerawdata[item]:
                partdict["ImaxComp"]=999
#                        break
#                for item in range(len(filerawdata)):
#                    if "I sense range:" in filerawdata[item]:
                partdict["Isenserange"]=999
#                        break
                for item in range(len(filerawdata)):
                    if "User name:" in filerawdata[item]:
                        partdict["Operator"]=filerawdata[item][11:-1]
                        break
                for item in range(len(filerawdata)):
                    if "MEASURED IV DATA" in filerawdata[item]:
                            pos=item+2
                            break
                    elif "MEASURED IV FRLOOP DATA" in filerawdata[item]:
                            pos=item+2
                            break
                ivpartdat = [[],[]]#[voltage,current]
                for item in range(pos,len(filerawdata),1):
                    ivpartdat[0].append(float(filerawdata[item].split("\t")[2]))
                    ivpartdat[1].append(0.1*float(filerawdata[item].split("\t")[3][:-1]))
                partdict["IVData"]=ivpartdat
                
                partdict["Group"]="Default group"
                partdict["Setup"]="TFIV"              
                partdict["RefNomCurr"]=999
                partdict["RefMeasCurr"]=999
                partdict["AirTemp"]=999
                partdict["ChuckTemp"]=999
    
                #still missing: test for transposition, mirror
                try:
                    if partdict["Illumination"]=="Light" and max(ivpartdat[0])>0.001*float(partdict["Voc"]):
                        f = interp1d(ivpartdat[0], ivpartdat[1], kind='cubic')
                        x2 = lambda x: f(x)
                        partdict["AreaJV"] = integrate.quad(x2,0,0.001*float(partdict["Voc"]))[0]
                    else:
                        partdict["AreaJV"] =""
                except ValueError:
                    print("there is a ValueError on sample ",i)
                
                if partdict["Illumination"]=="Light":
                    DATA.append(partdict)
                else:
                    DATAdark.append(partdict)
                
            #self.bytes += self.bytestep
            #self.progress["value"] = self.bytes
        #change name of samples to have all different
        
        DATA = sorted(DATA, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATA if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATA)):
            DATA[item]['SampleName']=groupednames[item]
        
        DATAFV = sorted(DATAFV, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATAFV if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATAFV)):
            DATAFV[item]['SampleName']=groupednames[item]
        
        DATAMPP = sorted(DATAMPP, key=itemgetter('SampleName')) 
        names=[d["SampleName"] for d in DATAMPP if "SampleName" in d]
        groupednames=[list(j) for i, j in groupby(names)]
        for item in range(len(groupednames)):
            if len(groupednames[item])!=1:
                for item0 in range(1,len(groupednames[item]),1):
                    groupednames[item][item0]+= "_"+str(item0)
        groupednames=list(chain.from_iterable(groupednames))
        for item in range(len(DATAMPP)):
            DATAMPP[item]['SampleName']=groupednames[item]
        
        self.updategrouptoplotdropbutton()
        self.updateCompgrouptoplotdropbutton()
        self.updateHistgrouptoplotdropbutton()
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        
#%%######################################################################
        
    def GraphJVsave_as(self):
        global DATAJVforexport
        global DATAJVtabforexport
        try:
            if self.CheckIVLegend.get()==1:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.IVsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4),bbox_extra_artists=(self.leg,))#, transparent=True) 
            else:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.IVsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4))#, transparent=True) 

            DATAJVforexport1=[]
            for item in DATAJVforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAJVforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAJVforexport1)
            file.close()   
            
            DATAJVforexport1=[]
            for item in DATAJVtabforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAJVforexport1.append(line)
            file = open(str(f[:-4]+"_tab.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAJVforexport1)
            file.close()

        except:
            print("there is an exception")
        
        
    def GraphMPPsave_as(self):
        global DATAmppforexport
        try:
            if self.CheckmppLegend.get()==1:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.mppsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4),bbox_extra_artists=(self.leg,))#, transparent=True)
            else:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.mppsubfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4))#, transparent=True)
                
            DATAmppforexport1=[]            
            for item in DATAmppforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAmppforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAmppforexport1)
            file.close()
        
        except:
            print("there is an exception")    
    def GraphCompsave_as(self):
        global DATAcompforexport
        
        try:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
            extent = self.CompParamGroupfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
            self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(3, 1.4),bbox_extra_artists=(self.leg,))#, transparent=True)
                           
            DATAcompforexport1=[]            
            for item in DATAcompforexport:
                line=""
                for item1 in item:
                    line=line+str(item1)+"\t"
                line=line[:-1]+"\n"
                DATAcompforexport1.append(line)
                
            file = open(str(f[:-4]+"_dat.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAcompforexport1)
            file.close()
        
        except:
            print("there is an exception") 
        
    def GraphTimesave_as(self):
        global DATAtimeevolforexport
        try:
            if self.big4Timegraph.get()==0:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.TimeEvolfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=True)
                else:
                    self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=False)
                
                                
                for key in list(DATAtimeevolforexport.keys()):
                    DATAgroupforexport1=["realtimeF\trelativetimeF\tvalueF\tnormalizedvaluetot0F\trealtimeR\trelativetimeR\tvalueR\tnormalizedvaluetot0R\n"] 
                    templist=map(list, six.moves.zip_longest(*DATAtimeevolforexport[key], fillvalue=' '))
                    for item in templist:
                        line=""
                        for item1 in item:
                            line=line+str(item1)+"\t"
                        line=line[:-1]+"\n"
                        DATAgroupforexport1.append(line)
                    file = open(str(f[:-4]+"_"+self.TimeChoice.get()+'_'+str(key)+"_dat.txt"),'w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in DATAgroupforexport1)
                    file.close()
                
            elif self.big4Timegraph.get()==1:
                
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                self.TimeChoice.set("Eff")
                self.UpdateTimeGraph(1)
                extent = self.TimeEvolfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=False)
                    
                for key in list(DATAtimeevolforexport.keys()):
                    DATAgroupforexport1=["realtimeF\trelativetimeF\tvalueF\tnormalizedvaluetot0F\trealtimeR\trelativetimeR\tvalueR\tnormalizedvaluetot0R\n"] 
                    templist=map(list, six.moves.zip_longest(*DATAtimeevolforexport[key], fillvalue=' '))
                    for item in templist:
                        line=""
                        for item1 in item:
                            line=line+str(item1)+"\t"
                        line=line[:-1]+"\n"
                        DATAgroupforexport1.append(line)
                    file = open(str(f[:-4]+"_"+self.TimeChoice.get()+'_'+str(key)+"_dat.txt"),'w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in DATAgroupforexport1)
                    file.close()
                    
                self.TimeChoice.set("Voc")
                self.UpdateTimeGraph(1)
                
                extent = self.TimeEvolfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=False)
                
                for key in list(DATAtimeevolforexport.keys()):
                    DATAgroupforexport1=["realtimeF\trelativetimeF\tvalueF\tnormalizedvaluetot0F\trealtimeR\trelativetimeR\tvalueR\tnormalizedvaluetot0R\n"] 
                    templist=map(list, six.moves.zip_longest(*DATAtimeevolforexport[key], fillvalue=' '))
                    for item in templist:
                        line=""
                        for item1 in item:
                            line=line+str(item1)+"\t"
                        line=line[:-1]+"\n"
                        DATAgroupforexport1.append(line)
                    file = open(str(f[:-4]+"_"+self.TimeChoice.get()+'_'+str(key)+"_dat.txt"),'w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in DATAgroupforexport1)
                    file.close()
                self.TimeChoice.set("Jsc")
                self.UpdateTimeGraph(1)
                
                extent = self.TimeEvolfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=False)
                
                for key in list(DATAtimeevolforexport.keys()):
                    DATAgroupforexport1=["realtimeF\trelativetimeF\tvalueF\tnormalizedvaluetot0F\trealtimeR\trelativetimeR\tvalueR\tnormalizedvaluetot0R\n"] 
                    templist=map(list, six.moves.zip_longest(*DATAtimeevolforexport[key], fillvalue=' '))
                    for item in templist:
                        line=""
                        for item1 in item:
                            line=line+str(item1)+"\t"
                        line=line[:-1]+"\n"
                        DATAgroupforexport1.append(line)
                    file = open(str(f[:-4]+"_"+self.TimeChoice.get()+'_'+str(key)+"_dat.txt"),'w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in DATAgroupforexport1)
                    file.close()
                self.TimeChoice.set("FF")
                self.UpdateTimeGraph(1)
                
                extent = self.TimeEvolfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.TimeChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.8, 2), transparent=False)
                
                for key in list(DATAtimeevolforexport.keys()):
                    DATAgroupforexport1=["realtimeF\trelativetimeF\tvalueF\tnormalizedvaluetot0F\trealtimeR\trelativetimeR\tvalueR\tnormalizedvaluetot0R\n"] 
                    templist=map(list, six.moves.zip_longest(*DATAtimeevolforexport[key], fillvalue=' '))
                    for item in templist:
                        line=""
                        for item1 in item:
                            line=line+str(item1)+"\t"
                        line=line[:-1]+"\n"
                        DATAgroupforexport1.append(line)
                    file = open(str(f[:-4]+"_"+self.TimeChoice.get()+'_'+str(key)+"_dat.txt"),'w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in DATAgroupforexport1)
                    file.close()
                
#                images = list(map(ImageTk.open, [f[:-4]+"_Jsc"+f[-4:],f[:-4]+"_FF"+f[-4:],f[:-4]+"_Voc"+f[-4:],f[:-4]+"_Eff"+f[-4:]]))
#                widths, heights = zip(*(i.size for i in images))
#                total_width = max(widths[0]+widths[2],widths[1]+widths[3])
#                max_height = max(heights[0]+heights[1],heights[2]+heights[3])
#                new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
#                new_im.paste(im=images[0],box=(0,0))
#                new_im.paste(im=images[1],box=(0,max(heights[0],heights[2])))
#                new_im.paste(im=images[2],box=(max(widths[0],widths[1]),0))
#                new_im.paste(im=images[3],box=(max(widths[0],widths[1]),max(heights[0],heights[2])))
#                new_im.save(f[:-4]+"_big4"+f[-4:])
                
        except:
            print("there is an exception")  
        
    def GraphGroupsave_as(self):
        global DATAgroupforexport
        try:
            if self.Big4.get()==0:
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.5, 2), transparent=True)
                else:
                    self.fig.savefig(f, dpi=300, bbox_inches=extent.expanded(1.5, 2), transparent=False)
                    
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
            elif self.Big4.get()==1:
                
                f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
                self.GroupChoice.set("Eff")
                self.UpdateGroupGraph(1)
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=False)
                    
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
                self.GroupChoice.set("Voc")
                self.UpdateGroupGraph(1)
                
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=False)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
                self.GroupChoice.set("Jsc")
                self.UpdateGroupGraph(1)
                
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=False)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
                self.GroupChoice.set("FF")
                self.UpdateGroupGraph(1)
                
                extent = self.GroupStatfig.get_window_extent().transformed(self.fig.dpi_scale_trans.inverted())
                if self.transparentbkg.get():
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=True)
                else:
                    self.fig.savefig(f[:-4]+"_"+self.GroupChoice.get()+f[-4:], dpi=300, bbox_inches=extent.expanded(1.5, 1.5), transparent=False)
                
                DATAgroupforexport1=[]            
                for item in DATAgroupforexport:
                    line=""
                    for item1 in item:
                        line=line+str(item1)+"\t"
                    line=line[:-1]+"\n"
                    DATAgroupforexport1.append(line)
                
                file = open(str(f[:-4]+"_"+self.GroupChoice.get()+"dat.txt"),'w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in DATAgroupforexport1)
                file.close()
                
#                images = list(map(ImageTk.open, [f[:-4]+"_Jsc"+f[-4:],f[:-4]+"_FF"+f[-4:],f[:-4]+"_Voc"+f[-4:],f[:-4]+"_Eff"+f[-4:]]))
#                widths, heights = zip(*(i.size for i in images))
#                total_width = max(widths[0]+widths[2],widths[1]+widths[3])
#                max_height = max(heights[0]+heights[1],heights[2]+heights[3])
#                new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
#                new_im.paste(im=images[0],box=(0,0))
#                new_im.paste(im=images[1],box=(0,max(heights[0],heights[2])))
#                new_im.paste(im=images[2],box=(max(widths[0],widths[1]),0))
#                new_im.paste(im=images[3],box=(max(widths[0],widths[1]),max(heights[0],heights[2])))
#                new_im.save(f[:-4]+"_big4"+f[-4:])
                
        except:
            print("there is an exception")  
            
    def full_extent(ax, pad=0.0):
        """Get the full extent of an axes, including axes labels, tick labels, and
        titles."""
        # For text objects, we need to draw the figure first, otherwise the extents
        # are undefined.
        ax.figure.canvas.draw()
        items = ax.get_xticklabels() + ax.get_yticklabels() 
        #    items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
        items += [ax, ax.title]
        bbox = Bbox.union([item.get_window_extent() for item in items])

        return bbox.expanded(1.0 + pad, 1.0 + pad)      

#%%######################################################################

    def ExportAutoAnalysis(self):
        global DATA
        global DATAdark
        global DATAFV
        global DATAMPP
        global samplesgroups
           
        current_path = os.getcwd()
        folderName = filedialog.askdirectory(title = "choose a folder to export the auto-analysis results", initialdir=os.path.dirname(current_path))
        os.chdir(folderName)
        
        DATAx=copy.deepcopy(DATA)
        plt.close("all")
        sorted_datajv = sorted(DATAx, key=itemgetter('DepID')) 
        sorted_datampp = sorted(DATAMPP, key=itemgetter('DepID')) 
        sorted_datafv = sorted(DATAFV, key=itemgetter('DepID'))
        DATAbysubstrate=[] 
        DATAmppbysubstrate=[]
        DATAfvbysubstrate=[]
        DATAdarkbysubstrate=[] 
        bestEff=[]
        bestvocff =[]
        sorted_datadark = sorted(DATAdark, key=itemgetter('DepID'))
        try:
            batchname="P###"
            if "_" in DATAx[0]["DepID"]:
                batchname=DATAx[0]["DepID"].split("_")[0]
            elif "-" in DATAx[0]["DepID"]:
                batchname=DATAx[0]["DepID"].split("-")[0]
        except:
            print("there's an issue...")
        
        for key, group in groupby(sorted_datadark, key=lambda x:x['DepID']):
            substratpartdat=[key,list(group)]
            DATAdarkbysubstrate.append(copy.deepcopy(substratpartdat))
            try:
                if self.TxtforOrigin.get():
                    contenttxtfile=["","",""]
                    for item in range(len(substratpartdat[1])):
                        contenttxtfile[0] += "Voltage\t" + "Current density\t" 
                        contenttxtfile[1] += "mV\t" + "mA/cm2\t"
                        contenttxtfile[2] += " \t" + substratpartdat[1][item]["SampleName"] + '\t'
                    contenttxtfile[0]=contenttxtfile[0][:-1]+'\n'
                    contenttxtfile[1]=contenttxtfile[1][:-1]+'\n'
                    contenttxtfile[2]=contenttxtfile[2][:-1]+'\n'
                    #find max length of subjv lists => fill the others with blancks
                    lengthmax=max([len(substratpartdat[1][x]["IVData"][0]) for x in range(len(substratpartdat[1]))])
                    for item in range(len(substratpartdat[1])):
                        while (len(substratpartdat[1][item]["IVData"][0])<lengthmax):
                            substratpartdat[1][item]["IVData"][0].append('')   
                            substratpartdat[1][item]["IVData"][1].append('') 
                    #append them all in the content list
                    for item0 in range(lengthmax):
                        ligne=""
                        for item in range(len(substratpartdat[1])):
                            ligne += str(substratpartdat[1][item]["IVData"][0][item0]) +'\t' + str(substratpartdat[1][item]["IVData"][1][item0]) +'\t'   
                        ligne=ligne[:-1]+'\n'    
                        contenttxtfile.append(ligne)
                    #export it to txt files
                    file = open(str(substratpartdat[0]) + '_lowIllum.txt','w', encoding='ISO-8859-1')
                    file.writelines("%s" % item for item in contenttxtfile)
                    file.close()
            except:
                print("there's an issue with creating JVdark txt files")
            try:
                if self.IVgraphs.get():
                    plt.clf()
                    plt.close("all")
                    fig, axs =plt.subplots(1,2)
                    x1=min(DATAdarkbysubstrate[-1][1][0]["IVData"][0])
                    x2=max(DATAdarkbysubstrate[-1][1][0]["IVData"][0])
                    y1=min(DATAdarkbysubstrate[-1][1][0]["IVData"][1])
                    if max(DATAdarkbysubstrate[-1][1][0]["IVData"][1])<10:
                        y2=max(DATAdarkbysubstrate[-1][1][0]["IVData"][1])
                    else:
                        y2=10
                    for item in range(len(substratpartdat[1])):
                        axs[0].plot(DATAdarkbysubstrate[-1][1][item]["IVData"][0],DATAdarkbysubstrate[-1][1][item]["IVData"][1], label=DATAdarkbysubstrate[-1][1][item]["SampleName"])
                        if min(DATAdarkbysubstrate[-1][1][item]["IVData"][0])<x1:
                            x1=copy.deepcopy(min(DATAdarkbysubstrate[-1][1][item]["IVData"][0]))
                        if max(DATAdarkbysubstrate[-1][1][item]["IVData"][0])>x2:
                            x2=copy.deepcopy(max(DATAdarkbysubstrate[-1][1][item]["IVData"][0]))
                        if min(DATAdarkbysubstrate[-1][1][item]["IVData"][1])<y1:
                            y1=copy.deepcopy(min(DATAdarkbysubstrate[-1][1][item]["IVData"][1]))
                        if max(DATAdarkbysubstrate[-1][1][item]["IVData"][1])>y2 and max(DATAdarkbysubstrate[-1][1][item]["IVData"][1])<10:
                            y2=copy.deepcopy(max(DATAdarkbysubstrate[-1][1][item]["IVData"][1]))
                        slist=DATAdarkbysubstrate[-1][1][item]
                    axs[0].set_title("Low Illumination: "+str(substratpartdat[0]))
                    axs[0].set_xlabel('Voltage (mV)')
                    axs[0].set_ylabel('Current density (mA/cm'+'\xb2'+')')
                    axs[0].axhline(y=0, color='k')
                    axs[0].axvline(x=0, color='k')
                    axs[0].axis([x1,x2,y1,y2])
                    for item in range(len(substratpartdat[1])):
                        axs[1].semilogy(DATAdarkbysubstrate[-1][1][item]["IVData"][0],list(map(abs, DATAdarkbysubstrate[-1][1][item]["IVData"][1])), label=DATAdarkbysubstrate[-1][1][item]["SampleName"])
                    axs[1].set_title("logscale")
                    axs[1].set_xlabel('Voltage (mV)')
                    axs[1].axhline(y=0, color='k')
                    axs[1].axvline(x=0, color='k')
                    box = axs[0].get_position()
                    axs[0].set_position([box.x0, box.y0, box.width, box.height])
                    box = axs[1].get_position()
                    axs[1].set_position([box.x0, box.y0, box.width, box.height])
                    lgd=axs[1].legend(loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
                    #axs[1].legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.2)
                    plt.savefig(str(substratpartdat[0])+'_lowIllum.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                    plt.close(fig) 
                    plt.close('all')
                    plt.clf()
            except:
                print("there's an issue with creating JV lowillum graphs")
        plt.clf()
        #mpp data
        try:
            for key, group in groupby(sorted_datampp, key=lambda x:x['DepID']):
                substratpartdat=[key,list(group)]
                DATAmppbysubstrate.append(copy.deepcopy(substratpartdat))
                for item0 in range(len(substratpartdat[1])):
                    if self.TxtforOrigin.get():
                        contenttxtfile=["Voltage\tCurrent density\tTime\tPmpp\tTime\tVstep\n","V\tmA/cm2\ts\tW/m2\ts\tV\n"]
                        for item in range(len(substratpartdat[1][item0]["MppData"][0])):
                            contenttxtfile.append(str(substratpartdat[1][item0]["MppData"][0][item])+"\t"+str(substratpartdat[1][item0]["MppData"][1][item])+"\t"+str(substratpartdat[1][item0]["MppData"][2][item])+"\t"+str(substratpartdat[1][item0]["MppData"][3][item])+"\t"+str(substratpartdat[1][item0]["MppData"][2][item])+"\t"+str(substratpartdat[1][item0]["MppData"][4][item])+"\n")
                        #export to txt files
                        file = open(str(substratpartdat[1][item0]["SampleName"]) + '_Pmpp.txt','w', encoding='ISO-8859-1')
                        file.writelines("%s" % item for item in contenttxtfile)
                        file.close()
                    #export figures
                    if self.mppgraphs.get():
                        plt.plot(substratpartdat[1][item0]["MppData"][2],substratpartdat[1][item0]["MppData"][3])
                        plt.xlabel('Time (s)')
                        plt.ylabel('Power (mW/cm'+'\xb2'+')')        
                        plt.savefig(str(substratpartdat[1][item0]["SampleName"]) + '_Pmpp.png',dpi=300)
                    plt.close('all')
                    plt.clf()
        except:
            print("there's an issue with creating pmpp txt files")
        plt.clf()    
        try:     
            for key, group in groupby(sorted_datafv, key=lambda x:x['DepID']):
                substratpartdat=[key,list(group)]
                DATAfvbysubstrate.append(copy.deepcopy(substratpartdat))
                for item0 in range(len(substratpartdat[1])):
                    if self.TxtforOrigin.get():
                        contenttxtfile=["Time\tVoltage\tCurrent density\tPower\n","s\tV\tmA/cm2\tmW/cm2\n"]
                        for item in range(len(substratpartdat[1][item0]["FVData"][0])):
                            contenttxtfile.append(str(substratpartdat[1][item0]["FVData"][3][item])+"\t"+str(substratpartdat[1][item0]["FVData"][0][item])+"\t"+str(substratpartdat[1][item0]["FVData"][1][item])+"\t"+str(substratpartdat[1][item0]["FVData"][2][item])+"\n")
                        #export to txt files
                        file = open(str(substratpartdat[1][item0]["SampleName"]) + '_FV.txt','w', encoding='ISO-8859-1')
                        file.writelines("%s" % item for item in contenttxtfile)
                        file.close()
                    #export figures
                    if self.mppgraphs.get():
                        plt.plot(substratpartdat[1][item0]["FVData"][3],substratpartdat[1][item0]["FVData"][2])
                        plt.xlabel('Time (s)')
                        plt.ylabel('Power (mW/cm'+'\xb2'+')')        
                        plt.savefig(str(substratpartdat[1][item0]["SampleName"]) + '_FV.png',dpi=300)
                    plt.close('all')
                    plt.clf()
        except:
            print("there's an issue with creating FV txt files")
            
#        try:    
        for key, group in groupby(sorted_datajv, key=lambda x:x['DepID']):
            substratpartdat=[key,list(group)]
            DATAbysubstrate.append(copy.deepcopy(substratpartdat))
            if self.TxtforOrigin.get():
                contenttxtfile=["","",""]
                for item in range(len(substratpartdat[1])):
                    contenttxtfile[0] += "Voltage\t" + "Current density\t" 
                    contenttxtfile[1] += "mV\t" + "mA/cm2\t"
                    contenttxtfile[2] += " \t" + substratpartdat[1][item]["SampleName"] + '\t'
                contenttxtfile[0]=contenttxtfile[0][:-1]+'\n'
                contenttxtfile[1]=contenttxtfile[1][:-1]+'\n'
                contenttxtfile[2]=contenttxtfile[2][:-1]+'\n'
                #print(contenttxtfile)  
                #find max length of subjv lists => fill the others with blancks
                lengthmax=max([len(substratpartdat[1][x]["IVData"][0]) for x in range(len(substratpartdat[1]))])
                for item in range(len(substratpartdat[1])):
                    while (len(substratpartdat[1][item]["IVData"][0])<lengthmax):
                        substratpartdat[1][item]["IVData"][0].append('')   
                        substratpartdat[1][item]["IVData"][1].append('') 
                #append them all in the content list
                for item0 in range(lengthmax):
                    ligne=""
                    for item in range(len(substratpartdat[1])):
                        ligne += str(substratpartdat[1][item]["IVData"][0][item0]) +'\t' + str(substratpartdat[1][item]["IVData"][1][item0]) +'\t'   
                    ligne=ligne[:-1]+'\n'    
                    contenttxtfile.append(ligne)
                #export it to txt files
                file = open(str(substratpartdat[0]) + '.txt','w', encoding='ISO-8859-1')
                file.writelines("%s" % item for item in contenttxtfile)
                file.close()
            #graphs by substrate with JV table, separate graph and table production, then reassemble to export...
            plt.clf()
            if self.IVgraphs.get() or self.statGraphs.get() or self.mppgraphs.get():
                collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
                nrows, ncols = len(substratpartdat[1])+1, len(collabel)
                hcell, wcell = 0.3, 1.
                hpad, wpad = 0, 0 
                fig2=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
                ax2 = fig2.add_subplot(111)
                
                fig1=plt.figure()
                ax3 = fig1.add_subplot(111)
                
                x1=min(DATAbysubstrate[-1][1][0]["IVData"][0])
                x2=max(DATAbysubstrate[-1][1][0]["IVData"][0])
                y1=min(DATAbysubstrate[-1][1][0]["IVData"][1])
                if max(DATAbysubstrate[-1][1][0]["IVData"][1])<10:
                    y2=max(DATAbysubstrate[-1][1][0]["IVData"][1])
                else:
                    y2=10
                tabledata=[]
                rowlabel=[]
                for item in range(len(substratpartdat[1])):
                    ax3.plot(DATAbysubstrate[-1][1][item]["IVData"][0],DATAbysubstrate[-1][1][item]["IVData"][1], label=DATAbysubstrate[-1][1][item]["SampleName"])
                    if min(DATAbysubstrate[-1][1][item]["IVData"][0])<x1:
                        x1=copy.deepcopy(min(DATAbysubstrate[-1][1][item]["IVData"][0]))
                    if max(DATAbysubstrate[-1][1][item]["IVData"][0])>x2:
                        x2=copy.deepcopy(max(DATAbysubstrate[-1][1][item]["IVData"][0]))
                    if min(DATAbysubstrate[-1][1][item]["IVData"][1])<y1:
                        y1=copy.deepcopy(min(DATAbysubstrate[-1][1][item]["IVData"][1]))
                    if max(DATAbysubstrate[-1][1][item]["IVData"][1])>y2 and max(DATAbysubstrate[-1][1][item]["IVData"][1])<10:
                        y2=copy.deepcopy(max(DATAbysubstrate[-1][1][item]["IVData"][1]))
            
                    slist=DATAbysubstrate[-1][1][item]
                    rowlabel.append(slist["SampleName"])
                    tabledata.append(['%.f' % float(slist["Voc"]),'%.2f' % float(slist["Jsc"]),'%.2f' % float(slist["FF"]),'%.2f' % float(slist["Eff"]),'%.2f' % float(slist["Roc"]),'%.2f' % float(slist["Rsc"]),'%.2f' % float(slist["Vstart"]),'%.2f' % float(slist["Vend"]),'%.2f' % float(slist["CellSurface"])])
                
                ax3.set_title(str(substratpartdat[0]))
                ax3.set_xlabel('Voltage (mV)')
                ax3.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                ax3.axhline(y=0, color='k')
                ax3.axvline(x=0, color='k')
                ax3.axis([x1,x2,y1,y2])
                
                if self.IVgraphs.get():
                    rowlabel=tuple(rowlabel)
                    the_table = ax2.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
                    the_table.set_fontsize(18)
                    ax2.axis('off')
                    fig2.savefig(str(substratpartdat[0])+'_table.png',dpi=200,bbox_inches="tight")
                    handles, labels = ax3.get_legend_handles_labels()
                    lgd = ax3.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                    fig1.savefig(str(substratpartdat[0])+'.png',dpi=200, bbox_extra_artists=(lgd,),bbox_inches="tight")
                
                    images = list(map(ImageTk.open, [str(substratpartdat[0])+'.png',str(substratpartdat[0])+'_table.png']))
                    widths, heights = zip(*(i.size for i in images))
                    total_width = max(widths)
                    max_height = sum(heights)
                    new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                    new_im.paste(im=images[0],box=(0,0))
                    new_im.paste(im=images[1],box=(0,heights[0]))
                    new_im.save(str(substratpartdat[0])+'.png')
                    
                    os.remove(str(substratpartdat[0])+'_table.png')
                plt.close(fig2)
                plt.close(fig1)
                plt.close('all')
                plt.clf()
               
                if DATAx[0]["Setup"]=="TFIV"  or DATAx[0]["Setup"]=="SSIgorC215":
                    #graph best FR of this substrate
                    best = sorted(DATAbysubstrate[-1][1], key=itemgetter('VocFF'), reverse=True)
                    item=0
                    while item<len(best):
                        if float(best[item]["FF"])>10 and float(best[item]["Jsc"])<40:
                            bestvocff.append(copy.deepcopy(best[item]))
                            break
                        else:
                            item+=1
                    best = sorted(DATAbysubstrate[-1][1], key=itemgetter('Eff'), reverse=True)
                    item=0
                    while item<len(best):
                        if float(best[item]["FF"])>10 and float(best[item]["Jsc"])<40:
                            fig=plt.figure()
                            ax=fig.add_subplot(111)
                            bestEff.append(copy.deepcopy(best[item]))
                            if best[item]["ScanDirection"]=="Reverse":
                                ax.plot(best[item]["IVData"][0],best[item]["IVData"][1],"r", label=best[item]["SampleName"])
                                text = best[item]["ScanDirection"]+"; "+"Voc: " + '%.f' % float(best[item]["Voc"]) +" mV; " + "Jsc: " + '%.2f' % float(best[item]["Jsc"]) +" mA/cm2; " +"FF: " + '%.2f' % float(best[item]["FF"]) +" %; " +"Eff: " + '%.2f' % float(best[item]["Eff"]) +" %"
                                ax.set_title('Best:'+ best[item]["SampleName"]+"\n"+text, fontsize = 10, color="r")
                            elif best[item]["ScanDirection"]=="Forward":
                                ax.plot(best[item]["IVData"][0],best[item]["IVData"][1],"k", label=best[item]["SampleName"]) 
                                text = best[item]["ScanDirection"]+"; "+"Voc: " + '%.f' % float(best[item]["Voc"]) +" mV; " + "Jsc: " + '%.2f' % float(best[item]["Jsc"]) +" mA/cm2; " +"FF: " + '%.2f' % float(best[item]["FF"]) +" %; " +"Eff: " + '%.2f' % float(best[item]["Eff"]) +" %"
                                ax.set_title('Best:'+ best[item]["SampleName"]+"\n"+text, fontsize = 10, color="k")
                            pos=0
                            if best[item]["ScanDirection"]=="Reverse":
                                for item0 in range(item+1,len(best),1):
                                    if best[item0]["ScanDirection"]=="Forward" and best[item]["Cellletter"]==best[item0]["Cellletter"]:
                                        #other=best[item0]
                                        pos=item0
                                        ax.plot(best[pos]["IVData"][0],best[pos]["IVData"][1],"k", label=best[pos]["SampleName"])
                                        ax.set_title('Best:'+ best[item]["SampleName"]+"-"+best[pos]["SampleName"]+"\n"+text, fontsize = 10, color="r")
                                        break
                                
                            elif best[item]["ScanDirection"]=="Forward":
                                for item0 in range(item+1,len(best),1):
                                    if best[item0]["ScanDirection"]=="Reverse" and best[item]["Cellletter"]==best[item0]["Cellletter"]:
                                        #other=best[item0]
                                        pos=item0
                                        ax.plot(best[pos]["IVData"][0],best[pos]["IVData"][1],"r", label=best[pos]["SampleName"])
                                        ax.set_title('Best:'+ best[item]["SampleName"]+"-"+best[pos]["SampleName"]+"\n"+text, fontsize = 10, color="k")
                                        break
                            for item0 in range(len(DATAx)):
                                if DATAx[item0]["DepID"]==best[item]["DepID"] and DATAx[item0]["Cellletter"]==best[item]["Cellletter"] and DATAx[item0]["Illumination"]=="Dark":
                                    ax.plot(DATAx[item0]["IVData"][0],DATAx[item0]["IVData"][1],color='gray',linestyle='dashed', label=DATAx[item0]["SampleName"])
                                    break
                            
                            ax.set_xlabel('Voltage (mV)')
                            ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                            ax.axhline(y=0, color='k')
                            ax.axvline(x=0, color='k')
                            
                            x1=min(best[item]["IVData"][0][0],best[pos]["IVData"][0][0])
                            x2=max(best[item]["IVData"][0][-1],best[pos]["IVData"][0][-1])
                            y1=1.1*min(best[item]["IVData"][1]+best[pos]["IVData"][1])
                            if max(best[item]["IVData"][1]+best[pos]["IVData"][1])>10:
                                y2=10
                            else:
                                y2=max(best[item]["IVData"][1]+best[pos]["IVData"][1])
                            ax.axis([x1,x2,y1,y2])
                            if self.IVgraphs.get():
                                handles, labels = ax.get_legend_handles_labels()
                                lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                                fig.savefig(str(substratpartdat[0])+'_BestRevForw.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                            plt.close('all')
                            plt.clf()
                            break
                        else:
                            item+=1 
                plt.clf()
                #specific power graph
                if self.mppgraphs.get(): 
                    for item in range(len(DATAmppbysubstrate)):
                        if substratpartdat[0]==DATAmppbysubstrate[item][0]:
                            for item0 in range(len(DATAmppbysubstrate[item][1])):
                                fig=plt.figure()
                                ax=fig.add_subplot(111)
                                ax.plot([],[],label="Initial scans",color="White") 
                                checkaftermpp=1
                                for item1 in range(len(DATAbysubstrate[-1][1])):
                                    if DATAmppbysubstrate[item][1][item0]["Cellletter"]==DATAbysubstrate[-1][1][item1]["Cellletter"] and DATAbysubstrate[-1][1][item1]["Illumination"]=="Light":
                                        if DATAbysubstrate[-1][1][item1]["aftermpp"] and checkaftermpp:
                                            ax.plot([],[],label="After mpp",color="White") 
                                            checkaftermpp=0
                                            ax.plot(DATAbysubstrate[-1][1][item1]["IVData"][0],[-a*b for a,b in zip(DATAbysubstrate[-1][1][item1]["IVData"][0],DATAbysubstrate[-1][1][item1]["IVData"][1])],label=DATAbysubstrate[-1][1][item1]["SampleName"])   
                                        else:
                                            ax.plot(DATAbysubstrate[-1][1][item1]["IVData"][0],[-a*b for a,b in zip(DATAbysubstrate[-1][1][item1]["IVData"][0],DATAbysubstrate[-1][1][item1]["IVData"][1])],label=DATAbysubstrate[-1][1][item1]["SampleName"])
                                ax.plot([abs(a) for a in DATAmppbysubstrate[item][1][item0]["MppData"][0]],DATAmppbysubstrate[item][1][item0]["MppData"][3])
                                ax.set_xlabel('Voltage (mV)')
                                ax.set_ylabel('Specific power (mW/cm$^2$)')
                                ax.axhline(y=0, color='k')
                                ax.axvline(x=0, color='k')
                                ax.set_xlim(left=0)
                                ax.set_ylim(bottom=0)
                                ax.legend()
                                fig.savefig(DATAmppbysubstrate[item][1][item0]["SampleName"]+'_specpower.png',dpi=300,bbox_inches="tight")
                                plt.close("all")
                                plt.clf()
                            break
#        except:
#            print("there's an issue with creating JV graph files")     
        plt.close("all")
        plt.clf()
        if DATAx[0]["Setup"]=="TFIV" or DATAx[0]["Setup"]=="SSIgorC215":
#            try:        
            if self.statGraphs.get():
                #graph with all best efficient cells from all substrates
                fig=plt.figure()
                ax=fig.add_subplot(111)
                bestEff2=[item for item in bestEff if item["Illumination"]=="Light"]
                bestEffsorted = sorted(bestEff2, key=itemgetter('Eff'), reverse=True) 
                tabledata=[]
                rowlabel=[]
                minJscfind=[]
                maxcurrentfind=[]
                minVfind=[]
                maxVfind=[]
                for item in range(len(bestEffsorted)):
                    ax.plot(bestEffsorted[item]["IVData"][0],bestEffsorted[item]["IVData"][1], label=bestEffsorted[item]["SampleName"]) 
                    rowlabel.append(bestEffsorted[item]["SampleName"])
                    tabledata.append(['%.f' % float(bestEffsorted[item]["Voc"]),'%.2f' % float(bestEffsorted[item]["Jsc"]),'%.2f' % float(bestEffsorted[item]["FF"]),'%.2f' % float(bestEffsorted[item]["Eff"]),'%.2f' % float(bestEffsorted[item]["Roc"]),'%.2f' % float(bestEffsorted[item]["Rsc"]),'%.2f' % float(bestEffsorted[item]["Vstart"]),'%.2f' % float(bestEffsorted[item]["Vend"]),'%.2f' % float(bestEffsorted[item]["CellSurface"])])
                    minJscfind.append(min(bestEffsorted[item]["IVData"][1]))
                    maxcurrentfind.append(max(bestEffsorted[item]["IVData"][1]))
                    minVfind.append(min(bestEffsorted[item]["IVData"][0]))
                    maxVfind.append(max(bestEffsorted[item]["IVData"][0]))
                ax.set_xlabel('Voltage (mV)')
                ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                ax.axhline(y=0, color='k')
                ax.axvline(x=0, color='k')
                x1=min(minVfind)
                x2=max(maxVfind)
                y1=1.1*min(minJscfind)
                if max(maxcurrentfind)>10:
                    y2=10
                else:
                    y2=max(maxcurrentfind)
                ax.axis([x1,x2,y1,y2])
                handles, labels = ax.get_legend_handles_labels()
                lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                fig.savefig(batchname+'_MostEfficientCells.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                plt.close()
                collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
                nrows, ncols = len(bestEffsorted)+1, len(collabel)
                hcell, wcell = 0.3, 1.
                hpad, wpad = 0, 0 
                fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
                ax = fig.add_subplot(111)
                rowlabel=tuple(rowlabel)
                the_table = ax.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
                the_table.set_fontsize(18)
                ax.axis('off')
                fig.savefig('MostEfficientCellstable.png',dpi=300,bbox_inches="tight")
                plt.close("all")
                images = list(map(ImageTk.open, [batchname+'_MostEfficientCells.png','MostEfficientCellstable.png']))
                widths, heights = zip(*(i.size for i in images))
                total_width = max(widths)
                max_height = sum(heights)
                new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                new_im.paste(im=images[0],box=(0,0))
                new_im.paste(im=images[1],box=(0,heights[0]))
                new_im.save(batchname+'_MostEfficientCells.png')
                os.remove('MostEfficientCellstable.png')
                plt.close()
                plt.clf()
                #graph with all best voc*FF cells from all substrates  
                fig=plt.figure()
                ax=fig.add_subplot(111)
                bestvocff2=[item for item in bestvocff if item["Illumination"]=="Light"]
                bestvocffsorted = sorted(bestvocff2, key=itemgetter('VocFF'), reverse=True) 
                tabledata=[]
                rowlabel=[]
                minJscfind=[]
                maxcurrentfind=[]
                minVfind=[]
                maxVfind=[]
                for item in range(len(bestvocffsorted)):
                    x=bestvocffsorted[item]["IVData"][0]
                    y=bestvocffsorted[item]["IVData"][1]
                    ax.plot(x,y, label=bestvocffsorted[item]["SampleName"]) 
                    rowlabel.append(bestvocffsorted[item]["SampleName"])
                    tabledata.append(['%.f' % float(bestvocffsorted[item]["Voc"]),'%.2f' % float(bestvocffsorted[item]["Jsc"]),'%.2f' % float(bestvocffsorted[item]["FF"]),'%.2f' % float(bestvocffsorted[item]["Eff"]),'%.2f' % float(bestvocffsorted[item]["Roc"]),'%.2f' % float(bestvocffsorted[item]["Rsc"]),'%.2f' % float(bestvocffsorted[item]["Vstart"]),'%.2f' % float(bestvocffsorted[item]["Vend"]),'%.2f' % float(bestvocffsorted[item]["CellSurface"])])
                    minJscfind.append(min(bestvocffsorted[item]["IVData"][1]))
                    maxcurrentfind.append(max(bestvocffsorted[item]["IVData"][1]))
                    minVfind.append(min(bestvocffsorted[item]["IVData"][0]))
                    maxVfind.append(max(bestvocffsorted[item]["IVData"][0]))
                ax.set_xlabel('Voltage (mV)')
                ax.set_ylabel('Current density (mA/cm'+'\xb2'+')')
                ax.axhline(y=0, color='k')
                ax.axvline(x=0, color='k')
                x1=min(minVfind)
                x2=max(maxVfind)
                y1=1.1*min(minJscfind)
                if max(maxcurrentfind)>10:
                    y2=10
                else:
                    y2=max(maxcurrentfind)
                ax.axis([x1,x2,y1,y2])
                handles, labels = ax.get_legend_handles_labels()
                lgd = ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1, 0.5))
                fig.savefig(batchname+'_bestvocff.png',dpi=300, bbox_extra_artists=(lgd,),bbox_inches="tight")
                plt.close(fig)
                plt.clf()
                collabel=("Voc","Jsc","FF","Eff","Roc","Rsc","Vstart","Vend","CellSurface")
                nrows, ncols = len(bestvocffsorted)+1, len(collabel)
                hcell, wcell = 0.3, 1.
                hpad, wpad = 0, 0 
                fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad))
                ax = fig.add_subplot(111)
                rowlabel=tuple(rowlabel)
                the_table = ax.table(cellText=tabledata,colLabels=collabel,rowLabels=rowlabel,loc='center')
                the_table.set_fontsize(18)
                ax.axis('off')
                fig.savefig('bestvocfftable.png',dpi=300,bbox_inches="tight")
                plt.close(fig)
                plt.clf()
                images = list(map(ImageTk.open, [batchname+'_bestvocff.png','bestvocfftable.png']))
                widths, heights = zip(*(i.size for i in images))
                total_width = max(widths)
                max_height = sum(heights)
                new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                new_im.paste(im=images[0],box=(0,0))
                new_im.paste(im=images[1],box=(0,heights[0]))
                new_im.save(batchname+'_bestvocff.png')
                os.remove('bestvocfftable.png')
                plt.close("all")
                plt.clf()
#            except:
#                print("there's an issue with creating Bestof graphs")
        plt.clf()    
        plt.close("all")    
        if len(samplesgroups)>1:            
            grouplistdict=[]
            for item in range(len(samplesgroups)):
                groupdict={}
                groupdict["Group"]=samplesgroups[item]
                listofthegroup=[]
                listofthegroupNames=[]
                for item1 in range(len(DATAx)):
                    if DATAx[item1]["Group"]==groupdict["Group"] and DATAx[item1]["Illumination"]=="Light":
                        listofthegroup.append(DATAx[item1])
                        listofthegroupNames.append(DATAx[item1]['DepID']+'_'+DATAx[item1]['Cellletter'])
                groupdict["numbCell"]=len(list(set(listofthegroupNames)))
                listofthegroupRev=[]
                listofthegroupFor=[]
                for item1 in range(len(listofthegroup)):
                    if listofthegroup[item1]["ScanDirection"]=="Reverse":
                        listofthegroupRev.append(listofthegroup[item1])
                    else:
                        listofthegroupFor.append(listofthegroup[item1])
               
                groupdict["RevVoc"]=[x['Voc'] for x in listofthegroupRev if 'Voc' in x]
                groupdict["ForVoc"]=[x['Voc'] for x in listofthegroupFor if 'Voc' in x]
                groupdict["RevJsc"]=[x['Jsc'] for x in listofthegroupRev if 'Jsc' in x]
                groupdict["ForJsc"]=[x['Jsc'] for x in listofthegroupFor if 'Jsc' in x]
                groupdict["RevFF"]=[x['FF'] for x in listofthegroupRev if 'FF' in x]
                groupdict["ForFF"]=[x['FF'] for x in listofthegroupFor if 'FF' in x]
                groupdict["RevEff"]=[x['Eff'] for x in listofthegroupRev if 'Eff' in x]
                groupdict["ForEff"]=[x['Eff'] for x in listofthegroupFor if 'Eff' in x]
                
                grouplistdict.append(groupdict)
        
        plt.close("all")  
        plt.clf()
        #excel summary file with all data: tabs (rawdataLight, rawdatadark, besteff, bestvocff, pmpp, fixedvoltage)
        if self.CheckXlsxSum.get():   
            workbook = xlsxwriter.Workbook(batchname+'_Summary.xlsx')
            
            LandD=DATAx + DATAdark
            timeLandD =sorted(LandD, key=itemgetter('MeasDayTime')) 
            
            if len(samplesgroups)>1:
#                try:
                worksheet = workbook.add_worksheet("GroupStat")
                summary=[]
                for item in range(len(samplesgroups)):
                    ncell=1
                    if grouplistdict[item]["ForVoc"]!=[]:
                        lengthofgroup=len(grouplistdict[item]["ForVoc"])
                        summary.append([grouplistdict[item]["Group"],grouplistdict[item]["numbCell"],"Forward",lengthofgroup,sum(grouplistdict[item]["ForVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForVoc"]),sum(grouplistdict[item]["ForJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForJsc"]),sum(grouplistdict[item]["ForFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForFF"]),sum(grouplistdict[item]["ForEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["ForEff"])])
                        ncell=0
                    if grouplistdict[item]["RevVoc"]!=[]:  
                        if ncell==0:
                            lengthofgroup=len(grouplistdict[item]["RevVoc"])
                            summary.append([grouplistdict[item]["Group"]," ","Reverse",lengthofgroup,sum(grouplistdict[item]["RevVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevVoc"]),sum(grouplistdict[item]["RevJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevJsc"]),sum(grouplistdict[item]["RevFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevFF"]),sum(grouplistdict[item]["RevEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevEff"])])
                        else:
                            lengthofgroup=len(grouplistdict[item]["RevVoc"])
                            summary.append([grouplistdict[item]["Group"],grouplistdict[item]["numbCell"],"Reverse",lengthofgroup,sum(grouplistdict[item]["RevVoc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevVoc"]),sum(grouplistdict[item]["RevJsc"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevJsc"]),sum(grouplistdict[item]["RevFF"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevFF"]),sum(grouplistdict[item]["RevEff"],0.0)/lengthofgroup,np.std(grouplistdict[item]["RevEff"])])
    
                summary.insert(0, [" ", " "," ", "-", "mV","-","mA/cm2","-","%","-","%","-"])
                summary.insert(0, ["Group","#Cells","Scan Dir.","#ofmeas", "Voc"," ","Jsc"," ","FF"," ","Eff"," "])
                summary.insert(0, [" "," "," "," ", "Avg","StdDev","Avg","StdDev","Avg","StdDev","Avg","StdDev"])
                for item in range(len(summary)):
                    for item0 in range(len(summary[item])):
                        worksheet.write(item,item0, str(summary[item][item0]))
#                except:
#                    print("exception: excel summary - groupstat")
        
            if timeLandD!=[]:
                try:
                    worksheet = workbook.add_worksheet("AllJVrawdata")
                    summary=[]
                    for item in range(len(timeLandD)):
                        summary.append([timeLandD[item]["Group"],timeLandD[item]["SampleName"],timeLandD[item]["Cellletter"],timeLandD[item]["MeasDayTime"],timeLandD[item]["CellSurface"],str(timeLandD[item]["Voc"]),str(timeLandD[item]["Jsc"]),str(timeLandD[item]["FF"]),str(timeLandD[item]["Eff"]),str(timeLandD[item]["Pmpp"]),str(timeLandD[item]["Vmpp"]),str(timeLandD[item]["Jmpp"]),str(timeLandD[item]["Roc"]),str(timeLandD[item]["Rsc"]),str(timeLandD[item]["VocFF"]),str(timeLandD[item]["RscJsc"]),str(timeLandD[item]["NbPoints"]),timeLandD[item]["Delay"],timeLandD[item]["IntegTime"],timeLandD[item]["Vstart"],timeLandD[item]["Vend"],timeLandD[item]["Illumination"],timeLandD[item]["ScanDirection"],str('%.2f' % float(timeLandD[item]["ImaxComp"])),timeLandD[item]["Isenserange"],str(timeLandD[item]["AreaJV"]),timeLandD[item]["Operator"],timeLandD[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                except:
                    print("exception: excel summary - AllJVrawdata")
            
            if DATAx!=[]:
                try:
                    worksheet = workbook.add_worksheet("rawdataLight")
                    summary=[]
                    for item in range(len(DATAx)):
                        if DATAx[item]["Illumination"]=='Light':
                            summary.append([DATAx[item]["Group"],DATAx[item]["SampleName"],DATAx[item]["Cellletter"],DATAx[item]["MeasDayTime"],DATAx[item]["CellSurface"],str(DATAx[item]["Voc"]),str(DATAx[item]["Jsc"]),str(DATAx[item]["FF"]),str(DATAx[item]["Eff"]),str(DATAx[item]["Pmpp"]),str(DATAx[item]["Vmpp"]),str(DATAx[item]["Jmpp"]),str(DATAx[item]["Roc"]),str(DATAx[item]["Rsc"]),str(DATAx[item]["VocFF"]),str(DATAx[item]["RscJsc"]),str(DATAx[item]["NbPoints"]),str(DATAx[item]["Delay"]),str(DATAx[item]["IntegTime"]),str(DATAx[item]["Vstart"]),str(DATAx[item]["Vend"]),str(DATAx[item]["Illumination"]),str(DATAx[item]["ScanDirection"]),str('%.2f' % float(DATAx[item]["ImaxComp"])),str(DATAx[item]["Isenserange"]),str(DATAx[item]["AreaJV"]),DATAx[item]["Operator"],DATAx[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                    worksheet = workbook.add_worksheet("rawdatadark")
                    summary=[]
                    for item in range(len(DATAx)):
                        if DATAx[item]["Illumination"]=='Dark':
                            summary.append([DATAx[item]["Group"],DATAx[item]["SampleName"],DATAx[item]["Cellletter"],DATAx[item]["MeasDayTime"],DATAx[item]["CellSurface"],str(DATAx[item]["Voc"]),str(DATAx[item]["Jsc"]),str(DATAx[item]["FF"]),str(DATAx[item]["Eff"]),str(DATAx[item]["Pmpp"]),str(DATAx[item]["Vmpp"]),str(DATAx[item]["Jmpp"]),str(DATAx[item]["Roc"]),str(DATAx[item]["Rsc"]),str(DATAx[item]["VocFF"]),str(DATAx[item]["RscJsc"]),str(DATAx[item]["NbPoints"]),str(DATAx[item]["Delay"]),str(DATAx[item]["IntegTime"]),str(DATAx[item]["Vstart"]),str(DATAx[item]["Vend"]),str(DATAx[item]["Illumination"]),str(DATAx[item]["ScanDirection"]),str('%.2f' % float(DATAx[item]["ImaxComp"])),str(DATAx[item]["Isenserange"]),str(DATAx[item]["AreaJV"]),DATAx[item]["Operator"],DATAx[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                except:
                    print("exception: excel summary - rawdataLight")
#                if DATAdark!=[]:
#                    worksheet = workbook.add_worksheet("rawdatadark")
#                    summary=[]
#                    for item in range(len(DATAdark)):
#                        summary.append([DATAdark[item]["Group"],DATAdark[item]["SampleName"],DATAdark[item]["Cellletter"],DATAdark[item]["MeasDayTime"],DATAdark[item]["CellSurface"],str(DATAdark[item]["Voc"]),str(DATAdark[item]["Jsc"]),str(DATAdark[item]["FF"]),str(DATAdark[item]["Eff"]),str(DATAdark[item]["Pmpp"]),str(DATAdark[item]["Vmpp"]),str(DATAdark[item]["Jmpp"]),str(DATAdark[item]["Roc"]),str(DATAdark[item]["Rsc"]),str(DATAdark[item]["VocFF"]),str(DATAdark[item]["RscJsc"]),str(DATAdark[item]["NbPoints"]),DATAdark[item]["Delay"],DATAdark[item]["IntegTime"],DATAdark[item]["Vstart"],DATAdark[item]["Vend"],DATAdark[item]["Illumination"],DATAdark[item]["ScanDirection"],str('%.2f' % float(DATAdark[item]["ImaxComp"])),DATAdark[item]["Isenserange"],str(DATAdark[item]["AreaJV"]),DATAdark[item]["Operator"],DATAdark[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
#                    summary.insert(0, ["-", "-", "-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
#                    summary.insert(0, ["Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
#                    for item in range(len(summary)):
#                        for item0 in range(len(summary[item])):
#                            worksheet.write(item,item0,summary[item][item0])
                        
            sorted_bestEff= sorted(bestEff, key=itemgetter('Eff'), reverse=True) 
            if sorted_bestEff!=[]:  
                try:
                    worksheet = workbook.add_worksheet("besteff")
                    summary=[]
                    for item in range(len(sorted_bestEff)):
                        summary.append([sorted_bestEff[item]["Group"],sorted_bestEff[item]["SampleName"],sorted_bestEff[item]["Cellletter"],sorted_bestEff[item]["MeasDayTime"],sorted_bestEff[item]["CellSurface"],str(sorted_bestEff[item]["Voc"]),str(sorted_bestEff[item]["Jsc"]),str(sorted_bestEff[item]["FF"]),str(sorted_bestEff[item]["Eff"]),str(sorted_bestEff[item]["Pmpp"]),str(sorted_bestEff[item]["Vmpp"]),str(sorted_bestEff[item]["Jmpp"]),str(sorted_bestEff[item]["Roc"]),str(sorted_bestEff[item]["Rsc"]),str(sorted_bestEff[item]["VocFF"]),str(sorted_bestEff[item]["RscJsc"]),str(sorted_bestEff[item]["NbPoints"]),sorted_bestEff[item]["Delay"],sorted_bestEff[item]["IntegTime"],sorted_bestEff[item]["Vstart"],sorted_bestEff[item]["Vend"],sorted_bestEff[item]["Illumination"],sorted_bestEff[item]["ScanDirection"],str('%.2f' % float(sorted_bestEff[item]["ImaxComp"])),sorted_bestEff[item]["Isenserange"],str(sorted_bestEff[item]["AreaJV"]),sorted_bestEff[item]["Operator"],sorted_bestEff[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-", "-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                except:
                    print("exception: excel summary - besteff")
            sorted_bestvocff= sorted(bestvocff, key=itemgetter('VocFF'), reverse=True) 
            if sorted_bestvocff!=[]: 
                try:
                    worksheet = workbook.add_worksheet("bestvocff")
                    summary=[]
                    for item in range(len(sorted_bestvocff)):
                        summary.append([sorted_bestvocff[item]["Group"], sorted_bestvocff[item]["SampleName"],sorted_bestvocff[item]["Cellletter"],sorted_bestvocff[item]["MeasDayTime"],sorted_bestvocff[item]["CellSurface"],str(sorted_bestvocff[item]["Voc"]),str(sorted_bestvocff[item]["Jsc"]),str(sorted_bestvocff[item]["FF"]),str(sorted_bestvocff[item]["Eff"]),str(sorted_bestvocff[item]["Pmpp"]),str(sorted_bestvocff[item]["Vmpp"]),str(sorted_bestvocff[item]["Jmpp"]),str(sorted_bestvocff[item]["Roc"]),str(sorted_bestvocff[item]["Rsc"]),str(sorted_bestvocff[item]["VocFF"]),str(sorted_bestvocff[item]["RscJsc"]),str(sorted_bestvocff[item]["NbPoints"]),sorted_bestvocff[item]["Delay"],sorted_bestvocff[item]["IntegTime"],sorted_bestvocff[item]["Vstart"],sorted_bestvocff[item]["Vend"],sorted_bestvocff[item]["Illumination"],sorted_bestvocff[item]["ScanDirection"],str('%.2f' % float(sorted_bestvocff[item]["ImaxComp"])),sorted_bestvocff[item]["Isenserange"],str(sorted_bestvocff[item]["AreaJV"]),sorted_bestvocff[item]["Operator"],sorted_bestvocff[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                    summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                except:
                    print("exception: excel summary - bestvocff")
            
            if DATAMPP!=[]: 
                try:
                    worksheet = workbook.add_worksheet("Pmpp")
                    summary=[]
                    for item in range(len(DATAMPP)):
                        summary.append([DATAMPP[item]["Group"],DATAMPP[item]["SampleName"],DATAMPP[item]["Cellletter"],DATAMPP[item]["MeasDayTime"],float('%.2f' % float(DATAMPP[item]["CellSurface"])),DATAMPP[item]["Delay"],DATAMPP[item]["IntegTime"],float(DATAMPP[item]["Vstep"]),float(DATAMPP[item]["Vstart"]),float('%.1f' % float(DATAMPP[item]["MppData"][2][-1])),DATAMPP[item]["Operator"],DATAMPP[item]["MeasComment"]])
                    summary.insert(0, ["Group","Sample Name", "Cell","MeasDayTime","Cell Surface","Delay","IntegTime","Vstep","Vstart","ExecTime","Operator","MeasComment"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                except:
                    print("exception: excel summary - Pmpp")
            
            if DATAFV!=[]: 
                try:
                    worksheet = workbook.add_worksheet("fixedvoltage")
                    summary=[]
                    for item in range(len(DATAFV)):
                        summary.append([DATAFV[item]["Group"],DATAFV[item]["SampleName"],DATAFV[item]["Cellletter"],DATAFV[item]["MeasDayTime"],float('%.2f' % float(DATAFV[item]["CellSurface"])),DATAFV[item]["Delay"],DATAFV[item]["IntegTime"],DATAFV[item]["NbCycle"],float(DATAFV[item]["Vstep"]),float(DATAFV[item]["ExecTime"]),float(DATAFV[item]["TimeatZero"]),DATAFV[item]["Operator"],DATAFV[item]["MeasComment"]])
                    summary.insert(0, ["Group", "Sample Name", "Cell","MeasDayTime","Cell Surface","Delay","IntegTime","NbCycle","Initial voltage step", "Time at voltage bias", "Time at zero", "Operator","MeasComment"])
                    for item in range(len(summary)):
                        for item0 in range(len(summary[item])):
                            worksheet.write(item,item0,summary[item][item0])
                except:
                    print("exception: excel summary - fixedvoltage")
                    
            if LandD!=[]:   
                try:
                    sorted_dataall = sorted(LandD, key=itemgetter('DepID')) 
                    for key, group in groupby(sorted_dataall, key=lambda x:x['DepID']):
                        partdat=list(group)
                        worksheet = workbook.add_worksheet(key)
                        summary=[]
                        for item in range(len(partdat)):
                            summary.append([partdat[item]["Group"],partdat[item]["SampleName"],partdat[item]["Cellletter"],partdat[item]["MeasDayTime"],partdat[item]["CellSurface"],str(partdat[item]["Voc"]),str(partdat[item]["Jsc"]),str(partdat[item]["FF"]),str(partdat[item]["Eff"]),str(partdat[item]["Pmpp"]),str(partdat[item]["Vmpp"]),str(partdat[item]["Jmpp"]),str(partdat[item]["Roc"]),str(partdat[item]["Rsc"]),str(partdat[item]["VocFF"]),str(partdat[item]["RscJsc"]),str(partdat[item]["NbPoints"]),partdat[item]["Delay"],partdat[item]["IntegTime"],partdat[item]["Vstart"],partdat[item]["Vend"],partdat[item]["Illumination"],partdat[item]["ScanDirection"],str('%.2f' % float(partdat[item]["ImaxComp"])),partdat[item]["Isenserange"],str(partdat[item]["AreaJV"]),partdat[item]["Operator"],partdat[item]["MeasComment"],timeLandD[item]["RefNomCurr"],timeLandD[item]["RefMeasCurr"],str(timeLandD[item]["AirTemp"]),str(timeLandD[item]["ChuckTemp"])])
                        summary.insert(0, ["-", "-", "-","-","cm2","mV","mA/cm2","%","%","W/cm2","mV","mA/cm2","Ohm*cm2","Ohm*cm2","-","-","-","s","s","mV","mV","-","-","A","A","-","-","-","mA","mA","DegC","DegC"])
                        summary.insert(0, ["Group", "Sample Name", "Cell","MeasDayTime","Cell Surface","Voc","Jsc","FF","Eff","Pmpp","Vmpp","Jmpp","Roc","Rsc","VocFF","RscJsc","NbPoints","Delay","IntegTime","Vstart","Vend","Illumination","ScanDirection","ImaxComp","Isenserange","AreaJV","Operator","MeasComment","RefNomCurr","RefMeasCurr","AirTemp","ChuckTemp"])
                        for item in range(len(summary)):
                            for item0 in range(len(summary[item])):
                                worksheet.write(item,item0,summary[item][item0])
                except:
                    print("exception: excel summary - LandD")
                            
            workbook.close()
            
        plt.close("all")
        plt.clf()
        if DATAx[0]["Setup"]=="SSIgorC215":
            if self.statGraphs.get():
                fig = plt.figure()
                Effsubfig = fig.add_subplot(224)
                Vocsubfig = fig.add_subplot(221)
                Jscsubfig = fig.add_subplot(222)
                FFsubfig = fig.add_subplot(223)
                
                
                eff=[[],[],[],[],[],[]]
                for item in DATAx:
                    if item["Illumination"]=='Light':
                        if item["Cellletter"]=="A":
                            eff[0].append(item["Eff"])
                        elif item["Cellletter"]=="B":
                            eff[1].append(item["Eff"]) 
                        elif item["Cellletter"]=="C":
                            eff[2].append(item["Eff"]) 
                        elif item["Cellletter"]=="D":
                            eff[3].append(item["Eff"]) 
                        elif item["Cellletter"]=="E":
                            eff[4].append(item["Eff"]) 
                        elif item["Cellletter"]=="F":
                            eff[5].append(item["Eff"]) 
                names=["A","B","C","D","E","F"]
                for i in range(len(names)):
                    y=eff[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Effsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                span=range(1,len(names)+1)
                Effsubfig.set_xticks(span)
                Effsubfig.set_xticklabels(names)
                Effsubfig.set_xlim([0.5,span[-1]+0.5])
                Effsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-1,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+1])
                Effsubfig.set_ylabel('Efficiency (%)')
                
                eff=[[],[],[],[],[],[]]
                for item in DATAx:
                    if item["Illumination"]=='Light':
                        if item["Cellletter"]=="A":
                            eff[0].append(item["Voc"])
                        elif item["Cellletter"]=="B":
                            eff[1].append(item["Voc"]) 
                        elif item["Cellletter"]=="C":
                            eff[2].append(item["Voc"]) 
                        elif item["Cellletter"]=="D":
                            eff[3].append(item["Voc"]) 
                        elif item["Cellletter"]=="E":
                            eff[4].append(item["Voc"]) 
                        elif item["Cellletter"]=="F":
                            eff[5].append(item["Voc"]) 
    #            names=["A","B","C","D","E","F"]
                for i in range(len(names)):
                    y=eff[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Vocsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                span=range(1,len(names)+1)
                Vocsubfig.set_xticks(span)
                Vocsubfig.set_xticklabels(names)
                Vocsubfig.set_xlim([0.5,span[-1]+0.5])
                Vocsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-5,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+5])
                Vocsubfig.set_ylabel('Voc (mV)')
                
                eff=[[],[],[],[],[],[]]
                for item in DATAx:
                    if item["Illumination"]=='Light':
                        if item["Cellletter"]=="A":
                            eff[0].append(item["Jsc"])
                        elif item["Cellletter"]=="B":
                            eff[1].append(item["Jsc"]) 
                        elif item["Cellletter"]=="C":
                            eff[2].append(item["Jsc"]) 
                        elif item["Cellletter"]=="D":
                            eff[3].append(item["Jsc"]) 
                        elif item["Cellletter"]=="E":
                            eff[4].append(item["Jsc"]) 
                        elif item["Cellletter"]=="F":
                            eff[5].append(item["Jsc"]) 
    #            names=["A","B","C","D","E","F"]
                for i in range(len(names)):
                    y=eff[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Jscsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                span=range(1,len(names)+1)
                Jscsubfig.set_xticks(span)
                Jscsubfig.set_xticklabels(names)
                Jscsubfig.set_xlim([0.5,span[-1]+0.5])
                Jscsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-5,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+5])
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                
                eff=[[],[],[],[],[],[]]
                for item in DATAx:
                    if item["Illumination"]=='Light':
                        if item["Cellletter"]=="A":
                            eff[0].append(item["FF"])
                        elif item["Cellletter"]=="B":
                            eff[1].append(item["FF"]) 
                        elif item["Cellletter"]=="C":
                            eff[2].append(item["FF"]) 
                        elif item["Cellletter"]=="D":
                            eff[3].append(item["FF"]) 
                        elif item["Cellletter"]=="E":
                            eff[4].append(item["FF"]) 
                        elif item["Cellletter"]=="F":
                            eff[5].append(item["FF"]) 
    #            names=["A","B","C","D","E","F"]
                for i in range(len(names)):
                    y=eff[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        FFsubfig.scatter(x,y,s=15,color='red', alpha=0.5)
                span=range(1,len(names)+1)
                FFsubfig.set_xticks(span)
                FFsubfig.set_xticklabels(names)
                FFsubfig.set_xlim([0.5,span[-1]+0.5])
                FFsubfig.set_ylim([min([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])-5,max([*eff[0],*eff[1],*eff[2],*eff[3],*eff[4],*eff[5]])+5])
                FFsubfig.set_ylabel('FF (%)')
                
                
                fig.subplots_adjust(wspace=.25)
                fig.savefig(batchname+'_StatCells.png',dpi=300,bbox_inches="tight")
                
                plt.close("all")
                plt.clf()
            
        #stat graphs
        if self.statGraphs.get():
            #group
#            try:
            plt.close("all")
            plt.clf()
            if len(samplesgroups)>1:
                fig = plt.figure()
                Effsubfig = fig.add_subplot(224) 
                names=samplesgroups
                valsRev=[]
                for item in names:
                    valsRev.append([i["RevEff"] for i in grouplistdict if i["Group"]==item and "RevEff" in i])
                valsFor=[]
                for item in names:
                    valsFor.append([i["ForEff"] for i in grouplistdict if i["Group"]==item and "ForEff" in i])
                    
                valstot=[]
                Rev=[]
                Forw=[]
                namelist=[]
                for i in range(len(names)):
                    if valsRev[i][0]==[] and valsFor[i][0]==[]:
                        print(" ")
                    else:
                        Rev.append(valsRev[i][0])
                        Forw.append(valsFor[i][0])
                        valstot.append(valsRev[i][0]+valsFor[i][0])
                        namelist.append(names[i])
                
                Effsubfig.boxplot(valstot,0,'',labels=namelist)
                
                for i in range(len(namelist)):
                    y=Rev[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Effsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                    y=Forw[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Effsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                
                #Effsubfig.set_xlabel('Red=reverse; Blue=forward')
                
                Effsubfig.set_ylabel('Efficiency (%)')
                for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                             Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                
                Vocsubfig = fig.add_subplot(221) 
                names=samplesgroups
                valsRev=[]
                for item in names:
                    valsRev.append([i["RevVoc"] for i in grouplistdict if i["Group"]==item and "RevVoc" in i])
                valsFor=[]
                for item in names:
                    valsFor.append([i["ForVoc"] for i in grouplistdict if i["Group"]==item and "ForVoc" in i])
                    
                valstot=[]
                Rev=[]
                Forw=[]
                namelist=[]
                for i in range(len(names)):
                    if valsRev[i][0]==[] and valsFor[i][0]==[]:
                        print(" ")
                    else:
                        Rev.append(valsRev[i][0])
                        Forw.append(valsFor[i][0])
                        valstot.append(valsRev[i][0]+valsFor[i][0])
                        namelist.append(names[i])
                
                Vocsubfig.boxplot(valstot,0,'',labels=namelist)
                
                for i in range(len(namelist)):
                    y=Rev[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Vocsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                    y=Forw[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Vocsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                
                #Vocsubfig.set_xlabel('Red=reverse; Blue=forward')
                
                Vocsubfig.set_ylabel('Voc (mV)')
                for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                             Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                    
                Jscsubfig = fig.add_subplot(222) 
                names=samplesgroups
                valsRev=[]
                for item in names:
                    valsRev.append([i["RevJsc"] for i in grouplistdict if i["Group"]==item and "RevJsc" in i])
                valsFor=[]
                for item in names:
                    valsFor.append([i["ForJsc"] for i in grouplistdict if i["Group"]==item and "ForJsc" in i])
                    
                valstot=[]
                Rev=[]
                Forw=[]
                namelist=[]
                for i in range(len(names)):
                    if valsRev[i][0]==[] and valsFor[i][0]==[]:
                        print(" ")
                    else:
                        Rev.append(valsRev[i][0])
                        Forw.append(valsFor[i][0])
                        valstot.append(valsRev[i][0]+valsFor[i][0])
                        namelist.append(names[i])
                
                Jscsubfig.boxplot(valstot,0,'',labels=namelist)
                
                for i in range(len(namelist)):
                    y=Rev[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Jscsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                    y=Forw[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        Jscsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                
                #Jscsubfig.set_xlabel('Red=reverse; Blue=forward')
                
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                             Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                
                FFsubfig = fig.add_subplot(223) 
                names=samplesgroups
                valsRev=[]
                for item in names:
                    valsRev.append([i["RevFF"] for i in grouplistdict if i["Group"]==item and "RevFF" in i])
                valsFor=[]
                for item in names:
                    valsFor.append([i["ForFF"] for i in grouplistdict if i["Group"]==item and "ForFF" in i])
                    
                valstot=[]
                Rev=[]
                Forw=[]
                namelist=[]
                for i in range(len(names)):
                    if valsRev[i][0]==[] and valsFor[i][0]==[]:
                        print(" ")
                    else:
                        Rev.append(valsRev[i][0])
                        Forw.append(valsFor[i][0])
                        valstot.append(valsRev[i][0]+valsFor[i][0])
                        namelist.append(names[i])
                
                FFsubfig.boxplot(valstot,0,'',labels=namelist)
                
                for i in range(len(namelist)):
                    y=Rev[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        FFsubfig.scatter(x,y,s=5,color='red', alpha=0.5)
                    y=Forw[i]
                    if len(y)>0:
                        x=np.random.normal(i+1,0.04,size=len(y))
                        FFsubfig.scatter(x,y,s=5,color='blue', alpha=0.5)  
                
                #FFsubfig.set_xlabel('Red=reverse; Blue=forward')
                
                FFsubfig.set_ylabel('FF (%)')
                for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                             FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                    item.set_fontsize(4)
                    
                FFsubfig.annotate('Red=reverse; Blue=forward', xy=(1.3,-0.2), xycoords='axes fraction', fontsize=4,
                            horizontalalignment='right', verticalalignment='bottom')
                annotation="#ofCells: "
                for item in range(len(samplesgroups)):
                    if samplesgroups[item] in namelist:
                        annotation+=samplesgroups[item]+"=>"+str(grouplistdict[item]["numbCell"])+"; "
                FFsubfig.annotate(annotation, xy=(0,-0.3), xycoords='axes fraction', fontsize=4,
                            horizontalalignment='left', verticalalignment='bottom')
                
                fig.subplots_adjust(wspace=.25)
                fig.savefig(batchname+'_StatGroupgraph.png',dpi=300,bbox_inches="tight")
                
                
                
                plt.close("all")
            plt.clf()
#            except:
#                print("Exception: statgraphs - group")
            
            #time
            if DATAx[0]["Setup"]=="TFIV" or DATAx[0]["Setup"]=='SSIgorC215':
                try: 
                    if DATAx[0]["Setup"]=="TFIV":
                        time=[float(i["MeasDayTime"].split()[1].split(':')[0])+ float(i["MeasDayTime"].split()[1].split(':')[1])/60 + float(i["MeasDayTime"].split()[1].split(':')[2])/3600 for i in DATAx if i["Illumination"]=="Light"]
                    elif DATAx[0]["Setup"]=='SSIgorC215':
                        time=[]
                        for i in DATAx:
                            if i["Illumination"]=="Light":
                                if i["MeasDayTime"].split(' ')[-1]=='PM' and float(i["MeasDayTime"].split(' ')[-2].split(':')[0])!=12: 
                                    time.append(float(i["MeasDayTime"].split(' ')[-2].split(':')[0])+12+ float(i["MeasDayTime"].split(' ')[-2].split(':')[1])/60 + float(i["MeasDayTime"].split(' ')[-2].split(':')[2])/3600)
                                else:
                                    time.append(float(i["MeasDayTime"].split(' ')[-2].split(':')[0])+ float(i["MeasDayTime"].split(' ')[-2].split(':')[1])/60 + float(i["MeasDayTime"].split(' ')[-2].split(':')[2])/3600)
                                           
                    Voct=[i["Voc"] for i in DATAx if i["Illumination"]=="Light"]
                    Jsct=[i["Jsc"] for i in DATAx if i["Illumination"]=="Light"]
                    FFt=[i["FF"] for i in DATAx if i["Illumination"]=="Light"]
                    Efft=[i["Eff"] for i in DATAx if i["Illumination"]=="Light"]
                    
                    fig = plt.figure()
                    Vocsubfig = fig.add_subplot(221) 
                    Vocsubfig.scatter(time, Voct, s=5, c='k', alpha=0.5)
                    Vocsubfig.set_ylabel('Voc (mV)')
                    for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                                 Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    Jscsubfig = fig.add_subplot(222) 
                    Jscsubfig.scatter(time, Jsct, s=5, c='k', alpha=0.5)
                    Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                    for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                                 Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    FFsubfig = fig.add_subplot(223) 
                    FFsubfig.scatter(time, FFt, s=5, c='k', alpha=0.5)
                    FFsubfig.set_xlabel('Time')
                    FFsubfig.set_ylabel('FF (%)')
                    for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                                 FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    Effsubfig = fig.add_subplot(224) 
                    Effsubfig.scatter(time, Efft, s=5, c='k', alpha=0.5)
                    Effsubfig.set_xlabel('Time')
                    Effsubfig.set_ylabel('Eff (%)')
                    for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                                 Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                        item.set_fontsize(8)
                    plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                    Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    fig.subplots_adjust(wspace=.25)
                    fig.savefig(batchname+'_StatTimegraph.png',dpi=300,bbox_inches="tight")
                    plt.close("all")
                except:
                    print("Exception: statgraph - time")
            plt.clf()
            
            #Resistances
            try:
                Rsclist=[float(i["Rsc"]) for i in DATAx]
                Roclist=[float(i["Roc"]) for i in DATAx]
                Voct=[i["Voc"] for i in DATAx]
                Jsct=[i["Jsc"] for i in DATAx]
                FFt=[i["FF"] for i in DATAx]
                Efft=[i["Eff"] for i in DATAx]
                
                
                fig = plt.figure()
                Vocsubfig = fig.add_subplot(221) 
                Vocsubfig.scatter(Rsclist, Voct, s=5, c='k', alpha=0.5)
                Vocsubfig.set_ylabel('Voc (mV)')
                for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                             Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Vocsubfig.set_xlim(left=0)
                Vocsubfig.set_ylim(bottom=0)
                Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                
                Jscsubfig = fig.add_subplot(222) 
                Jscsubfig.scatter(Rsclist, Jsct, s=5, c='k', alpha=0.5)
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                             Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Jscsubfig.set_xlim(left=0)
                Jscsubfig.set_ylim(bottom=0)
                Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                FFsubfig = fig.add_subplot(223) 
                FFsubfig.scatter(Rsclist, FFt, s=5, c='k', alpha=0.5)
                FFsubfig.set_xlabel('Rsc')
                FFsubfig.set_ylabel('FF (%)')
                for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                             FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                FFsubfig.set_xlim(left=0)
                FFsubfig.set_ylim(bottom=0)
                FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Effsubfig = fig.add_subplot(224) 
                Effsubfig.scatter(Rsclist, Efft, s=5, c='k', alpha=0.5)
                Effsubfig.set_xlabel('Rsc')
                Effsubfig.set_ylabel('Eff (%)')
                for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                             Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Effsubfig.set_xlim(left=0)
                Effsubfig.set_ylim(bottom=0)
                Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                fig.subplots_adjust(wspace=.3)
                fig.savefig(batchname+'_StatRscgraph.png',dpi=300,bbox_inches="tight")
                plt.close("all")
                
                
                fig = plt.figure()
                Vocsubfig = fig.add_subplot(221) 
                Vocsubfig.scatter(Roclist, Voct, s=5, c='k', alpha=0.5)
                Vocsubfig.set_ylabel('Voc (mV)')
                for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] +
                             Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Vocsubfig.set_xlim(left=0)
                Vocsubfig.set_ylim(bottom=0)
                Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Jscsubfig = fig.add_subplot(222) 
                Jscsubfig.scatter(Roclist, Jsct, s=5, c='k', alpha=0.5)
                Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                             Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Jscsubfig.set_xlim(left=0)
                Jscsubfig.set_ylim(bottom=0)
                Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                FFsubfig = fig.add_subplot(223) 
                FFsubfig.scatter(Roclist, FFt, s=5, c='k', alpha=0.5)
                FFsubfig.set_xlabel('Roc')
                FFsubfig.set_ylabel('FF (%)')
                for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                             FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                FFsubfig.set_xlim(left=0)
                FFsubfig.set_ylim(bottom=0)
                FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                Effsubfig = fig.add_subplot(224) 
                Effsubfig.scatter(Roclist, Efft, s=5, c='k', alpha=0.5)
                Effsubfig.set_xlabel('Roc')
                Effsubfig.set_ylabel('Eff (%)')
                for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                             Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                    item.set_fontsize(8)
                #plt.xticks(np.arange(min(time), max(time)+1, 1.0))
                Effsubfig.set_xlim(left=0)
                Effsubfig.set_ylim(bottom=0)
                Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                
                fig.subplots_adjust(wspace=.3)
                fig.savefig(batchname+'_StatRocgraph.png',dpi=300,bbox_inches="tight")
                plt.close("all")
                plt.clf()
            except:
                print("Exception: statgraph - resistance")
            
            #stat graph with diff colors for ABC and Forw Rev, by substrate
            #get substrate number without run number
            if DATAx[0]["Setup"]=="TFIV" or DATAx[0]["Setup"]=='SSIgorC215':
                try:
                    fig = plt.figure()
                    
                    VocAFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    VocAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    VocBFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    VocBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    VocCFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    VocCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    VocDFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    VocDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    VocEFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    VocEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    VocFFy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    VocFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    VocARy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    VocARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    VocBRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    VocBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    VocCRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    VocCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    VocDRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    VocDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    VocERy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    VocERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    VocFRy=[float(i["Voc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    VocFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    Vocsubfig = fig.add_subplot(221) 
                    Vocsubfig.scatter(VocAFx, VocAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                    Vocsubfig.scatter(VocBFx, VocBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                    Vocsubfig.scatter(VocCFx, VocCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                    Vocsubfig.scatter(VocARx, VocARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                    Vocsubfig.scatter(VocBRx, VocBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                    Vocsubfig.scatter(VocCRx, VocCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                    Vocsubfig.scatter(VocDFx, VocDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                    Vocsubfig.scatter(VocEFx, VocEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                    Vocsubfig.scatter(VocFFx, VocFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                    Vocsubfig.scatter(VocDRx, VocDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                    Vocsubfig.scatter(VocERx, VocERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                    Vocsubfig.scatter(VocFRx, VocFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                    
#                    Vocsubfig.scatter(VocSFx, VocSFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
#                    Vocsubfig.scatter(VocSRx, VocSRy, s=5, edgecolors='k', lw=0.5)
                    Vocsubfig.set_ylabel('Voc (mV)')
                    Vocsubfig.set_xlabel("Sample #")
                    for item in ([Vocsubfig.title, Vocsubfig.xaxis.label, Vocsubfig.yaxis.label] + Vocsubfig.get_xticklabels() + Vocsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                    Vocsubfig.set_ylim(bottom=0)
                    Vocsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    Vocsubfig.set_xticks(np.arange(float(min(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))-0.5,float(max(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))+0.5,1), minor=True)
                    #Vocsubfig.set_xticks(np.arange(float(min(VocAFx))-0.5,float(max(VocAFx))+0.5,1), minor=True)
                    Vocsubfig.xaxis.grid(False, which='major')
                    Vocsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                    
                    Vocsubfig.axis([float(min(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))-0.5,float(max(VocAFx+VocBFx+VocCFx+VocARx+VocBRx+VocCRx+VocDFx+VocEFx+VocFFx+VocDRx+VocERx+VocFRx))+0.5,0.5*float(min(VocAFy+VocBFy+VocCFy+VocARy+VocBRy+VocCRy+VocDFy+VocEFy+VocFFy+VocDRy+VocERy+VocFRy)),1.1*float(max(VocAFy+VocBFy+VocCFy+VocARy+VocBRy+VocCRy+VocDFy+VocEFy+VocFFy+VocDRy+VocERy+VocFRy))])
                    for axis in ['top','bottom','left','right']:
                      Vocsubfig.spines[axis].set_linewidth(0.5)
                    Vocsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                    
                    
                    
                    JscAFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    JscAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    JscBFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    JscBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    JscCFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    JscCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    JscARy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    JscARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    JscBRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    JscBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    JscCRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    JscCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]

                    JscDFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    JscDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    JscEFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    JscEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    JscFFy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    JscFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    JscDRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    JscDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    JscERy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    JscERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    JscFRy=[float(i["Jsc"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    JscFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]                    
                    
                    Jscsubfig = fig.add_subplot(222) 
                    Jscsubfig.scatter(JscAFx, JscAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                    Jscsubfig.scatter(JscBFx, JscBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                    Jscsubfig.scatter(JscCFx, JscCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                    Jscsubfig.scatter(JscARx, JscARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                    Jscsubfig.scatter(JscBRx, JscBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                    Jscsubfig.scatter(JscCRx, JscCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                    Jscsubfig.scatter(JscDFx, JscDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                    Jscsubfig.scatter(JscEFx, JscEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                    Jscsubfig.scatter(JscFFx, JscFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                    Jscsubfig.scatter(JscDRx, JscDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                    Jscsubfig.scatter(JscERx, JscERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                    Jscsubfig.scatter(JscFRx, JscFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                    
                    Jscsubfig.set_ylabel('Jsc (mA/cm'+'\xb2'+')')
                    Jscsubfig.set_xlabel("Sample #")
                    for item in ([Jscsubfig.title, Jscsubfig.xaxis.label, Jscsubfig.yaxis.label] +
                                 Jscsubfig.get_xticklabels() + Jscsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                    Jscsubfig.set_ylim(bottom=0)
                    Jscsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    Jscsubfig.set_xticks(np.arange(float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))+0.5,1), minor=True)
                    #Jscsubfig.set_xticks(np.arange(float(min(JscAFx))-0.5,float(max(JscAFx))+0.5,1), minor=True)
                    Jscsubfig.xaxis.grid(False, which='major')
                    Jscsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                    
                    Jscsubfig.axis([float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))+0.5,0.5*float(min(JscAFy+JscBFy+JscCFy+JscARy+JscBRy+JscCRy+JscDFy+JscEFy+JscFFy+JscDRy+JscERy+JscFRy)),1.1*float(max(JscAFy+JscBFy+JscCFy+JscARy+JscBRy+JscCRy+JscDFy+JscEFy+JscFFy+JscDRy+JscERy+JscFRy))])
#                    print([float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))-0.5,float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))+0.5,0.5*float(min(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx)),1.1*float(max(JscAFx+JscBFx+JscCFx+JscARx+JscBRx+JscCRx+JscDFx+JscEFx+JscFFx+JscDRx+JscERx+JscFRx))])
                    for axis in ['top','bottom','left','right']:
                      Jscsubfig.spines[axis].set_linewidth(0.5)
                    Jscsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                    
                    
                    FFAFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    FFAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    FFBFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    FFBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    FFCFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    FFCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    FFARy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    FFARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    FFBRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    FFBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    FFCRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    FFCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]

                    FFDFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    FFDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    FFEFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    FFEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    FFFFy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    FFFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    FFDRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    FFDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    FFERy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    FFERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    FFFRy=[float(i["FF"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    FFFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]                    
                    
                    FFsubfig = fig.add_subplot(223) 
                    FFsubfig.scatter(FFAFx, FFAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                    FFsubfig.scatter(FFBFx, FFBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                    FFsubfig.scatter(FFCFx, FFCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                    FFsubfig.scatter(FFARx, FFARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                    FFsubfig.scatter(FFBRx, FFBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                    FFsubfig.scatter(FFCRx, FFCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                    FFsubfig.scatter(FFDFx, FFDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                    FFsubfig.scatter(FFEFx, FFEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                    FFsubfig.scatter(FFFFx, FFFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                    FFsubfig.scatter(FFDRx, FFDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                    FFsubfig.scatter(FFERx, FFERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                    FFsubfig.scatter(FFFRx, FFFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                    
                    FFsubfig.set_ylabel('FF (%)')
                    FFsubfig.set_xlabel("Sample #")
                    for item in ([FFsubfig.title, FFsubfig.xaxis.label, FFsubfig.yaxis.label] +
                                 FFsubfig.get_xticklabels() + FFsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                    FFsubfig.set_ylim(bottom=0)
                    FFsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    FFsubfig.set_xticks(np.arange(float(min(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))-0.5,float(max(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))+0.5,1), minor=True)
                    #FFsubfig.set_xticks(np.arange(float(min(FFAFx))-0.5,float(max(FFAFx))+0.5,1), minor=True)
                    FFsubfig.xaxis.grid(False, which='major')
                    FFsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                    
                    FFsubfig.axis([float(min(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))-0.5,float(max(FFAFx+FFBFx+FFCFx+FFARx+FFBRx+FFCRx+FFDFx+FFEFx+FFFFx+FFDRx+FFERx+FFFRx))+0.5,0.5*float(min(FFAFy+FFBFy+FFCFy+FFARy+FFBRy+FFCRy+FFDFy+FFEFy+FFFFy+FFDRy+FFERy+FFFRy)),1.1*float(max(FFAFy+FFBFy+FFCFy+FFARy+FFBRy+FFCRy+FFDFy+FFEFy+FFFFy+FFDRy+FFERy+FFFRy))])
                    for axis in ['top','bottom','left','right']:
                      FFsubfig.spines[axis].set_linewidth(0.5)
                    FFsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                    
                    
                    EffAFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    EffAFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    EffBFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    EffBFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    EffCFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    EffCFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    EffARy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    EffARx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='A' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    EffBRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    EffBRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='B' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    EffCRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    EffCRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='C' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    EffDFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    EffDFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    EffEFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    EffEFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    EffFFy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    EffFFx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Forward" and i["Illumination"]=="Light"]
                    
                    EffDRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    EffDRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='D' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    EffERy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    EffERx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='E' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    EffFRy=[float(i["Eff"]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    EffFRx=[int(i["DepID"].split('_')[1]) for i in DATAx if i["Cellletter"]=='F' and i["ScanDirection"]=="Reverse" and i["Illumination"]=="Light"]
                    
                    Effsubfig = fig.add_subplot(224) 
                    Effsubfig.scatter(EffAFx, EffAFy, s=5, facecolors='none', edgecolors='r', lw=0.5)
                    Effsubfig.scatter(EffBFx, EffBFy, s=5, facecolors='none', edgecolors='g', lw=0.5)
                    Effsubfig.scatter(EffCFx, EffCFy, s=5, facecolors='none', edgecolors='b', lw=0.5)
                    Effsubfig.scatter(EffARx, EffARy, s=5, facecolors='r', edgecolors='r', lw=0.5)
                    Effsubfig.scatter(EffBRx, EffBRy, s=5, facecolors='g', edgecolors='g', lw=0.5)
                    Effsubfig.scatter(EffCRx, EffCRy, s=5, facecolors='b', edgecolors='b', lw=0.5)
                    Effsubfig.scatter(EffDFx, EffDFy, s=5, facecolors='none', edgecolors='c', lw=0.5)
                    Effsubfig.scatter(EffEFx, EffEFy, s=5, facecolors='none', edgecolors='m', lw=0.5)
                    Effsubfig.scatter(EffFFx, EffFFy, s=5, facecolors='none', edgecolors='k', lw=0.5)
                    Effsubfig.scatter(EffDRx, EffDRy, s=5, facecolors='c', edgecolors='c', lw=0.5)
                    Effsubfig.scatter(EffERx, EffERy, s=5, facecolors='m', edgecolors='m', lw=0.5)
                    Effsubfig.scatter(EffFRx, EffFRy, s=5, facecolors='k', edgecolors='k', lw=0.5)
                    Effsubfig.set_ylabel('Eff (%)')
                    Effsubfig.set_xlabel("Sample #")
                    for item in ([Effsubfig.title, Effsubfig.xaxis.label, Effsubfig.yaxis.label] +
                                 Effsubfig.get_xticklabels() + Effsubfig.get_yticklabels()):
                        item.set_fontsize(4)
                    Effsubfig.set_ylim(bottom=0)
                    Effsubfig.xaxis.set_major_locator(MaxNLocator(integer=True))
                    
                    Effsubfig.set_xticks(np.arange(float(min(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))-0.5,float(max(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))+0.5,1), minor=True)
                    Effsubfig.xaxis.grid(False, which='major')
                    Effsubfig.xaxis.grid(True, which='minor', color='k', linestyle='-', alpha=0.2)
                    
                    Effsubfig.axis([float(min(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))-0.5,float(max(EffAFx+EffBFx+EffCFx+EffARx+EffBRx+EffCRx+EffDFx+EffEFx+EffFFx+EffDRx+EffERx+EffFRx))+0.5,0.5*float(min(EffAFy+EffBFy+EffCFy+EffARy+EffBRy+EffCRy+EffDFy+EffEFy+EffFFy+EffDRy+EffERy+EffFRy)),1.1*float(max(EffAFy+EffBFy+EffCFy+EffARy+EffBRy+EffCRy+EffDFy+EffEFy+EffFFy+EffDRy+EffERy+EffFRy))])
                    for axis in ['top','bottom','left','right']:
                      Effsubfig.spines[axis].set_linewidth(0.5)
                    Effsubfig.tick_params(axis='x', which='both',bottom='off', top='off')
                    
                    
                    FFsubfig.annotate('Red=A; Green=B; Blue=C; Cyan=D; Magenta=E; Black=F; empty=Forward; full=Reverse;', xy=(1.55,-0.3), xycoords='axes fraction', fontsize=4,
                                    horizontalalignment='right', verticalalignment='bottom')
                    
                    fig.savefig(batchname+'_StatJVgraph.png',dpi=300,bbox_inches="tight")
                    plt.close("all")
                    plt.clf()
                except:
                    print("Exception: statgraph - bysubstrate")
                    
        plt.close("all")
        plt.clf()
        
        if self.statGraphs.get():
            try:
                images = list(map(ImageTk.open, [batchname+'_StatCells.png',batchname+'_StatTimegraph.png',batchname+'_StatJVgraph.png',batchname+'_StatGroupgraph.png']))
                widths, heights = zip(*(i.size for i in images))
                total_width = max(widths[0]+widths[2],widths[1]+widths[3])
                max_height = max(heights[0]+heights[1],heights[2]+heights[3])
                new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                new_im.paste(im=images[0],box=(0,0))
                new_im.paste(im=images[1],box=(0,max(heights[0],heights[2])))
                new_im.paste(im=images[2],box=(max(widths[0],widths[1]),0))
                new_im.paste(im=images[3],box=(max(widths[0],widths[1]),max(heights[0],heights[2])))
                new_im.save(batchname+'_controls.png')
            except:
                images = list(map(ImageTk.open, [batchname+'_StatCells.png',batchname+'_StatTimegraph.png',batchname+'_StatJVgraph.png']))
                widths, heights = zip(*(i.size for i in images))
                total_width = max(widths[0]+widths[2],2*widths[1])
                max_height = max(heights[0]+heights[1],2*heights[2])
                new_im = ImageTk.new('RGB', (total_width, max_height), (255, 255, 255))
                new_im.paste(im=images[0],box=(0,0))
                new_im.paste(im=images[1],box=(0,max(heights[0],heights[2])))
                new_im.paste(im=images[2],box=(max(widths[0],widths[1]),0))
                new_im.save(batchname+'_controls.png')
                
        
        self.window.destroy()
        self.destroy()
        self.__init__()
        
        if DATAx!=[]:          
            self.UpdateIVGraph()
        
        if DATAMPP!=[]:
#            print("il y a des mpp")
            self.mppnames = ()
            self.mppnames=self.SampleMppNames(DATAMPP)
            self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
            self.mppmenubutton.configure(menu=self.mppmenu)
            self.choicesmpp = {}
            for choice in range(len(self.mppnames)):
                self.choicesmpp[choice] = tk.IntVar(value=0)
                self.mppmenu.add_checkbutton(label=self.mppnames[choice], variable=self.choicesmpp[choice], 
                                     onvalue=1, offvalue=0, command = self.UpdateMppGraph0)
            self.UpdateMppGraph0() 
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        self.updateTable()
        
#%%######################################################################
        
#    def CreateWindowExportAA(self):
#        self.window = tk.Toplevel()
#        self.window.wm_title("Export Auto-Analysis")
#        center(self.window)
#        self.window.geometry("360x100")
#        self.windowRef.destroy()
#        self.CheckXlsxSum = IntVar()
#        legend=Checkbutton(self.window,text='Xlsx Summary',variable=self.CheckXlsxSum, 
#                           onvalue=1,offvalue=0,height=1, width=10)
#        legend.grid(row=0, column=0, columnspan=10)
#        self.CheckXlsxSum.set(1)
#        self.AutoGraphs = IntVar()
#        legend=Checkbutton(self.window,text='Auto-Graphs',variable=self.AutoGraphs, 
#                           onvalue=1,offvalue=0,height=1, width=10)
#        legend.grid(row=0, column=11, columnspan=10)
#        self.AutoGraphs.set(1)
#        self.TxtforOrigin = IntVar()
#        legend=Checkbutton(self.window,text='Txt for Origin',variable=self.TxtforOrigin, 
#                           onvalue=1,offvalue=0,height=1, width=10)
#        legend.grid(row=0, column=23, columnspan=10)
#        self.TxtforOrigin.set(1)
#        
#        label = tk.Label(self.window, text="...this window will be automatically shut down when the task is completed...", font=("Helvetica", 6))
#        label.grid(row=2, column=0,columnspan=30)
#        
#        self.ExportAll = Button(self.window, text="Start Auto-Analysis",
#                            command = self.ExportAutoAnalysis)
#        self.ExportAll.grid(row=1, column=0, columnspan=30,rowspan=1) 

    def CreateWindowExportAA(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Export Auto-Analysis")
        center(self.window)
        self.window.geometry("300x300")
        self.windowRef.destroy()
        
        
        self.CheckXlsxSum = IntVar()
        legend=Checkbutton(self.window,text='Xlsx Summary',variable=self.CheckXlsxSum, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.pack()
        self.CheckXlsxSum.set(1)
        
        #main stat graphs
        self.statGraphs = IntVar()
        legend=Checkbutton(self.window,text='statGraphs',variable=self.statGraphs, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.pack()
        self.statGraphs.set(1)
        
        #substrate IV summary graphs
        self.IVgraphs = IntVar()
        legend=Checkbutton(self.window,text='IVgraphs',variable=self.IVgraphs, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.pack()
        self.IVgraphs.set(1)
        
        #substrate mpp and specific power graphs
        self.mppgraphs = IntVar()
        legend=Checkbutton(self.window,text='mppgraphs',variable=self.mppgraphs, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.pack()
        self.mppgraphs.set(1)
        
        #text files with data
        self.TxtforOrigin = IntVar()
        legend=Checkbutton(self.window,text='Txt for Origin',variable=self.TxtforOrigin, 
                           onvalue=1,offvalue=0,height=1, width=10)
        legend.pack()
        self.TxtforOrigin.set(1)
        
        label = tk.Label(self.window, text="...this window will be automatically shut down when the task is completed...", font=("Helvetica", 6))
        label.pack()
        
        self.ExportAll = Button(self.window, text="Start Auto-Analysis",
                            command = self.ExportAutoAnalysis)
        self.ExportAll.pack()
        
    def AskforRefcells(self):
        global DATA
        
        self.windowRef = tk.Toplevel()
        self.windowRef.wm_title("Save .iv or load to DB?")
        center(self.windowRef)
        self.windowRef.geometry("290x100")
        
        if DATA!=[]:
            Button(self.windowRef, text="save all .iv",
                                command =self.SaveAllrawdatafiles).pack()
            Button(self.windowRef, text="save to database",
                                command =self.WriteJVtoDatabase).pack()
            Button(self.windowRef, text="No! take me to the autoanalysis!",
                                command = self.CreateWindowExportAA).pack()
    
    def WriteJVtoDatabase(self):
        global DATA, DATAdark, DATAMPP
        print("writting...")
        
        #connection to DB
        path =filedialog.askopenfilenames(title="Please select the DB file")[0]
        self.db_conn=sqlite3.connect(path)
        self.theCursor=self.db_conn.cursor()
       
        #for light&dark data
        print("JVs...")
        allDATA=DATA+DATAdark
        for i in range(len(allDATA)):
            batchname=allDATA[i]["DepID"].split("_")[0]
            self.theCursor.execute("SELECT id FROM batch WHERE batchname=?",(batchname,))
            batch_id_exists = self.theCursor.fetchone()[0]
            self.theCursor.execute("SELECT id FROM samples WHERE samplename=?",(allDATA[i]["DepID"],))            
            sample_id_exists = self.theCursor.fetchone()[0]
            
#            print(allDATA[i]["Cellletter"])
            
            self.theCursor.execute("SELECT id FROM cells WHERE samples_id=? AND batch_id=?",(sample_id_exists,batch_id_exists))            
            cellletter_id_exists = self.theCursor.fetchall()
            if len(cellletter_id_exists)>1:
                self.theCursor.execute("SELECT id FROM cells WHERE cellname=? AND samples_id=? AND batch_id=?",(allDATA[i]["Cellletter"],sample_id_exists,batch_id_exists))            
                cellletter_id_exists = self.theCursor.fetchone()[0]
#                print(cellletter_id_exists)
            else:
                cellletter_id_exists=cellletter_id_exists[0][0]
            print(cellletter_id_exists)
            if batch_id_exists and sample_id_exists and cellletter_id_exists:
                try:
                    self.db_conn.execute("""INSERT INTO JVmeas (
                                    DateTimeJV,
                                    Eff,
                                    Voc,
                                    Jsc,
                                    FF,
                                    Vmpp,
                                    Jmpp,
                                    Pmpp,
                                    Roc,
                                    Rsc,
                                    ScanDirect,
                                    Delay,
                                    IntegTime,
                                    CellArea,
                                    Vstart,
                                    Vend,
                                    Setup,
                                    NbPoints,
                                    ImaxComp,
                                    Isenserange,
                                    Operator,
                                    GroupJV,
                                    IlluminationIntensity,
                                    commentJV,
                                    linktorawdata,
                                    aftermpp,
                                    samples_id,
                                    batch_id,
                                    cells_id
                                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                                (    allDATA[i]["MeasDayTime"],
                                     allDATA[i]["Eff"],
                                     allDATA[i]["Voc"],
                                     allDATA[i]["Jsc"],
                                     allDATA[i]["FF"],
                                     allDATA[i]["Vmpp"],
                                     allDATA[i]["Jmpp"],
                                     allDATA[i]["Pmpp"],
                                     allDATA[i]["Roc"],
                                     allDATA[i]["Rsc"],
                                     allDATA[i]["ScanDirection"],
                                     allDATA[i]["Delay"],
                                     allDATA[i]["IntegTime"],
                                     allDATA[i]["CellSurface"],
                                     allDATA[i]["Vstart"],
                                     allDATA[i]["Vend"],
                                     allDATA[i]["Setup"],
                                     allDATA[i]["NbPoints"],
                                     allDATA[i]["ImaxComp"],
                                     allDATA[i]["Isenserange"],
                                     allDATA[i]["Operator"],
                                     allDATA[i]["Group"],
                                     allDATA[i]["Illumination"],
                                     allDATA[i]["MeasComment"],
                                     allDATA[i]["filepath"],
                                     allDATA[i]["aftermpp"],
                                     sample_id_exists,
                                     batch_id_exists,
                                     cellletter_id_exists))
    
                    self.db_conn.commit()
                except sqlite3.IntegrityError:
                    print("the file already exists in the DB")
        
        #for mpp data
        
        print("mpps...")
        for i in range(len(DATAMPP)):
            batchname=DATAMPP[i]["DepID"].split("_")[0]
            self.theCursor.execute("SELECT id FROM batch WHERE batchname=?",(batchname,))
            batch_id_exists = self.theCursor.fetchone()[0]
#            print(batch_id_exists)
            self.theCursor.execute("SELECT id FROM samples WHERE samplename=?",(DATAMPP[i]["DepID"],))            
            sample_id_exists = self.theCursor.fetchone()[0]
#            print(sample_id_exists)
            self.theCursor.execute("SELECT id FROM cells WHERE samples_id=? AND batch_id=?",(sample_id_exists,batch_id_exists))            
            cellletter_id_exists = self.theCursor.fetchall()
            if len(cellletter_id_exists)>1:
                self.theCursor.execute("SELECT id FROM cells WHERE cellname=? AND samples_id=? AND batch_id=?",(DATAMPP[i]["Cellletter"],sample_id_exists,batch_id_exists))            
                cellletter_id_exists = self.theCursor.fetchone()[0]
            else:
                cellletter_id_exists=cellletter_id_exists[0][0]
            print(cellletter_id_exists)
            if batch_id_exists and sample_id_exists and cellletter_id_exists:
                try:
                    self.db_conn.execute("""INSERT INTO MPPmeas (
                            linktorawdata,
                            commentmpp,
                            DateTimeMPP,
                            CellArea,
                            Vstep,
                            Vstart,
                            Operator,
                            TrackingDuration,
                            PowerEnd,
                            PowerAvg,
                            samples_id,
                            batch_id,
                            cells_id
                            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (   DATAMPP[i]["filepath"],
                            DATAMPP[i]["MeasComment"],
                            DATAMPP[i]["MeasDayTime"],
                            DATAMPP[i]["CellSurface"],
                            DATAMPP[i]["Vstep"],
                            DATAMPP[i]["Vstart"],
                            DATAMPP[i]["Operator"],
                            DATAMPP[i]["trackingduration"],
                            DATAMPP[i]["PowerEnd"], 
                            DATAMPP[i]["PowerAvg"], 
                            sample_id_exists,
                            batch_id_exists,
                            cellletter_id_exists))
                    self.db_conn.commit()
                except sqlite3.IntegrityError:
                    print("the file already exists in the DB")
#                print("done")
        
        #disconnect from DB
        self.theCursor.close()
        self.db_conn.close()
        
        #exit window
        print("it's in the DB!")
        messagebox.askokcancel("", "it's all in the DB!")
        self.windowRef.destroy()
        self.CreateWindowExportAA()

    
    def SaveReferenceCells(self):
        global DATA
        
        takenforexport=[]
        for name, var in self.choicesRef.items():
            takenforexport.append(var.get())
        #print(takenforexport)
        m=[]
        indices=[]
        for i in range(len(takenforexport)):
            if takenforexport[i]==1:
                indices.append(i)
                m.append(self.listofsamples[i])
            else:
                m.append("999")
        #print(indices)

        pathtofolder="//sti1files.epfl.ch/pv-lab/pvlab-commun/Groupe-Perovskite/Experiments/CellParametersFollowUP/"
        
        for item in indices:
            pathtosave=pathtofolder+self.RefCelltype.get()+"/"+m[item]+".iv"
            shutil.copy(DATA[item]["filepath"], pathtosave)
        
        
        self.CreateWindowExportAA()
    
    def SaveAllrawdatafiles(self):
        global DATA
        
        current_path = os.getcwd()
        folderName = filedialog.askdirectory(title = "choose a folder to export the .iv files", initialdir=os.path.dirname(current_path))
        os.chdir(folderName)
        
        for item in DATA:
            datetime=item["MeasDayTime"]
            datetime=datetime.replace(':','')
            datetime=datetime.replace('-','')
            datetime=datetime.replace('.','')
            datetime=datetime.replace(' ','')
            shutil.copy(item["filepath"], item["SampleName"]+'_'+datetime+'.iv')
        self.CreateWindowExportAA()
    

    def SaveSession(self):
        global DATA, DATAMPP, DATAdark, DATAFV, IVlegendMod, MPPlegendMod
        global testdata, DATAJVforexport, DATAJVtabforexport, DATAmppforexport, DATAgroupforexport
        global takenforplot, takenforplotmpp, IVlinestyle, MPPlinestyle, samplesgroups
        global listofanswer, listoflinestyle, listofcolorstyle
        global numbLightfiles, numbDarkfiles, groupstoplot
        global titIV, titmpp, titStat
        
        directory = filedialog.askdirectory()
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chdir(directory)
        else :
            os.chdir(directory)
        
        pickle.dump(DATA,open('DATA.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAdark,open('DATAdark.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAMPP,open('DATAMPP.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAMPP,open('DATAFV.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)        
        pickle.dump(IVlegendMod,open('IVlegendMod.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(MPPlegendMod,open('MPPlegendMod.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)

        pickle.dump(testdata,open('testdata.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAJVforexport,open('DATAJVforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAJVtabforexport,open('DATAJVtabforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(DATAmppforexport,open('DATAmppforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)        
        pickle.dump(DATAgroupforexport,open('DATAgroupforexport.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)

        pickle.dump(takenforplot,open('takenforplot.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(takenforplotmpp,open('takenforplotmpp.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(IVlinestyle,open('IVlinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(MPPlinestyle,open('MPPlinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(samplesgroups,open('samplesgroups.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        
#        pickle.dump(listofanswer,open('listofanswer.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
#        pickle.dump(listoflinestyle,open('listoflinestyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL)
#        pickle.dump(listofcolorstyle,open('listofcolorstyle.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        pickle.dump(numbLightfiles,open('numbLightfiles.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        pickle.dump(numbDarkfiles,open('numbDarkfiles.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        pickle.dump(groupstoplot,open('groupstoplot.pkl','wb'), protocol=pickle.HIGHEST_PROTOCOL) 
        
        print("dumped")
        """
        try:
            self.dumpfilename = filedialog.asksaveasfilename(defaultextension=".pkl")
            dill.dump_session(self.dumpfilename)
        except:
            print("there is an exception")
        """
        
        
    def LoadSession(self):
        global DATA, DATAMPP, DATAdark, DATAFV, IVlegendMod, MPPlegendMod
        global testdata, DATAJVforexport, DATAJVtabforexport, DATAmppforexport, DATAgroupforexport
        global takenforplot, takenforplotmpp, IVlinestyle, MPPlinestyle, samplesgroups
        global listofanswer, listoflinestyle, listofcolorstyle

        global numbLightfiles, numbDarkfiles, groupstoplot
        global titIV, titmpp, titStat

        try:
            path = filedialog.askdirectory()
            os.chdir(path)
        except:
            print("there is an exception")
            
        
        
        DATA = pickle.load(open('DATA.pkl','rb'))
        DATAdark = pickle.load(open('DATAdark.pkl','rb'))
        DATAMPP = pickle.load(open('DATAMPP.pkl','rb'))
        DATAFV = pickle.load(open('DATAFV.pkl','rb'))
        IVlegendMod = pickle.load(open('IVlegendMod.pkl','rb'))
        MPPlegendMod = pickle.load(open('MPPlegendMod.pkl','rb'))
        testdata = pickle.load(open('testdata.pkl','rb'))
        DATAJVforexport = pickle.load(open('DATAJVforexport.pkl','rb'))
        DATAJVtabforexport = pickle.load(open('DATAJVtabforexport.pkl','rb'))
        DATAmppforexport = pickle.load(open('DATAmppforexport.pkl','rb'))
        DATAgroupforexport = pickle.load(open('DATAgroupforexport.pkl','rb'))
        takenforplot = pickle.load(open('takenforplot.pkl','rb'))
        takenforplotmpp = pickle.load(open('takenforplotmpp.pkl','rb'))
        IVlinestyle = pickle.load(open('IVlinestyle.pkl','rb'))
        MPPlinestyle = pickle.load(open('MPPlinestyle.pkl','rb'))
        samplesgroups = pickle.load(open('samplesgroups.pkl','rb'))
#        listofanswer = pickle.load(open('listofanswer.pkl','rb'))
#        listoflinestyle = pickle.load(open('listoflinestyle.pkl','rb'))
#        listofcolorstyle = pickle.load(open('listofcolorstyle.pkl','rb'))
        groupstoplot = pickle.load(open('groupstoplot.pkl','rb'))
        numbDarkfiles = pickle.load(open('numbDarkfiles.pkl','rb'))
        numbLightfiles = pickle.load(open('numbLightfiles.pkl','rb'))
        
        
        """
        try:
            self.dumpfilename = filedialog.asksaveasfilename(defaultextension=".pkl")
            dill.load_session(self.dumpfilename)
        except:
            print("there is an exception")
        """
        print("loaded")
        
            
        if DATAMPP!=[]:
            print("il y a des mpp")
            self.mppnames = ()
            self.mppnames=self.SampleMppNames(DATAMPP)
            self.mppmenu = tk.Menu(self.mppmenubutton, tearoff=False)
            self.mppmenubutton.configure(menu=self.mppmenu)
            self.choicesmpp = {}
            for choice in range(len(self.mppnames)):
                self.choicesmpp[choice] = tk.IntVar(value=0)
                self.mppmenu.add_checkbutton(label=self.mppnames[choice], variable=self.choicesmpp[choice], 
                                     onvalue=1, offvalue=0, command = self.UpdateMppGraph0)
            self.UpdateMppGraph0()
            
        if DATA!=[]:
            titIV =0
            titmpp=0
            titStat=0
            self.updateTable()
            self.UpdateIVGraph()
            self.updategrouptoplotdropbutton()
            self.updateCompgrouptoplotdropbutton()
            self.updateHistgrouptoplotdropbutton()
            self.UpdateGroupGraph(1)
            self.UpdateCompGraph(1)
#%%######################################################################
    
    def GiveIVatitle(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Change title of IV graph")
        center(self.window)
        self.window.geometry("325x55")
        self.titleIV = tk.StringVar()
        entry=Entry(self.window, textvariable=self.titleIV,width=40)
        entry.grid(row=0,column=0,columnspan=1)
        self.addtitlebutton = Button(self.window, text="Update",
                            command = self.giveivatitleupdate)
        self.addtitlebutton.grid(row=1, column=0, columnspan=1)
    def giveivatitleupdate(self): 
        global titIV
        titIV=1
        self.UpdateIVGraph()
        
    
    ################
    class PopulateListofSampleStyling(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global DATA
            global takenforplot
            global IVlegendMod
            global IVlinestyle
            global colorstylelist
            global listofanswer
            global listoflinestyle
            global listofcolorstyle, listoflinewidthstyle
            
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]
            listoflinewidthstyle=[]
            
            for item in range(len(IVlegendMod)):
                listofanswer.append(IVlegendMod[item][1])
            
            for item in range(len(IVlinestyle)):
                listoflinestyle.append(IVlinestyle[item][1])
                listofcolorstyle.append(IVlinestyle[item][2])
                listoflinewidthstyle.append(str(IVlinestyle[item][3]))
            rowpos=1
            
            for itemm in takenforplot:
                for rowitem in range(len(IVlegendMod)):
                    if IVlegendMod[rowitem][0] == itemm:
                        label=tk.Label(self.frame,text=IVlegendMod[rowitem][0],fg='black',background='white')
                        label.grid(row=rowpos,column=0, columnspan=1)
                        textinit = tk.StringVar()
                        #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                        listofanswer[rowitem]=Entry(self.frame,textvariable=textinit)
                        textinit.set(IVlegendMod[rowitem][1])
                        listofanswer[rowitem].grid(row=rowpos,column=1, columnspan=2)
            
                        linestylelist = ["-","--","-.",":"]
                        listoflinestyle[rowitem]=tk.StringVar()
                        listoflinestyle[rowitem].set(IVlinestyle[rowitem][1]) # default choice
                        self.dropJVstyle=OptionMenu(self.frame, listoflinestyle[rowitem], *linestylelist, command=())
                        self.dropJVstyle.grid(row=rowpos, column=4, columnspan=2)

                        self.positioncolor=rowitem
                        JVcolstyle=Button(self.frame, text='Select Color', foreground=listofcolorstyle[rowitem], command=partial(self.getColor,rowitem))
                        JVcolstyle.grid(row=rowpos, column=6, columnspan=2)

                        linewidth = tk.StringVar()
                        listoflinewidthstyle[rowitem]=Entry(self.frame,textvariable=linewidth)
                        listoflinewidthstyle[rowitem].grid(row=rowpos,column=8, columnspan=1)
                        linewidth.set(str(IVlinestyle[rowitem][3]))

                        rowpos=rowpos+1
        
        def getColor(self,rowitem):
            global listofcolorstyle
            color = colorchooser.askcolor() 
            listofcolorstyle[rowitem]=color[1]
            
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
            
            
    class Drag_and_Drop_Listbox(tk.Listbox):
        #A tk listbox with drag'n'drop reordering of entries.
        def __init__(self, master, **kw):
            #kw['selectmode'] = tk.MULTIPLE
            kw['selectmode'] = tk.SINGLE
            kw['activestyle'] = 'none'
            tk.Listbox.__init__(self, master, kw)
            self.bind('<Button-1>', self.getState, add='+')
            self.bind('<Button-1>', self.setCurrent, add='+')
            self.bind('<B1-Motion>', self.shiftSelection)
            self.curIndex = None
            self.curState = None
        def setCurrent(self, event):
            ''' gets the current index of the clicked item in the listbox '''
            self.curIndex = self.nearest(event.y)
        def getState(self, event):
            ''' checks if the clicked item in listbox is selected '''
            #i = self.nearest(event.y)
            #self.curState = self.selection_includes(i)
            self.curState = 1
        def shiftSelection(self, event):
            ''' shifts item up or down in listbox '''
            i = self.nearest(event.y)
            if self.curState == 1:
              self.selection_set(self.curIndex)
            else:
              self.selection_clear(self.curIndex)
            if i < self.curIndex:
              # Moves up
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i+1, x)
              if selected:
                self.selection_set(i+1)
              self.curIndex = i
            elif i > self.curIndex:
              # Moves down
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i-1, x)
              if selected:
                self.selection_set(i-1)
              self.curIndex = i
              

    def reorder(self): 
        global takenforplot
        self.reorderwindow = tk.Tk()
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
        for name in takenforplot:
          self.listbox.insert(tk.END, name)
          self.listbox.selection_set(0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        printbut = tk.Button(self.reorderwindow, text="reorder",
                                    command = self.printlist)
        printbut.pack()
        self.reorderwindow.mainloop()    
            
    def printlist(self):
        global takenforplot
        takenforplot=list(self.listbox.get(0,tk.END))
        self.UpdateIVLegMod()
        self.reorderwindow.destroy()
            
    def ChangeLegendTimegraph(self):
        print("changingtimelegend")   
        
    def ChangeLegendIVgraph(self):
        
        if self.CheckIVLegend.get()==1:
            self.window = tk.Toplevel()
            self.window.wm_title("Change Legends")
            center(self.window)
            self.window.geometry("450x350")
            self.changeIVlegend = Button(self.window, text="Update",
                                command = self.UpdateIVLegMod)
            self.changeIVlegend.pack()
            self.changeIVorder = Button(self.window, text="Reorder",
                                command = self.reorder)
            self.changeIVorder.pack()
            
            
            self.PopulateListofSampleStyling(self.window).pack(side="top", fill="both", expand=True)
    
    def UpdateIVLegMod(self):
        global IVlegendMod
        global IVlinestyle
        global listofanswer
        global listoflinestyle
        global listofcolorstyle,listoflinewidthstyle
        
                
        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        
        for item in range(len(IVlegendMod)):
            IVlegendMod[item][1]=leglist[item]
        
        leglist=[]
        for e in listoflinestyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listoflinestyle]
        for item in range(len(IVlinestyle)):
            IVlinestyle[item][1]=leglist[item]
        
        leglist=[]
        for e in listofcolorstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listofcolorstyle]
        for item in range(len(IVlinestyle)):
            IVlinestyle[item][2]=leglist[item]
            
        leglist=[]
        for e in listoflinewidthstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        for item in range(len(IVlinestyle)):
            IVlinestyle[item][3]=int(leglist[item])
            
        self.UpdateIVGraph()
        self.window.destroy()
        self.ChangeLegendIVgraph()
    ################
    
    class PopulateListofSampleStylingMPP(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global DATAMPP
            global takenforplotmpp
            global MPPlegendMod
            global MPPlinestyle
            global colorstylelist
            global listofanswer
            global listoflinestyle
            global listofcolorstyle, listoflinewidthstyle
            
            listofanswer=[]
            listoflinestyle=[]
            listofcolorstyle=[]
            
            for item in range(len(MPPlegendMod)):
                listofanswer.append(MPPlegendMod[item][1])
            
            for item in range(len(MPPlinestyle)):
                listoflinestyle.append(MPPlinestyle[item][1])
                listofcolorstyle.append(MPPlinestyle[item][2])
                listoflinewidthstyle.append(str(MPPlinestyle[item][3]))
            rowpos=1
            
            for itemm in takenforplotmpp:
                for rowitem in range(len(MPPlegendMod)):
                    if MPPlegendMod[rowitem][0] == itemm:
                        label=tk.Label(self.frame,text=MPPlegendMod[rowitem][0],fg='black',background='white')
                        label.grid(row=rowpos,column=0, columnspan=1)
                        textinit = tk.StringVar()
                        #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                        listofanswer[rowitem]=Entry(self.frame,textvariable=textinit)
                        textinit.set(MPPlegendMod[rowitem][1])
                        listofanswer[rowitem].grid(row=rowpos,column=1, columnspan=2)
            
                        linestylelist = ["-","--","-.",":"]
                        listoflinestyle[rowitem]=tk.StringVar()
                        listoflinestyle[rowitem].set(MPPlinestyle[rowitem][1]) # default choice
                        self.dropMPPstyle=OptionMenu(self.frame, listoflinestyle[rowitem], *linestylelist, command=())
                        self.dropMPPstyle.grid(row=rowpos, column=4, columnspan=2)

                        linewidth = tk.StringVar()
                        listoflinewidthstyle[rowitem]=Entry(self.frame,textvariable=linewidth)
                        listoflinewidthstyle[rowitem].grid(row=rowpos,column=8, columnspan=1)
                        linewidth.set(str(MPPlinestyle[rowitem][3]))

                        self.positioncolor=rowitem
                        Button(self.frame, text='Select Color', foreground=MPPlinestyle[rowitem][2], command=partial(self.getColor,rowitem)).grid(row=rowpos, column=6, columnspan=2)

                        rowpos=rowpos+1
        
        def getColor(self,rowitem):
            global listofcolorstyle
            color = colorchooser.askcolor()
            listofcolorstyle[rowitem]=color[1]
            
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))

    def reordermpp(self): 
        global takenforplotmpp

        self.reorderwindow = tk.Tk()
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox(self.reorderwindow)
        for name in takenforplotmpp:
          self.listbox.insert(tk.END, name)
          self.listbox.selection_set(0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        Button(self.reorderwindow, text="reorder",command = self.printlistmpp).pack()
        self.reorderwindow.mainloop()    
            
    def printlistmpp(self):
        global takenforplotmpp
        takenforplotmpp=list(self.listbox.get(0,tk.END))
        self.UpdateMPPLegMod()
        self.reorderwindow.destroy()
            
    def ChangeLegendMPPgraph(self):
        global takenforplotmpp
        global MPPlegendMod
        
        if self.CheckmppLegend.get()==1:
            
            self.window = tk.Toplevel()
            self.window.wm_title("Change Legends")
            center(self.window)
            self.window.geometry("400x300")
            Button(self.window, text="Update",command = self.UpdateMPPLegMod).pack()
            Button(self.window, text="Reorder",command = self.reordermpp).pack()
            
            self.PopulateListofSampleStylingMPP(self.window).pack(side="top", fill="both", expand=True)
        
       
    def UpdateMPPLegMod(self):
        global MPPlegendMod
        global MPPlinestyle
        global listofanswer
        global listoflinestyle
        global listofcolorstyle,listoflinewidthstyle


        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        
        for item in range(len(MPPlegendMod)):
            MPPlegendMod[item][1]=leglist[item]

        leglist=[]
        for e in listoflinestyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listoflinestyle]
        for item in range(len(MPPlinestyle)):
            MPPlinestyle[item][1]=leglist[item]
        
        leglist=[]
        for e in listoflinewidthstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listoflinestyle]
        for item in range(len(MPPlinestyle)):
            MPPlinestyle[item][3]=int(leglist[item])
            
        leglist=[]
        for e in listofcolorstyle:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        #leglist=[e.get() for e in self.listofcolorstyle]
        for item in range(len(MPPlinestyle)):
            MPPlinestyle[item][2]=leglist[item]
        
        self.UpdateMppGraph()
        self.window.destroy()
        self.ChangeLegendMPPgraph()
        
    
    def GiveMPPatitle(self):
        self.window = tk.Toplevel()
        self.window.wm_title("Change title of Mpp graph")
        center(self.window)
        self.window.geometry("325x55")
        self.titlempp = tk.StringVar()
        entry=Entry(self.window, textvariable=self.titlempp,width=40)
        entry.grid(row=0,column=0,columnspan=1)
        self.addtitlebutton = Button(self.window, text="Update",
                            command = self.givemppatitleupdate)
        self.addtitlebutton.grid(row=1, column=0, columnspan=1)
    def givemppatitleupdate(self): 
        global titmpp
        titmpp=1
        self.UpdateMppGraph()
 
#########################################################
#########################################################       
    #Change cell area
    class PopulateListofSampleChangeArea(tk.Frame):
        def __init__(self, root):
    
            tk.Frame.__init__(self, root)
            self.canvas0 = tk.Canvas(root, borderwidth=0, background="#ffffff")
            self.frame = tk.Frame(self.canvas0, background="#ffffff")
            self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas0.yview)
            self.canvas0.configure(yscrollcommand=self.vsb.set)
    
            self.vsb.pack(side="right", fill="y")
            self.canvas0.pack(side="left", fill="both", expand=True)
            self.canvas0.create_window((4,4), window=self.frame, anchor="nw", 
                                      tags="self.frame")
    
            self.frame.bind("<Configure>", self.onFrameConfigure)
    
            self.populate()
    
        def populate(self):
            global DATA
            global listofanswer
            
            listofanswer=[]
            
            
            for item in range(len(DATA)):
                listofanswer.append(DATA[item]["CellSurface"])
                
            rowpos=1
            
            for rowitem in range(len(DATA)):
                label=tk.Label(self.frame,text=DATA[rowitem]["SampleName"],fg='black',background='white')
                label.grid(row=rowpos,column=0, columnspan=1)
                textinit = tk.StringVar()
                #self.listofanswer.append(Entry(self.window,textvariable=textinit))
                listofanswer[rowitem]=Entry(self.frame,textvariable=textinit)
                textinit.set(DATA[rowitem]["CellSurface"])
                listofanswer[rowitem].grid(row=rowpos,column=1, columnspan=2)
                label=tk.Label(self.frame,text=DATA[rowitem]["Jsc"],fg='black',background='white')
                label.grid(row=rowpos,column=3, columnspan=1)
                rowpos=rowpos+1
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))  
            
    def changecellarea(self):
        global DATA
        
        if DATA!=[]:
            self.window = tk.Toplevel()
            self.window.wm_title("Change the cell area")
            center(self.window)
            self.window.geometry("360x100")
            Button(self.window, text="Update",command = self.UpdateChangeArea).pack()
            
            self.PopulateListofSampleChangeArea(self.window).pack(side="top", fill="both", expand=True)

    def UpdateChangeArea(self):
        global listofanswer
        global DATA
        
        leglist=[]
        for e in listofanswer:
            if type(e)!=str:
                leglist.append(e.get())
            else:
                leglist.append(e)
        
        for item in range(len(DATA)):
            DATA[item]["Jsc"]=float(DATA[item]["Jsc"])*float(DATA[item]["CellSurface"])/float(leglist[item]) 
            DATA[item]["Jmpp"]=float(DATA[item]["Jmpp"])*float(DATA[item]["CellSurface"])/float(leglist[item]) 
            DATA[item]["Pmpp"]=float(DATA[item]["Pmpp"])*float(DATA[item]["CellSurface"])/float(leglist[item])
            DATA[item]["Eff"]=float(DATA[item]["Eff"])*float(DATA[item]["CellSurface"])/float(leglist[item])
            newCurrent=[]
            for i in range(len(DATA[item]["IVData"][1])):
                newCurrent.append(DATA[item]["IVData"][1][i]*float(DATA[item]["CellSurface"])/float(leglist[item]))
            DATA[item]["IVData"][1]=copy.deepcopy(newCurrent)
            
        #change also the rawdata file, use the filepath to access it. 
#        old file is renamed with _old
#        new file has original name and saved at same place so that all links are still valid
        
        for item0 in range(len(DATA)):
            newarea=float(leglist[item0])
            oldcellarea=DATA[item0]["CellSurface"]
            file_path=DATA[item0]["filepath"]
            
            filetoread = open(file_path,"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            
            for item in range(len(filerawdata)):
                if "Cell size [m2]:" in filerawdata[item]:
                    oldcellarea=copy.deepcopy(float(filerawdata[item][17:-1]))
                    filerawdata[item]=filerawdata[item][:17]+str(newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "Jsc [A/m2]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:19]+str(float(filerawdata[item][19:-1])*oldcellarea/newarea)+"\n"
                    break   
            for item in range(len(filerawdata)):
                if "Efficiency [.]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:19]+str(float(filerawdata[item][19:-1])*oldcellarea/newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "Pmpp [W/m2]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:19]+str(float(filerawdata[item][19:-1])*oldcellarea/newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "Jmpp [A]:" in filerawdata[item]:
                    filerawdata[item]=filerawdata[item][:10]+str(float(filerawdata[item][10:-1])*oldcellarea/newarea)+"\n"
                    break
            for item in range(len(filerawdata)):
                if "MEASURED IV DATA" in filerawdata[item]:
                        pos=item+2
                        break
                elif "MEASURED IV FRLOOP DATA" in filerawdata[item]:
                        pos=item+2
                        break
            for item in range(pos,len(filerawdata),1):
                filerawdata[item]=filerawdata[item].split("\t")[0]+"\t"+filerawdata[item].split("\t")[1]+"\t"+filerawdata[item].split("\t")[2]+"\t"+str(float(filerawdata[item].split("\t")[3][:-1])*oldcellarea/newarea)+"\n"

            file = open(file_path,'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in filerawdata)
            file.close()
            DATA[item0]["CellSurface"]=newarea
        
        self.window.destroy()
        self.updateTable()
        self.UpdateIVGraph()
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        
#########################################################
#########################################################        
           
    
    def TableBuilder(self):
        global DATA
        global testdata
        testdata=[]
        #self.parent.grid_rowconfigure(0,weight=1)
        #self.parent.grid_columnconfigure(0,weight=1)
        self.frame01.config(background="white")
                  
        for item in range(len(DATA)):
            testdata.append([DATA[item]["Group"],DATA[item]["SampleName"],DATA[item]["MeasDayTime2"],float('%.2f' % float(DATA[item]["CellSurface"])),DATA[item]["ScanDirection"],float('%.2f' % float(DATA[item]["Jsc"])),float('%.2f' % float(DATA[item]["Voc"])),float('%.2f' % float(DATA[item]["FF"])),float('%.2f' % float(DATA[item]["Eff"])),float('%.2f' % float(DATA[item]["Roc"])),float('%.2f' % float(DATA[item]["Rsc"])),float('%.2f' % float(DATA[item]["Vmpp"])),float('%.2f' % float(DATA[item]["Jmpp"]))])
            
        self.tableheaders=('Group','Sample','DateTime','Area','Scan direct.','Jsc','Voc','FF','Eff.','Roc','Rsc','Vmpp','Jmpp')
                    
        # Set the treeview
        self.tree = Treeview( self.frame01, columns=self.tableheaders, show="headings")
        
        for col in self.tableheaders:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
            #self.tree.column(col,stretch=tkinter.YES)
            self.tree.column(col, width=int(round(2*tkFont.Font().measure(col.title()))), anchor='n')   
            #print(int(round(1.2*tkFont.Font().measure(col.title()))))
        
        vsb = Scrollbar(self.frame01, orient="vertical", command=self.tree.yview)
        #hsb = ttk.Scrollbar(orient="horizontal",command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=())
        self.tree.grid(row=1,column=0, columnspan=15,rowspan=15, sticky='nsew', in_=self.frame01)
        vsb.grid(column=20, row=1,rowspan=15, sticky='ns', in_=self.frame01)
        #hsb.grid(column=0, row=11, sticky='ew', in_=self.parent)
        self.treeview = self.tree
        
        self.insert_data(testdata)
    
    
    def deletedatatreeview(self):
        global DATA
        try:
            for j in range(len(self.treeview.selection())):
                selected_item = self.treeview.selection()[j] ## get selected item
                for i in range(len(DATA)):
                    if DATA[i]["SampleName"]==self.treeview.item(selected_item)["values"][1]:
                        DATA.pop(i)
                        break
            selected_items = self.treeview.selection()
            for item in selected_items:
                self.treeview.delete(item)
            self.UpdateGroupGraph(1)
            self.UpdateCompGraph(1)
        except IndexError:
            messagebox.showinfo("Information","you didn't select an element in the table")
#                print("you didn't select an element in the table")

    def insert_data(self, testdata):
        for item in testdata:
            self.treeview.insert('', 'end', values=item)
            
            #for ix, val in enumerate(item):
            #    col_w = tkFont.Font().measure(val)
            #    if tkFont.Font().measure(self.tableheaders[ix].title())<col_w:
            #        self.tree.column(self.tableheaders[ix], width=col_w)
            
    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]), reverse=descending)
        except ValueError:
            data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col,text=col.capitalize(), command=lambda _col_=col: self.sortby(tree, _col_, int(not descending)))
    
    
    def plottingTimefromTable(self):
        global takenforplotTime
        totake=self.treeview.selection()
        takenforplotTime=[str(self.treeview.item(item)["values"][1]) for item in totake]
        
        self.UpdateTimeGraph(1)
    
    def plottingfromTable(self):
        global takenforplot
        
        totake=self.treeview.selection()
        takenforplot=[str(self.treeview.item(item)["values"][1]) for item in totake]
        
        self.UpdateIVGraph()
        
    def groupfromTable(self):
        global samplesgroups, groupstoplot
        
        self.window = tk.Toplevel()
        self.window.wm_title("Group samples")
        center(self.window)
        self.window.geometry("600x120")
         
        label=tk.Label(self.window,text="                ")
        label.grid(row=0,column=0, columnspan=8)
        label=tk.Label(self.window,text="  ")
        label.grid(row=0,column=0, rowspan=8)
        
        self.groupupdate = Button(self.window, text="new group",
                            command = self.validategroup)
        self.groupupdate.grid(row=1, column=1, columnspan=3)
        
        self.newgroup = tk.StringVar()
        self.newgroup.set(samplesgroups[0])
        entry=Entry(self.window, textvariable=self.newgroup,width=13)
        entry.grid(row=2,column=1,columnspan=3)
        
        label=tk.Label(self.window,text="      or      ")
        label.grid(row=1,column=5, columnspan=1)
        
        self.groupupdate = Button(self.window, text="existing group",
                            command = self.validategroup)
        self.groupupdate.grid(row=1, column=6, columnspan=3)
        
        self.groupchoice=tk.StringVar()
        self.groupchoice.set(samplesgroups[0]) # default choice
        self.dropgroupchoice=OptionMenu(self.window, self.groupchoice, *samplesgroups, command=())
        self.dropgroupchoice.grid(row=2, column=6, columnspan=3)
        
        label=tk.Label(self.window,text="      or      ")
        label.grid(row=1,column=9, columnspan=1)
        
        self.groupdel = Button(self.window, text="delete group",
                            command = self.deletegroup)
        self.groupdel.grid(row=1, column=10, columnspan=3)
        
        self.groupdellist=tk.StringVar()
        self.groupdellist.set(samplesgroups[0]) # default choice
        self.dropgroupchoice=OptionMenu(self.window, self.groupdellist, *samplesgroups, command=())
        self.dropgroupchoice.grid(row=2, column=10, columnspan=3)
        
        label=tk.Label(self.window,text="      or      ")
        label.grid(row=1,column=15, columnspan=1)
        
        self.groupOrder = Button(self.window, text="reorder group",
                            command = self.reordergroup)
        self.groupOrder.grid(row=1, column=20, columnspan=3)
        
#        self.grouptoplotbutton = tk.Menubutton(self.window, text="grouptoplot", 
#                                   indicatoron=True, borderwidth=1, relief="raised")
#        self.grouptoplotmenu = tk.Menu(self.grouptoplotbutton, tearoff=False)
#        self.grouptoplotbutton.configure(menu=self.grouptoplotmenu)
#        self.grouptoplotbutton.grid(row=3, column=20, columnspan=3)
    
    
    
    class Drag_and_Drop_Listbox2(tk.Listbox):
        #A tk listbox with drag'n'drop reordering of entries.
        def __init__(self, master, **kw):
            #kw['selectmode'] = tk.MULTIPLE
            kw['selectmode'] = tk.SINGLE
            kw['activestyle'] = 'none'
            tk.Listbox.__init__(self, master, kw)
            self.bind('<Button-1>', self.getState, add='+')
            self.bind('<Button-1>', self.setCurrent, add='+')
            self.bind('<B1-Motion>', self.shiftSelection)
            self.curIndex = None
            self.curState = None
        def setCurrent(self, event):
            ''' gets the current index of the clicked item in the listbox '''
            self.curIndex = self.nearest(event.y)
        def getState(self, event):
            ''' checks if the clicked item in listbox is selected '''
            #i = self.nearest(event.y)
            #self.curState = self.selection_includes(i)
            self.curState = 1
        def shiftSelection(self, event):
            ''' shifts item up or down in listbox '''
            i = self.nearest(event.y)
            if self.curState == 1:
              self.selection_set(self.curIndex)
            else:
              self.selection_clear(self.curIndex)
            if i < self.curIndex:
              # Moves up
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i+1, x)
              if selected:
                self.selection_set(i+1)
              self.curIndex = i
            elif i > self.curIndex:
              # Moves down
              x = self.get(i)
              selected = self.selection_includes(i)
              self.delete(i)
              self.insert(i-1, x)
              if selected:
                self.selection_set(i-1)
              self.curIndex = i
    
    def reordergroup(self):
        global groupstoplot
        
        self.reorderwindow = tk.Tk()
        center(self.reorderwindow)
        self.listbox = self.Drag_and_Drop_Listbox2(self.reorderwindow)
        for name in range(1,len(groupstoplot)):
          self.listbox.insert(tk.END, groupstoplot[name])
          self.listbox.selection_set(0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(self.listbox, orient="vertical")
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        printbut = tk.Button(self.reorderwindow, text="reorder",
                                    command = self.printlist2)
        printbut.pack()
        self.reorderwindow.mainloop()    
        
        #print(samplesgroups)
    def updategrouptoplotdropbutton(self):
        global groupstoplot
        
        self.grouptoplotmenu = tk.Menu(self.grouptoplotbutton, tearoff=False)
        self.grouptoplotbutton.configure(menu=self.grouptoplotmenu)
        self.choicesgrouptoplot = {}
        for choice in range(len(groupstoplot)):
            self.choicesgrouptoplot[choice] = tk.IntVar(value=1)
            self.grouptoplotmenu.add_checkbutton(label=groupstoplot[choice], variable=self.choicesgrouptoplot[choice], 
                                 onvalue=1, offvalue=0, command = lambda: self.UpdateGroupGraph(1))
    
    def updateCompgrouptoplotdropbutton(self):
        global groupstoplot
        
        self.Compgrouptoplotmenu = tk.Menu(self.Compgrouptoplotbutton, tearoff=False)
        self.Compgrouptoplotbutton.configure(menu=self.Compgrouptoplotmenu)
        self.choicesgroupcomptoplot = {}
        for choice in range(len(groupstoplot)):
            self.choicesgroupcomptoplot[choice] = tk.IntVar(value=1)
            self.Compgrouptoplotmenu.add_checkbutton(label=groupstoplot[choice], variable=self.choicesgroupcomptoplot[choice], 
                                 onvalue=1, offvalue=0, command = lambda: self.UpdateCompGraph(1))

    def updateHistgrouptoplotdropbutton(self):
        global groupstoplot
        
        self.Histgrouptoplotmenu = tk.Menu(self.Histgrouptoplotbutton, tearoff=False)
        self.Histgrouptoplotbutton.configure(menu=self.Histgrouptoplotmenu)
        self.choicesgroupHisttoplot = {}
        for choice in range(len(groupstoplot)):
            self.choicesgroupHisttoplot[choice] = tk.IntVar(value=1)
            self.Histgrouptoplotmenu.add_checkbutton(label=groupstoplot[choice], variable=self.choicesgroupHisttoplot[choice], 
                                 onvalue=1, offvalue=0, command = lambda: self.UpdateHistGraph(1))
        
    def printlist2(self):
        global samplesgroups,groupstoplot
        groupstoplot=list(self.listbox.get(0,tk.END))
        groupstoplot=["Default group"]+ groupstoplot
        #self.UpdateIVLegMod()
        self.reorderwindow.destroy()
        self.window.destroy()
        self.updategrouptoplotdropbutton()
        self.updateCompgrouptoplotdropbutton()
        self.updateHistgrouptoplotdropbutton()
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        #self.groupfromTable()
    
    def validategroup(self):
        global takenforplot
        global samplesgroups,groupstoplot
        global DATA
        
        totake=self.treeview.selection()
        takenforplot=[str(self.treeview.item(item)["values"][1]) for item in totake]

        if self.newgroup.get() != samplesgroups[0] and totake!=():
            if self.newgroup.get() not in samplesgroups:
                samplesgroups.append(self.newgroup.get())
                groupstoplot.append(self.newgroup.get())
            for item in range(len(takenforplot)):
                for item1 in range(len(DATA)):
                    if takenforplot[item]==DATA[item1]["SampleName"]:
                        DATA[item1]["Group"]=self.newgroup.get()
                        break
        elif totake!=():
            for item in range(len(takenforplot)):
                for item1 in range(len(DATA)):
                    if takenforplot[item]==DATA[item1]["SampleName"]:
                        DATA[item1]["Group"]=self.groupchoice.get()
                        break
        self.TableBuilder()
        self.updategrouptoplotdropbutton()
        self.updateCompgrouptoplotdropbutton()
        self.updateHistgrouptoplotdropbutton()
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        self.window.destroy()
        
    def deletegroup(self):
        global samplesgroups, groupstoplot
        global DATA
        
        if self.groupdellist.get()!="Default group":
            while self.groupdellist.get() in samplesgroups: samplesgroups.remove(self.groupdellist.get()) 
            while self.groupdellist.get() in groupstoplot: groupstoplot.remove(self.groupdellist.get()) 
        
        for i in range(len(DATA)):
            if DATA[i]["Group"]==self.groupdellist.get():
                DATA[i]["Group"]="Default group"
        self.TableBuilder()
        self.updategrouptoplotdropbutton()
        self.updateCompgrouptoplotdropbutton()
        self.updateHistgrouptoplotdropbutton()
        self.UpdateGroupGraph(1)
        self.UpdateCompGraph(1)
        self.window.destroy()
        
    def SampleMppNames(self, DATAx):
        Names = list(self.mppnames)
        for item in range(len(DATAx)):
            Names.append(DATAx[item]["SampleName"])
        return tuple(Names)
    
#%%######################################################################
        
if __name__ == '__main__':
    app = IVApp()
    app.mainloop()
    