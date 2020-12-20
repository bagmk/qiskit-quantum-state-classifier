#!/usr/bin/env python
# coding: utf-8

# In[ ]:
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from cycler import cycler
from scipy.stats import linregress

def define_color_cycle(name) :  
    cmap = get_cmap(name)  
    colors = cmap.colors  
    plt.rc('axes', prop_cycle=cycler(color=colors))

def plot_curves(data,curve_set, tit_0, tit_its=[], lab_its=[],
                left_xlimit = 0, right_xlimit = 120,
                bottom_ylimit = -0.05, top_ylimit = 1.0,plot_raw = False,
                color_name = "tab20", max_x = 500):
    define_color_cycle(color_name)    
    plt.clf()
    plt.figure(figsize=(12.,8.)) 
    plt.xlim(left_xlimit,right_xlimit)
    plt.ylim(bottom_ylimit,top_ylimit)

    shots_list = []
    for mark_ind,exp_index in enumerate(curve_set):  
        exp = data[exp_index]
        eps = exp["epsilon"]
        ydata = exp["error_curve"]
        window = exp["window"]        
        pol = exp["SG_pol"]
        shots = exp["shots"]
        shots_rate = exp["shots_rate"] 
        label_0 = ""                
        for lab_it in lab_its: 
            label_0 = label_0 + lab_it +": "+ str(exp[lab_it])+"  "
        
        xdata = np.array(range(1,len(ydata)+1))
                    
        if shots< max_x-window:
            label_scat = label_0 + '$\hat{r}_{max}$= %5.4f for%4.0f shots' %(shots_rate,shots)
        else:
            label_scat = label_0 + "! $n_s$ > " + str(max_x)
        
        c=None        
        if exp["device"] == "ideal_device":
            c="grey"
            if exp["metric"] == "sqeuclidean":
                    c="k"
        plt.plot(xdata, ydata[0:], c=c)     

        offset = 0.0
        offset += 0.25*shots_list.count(shots)*(-1)**shots        
        
        plt.scatter(shots+offset,shots_rate,
            label = label_scat, s=100, c=c)
        shots_list.append(shots)
                                
    label_eps = "$\epsilon:$ "+str(eps)+"  $\hat{r}$: interpolated error rate" 
    
    zero_level = plt.plot([left_xlimit, right_xlimit],[0.0,0.0], '--')
                         
    plt.setp(zero_level, color='k', linewidth=1.0)
    plt.xticks(np.arange(0, right_xlimit+5,5))
    plt.xlabel("$n$")
    plt.ylabel('$\widehat{r}_{mean}$ ')
    
    tit_1 =""
    for tit_it in tit_its: 
            tit_1 = tit_1 + " - " + tit_it +": "+ exp[tit_it]
    
    plt.title(tit_0+tit_1)
    plt.legend()
    plt.show()
    return

def plot_scatter(df, xdata, title,
            left_xlimit = 0.0, right_xlimit = 1.05,
            bottom_ylimit = 0.0, top_ylimit = 100,
            color_name = "tab10"):
    define_color_cycle(color_name)
    plt.figure(figsize=(10.,6.))
    plt.figure(figsize=(12.,8.)) 
    plt.xlim(left_xlimit,right_xlimit)
    plt.ylim(bottom_ylimit,top_ylimit)
    shots_list = []
    x_list = []
    for index in df.index:        
        offset = 0.0
        x = df[xdata][index]
        y = df['log_shots'][index]

        c=None        
        if df['device'][index] == "ideal_device":
            c="grey"
            if df["metric"][index] == "sqeuclidean":
                    c="k"
        offset=0.0 # because the two following statements are not used 
       # if x in x_list:
            #offset += 0.5*shots_list.count(y)*(-1)**y
        
        plt.scatter(x,y+offset,
                    label = df.device[index]+", log_shots="+str(round(y,3)),
                    s=100, c=c)
        shots_list.append(y)
        x_list.append(x)
    start_index = 0
    if xdata == 'fidelity':
        start_index = 1 # case where the first value concerns the ideal device
    
    if xdata == 'QV': # specific for QV
        plt.xticks([8,16,32])
        
    x = df[xdata].values.tolist()
    y = df['log_shots'].values.tolist()
    
    gradient, intercept, r_value, p_value, std_err = linregress(x[start_index:],y[start_index:])
    mn=np.min(x)
    mx=np.max(x)
    x1=np.linspace(left_xlimit,right_xlimit,500)
    y1=gradient*x1+intercept
    comment = "r="+str(round(r_value,3))+"  p="+str(round(p_value,5))
    plt.plot(x1,y1,'k--',label=comment)

    plt.ylabel("$\ln \; n_s$")
    plt.xlabel(xdata)
    plt.title(title)
    plt.legend() 
    plt.show()        