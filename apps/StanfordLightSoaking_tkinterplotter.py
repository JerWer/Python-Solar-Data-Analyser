#! python3

import os,datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NavigationToolbar2TkAgg
import tkinter as tk
from tkinter import *
from tkinter import messagebox, Button, Frame, Toplevel, OptionMenu, StringVar
from tkinter import filedialog
import numpy as np
import os.path
import scipy.interpolate as interp
import os
#import datetime

'''
To Do:

normalize at time X specified by user

selectable substrates to plot in listbox
    
Add option to only plot MPPT
Add option to only plot every x IV curves
Add option to only plot first x IV curves (follow same rule as stop plotting condition)
'''

#get folder path 
#show to the user a listbox with the subdirectories names, selectable
#user can therefore select the samples he wants 
#import the data only from those samples
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

importedData = []

class StanfordStabilityDat(Toplevel):

    def __init__(self, *args, **kwargs):
        
        Toplevel.__init__(self, *args, **kwargs)
        Toplevel.wm_title(self, "StanfordStabilityDat")
        Toplevel.config(self,background="white")
        self.wm_geometry("100x100")
        center(self)
        self.initUI()

    def initUI(self):
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        
        
        
#        self.canvas0 = tk.Canvas(self, borderwidth=0, background="white")
#        self.superframe=Frame(self.canvas0,background="white")
        
#        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas0.yview)
#        self.canvas0.configure(yscrollcommand=self.vsb.set)
#        self.vsb.pack(side="right", fill="y")
#        self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas0.xview)
#        self.canvas0.configure(xscrollcommand=self.hsb.set)
#        self.hsb.pack(side="bottom", fill="x")
        
#        self.canvas0.pack(side="left", fill="both", expand=True)
#        frame1=Frame(self.canvas0,borderwidth=0,  bg="white")
#        frame1.pack(fill=tk.BOTH,expand=1)
#        frame1.bind("<Configure>", self.onFrameConfigure)
#        self.canvas0.create_window((1,4), window=self.superframe, anchor="nw", 
#                                  tags="self.superframe")
#        self.superframe.bind("<Configure>", self.onFrameConfigure)
        
        ############ the figures #################
#        self.fig = plt.figure(figsize=(9, 6))
#        self.fig.patch.set_facecolor('white')
#        canvas = FigureCanvasTkAgg(self.fig, frame1)
#        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
#        self.fig1 = self.fig.add_subplot(221)   
#        self.fig2 = self.fig.add_subplot(222)
#        self.fig3 = self.fig.add_subplot(223)
#        self.fig4 = self.fig.add_subplot(247)
#        self.fig5 = self.fig.add_subplot(248)
#        
#        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
#        self.toolbar.update()
#        canvas._tkcanvas.pack(fill = BOTH, expand = 1) 
        
        self.selectSamplesBut = Button(self, text="SelectFolder", command = self.SelectFolder)
        self.selectSamplesBut.pack(side=tk.LEFT,expand=1)
        
#        Ytype = ["Original","Normalized"]
#        self.YtypeChoice=StringVar()
#        self.YtypeChoice.set("Original") # default choice
#        self.dropMenuFrame = OptionMenu(self.canvas0, self.YtypeChoice, *Ytype, command=self.plotter())
#        self.dropMenuFrame.pack(side=tk.LEFT,fill=tk.X,expand=1)
#        
#        self.exportTxt = Button(self.canvas0, text="Export Txt rawdat", command = ())
#        self.exportTxt.pack(side=tk.LEFT,expand=1)

    def onFrameConfigure(self, event):
        self.canvas1.configure(scrollregion=self.canvas1.bbox("all"))
        #self.canvas0.configure(scrollregion=(0,0,500,500))
        
    def SelectFolder(self):
        current_path = os.getcwd()
        self.changedFilePath = filedialog.askdirectory(title = "Choose the folder that has the date title", initialdir=os.path.dirname(current_path))
        
        self.subDirs = [i for i in os.listdir(self.changedFilePath) if os.path.isdir(os.path.join(self.changedFilePath,i))]
        self.subDirs.sort()
        print(self.subDirs)
        
        self.selectSamples() 
        
        
    def selectSamples(self):
        self.withdraw()
        self.selectwin=tk.Tk()
        self.selectwin.wm_title("Select 1 or more")
        self.selectwin.geometry("250x200")
        center(self.selectwin)
        self.lb=tk.Listbox(self.selectwin, selectmode=tk.MULTIPLE)
    
        for i in range(len(self.subDirs)):
            self.lb.insert("end",self.subDirs[i])
        self.lb.pack(side="top",fill="both",expand=True)
        scrollbar = tk.Scrollbar(self.lb, orient="vertical")
        scrollbar.config(command=self.lb.yview)
        scrollbar.pack(side="right", fill="y")
        self.lb.config(yscrollcommand=scrollbar.set)
        
        delbut = tk.Button(self.selectwin, text="Select", command = self.selectbut)
        delbut.pack()
    
    def selectbut(self): 
        self.samplelist=[self.subDirs[i] for i in list(self.lb.curselection())]
#        print(self.samplelist)
        self.selectwin.destroy() 
        self.importData()
    
    def on_closing(self):
        
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            plt.close()
            self.destroy()
            self.master.deiconify()
    def on_closingPlot(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            plt.close()
            self.plotwin.destroy()
            self.deiconify()
    
    def importData(self):
        #written by Eli Wolf
        
        # loop over each cell
        global importedData #importedData[samplename][]
        importedData=[]
        subDirs=self.samplelist
        for i, subDir in enumerate(subDirs):
            print('Processing Cell: '+subDir)           
            
            files = os.listdir(os.path.join(self.changedFilePath,subDir))
            files.sort()
        
            mpptFiles = [file for file in files if subDir+'_LT_' in file]
            mpptFiles.sort()
            # mpptFiles = mpptFiles[0:4]
        
            self.ivFiles = [file for file in files if subDir+'_IV_' in file]
            self.ivFiles.sort()
            # ivFiles = ivFiles[0:1]
        
            importedData.append([])
            importedData[i].append([])
            importedData[i].append([])
            
            #import IV Scans
            n_skip=5
            
            for j, ivFile in enumerate(self.ivFiles):
                print ('Processing IV File: '+ivFile)
                iFile = (os.path.join(self.changedFilePath,subDir,ivFile))
                filetoread = open(iFile,"r", encoding='ISO-8859-1')
                filerawdata = list(filetoread.readlines())
                importedData[i][0].append([])
                voltage=[]
                current=[]
                for line in range(n_skip,len(filerawdata)):
                    voltage.append(float(filerawdata[line].split('\t')[2]))
                    current.append(float(filerawdata[line].split('\t')[3]))
#                print(len(voltage))
#                print(len(current))
                importedData[i][0][j].append(voltage)
                importedData[i][0][j].append(current)
        
                with open(iFile, 'r', encoding='ISO-8859-1') as file:
                     for k, line in enumerate(file):
                         if k == 2:
                             ivTime = datetime.datetime.strptime(line[:-1],'%m/%d/%Y %H:%M:%S')
                             ivTime -= datetime.datetime(1899,12,30,0,0,0,0)
                             ivTime = ivTime.total_seconds()/(24*3600)
        
                importedData[i][0][j].insert(0,ivTime)

            #import MPPT Data
            n_skip = 1
            mpptTime = []
            mpptPower = []
            mpptVoltage = []
            mpptCurrent = []
            for k, mpptFile in enumerate(mpptFiles):
                print ('Processing MPPT File: '+mpptFiles[k])
                iFile = (os.path.join(self.changedFilePath,subDirs[i],mpptFiles[k]))
                filetoread = open(iFile,"r", encoding='ISO-8859-1')
                filerawdata = list(filetoread.readlines())
#                iData = pd.read_csv(iFile, delimiter='\t', header = None, names=['Time', 'Hour', 'Voltage', 'Current', 'Power', 'B', 'Jsc', 'Voc', 'FF', 'P/B', 'Temp'], skiprows = n_skip)
                Time=[]
                Power=[]
                voltage=[]
                current=[]
                for line in range(n_skip,len(filerawdata)):
                    Time.append(float(filerawdata[line].split('\t')[0]))
                    Power.append(float(filerawdata[line].split('\t')[4]))
                    voltage.append(float(filerawdata[line].split('\t')[2]))
                    current.append(float(filerawdata[line].split('\t')[3]))
#                print(len(Time))
#                print(len(Power))
#                print(len(voltage))
#                print(len(current))
                mpptTime += Time
                mpptPower += Power
                mpptVoltage += voltage
                current =[-x for x in current]
                mpptCurrent += current
#                print(len(current))
#            print(type(importedData[i][0][0][0]))
#            print(len(mpptTime))
#            print(len(mpptCurrent))
            importedData[i][1].append([24*(x - importedData[i][0][0][0]) for x in mpptTime])#0
            importedData[i][1].append(mpptPower)#1
            importedData[i][1].append(mpptVoltage)#2
            importedData[i][1].append(mpptCurrent)#3
            importedData[i][1].append([1+(m-mpptPower[0])/mpptPower[0] for m in mpptPower])#4
            importedData[i][1].append([1+(m-mpptVoltage[0])/mpptVoltage[0] for m in mpptVoltage])#5
            importedData[i][1].append([1+(m-mpptCurrent[0])/mpptCurrent[0] for m in mpptCurrent])#6
            maxp=max(mpptPower)
            importedData[i][1].append([1+(m-maxp)/maxp for m in mpptPower])#7
            maxv=max(mpptVoltage)
            importedData[i][1].append([1+(m-maxv)/maxv for m in mpptVoltage])#8
            maxc=max(mpptCurrent)
            importedData[i][1].append([1+(m-maxc)/maxc for m in mpptCurrent])#9
            
        self.plotter()
            
    def plotter(self):
        global importedData
        
        self.plotwin=tk.Tk()
        self.plotwin.wm_title("The graphs")
        self.plotwin.geometry("800x600")
        center(self.plotwin)
        self.plotwin.protocol("WM_DELETE_WINDOW", self.on_closingPlot)
        self.canvas1 = tk.Canvas(self.plotwin, borderwidth=0, background="white")
        self.canvas1.pack(side="left", fill="both", expand=True)
        frame1=Frame(self.canvas1,borderwidth=0,  bg="white")
        frame1.pack(fill=tk.BOTH,expand=1)
        frame1.bind("<Configure>", self.onFrameConfigure)
        ############ the figures #################
        self.fig = plt.figure(figsize=(6, 4))
        self.fig.patch.set_facecolor('white')
        canvas = FigureCanvasTkAgg(self.fig, frame1)
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=1)
        self.fig1 = self.fig.add_subplot(221)   
        self.fig2 = self.fig.add_subplot(222)
        self.fig3 = self.fig.add_subplot(223)
        self.fig4 = self.fig.add_subplot(247)
        self.fig5 = self.fig.add_subplot(248)
        
        self.toolbar = NavigationToolbar2TkAgg(canvas, frame1)
        self.toolbar.update()
        canvas._tkcanvas.pack(fill = tk.BOTH, expand = 1) 
        
        Ytype = ["Original","NormalizedAtT0", "NormalizedAtMax"]
        self.YtypeChoice=StringVar()
        self.YtypeChoice.set("Original") # default choice
        self.dropMenuFrame = OptionMenu(self.canvas1, self.YtypeChoice, *Ytype, command=self.plot)
        self.dropMenuFrame.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        
        self.exportTxt = Button(self.canvas1, text="Export Txt rawdat", command = self.exportTxtfiles)
        self.exportTxt.pack(side=tk.LEFT,expand=1)
        
        self.plot(1)
        
    def exportTxtfiles(self):
#        print('exporting')
        current_path = os.getcwd()
        f = filedialog.askdirectory(title = "Choose the folder to save the raw txt files", initialdir=os.path.dirname(current_path))

#        f = filedialog.asksaveasfilename(defaultextension=".txt")
        for j,subDir in enumerate(self.samplelist):
            #mppt data
            DATAforexport=['Time\tPower\tVoltage\tCurrent\n']
            for i in range(len(importedData[j][1][0])):
                DATAforexport.append(str(importedData[j][1][0][i])+'\t'+str(importedData[j][1][1][i])+'\t'+str(importedData[j][1][2][i])+'\t'+str(importedData[j][1][3][i])+'\n')
            
            if self.YtypeChoice.get()=='NormalizedAtT0':
                DATAforexport=['Time\tPower\tVoltage\tCurrent\n']
                for i in range(len(importedData[j][1][0])):
                    DATAforexport.append(str(importedData[j][1][0][i])+'\t'+str(importedData[j][1][4][i])+'\t'+str(importedData[j][1][5][i])+'\t'+str(importedData[j][1][6][i])+'\n')
            elif self.YtypeChoice.get()=='NormalizedAtMax': 
                DATAforexport=['Time\tPower\tVoltage\tCurrent\n']
                for i in range(len(importedData[j][1][0])):
                    DATAforexport.append(str(importedData[j][1][0][i])+'\t'+str(importedData[j][1][7][i])+'\t'+str(importedData[j][1][8][i])+'\t'+str(importedData[j][1][9][i])+'\n')           
            else:
                DATAforexport=['Time\tPower\tVoltage\tCurrent\n']
                for i in range(len(importedData[j][1][0])):
                    DATAforexport.append(str(importedData[j][1][0][i])+'\t'+str(importedData[j][1][1][i])+'\t'+str(importedData[j][1][2][i])+'\t'+str(importedData[j][1][3][i])+'\n')

#            file = open(str(f[:-4]+'_'+subDir+".txt"),'w', encoding='ISO-8859-1')
            file = open(os.path.join(f,subDir+"_mppt.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAforexport)
            file.close()
            
            #iv curves
            DATAforexport=[]
            dat=list(zip(*self.ivcurvestoexport[j]))
            for i in range(len(dat)):
                line=''
                for item in dat[i]:
                    line+=str(item)+'\t'
                DATAforexport.append(line[:-2]+'\n')
            
            file = open(os.path.join(f,subDir+"_ivcurves.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in DATAforexport)
            file.close()
            #iv parameters
            
            file = open(os.path.join(f,subDir+"_ivparam.txt"),'w', encoding='ISO-8859-1')
            file.writelines("%s" % item for item in self.ivparamtoexport[j])
            file.close()
        
    def plot(self,a):
        global importedData
        self.fig1.clear()
        self.fig2.clear()
        self.fig3.clear()
        self.fig4.clear()
        self.fig5.clear()
        
        subDirs=self.samplelist
#        normalize = 1
#        figs = []
        axs = [self.fig1,self.fig2,self.fig3]
        
        for i,parameter in enumerate(['Power','Voltage','Current']):
#        	figs.append(plt.figure(parameter))
#        	axs.append(figs[i].add_subplot(111))
            for j,subDir in enumerate(subDirs):
                if self.YtypeChoice.get()=='NormalizedAtT0':
#                    axs[i].plot(importedData[j][1][0],[1+(m-importedData[j][1][i+1][0])/importedData[j][1][i+1][0] for m in importedData[j][1][i+1]],linestyle='-',label=subDir)
                    axs[i].plot(importedData[j][1][0],importedData[j][1][i+4],linestyle='-',label=subDir)
                elif self.YtypeChoice.get()=='NormalizedAtMax':
#                    axs[i].plot(importedData[j][1][0],[1+(m-max(importedData[j][1][i+1]))/max(importedData[j][1][i+1]) for m in importedData[j][1][i+1]],linestyle='-',label=subDir)                   
                    axs[i].plot(importedData[j][1][0],importedData[j][1][i+7],linestyle='-',label=subDir)
                else:
                    axs[i].plot(importedData[j][1][0],importedData[j][1][i+1],linestyle='-',label=subDir)
            axs[i].set_ylabel(parameter)
            axs[i].set_xlabel('Time (Hours)')
            axs[i].legend()
        
        # Plot One Device
        # Make Plot Canvas
#        fig, ax = plt.subplots(1,2)
        ax=[self.fig4,self.fig5]
        
        # Add Origin Lines for IV Curves
        ax[0].axhline(y=0, color='k')
        ax[0].axvline(x=0, color='k')
        
        self.ivcurvestoexport=[]
        self.ivparamtoexport=[]
        currentMax = 0
        for i, subDir in enumerate(subDirs):
            ivcurvestoexport=[]
            ivparamtoexport=['Jsc\tVoc\tVmpp\tJmpp\tPmpp\n']
            for j, ivFile in enumerate(self.ivFiles):
                # Find Voc and Jsc
                xs = importedData[i][0][j][1]
                ys = importedData[i][0][j][2]
                ys=[-y for y in ys]
                
                ivcurvestoexport.append(['Voltage']+xs)
                ivcurvestoexport.append(['Current']+ys)
            
                ps=[a*b for a,b in zip(xs,ys)]
#               ps = xs*ys
            
                pMax = max(ps)
                xMax = [i for i, j in enumerate(ps) if j == pMax][0]
#                print(xMax)
            
                fjsc = interp.interp1d(xs,ys)
                fvoc = interp.interp1d(ys,xs)
            
                jsc = fjsc(0)
                voc = fvoc(0)
            
                ax[0].plot(voc,0,marker='o',color='k')
                ax[0].plot(0,jsc,marker='o',color='k')
                ax[0].plot(xs[xMax],ys[xMax],marker='o',color='k')
                ax[0].plot(xs,ys,linestyle='-')
                
                ivparamtoexport.append(str(jsc)+'\t'+str(voc)+'\t'+str(xs[xMax])+'\t'+str(ys[xMax])+'\t'+str(pMax)+'\n')
            
                ax[1].plot(24*(importedData[i][0][j][0] - importedData[0][0][0][0]),pMax,marker='o')
            
                mag = abs(np.floor(np.log10(pMax)))
                newMax = np.ceil(10**mag*pMax)*10**(-1*mag)
                if newMax > currentMax:
                    currentMax = newMax
            
                ax[0].grid()
            self.ivcurvestoexport.append(ivcurvestoexport)
            self.ivparamtoexport.append(ivparamtoexport)
            ax[1].plot(importedData[i][1][0],importedData[i][1][1],linestyle='-',color='k')
        
        #change ylim properly
        mag = abs(np.floor(np.log10(max(importedData[i][1][1]))))
        # mag += 0
        newMax = np.ceil(10**mag*max(importedData[i][1][1]))*10**(-1*mag)
        if newMax > currentMax:
            currentMax = newMax
        
        ax[1].set_ylim(bottom = 0, top = currentMax)
        
        plt.gcf().canvas.draw()
#        plt.show()
        

###############################################################################        
if __name__ == '__main__':
    app = StanfordStabilityDat()
    app.mainloop()

