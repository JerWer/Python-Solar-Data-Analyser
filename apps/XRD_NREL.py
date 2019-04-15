#! python3

import os, datetime

import matplotlib.pyplot as plt
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
from matplotlib import collections as matcoll
from matplotlib import colors as mcolors
from tkinter.ttk import Treeview
import tkinter as tk
from tkinter import ttk, Tk, messagebox, Entry, Button, Checkbutton, IntVar, Toplevel, OptionMenu, Frame, StringVar, Scrollbar, Listbox
from tkinter import filedialog
from tkinter import *
from pathlib import Path
import numpy as np
import xlsxwriter
import xlrd
from scipy.interpolate import interp1d, UnivariateSpline
from scipy import integrate, stats
from tkcolorpicker import askcolor 
import six
from functools import partial
import math
import sqlite3
import csv
from scipy.optimize import curve_fit
import peakutils
from peakutils.plot import plot as pplot
from tkinter import font as tkFont


"""
TODOLIST

- (shift to ref auto)

- show peak fitting

- export as ref file function

- background removal import function: import a file with background and substract it from the selected samples. 

- delete entry from list of samples

- legend, change color of plots... similar to IVapp


"""
#%%
LARGE_FONT= ("Verdana", 12)

def center(win):
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

DATA={}# {"name":[[x original...],[y original...],[x corrected...],[y corrected...],[{"Position":1,"PeakName":'(005)',"Intensity":1,"FWHM":1},...]],"name2":[]}

colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
owd = os.getcwd()

xrdRefPattDir	= os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'crystalloData')	# materials data


reflist=os.listdir(xrdRefPattDir)
refsamplenameslist=[]
for item in reflist:
    refsamplenameslist.append(item.split('.')[0])

RefPattDATA={}
os.chdir(xrdRefPattDir)
for item in range(len(refsamplenameslist)):
    RefPattDATA[refsamplenameslist[item]]=[[],[],[]]
    if reflist[item].split('.')[1]=='txt':
        filetoread = open(reflist[item],"r", encoding='ISO-8859-1')
        filerawdata = filetoread.readlines()
        for row in filerawdata:
            RefPattDATA[refsamplenameslist[item]][0].append(float(row.split("\t")[0]))
            RefPattDATA[refsamplenameslist[item]][1].append(float(row.split("\t")[1]))
            try:
                RefPattDATA[refsamplenameslist[item]][2].append(str(row.split("\t")[2])[:-1])
            except:
                RefPattDATA[refsamplenameslist[item]][2].append("")
    
#print(RefPattDATA["jems-Si"])

os.chdir(owd)
#refsamplenameslist=["Si","pkcubic"]#to be replaced by reading the folder and putting all data in a list and getting the file names in this list
Patternsamplenameslist=[]

listofanswer={}
samplestakenforplot=[]
peaknamesforplot=[]

lambdaXRD=1.54

def q_to_tth(Q):
    "convert q to tth, lam is wavelength in angstrom"
    return 360/np.pi * np.arcsin(Q * lambdaXRD / (4 * np.pi))

def tth_to_q(tth):
    "convert tth to q, lam is wavelength in angstrom"
    return 4 * np.pi * np.sin(tth * np.pi/(2 * 180)) / lambdaXRD

def q_to_tth_list(Q):
    "convert q to tth, lam is wavelength in angstrom"
    return [360/np.pi * np.arcsin(Qitem * lambdaXRD / (4 * np.pi)) for Qitem in Q]

def tth_to_q_list(tth):
    "convert tth to q, lam is wavelength in angstrom"
    return [4 * np.pi * np.sin(tthitem * np.pi/(2 * 180)) / lambdaXRD for tthitem in tth]

#%%###############################################################################             
    
class XRDApp(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "XRDApp")
        Toplevel.config(self,background="white")
        self.wm_geometry("650x650")
        center(self)
        self.initUI()


    def initUI(self):
        global refsamplenameslist, Patternsamplenameslist
        
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas0 = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.superframe=Frame(self.canvas0,background="#ffffff")
        self.canvas0.pack(side="left", fill="both", expand=True)
        
        label = tk.Label(self.canvas0, text="XRD DATA Analyzer", font=LARGE_FONT, bg="black",fg="white")
        label.pack(fill=tk.X,expand=0)
        
        frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        frame1.bind("<Configure>", self.onFrameConfigure)
        self.fig1 = plt.figure(figsize=(1, 3))
        canvas = FigureCanvasTkAgg(self.fig1, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.XRDgraph = plt.subplot2grid((1, 1), (0, 0), colspan=3)
#        self.XRDgraphtwin=self.XRDgraph.twiny()
        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH,expand=1) 
        
        frame2=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame2.pack(fill=tk.BOTH,expand=0)
        
        frame21=Frame(frame2,borderwidth=0,  bg="lightgrey")
        frame21.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        frame211=Frame(frame21,borderwidth=0,  bg="lightgrey")
        frame211.pack(fill=tk.BOTH,expand=1)
        self.shift = tk.DoubleVar()
        Entry(frame211, textvariable=self.shift,width=3).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.shiftBut = Button(frame211, text="X Shift",command = self.shiftX).pack(side=tk.LEFT,expand=1)
        self.shift.set(0)
        self.shiftYval = tk.DoubleVar()
        Entry(frame211, textvariable=self.shiftYval,width=3).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.shiftYBut = Button(frame211, text="Y Shift",command = self.shiftY).pack(side=tk.LEFT,expand=1)
        self.shiftYval.set(0)
        self.ylabel = IntVar()
        Checkbutton(frame211,text="noylab",variable=self.ylabel, command = lambda: self.updateXRDgraph(0),
                           onvalue=1,offvalue=0,height=1, width=3, fg='black',background='lightgrey').pack(side=tk.LEFT,expand=1)
        self.changetoQ = IntVar()
        Checkbutton(frame211,text="q?",variable=self.changetoQ, command = lambda: self.updateXRDgraph(0),
                           onvalue=1,offvalue=0,height=1, width=3, fg='black',background='lightgrey').pack(side=tk.LEFT,expand=1)

                        
        frame212=Frame(frame21,borderwidth=0,  bg="lightgrey")
        frame212.pack(fill=tk.BOTH,expand=1)
        self.backgroundorder = tk.IntVar()
        Entry(frame212, textvariable=self.backgroundorder,width=1).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.backgroundorder.set(12)
        self.CheckBkgRemoval = Button(frame212, text="BkgRemoval",command = self.backgroundremoval).pack(side=tk.LEFT,expand=1)
        self.CheckBkgRemovalImport = Button(frame212, text="BkgRemImport",command = self.backgroundremovalImport).pack(side=tk.LEFT,expand=1)

#        refpattern=StringVar()
#        refpatternlist=['Original','Si','ITO']#to be replace by actual files in a specific folder
#        cbbox = ttk.Combobox(frame212, textvariable=refpattern, values=refpatternlist)            
#        cbbox.pack(side=tk.LEFT,expand=0)
#        refpattern.set(refpatternlist[0])
#        self.refbut = Button(frame212, text="ShiftToRef",command = self.shifttoRef).pack(side=tk.LEFT,expand=1)
                
        frame213=Frame(frame21,borderwidth=0,  bg="lightgrey")
        frame213.pack(fill=tk.BOTH,expand=1)        
        self.rescale = tk.DoubleVar()
        Entry(frame213, textvariable=self.rescale,width=3).pack(side=tk.LEFT,fill=tk.X,expand=1)
        self.rescale.set(1000)
        self.rescaleBut = Button(frame213, text="Rescale to ref",command = self.scaleYtoRef).pack(side=tk.LEFT,expand=1)
        self.backtoOriginalBut = Button(frame213, text="BackToOriginal",command = self.backtoOriginal).pack(side=tk.LEFT,expand=1)

        
        frame22=Frame(frame2,borderwidth=0,  bg="white")
        frame22.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        frame221=Frame(frame22,borderwidth=0,  bg="white")
        frame221.pack(fill=tk.BOTH,expand=1)
        self.importBut = Button(frame221, text="Import",command = self.importDATA).pack(side=tk.LEFT,expand=1)
        self.importRefBut = Button(frame221, text="ImportRef",command = self.importRefDATA).pack(side=tk.LEFT,expand=1)
        self.UpdateBut = Button(frame221, text="Update",command = lambda: self.updateXRDgraph(0)).pack(side=tk.LEFT,expand=1)
        frame222=Frame(frame22,borderwidth=0,  bg="grey")
        frame222.pack(fill=tk.BOTH,expand=1)
        self.ShowPeakDetectionBut = Button(frame222, text="Peak Detection",command = self.PeakDetection).pack(side="left",expand=1)
        self.ChangePeakNameBut = Button(frame222, text="Change Peak Names",command = self.ChangePeakNames).pack(side="left",expand=1)
        self.CheckPeakNames = IntVar()
        Checkbutton(frame222,text="ShowNames",variable=self.CheckPeakNames, 
                           onvalue=1,offvalue=0,height=1, width=10, command = lambda: self.updateXRDgraph(0),fg='black',background='grey').pack(side=tk.LEFT,expand=1)
        frame223=Frame(frame22,borderwidth=0,  bg="grey")
        frame223.pack(fill=tk.BOTH,expand=1)
        self.AutoPeakDetecAdjust = IntVar()
        Checkbutton(frame223,text="Auto",variable=self.AutoPeakDetecAdjust, 
                           onvalue=1,offvalue=0,height=1, width=3, fg='black',background='grey').pack(side=tk.LEFT,expand=1)
        self.thresholdPeakDet = tk.DoubleVar()
        Entry(frame223, textvariable=self.thresholdPeakDet,width=5).pack(side=tk.LEFT,expand=1)
        self.thresholdPeakDet.set(0.05)
        tk.Label(frame223, text="Threshold", bg="grey").pack(side=tk.LEFT,expand=1)
        self.MinDistPeakDet = tk.DoubleVar()
        Entry(frame223, textvariable=self.MinDistPeakDet,width=3).pack(side=tk.LEFT,expand=1)
        self.MinDistPeakDet.set(40)
        tk.Label(frame223, text="MinDist", bg="grey").pack(side=tk.LEFT,expand=1)
        self.CheckPeakDetec = IntVar()
        Checkbutton(frame223,text="Show",variable=self.CheckPeakDetec, 
                           onvalue=1,offvalue=0,height=1, width=3, command = lambda: self.updateXRDgraph(0),fg='black',background='grey').pack(side=tk.LEFT,expand=1)
        
               
#        frame23=Frame(frame2,borderwidth=0,  bg="lightgrey")
#        frame23.pack(fill=tk.BOTH,expand=1)
#        frame231=Frame(frame23,borderwidth=0,  bg="lightgrey")
#        frame231.pack(fill=tk.BOTH,expand=1)
        self.ExportBut = Button(frame221, text="Export",command =self.Export).pack(side="left",expand=1)
        self.ExportRefFileBut = Button(frame221, text="ExportasRefFile",command = ()).pack(side="left",expand=1)
#        self.GraphCheck = IntVar()
#        legend=Checkbutton(frame23,text='Graph',variable=self.GraphCheck, 
#                           onvalue=1,offvalue=0,height=1, width=10, command = (), bg="lightgrey")
#        legend.pack(expand=1)
#        self.PeakData = IntVar()
#        legend=Checkbutton(frame23,text='PeakData',variable=self.PeakData, 
#                           onvalue=1,offvalue=0,height=1, width=10, command = (), bg="lightgrey")
#        legend.pack(expand=1)
        
        frame5=Frame(self.canvas0,borderwidth=0,  bg="white")
        frame5.pack(fill=tk.BOTH,expand=1)
        frame3=Frame(frame5,borderwidth=0,  bg="white")
        frame3.pack(side="left", fill=tk.BOTH,expand=1)
        frame32=Frame(frame3,borderwidth=0,  bg="white")
        frame32.pack(fill=tk.BOTH,expand=1)
        
        #listbox for imported samples
        self.frame322=Frame(frame32,borderwidth=0,  bg="white")
        self.frame322.pack(fill=tk.BOTH,expand=1)
        self.frame3221=Frame(self.frame322,borderwidth=0,  bg="white")
        self.frame3221.pack(fill=tk.BOTH,expand=1)
        importedsamplenames = StringVar()
        self.listboxsamples=Listbox(self.frame3221,listvariable=importedsamplenames, selectmode=tk.MULTIPLE,width=15, height=3, exportselection=0)
        self.listboxsamples.bind('<<ListboxSelect>>', self.updateXRDgraph)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3221, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)
        
        for item in Patternsamplenameslist:
            self.listboxsamples.insert(tk.END,item)

        #lisbox for ref pattern
        self.frame323=Frame(frame32,borderwidth=0,  bg="white")
        self.frame323.pack(fill=tk.BOTH,expand=1)
        self.frame3231=Frame(self.frame323,borderwidth=0,  bg="white")
        self.frame3231.pack(fill=tk.BOTH,expand=1)
        refsamplenames = StringVar()
        self.listboxref=Listbox(self.frame3231,listvariable=refsamplenames, selectmode=tk.MULTIPLE,width=15, height=3, exportselection=0)
        self.listboxref.bind('<<ListboxSelect>>', self.updateXRDgraph)
        self.listboxref.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3231, orient="vertical")
        scrollbar.config(command=self.listboxref.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxref.config(yscrollcommand=scrollbar.set)
        
        for item in refsamplenameslist:
            self.listboxref.insert(tk.END,item)
            
        
#        frame321=Frame(frame32,borderwidth=0,  bg="white")
#        frame321.pack(fill=tk.X,expand=0)
#        self.addtolistBut = Button(frame321, text="Add to list",command = ()).pack(side=tk.LEFT,expand=1)
#        self.RemoveFromListBut = Button(frame321, text="Remove from list",command = ()).pack(side=tk.LEFT,expand=1)




        self.frame4=Frame(frame5,borderwidth=0,  bg="white")
        self.frame4.pack(side="right",fill=tk.BOTH,expand=1)
        self.frame41=Frame(self.frame4,borderwidth=0,  bg="white")
        self.frame41.pack(side="right",fill=tk.BOTH,expand=1)
        
        
#        self.addtolistBut = Button(self.frame4, text="Add to list",command = ()).pack(side=tk.LEFT,expand=1)
#        self.TableBuilder(self.frame4)
        self.CreateTable()

#%%############# 
    def on_closing(self):
        global DATA, RefPattDATA, Patternsamplenameslist, colorstylelist
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            DATA={}
            RefPattDATA={}
            Patternsamplenameslist=[]
            colorstylelist = ['black', 'red', 'blue', 'brown', 'green','cyan','magenta','olive','navy','orange','gray','aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','darkblue','darkcyan','darkgoldenrod','darkgray','darkgreen','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategray','darkturquoise','darkviolet','deeppink','deepskyblue','dimgray','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','greenyellow','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgreen','lightgray','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategray','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
            plt.close()
            self.destroy()
            self.master.deiconify()
    def onFrameConfigure(self, event):
        #self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))
        self.canvas0.configure(scrollregion=(0,0,500,500))
            
#%%    
    def updateXRDgraph(self,a):
        global DATA, RefPattDATA, colorstylelist, samplestakenforplot
          
        self.XRDgraph.clear()
#        self.XRDgraphtwin.clear()

        
        coloridx=0
        #plot patterns from DATA
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            if self.changetoQ.get():
                minX=min(tth_to_q_list(DATA[samplestakenforplot[0]][2]))
                maxX=max(tth_to_q_list(DATA[samplestakenforplot[0]][2]))
            else:
                minX=min(DATA[samplestakenforplot[0]][2])
                maxX=max(DATA[samplestakenforplot[0]][2])
            minY=min(DATA[samplestakenforplot[0]][3])
            maxY=max(DATA[samplestakenforplot[0]][3])
            for item in samplestakenforplot:
                if self.changetoQ.get():
                    x = tth_to_q_list(DATA[item][2])
                else:
                    x = DATA[item][2]
                y = DATA[item][3]
                if min(x)<minX:
                    minX=min(x)
                if max(x)>maxX:
                    maxX=max(x)
                if min(y)<minY:
                    minY=min(y)
                if max(y)>maxY:
                    maxY=max(y)
                
                self.XRDgraph.plot(x,y, color=colorstylelist[coloridx], label=item)
                coloridx+=1
                
#            if self.changetoQ.get():
#                # Find min and max two theta, make a list of tth values for the tick labels
#                tth_min = int(math.ceil(q_to_tth(minX))); tth_max = int(math.ceil(q_to_tth(maxX)))
#                # If tth_min is odd, increment to use evens
#                if tth_min % 2 == 1:
#                    tth_min += 1
#                tth_list = list(np.arange(tth_min,tth_max,2))
#                
#                # find the q-values associated with these tth values; these are the tick positions in q
#                q_list = tth_to_q_list(tth_list)
#                
#                # New axis sharing y-axis with ax. Ticks at the top
#                self.XRDgraphtwin.spines["top"].set_position(("axes", 1))
#                # Same x limits at xlim
#                self.XRDgraphtwin.set_xlim(self.XRDgraph.get_xlim())
#                # Place the ticks at the right q-positions
#                self.XRDgraphtwin.set_xticks(q_list)
#                # Label the ticks with the tth values
#                self.XRDgraphtwin.set_xticklabels(tth_list, fontsize=14)
#                self.XRDgraphtwin.tick_params(direction='in', pad=1)
#                # Label the axis
#                self.XRDgraphtwin.set_xlabel('$^o2\\theta$ , Cu K-$\\alpha$', position=(0.08,0.97))
            
            #add text for Peak Names
            if self.CheckPeakNames.get():
                for item in range(len(peaknamesforplot)):
                    if self.changetoQ.get():
                        plt.text(peaknamesforplot[item][3],peaknamesforplot[item][1],peaknamesforplot[item][2],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')                  
                    else:
                        plt.text(peaknamesforplot[item][0],peaknamesforplot[item][1],peaknamesforplot[item][2],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')

            
        #plot from RefPattDATA
        reftakenforplot = [self.listboxref.get(idx) for idx in self.listboxref.curselection()]
        for item in reftakenforplot:
            if self.changetoQ.get():
                x = tth_to_q_list(RefPattDATA[item][0])
            else:
                x = RefPattDATA[item][0]
            y = RefPattDATA[item][1]
            
            lines = []
            for i in range(len(x)):
                pair=[(x[i],0), (x[i], y[i])]
                lines.append(pair)
            
            linecoll = matcoll.LineCollection(lines, color='black', linestyle='dashed') 
#            linecoll = matcoll.LineCollection(lines)
            self.XRDgraph.add_collection(linecoll)
            self.XRDgraph.scatter(x,y,label=item, color=colorstylelist[coloridx])
            coloridx+=1
            
            if self.CheckPeakNames.get():
                for item1 in range(len(RefPattDATA[item][0])):
                    if samplestakenforplot!=[]:
                        if RefPattDATA[item][0][item1]>minX and RefPattDATA[item][0][item1]<maxX:
                            plt.text(RefPattDATA[item][0][item1],RefPattDATA[item][1][item1],RefPattDATA[item][2][item1],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')
                    else:
                        plt.text(RefPattDATA[item][0][item1],RefPattDATA[item][1][item1],RefPattDATA[item][2][item1],rotation=90,verticalalignment='bottom',horizontalalignment='left',multialignment='center')

        
        #legends and graph styles
        if samplestakenforplot!=[] or  reftakenforplot!=[]:
            self.XRDgraph.legend()
        self.XRDgraph.set_ylabel("Intensity (a.u.)")
        if self.changetoQ.get():
            self.XRDgraph.set_xlabel('q (A$^{-1}$)')
        else:
            self.XRDgraph.set_xlabel("2\u0398 (degree)")
        if samplestakenforplot!=[]:
            self.XRDgraph.axis([minX,maxX,minY,1.1*maxY])  
            if self.ylabel.get():
                self.XRDgraph.set_yticklabels([])
                self.XRDgraph.set_yticks([])
                
#            self.XRDgraph.tick_params(direction='in', pad=1)
#            if self.changetoQ.get()==0:
#                self.XRDgraphtwin.axis([minX,maxX,minY,1.1*maxY])
#                self.XRDgraphtwin.tick_params(direction='in', pad=1)
#                self.XRDgraphtwin.set_xticklabels([])
#            else:
#                self.XRDgraphtwin.axis([q_to_tth(minX),q_to_tth(maxX),minY,1.1*maxY])
#                self.XRDgraphtwin.tick_params(direction='in', pad=1)
#                self.XRDgraphtwin.set_xlabel('$^o2\\theta$ , Cu K-$\\alpha$', position=(0.08,0.97))
#        
        plt.gcf().canvas.draw()
        self.CreateTable()


    class PopulateListofPeakNames(tk.Frame):
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
            global DATA, listofanswer, samplestakenforplot
                     
            rowpos=1
            if samplestakenforplot!=[]:
                for item in samplestakenforplot:
                    for item1 in range(len(DATA[item][4])):
                        label=tk.Label(self.frame,text=item,fg='black',background='white')
                        label.grid(row=rowpos,column=0, columnspan=1)
                        label=tk.Label(self.frame,text="%.2f"%DATA[item][4][item1]["Position"],fg='black',background='white')
                        label.grid(row=rowpos,column=1, columnspan=1)
                        textinit = tk.StringVar()
                        listofanswer[str(DATA[item][4][item1]["Position"])]=Entry(self.frame,textvariable=textinit)
                        listofanswer[str(DATA[item][4][item1]["Position"])].grid(row=rowpos,column=2, columnspan=2)
                        textinit.set(DATA[item][4][item1]["PeakName"])
        
                        rowpos=rowpos+1
            
        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas0.configure(scrollregion=self.canvas0.bbox("all"))

        
    def ChangePeakNames(self):
        global DATA
        
        self.window = tk.Toplevel()
        self.window.wm_title("Change Peak Names")
        center(self.window)
        self.window.geometry("400x300")
        
        Button(self.window, text="Update",
                            command = self.UpdatePeakNames).pack()
        
        self.PopulateListofPeakNames(self.window).pack(side="top", fill="both", expand=True)
    
    def UpdatePeakNames(self):
        global DATA, listofanswer, samplestakenforplot, peaknamesforplot
        
        peaknamesforplot=[]
       
        for item in samplestakenforplot:
            for item1 in range(len(DATA[item][4])):
                DATA[item][4][item1]["PeakName"]=listofanswer[str(DATA[item][4][item1]["Position"])].get()
                peaknamesforplot.append([DATA[item][4][item1]["Position"],DATA[item][4][item1]["Intensity"],DATA[item][4][item1]["PeakName"],tth_to_q(DATA[item][4][item1]["Position"])])
        
        self.window.destroy()
        self.updateXRDgraph(0)

        
#%%    
    def backgroundremoval(self):
        global DATA
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                y = DATA[item][3]
                y=np.array(y)
                base = peakutils.baseline(y, self.backgroundorder.get())
                DATA[item][3]=list(y-base)
        
        self.updateXRDgraph(0)
    
    def backgroundremovalImport(self):
        global DATA
        
        
        self.updateXRDgraph(0)
    
    def shiftX(self):
        global DATA
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                x = DATA[item][2]
                DATA[item][2] = [item1+self.shift.get() for item1 in x]
    
        self.updateXRDgraph(0)
        
    def shiftY(self):
        global DATA
#        print("here")
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
#                print(self.shiftYval.get())
                y = DATA[item][3]
                DATA[item][3] = [item1+self.shiftYval.get() for item1 in y]
    
        self.updateXRDgraph(0)
        
    def shifttoRef(self):
        global DATA
#        still to be implemented
#        automatic detection of peaks and comparison to the selected RefPattern
#        then shifts the data to match the ref peak
        
        
        self.updateXRDgraph(0)    
    
    def scaleYtoRef(self):
        global DATA
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                y = DATA[item][3]
                maxy=max(y)
                miny=min(y)
                DATA[item][3]=[((item1-miny)/(maxy-miny))*self.rescale.get() for item1 in y]
        
        self.updateXRDgraph(0)
        
    def backtoOriginal(self):
        global DATA
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for item in samplestakenforplot:
                DATA[item][2]=DATA[item][0]
                DATA[item][3]=DATA[item][1]
        
        self.updateXRDgraph(0)

#%%        
   
    def PeakDetection(self):
        global DATA,peaknamesforplot
        peaknamesforplot=[]  
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
#            positionlist=[]
#            peaknamelist=[]
#            intensitylist=[]
#            fwhmlist=[]
#            print("")
            for item in samplestakenforplot:
                #reinitialize list of dict
                DATA[item][4]=[]
                x=np.array(DATA[item][2])
                y=np.array(DATA[item][3])
                #get peak position
                if self.AutoPeakDetecAdjust.get():
                    threshold=0.01
                    MinDist=50
                    while(1):
                        indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
                        if len(indexes)<15:
                            self.thresholdPeakDet.set(threshold)
                            self.MinDistPeakDet.set(MinDist)
                            break
                        else:
                            threshold+=0.01
                else:
                    indexes=peakutils.indexes(y, thres=self.thresholdPeakDet.get(), min_dist=self.MinDistPeakDet.get())
#                print("")
#                print(len(indexes))
#                print(len(y))
                for item1 in range(len(indexes)):
                    tempdat={}
                    nbofpoints=80#on each side of max position
                    appendcheck=0
#                    print(indexes[item1])
                    if indexes[item1]>nbofpoints:
                        while(1):
                            try:
                                x0=x[indexes[item1]-nbofpoints:indexes[item1]+nbofpoints]
                                y0=y[indexes[item1]-nbofpoints:indexes[item1]+nbofpoints]
#                                print(len(y0))
                                base=list(peakutils.baseline(y0,1))
                                #baseline height
                                bhleft=np.mean(y0[:15])
                                bhright=np.mean(y0[-15:])
#                                baselineheightatmaxpeak=(bhleft+bhright)/2
                                baselineheightatmaxpeak=base[nbofpoints]
    #                            print(baselineheightatmaxpeak)
    #                            print("")
    #                            print(abs(bhleft-bhright))
                                if abs(bhleft-bhright)<100:#arbitrary choice of criteria...
                                    #find FWHM
                                    d=y0-((max(y0)-bhright)/2)
                                    ind=np.where(d>bhright)[0]
                                    
                                    hl=(x0[ind[0]-1]*y0[ind[0]]-y0[ind[0]-1]*x0[ind[0]])/(x0[ind[0]-1]-x0[ind[0]])
                                    ml=(y0[ind[0]-1]-hl)/x0[ind[0]-1]
                                    yfwhm=((max(y0)-baselineheightatmaxpeak)/2)+baselineheightatmaxpeak
                                    xleftfwhm=(yfwhm - hl)/ml
                                    hr=(x0[ind[-1]]*y0[ind[-1]+1]-y0[ind[-1]]*x0[ind[-1]+1])/(x0[ind[-1]]-x0[ind[-1]+1])
                                    mr=(y0[ind[-1]]-hr)/x0[ind[-1]]
                                    xrightfwhm=(yfwhm - hr)/mr
                                    
                                    FWHM=abs(xrightfwhm-xleftfwhm)
    #                                Peakheight=max(y0)-baselineheightatmaxpeak
                                    Peakheight=max(y0)-baselineheightatmaxpeak
                                    center=x[indexes[item1]]
    #                                print(nbofpoints)
    #                                print(baselineheightatmaxpeak)
                                    tempdat["Position"]=center
                                    tempdat["PositionQ"]=tth_to_q(center)
                                    tempdat["FWHM"]=FWHM
                                    tempdat["Intensity"]=Peakheight
                                    tempdat["PeakName"]=''
                                    
                                    appendcheck=1
                                    break
                                else:
                                    if nbofpoints>=15:
                                        nbofpoints-=10
                                    else:
                                        print("indexerror unsolvable")
                                        print(y[indexes[item1]])
                                        break
                            except IndexError:
                                if nbofpoints>=15:
                                    nbofpoints-=10
                                else:
                                    print("indexerror unsolvable")
                                    break
                        
                    if appendcheck:
                        DATA[item][4].append(tempdat)
        
        for item in samplestakenforplot:
            for item1 in range(len(DATA[item][4])):
                peaknamesforplot.append([DATA[item][4][item1]["Position"],DATA[item][4][item1]["Intensity"],DATA[item][4][item1]["PeakName"],DATA[item][4][item1]["PositionQ"]])
 
        self.CreateTable()
        self.updateXRDgraph(0)
        
#%%
    def importRefDATA(self):#not yet updated to nrel
        global DATA, RefPattDATA, refsamplenameslist

        #ask for the files
        file_path =filedialog.askopenfilenames(title="Please select the reference XRD pattern")
        
        #read the files and fill the RefPattDATA dictionary 
        for filename in file_path:
            filetoread = open(filename,"r", encoding='ISO-8859-1')
            filerawdata = filetoread.readlines()
            samplename=os.path.splitext(os.path.basename(filename))[0]
            refsamplenameslist.append(samplename)
            
            RefPattDATA[samplename]=[[],[],[]]
            for row in filerawdata:
                RefPattDATA[samplename][0].append(float(row.split("\t")[0]))
                RefPattDATA[samplename][1].append(float(row.split("\t")[1]))
                try:
                    RefPattDATA[samplename][2].append(str(row.split("\t")[2])[:-1])
                except:
                    RefPattDATA[samplename][2].append("")

        
        
        #update the listbox
        self.frame3231.destroy()
        self.frame3231=Frame(self.frame323,borderwidth=0,  bg="white")
        self.frame3231.pack(fill=tk.BOTH,expand=1)
        refsamplenames = StringVar()
        self.listboxref=Listbox(self.frame3231,listvariable=refsamplenames, selectmode=tk.MULTIPLE,width=15, height=3, exportselection=0)
        self.listboxref.bind('<<ListboxSelect>>', self.updateXRDgraph)
        self.listboxref.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3231, orient="vertical")
        scrollbar.config(command=self.listboxref.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxref.config(yscrollcommand=scrollbar.set)
        
        for item in refsamplenameslist:
            self.listboxref.insert(tk.END,item)
        
    
    def importDATA(self):
        global DATA, Patternsamplenameslist
        
        #ask for the files
        file_path =filedialog.askopenfilenames(title="Please select the XRD files")
        
        #read the files and fill the DATA dictionary 
        for filename in file_path:
            tempdat=[]
            filetoread = open(filename,"r", encoding='ISO-8859-1')
            filerawdata = list(filetoread.readlines())
            samplename=os.path.splitext(os.path.basename(filename))[0]
#            print(samplename)
            x=[]
            y=[]
                
#            for item in filerawdata:
#                x.append(float(item.split(' ')[0]))
#                y.append(float(item.split(' ')[1]))
            
#            for item in filerawdata:
#                print(item)
#                print(item.split(',')[0])
#                x.append(float(item.split(',')[0]))
#                y.append(float(item.split(',')[1]))  
#                
#            tempdat.append(x)#original x data
#            tempdat.append(y)#original y data
#            tempdat.append(x)#corrected x, set as the original on first importation
#            tempdat.append(y)#corrected y, set as the original on first importation 
#            tempdat.append([])#peak data, list of dictionaries
#            tempdat.append([])#
#            
#            DATA[samplename]=tempdat
#            Patternsamplenameslist.append(samplename)
            if '3DExplore ascii' in filerawdata[0]:
                for j in range(14,len(filerawdata)):
                    x.append(float(filerawdata[j].split('\t')[0]))#assume 2theta
                    y.append(float(filerawdata[j].split('\t')[1]))  
                tempdat.append(x)#original x data 2theta
                tempdat.append(y)#original y data
                tempdat.append(x)#corrected x, set as the original on first importation 2theta
                tempdat.append(y)#corrected y, set as the original on first importation 
                tempdat.append([])#peak data, list of dictionaries
                tempdat.append([])#
                
                DATA[samplename]=tempdat
                Patternsamplenameslist.append(samplename)
                
#                i=0
#                for j in range(len(filerawdata)):
#                    if ',' in filerawdata[j]:
#                        x.append(float(filerawdata[j].split(',')[0]))
#                        y.append(float(filerawdata[j].split(',')[1]))  
#                    else:
#                        tempdat.append(x)#original x data
#                        tempdat.append(y)#original y data
#                        tempdat.append(x)#corrected x, set as the original on first importation
#                        tempdat.append(y)#corrected y, set as the original on first importation 
#                        tempdat.append([])#peak data, list of dictionaries
#                        tempdat.append([])#
#                        
#                        DATA[samplename+str(i)]=tempdat
#                        Patternsamplenameslist.append(samplename+str(i))
#                        i+=1
#                        x=[]
#                        y=[]
#                        tempdat=[]
            else:
                i=0
                for j in range(len(filerawdata)):
                    if ',' in filerawdata[j]:
                        x.append(float(filerawdata[j].split(',')[0]))
                        y.append(float(filerawdata[j].split(',')[1]))  
                    else:
                        tempdat.append(x)#original x data
                        tempdat.append(y)#original y data
                        tempdat.append(x)#corrected x, set as the original on first importation
                        tempdat.append(y)#corrected y, set as the original on first importation 
                        tempdat.append([])#peak data, list of dictionaries
                        tempdat.append([])#
                        
                        DATA[samplename+str(i)]=tempdat
                        Patternsamplenameslist.append(samplename+str(i))
                        i+=1
                        x=[]
                        y=[]
                        tempdat=[]
        
        #update the listbox
        self.frame3221.destroy()
        self.frame3221=Frame(self.frame322,borderwidth=0,  bg="white")
        self.frame3221.pack(fill=tk.BOTH,expand=1)
        importedsamplenames = StringVar()
        self.listboxsamples=Listbox(self.frame3221,listvariable=importedsamplenames, selectmode=tk.MULTIPLE,width=15, height=3, exportselection=0)
        self.listboxsamples.bind('<<ListboxSelect>>', self.updateXRDgraph)
        self.listboxsamples.pack(side="left", fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(self.frame3221, orient="vertical")
        scrollbar.config(command=self.listboxsamples.yview)
        scrollbar.pack(side="right", fill="y")
        self.listboxsamples.config(yscrollcommand=scrollbar.set)
        
        for item in Patternsamplenameslist:
            self.listboxsamples.insert(tk.END,item)

#%%

    def Export(self):
        global DATA 
        
        
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes = (("graph file", "*.png"),("All Files", "*.*")))
        self.fig1.savefig(f, dpi=300) 

        
        testdata=['name\tPeakName\tPosition\tIntensity\tFWHM\n']
        
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for key in samplestakenforplot:
                for item in DATA[key][4]:
                    testdata.append(key +'\t'+ item["PeakName"]+'\t'+str("%.2f"%item["Position"])+'\t'+str("%.2f"%item["Intensity"])+'\t'+str("%.2f"%item["FWHM"])+'\n')
            
        file = open(f[:-4]+"PeakDat.txt",'w', encoding='ISO-8859-1')
        file.writelines("%s" % item for item in testdata)
        file.close()    
        
        #to do: export 2theta-intensity data for all curves selected in the graph, in one txt file, plottable in origin
                
        
        
    def ExportasRef(self):
        global DATA,RefPattDATA
        
        print("tobedone")

#%%        
    def CreateTable(self):
        global DATA
        global testdata
        testdata=[]
        #self.parent.grid_rowconfigure(0,weight=1)
        #self.parent.grid_columnconfigure(0,weight=1)
#        self.parent.config(background="white")
        
        self.frame41.destroy()
        self.frame41=Frame(self.frame4,borderwidth=0,  bg="white")
        self.frame41.pack(side="right",fill=tk.BOTH,expand=1)
                    
        samplestakenforplot = [self.listboxsamples.get(idx) for idx in self.listboxsamples.curselection()]
        if samplestakenforplot!=[]:
            for key in samplestakenforplot:
                for item in DATA[key][4]:
                    testdata.append([key,item["PeakName"],"%.2f"%item["Position"],"%.2f"%item["PositionQ"],"%.2f"%item["Intensity"],"%.2f"%item["FWHM"]])
            
        self.tableheaders=('name','PeakName','Position 2\u0398','Position q','Intensity','FWHM')
                    
        # Set the treeview
        self.tree = Treeview(self.frame41, columns=self.tableheaders, show="headings")
        
        for col in self.tableheaders:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
            self.tree.column(col, width=int(round(1.1*tkFont.Font().measure(col.title()))), anchor='n')   
        
        scrollbar = tk.Scrollbar(self.frame41, orient="vertical")
        scrollbar.config(command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill=tk.BOTH, expand=1)
        
        self.treeview = self.tree
        
        self.insert_data(testdata)    
    
    def insert_data(self, testdata):
        for item in testdata:
            self.treeview.insert('', 'end', values=item)

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
        
            
#%%#############         
###############################################################################        
if __name__ == '__main__':
    
    app = XRDApp()
    app.mainloop()

