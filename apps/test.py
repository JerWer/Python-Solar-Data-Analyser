##! python3
#
#import os
#from tkinter import filedialog
#import csv
#import math
#from tkinter import Tk, messagebox
#import matplotlib.pyplot as plt
#from scipy.optimize import curve_fit
#import numpy as np
#from scipy import integrate
#from scipy.interpolate import interp1d
#import peakutils
#from peakutils.plot import plot as pplot
#import xlsxwriter
#import xlrd
#from matplotlib import colors as mcolors
#
#def listofpeakinfo(x,y,indexes,samplename):#x and y are np.arrays
#
#    peakdata=[]
#    try:
#        plt.clear()
#    except:
#        pass
#    plt.figure(figsize=(10,6))
#    plt.plot(x,y,'black',label=samplename)
#    
#    
#    for item in range(len(indexes)):
#        nbofpoints=80#on each side of max position
#        while(1):
#            try:
#                x0=x[indexes[item]-nbofpoints:indexes[item]+nbofpoints]
#                y0=y[indexes[item]-nbofpoints:indexes[item]+nbofpoints]
#                base=list(peakutils.baseline(y0,1))
#                #baseline height
#                bhleft=np.mean(y0[:20])
#                bhright=np.mean(y0[-20:])
##                baselineheightatmaxpeak=(bhleft+bhright)/2
#                baselineheightatmaxpeak=base[nbofpoints]
#                
#                if abs(bhleft-bhright)<100:#arbitrary choice of criteria...
#                    #find FWHM
#                    d=y0-((max(y0)-bhright)/2)
#                    ind=np.where(d>bhright)[0]
#                    
#                    hl=(x0[ind[0]-1]*y0[ind[0]]-y0[ind[0]-1]*x0[ind[0]])/(x0[ind[0]-1]-x0[ind[0]])
#                    ml=(y0[ind[0]-1]-hl)/x0[ind[0]-1]
#                    yfwhm=((max(y0)-baselineheightatmaxpeak)/2)+baselineheightatmaxpeak
#                    xleftfwhm=(yfwhm - hl)/ml
#                    hr=(x0[ind[-1]]*y0[ind[-1]+1]-y0[ind[-1]]*x0[ind[-1]+1])/(x0[ind[-1]]-x0[ind[-1]+1])
#                    mr=(y0[ind[-1]]-hr)/x0[ind[-1]]
#                    xrightfwhm=(yfwhm - hr)/mr
#                    
#                    FWHM=abs(xrightfwhm-xleftfwhm)
#                    Peakheight=max(y0)-baselineheightatmaxpeak
#                    center=x[indexes[item]]
#                    
#                    
#                    plt.plot(x0, y0, 'red')
##                    plt.plot([x0[0],x0[-1]],[bhleft,bhright],'blue')
#                    plt.plot(x0,base,'blue')
##                    plt.plot(x0,y0,ms=0)
#                    plt.plot([xleftfwhm,xrightfwhm],[yfwhm,yfwhm],'green')
#                    plt.text(center,max(y0)+200,str('%.1f' % float(center)),rotation=90,verticalalignment='bottom',horizontalalignment='center',multialignment='center')
##                    nbpoints=50
##                    plt.plot(x[indexes[item]-nbpoints:indexes[item]+nbpoints],peakutils.baseline(y[indexes[item]-nbpoints:indexes[item]+nbpoints],1),'blue')
#                    
#                    peakdata.append([center,FWHM,Peakheight])
##                    peakdata.append([center,Peakheight])
#                    break
#                else:
#                    if nbofpoints>=15:
#                        nbofpoints-=10
#                    else:
#                        print("indexerror unsolvable")
#                        break
#            except IndexError:
#                if nbofpoints>=15:
#                    nbofpoints-=10
#                else:
#                    print("indexerror unsolvable")
#                    break
#    plt.scatter(x[indexes],y[indexes],c='red',s=12)
#    plt.legend()
#    plt.ylabel("Intensity (a.u.)")
#    plt.xlabel("2\u0398 (degree)")
##    plt.savefig(samplename+'.pdf')
#    plt.show()
##    plt.close()
#    return peakdata
#
#
#
#file_path =filedialog.askopenfilenames(title="Please select the XRD files")
##select a result folder
#
#current_path=os.path.dirname(os.path.dirname(file_path[0]))
##    print(current_path)
##folderName = filedialog.askdirectory(title = "choose a folder to export the auto-analysis results", initialdir=current_path)
#os.chdir(current_path)
#
#DATA=[]
###analyze and create data list
###export graphs on-the-fly
##
##for filename in file_path:
##    filetoread = open(filename,"r", encoding='ISO-8859-1')
##    filerawdata = filetoread.readlines()
##    samplename=os.path.splitext(os.path.basename(filename))[0]
##
##    x=[]
##    y=[]
##        
##    i=0
##    for j in range(len(filerawdata)):
##        if ',' in filerawdata[j]:
##            x.append(float(filerawdata[j].split(',')[0]))
##            y.append(float(filerawdata[j].split(',')[1]))  
##        else:
##            x=np.array(x)
##            y=np.array(y)
###            threshold=0.01
###            MinDist=50
###            while(1):
###                indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
###        #        print(len(indexes))
###                if len(indexes)<15:
###                    break
###                else:
###                    threshold+=0.01
###            
###            dat=listofpeakinfo(x,y,indexes,samplename)
###            
###            DATA.append([str(samplename)+str(i),x,y])#[samplename,X,Y,[[center,FWHM,Peakheight],[]...],maxpeakheight]
##
##            
##            plt.figure(figsize=(10,6))
##            plt.plot(x,y,'black',label=samplename)  
##            plt.scatter(x,peakutils.baseline(y,7),c='red',s=5) 
###            plt.scatter(x,peakutils.baseline(y,7),c='blue',s=5)
###            plt.scatter(x,peakutils.baseline(y,8),c='green',s=5)
##              
##            i+=1
##            x=[]
##            y=[]            
##            
#lambdaXRD=1.54
#
#def q_to_tth(Q):
#    "convert q to tth, lam is wavelength in angstrom"
#    return 360/np.pi * np.arcsin(Q * lambdaXRD / (4 * np.pi))
#
#def tth_to_q(tth):
#    "convert tth to q, lam is wavelength in angstrom"
#    return 4 * np.pi * np.sin(tth * np.pi/(2 * 180)) / lambdaXRD    
#
#for filename in file_path:
#    filetoread = open(filename,"r", encoding='ISO-8859-1')
#    filerawdata = list(filetoread.readlines())
#    samplename=os.path.splitext(os.path.basename(filename))[0]
#
##    filedat=[]
##    for j in range(len(filerawdata)):
##        filedat.append(str(q_to_tth(float(filerawdata[j].split(',')[0])))+'\t'+filerawdata[j].split(',')[1])
##        
##    file = open(samplename+".txt",'w', encoding='ISO-8859-1')
##    file.writelines("%s" % item for item in filedat)
##    file.close() 
#    
#    x=[]
#    y=[]
#    for j in range(len(filerawdata)):
#        x.append(q_to_tth(float(filerawdata[j].split(',')[0])))
#        y.append(float(filerawdata[j].split(',')[1]))  
#    x=np.array(x)
#    y=np.array(y)
#    threshold=0.01
#    MinDist=50
#    while(1):
#        indexes = peakutils.indexes(y, thres=threshold, min_dist=MinDist)
##        print(len(indexes))
#        if len(indexes)<15:
#            break
#        else:
#            threshold+=0.01
#    
##    dat=listofpeakinfo(x,y,indexes,samplename)
#    dat2=[x[indexes],y[indexes]]
##    print(len(dat2[0]))
#            
##    dat2=list(map(list, zip(*dat)))
#    
#    y=[1000*(m-min(dat2[1]))/(max(dat2[1])-min(dat2[1])) for m in dat2[1]]#rescale between 0 and 1000
#
##    print(len(y))
#    filedat=[]
#    for j in range(len(dat2[0])):
#        filedat.append(str(dat2[0][j])+'\t'+str(y[j])+'\n')
#        
#    file = open('RohitJACS_'+samplename+".txt",'w', encoding='ISO-8859-1')
#    file.writelines("%s" % item for item in filedat)
#    file.close()     
#    
#
#
#"""
#need to make autoanalysis of peaks
#get position and intensities
#normalize to 1000
#export list of peaks for ref
#
#"""
#
#
#
#
#
#
#
#
#


import matplotlib.pyplot as plt
import numpy as np

num_plots = 20

# Have a look at the colormaps here and decide which one you'd like:
# http://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html
colormap = plt.cm.gist_ncar
plt.gca().set_prop_cycle(plt.cycler('color', plt.cm.jet(np.linspace(0, 1, num_plots))))

# Plot several different functions...
x = np.arange(10)
labels = []
for i in range(1, num_plots + 1):
    plt.plot(x, i * x + 5 * i)
#    labels.append(r'$y = %ix + %i$' % (i, 5*i))

# I'm basically just demonstrating several different legend options here...
#plt.legend(labels, ncol=4, loc='upper center', 
#           bbox_to_anchor=[0.5, 1.1], 
#           columnspacing=1.0, labelspacing=0.0,
#           handletextpad=0.0, handlelength=1.5,
#           fancybox=True, shadow=True)

plt.show()



      