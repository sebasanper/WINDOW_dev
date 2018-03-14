import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def bearing_plot(df, dirn='wind_dir', dir_info='Wind from the North', 
                 ax=None, N=16, bottom=0, loc_0='N', loc_90 ='E', zero_is_nan=True):
    # zero means that no wind is blowing so we will remove those values.
    if zero_is_nan:
        df = df[df[dirn]>0]
    if ax is None:
        ax = plt.subplot(111, polar=True)
    theta = np.linspace(0.0, 2 *np.pi, N+1)
    radii, _ = np.histogram(df[dirn].values, bins=(theta/np.pi*180))
    width = (2*np.pi) / N

    bars = ax.bar(theta[:-1], radii, width=width, bottom=bottom)
    
    ax.set_theta_zero_location(loc_0)
    clockwise = ['N', 'E', 'S','W', 'N']
    if clockwise[clockwise.index(loc_0)+1] == loc_90:
        ax.set_theta_direction(-1)

    # Use custom colors and opacity
    for r, bar in zip(radii, bars):
        bar.set_facecolor(plt.cm.jet(r/float(np.max(radii))))
        bar.set_alpha(0.8)
    ax.text(0.5,1.1,dir_info, horizontalalignment='center', transform=ax.transAxes, fontsize=14)
    return(ax)

def windrose(df, dirn='wind_dir', speed='wind_speed', dir_info='Wind from the North', 
             ax=None, N=16, bottom=0, loc_0='N', loc_90 ='E', zero_is_nan=True):
    if zero_is_nan:
        df = df[df[dirn]>0]
    if ax is None:
        ax = plt.subplot(111, polar=True)
    theta = np.linspace(0.0, 2 *np.pi, N+1)
    width = (2*np.pi) / N
    
    ax.set_theta_zero_location(loc_0)
    clockwise = ['N', 'E', 'S','W', 'N']
    if clockwise[clockwise.index(loc_0)+1] == loc_90:
        ax.set_theta_direction(-1)
    
    srange = zip([0,5,10,20,50], [5,10,20,50,100], ['#0000dd','green','#dddd00','#FF7800','#dd0000']) 
    ntot = df[dirn].count()
    
    radii0 = [bottom]*N
    for smin, smax, c in srange:
        cond = ((df[speed]>=smin) & (df[speed]<smax))
        radii, _ = np.histogram(df[dirn][cond].values, bins=(theta/np.pi*180))
        radii = radii/float(ntot)*100
        bars = ax.bar(theta[:-1], radii, width=width, bottom=radii0, facecolor=c, alpha=0.8)
        #print smin, smax, c, radii
        radii0+= radii
    ax.text(0.5,1.1,dir_info, horizontalalignment='center', transform=ax.transAxes, fontsize=14)
    return(ax)
        
def windrose_cbar(fig=None):
    '''
    If you have a figsize in mind, then pass a figure object to this function
    and the colorbar will be drawn to suit
    '''
    import matplotlib.patches as mpatch
    
    if fig is None:
        fig = plt.figure(figsize=(5,.7))
    y = fig.get_figwidth()
    
    srange = zip([0,5,10,20,50], [5,10,20,50,100], ['#0000dd','green','#dddd00','#FF7800','#dd0000']) 
    n=1
    for smin, smax, c in srange:
        ax = plt.subplot(1,5,n)
        patch = mpatch.FancyBboxPatch([0,0], 1, 1, boxstyle='square', facecolor=c)
        ax.add_patch(patch)
        plt.axis('off')
        if y>=12:
            ax.text(.1, .4, '{smin} - {smax} km/hr'.format(smin=smin, smax=smax),
                    fontsize=min(18, y+2), fontdict = {'color': 'white'})
        else:
            ax.text(.1, .4, '{smin} - {smax}\nkm/hr'.format(smin=smin, smax=smax),
                    fontsize=min(14, y+5), fontdict = {'color': 'white'})
        n+=1

wind_dir = np.random.rand(100)*360
wind_speed = np.random.rand(100)*70
a = np.array([wind_dir, wind_speed])
a.shape

df = pd.DataFrame(a.T, columns=['wind_dir', 'wind_speed'])

bearing_plot(df, dirn='wind_dir', dir_info='Wind from the North', loc_0 = 'N', loc_90='E')

windrose(df, dirn='wind_dir', speed='wind_speed', loc_0 = 'N', loc_90='E')
windrose_cbar()
