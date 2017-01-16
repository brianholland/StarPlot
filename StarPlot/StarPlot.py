
# coding: utf-8

import requests, pandas as pd, StringIO, re, matplotlib.pyplot as plt, math, numpy as np
from bs4 import BeautifulSoup
from mpl_toolkits.mplot3d import Axes3D
#%matplotlib notebook

def cart(d):
    """Function to give Cartesian coordinates from the record.  
Or use astropy if you don't want to roll your own.
Inputs:
    d: a dictionary or Pandas series that includes 'Galactic' with text of longitude and latitude, 
        and also 'Dist' for distance"""

    gal = d['Galactic']
    if '--' in gal: #handle special coords for Sol
        gal = '0 0'

    lon, lat= 2 * math.pi / 360 * np.array(map(float,re.split('\\s*',gal)))
    xyz     = math.cos(lat) * np.array([math.cos(lon), math.sin(lon), 0])
    xyz[-1] = math.sin(lat)
    xyz    *= d['Dist']
    x,y,z   = xyz
    return pd.Series(dict(gallat=lat, gallon=lon, x=x, y=y, z=z))

#Get the data we need.  It isn't all prettified - some numbers are left as text for example.

page = requests.get('http://www.atlasoftheuniverse.com/50lys.html') #get the whole page
soup = BeautifulSoup(page.content, 'lxml') #parse with BeautifulSoup so can easily grab tag with the meat
s =  soup.find('pre').text #the child with the data; it's the 'pre' tag

#You have to check what to skip: which rows, what footer etc.  Check footer notes on page for column meanings.
#pd.read_fwf reads a fixed-width file.
stars= pd.read_fwf(StringIO.StringIO(s), index_col=0, skiprows=[0,1,3,4], skipfooter=22)

#Add columns from the embedded data ...
stars = pd.concat([stars
     , stars.apply(lambda r: pd.Series(re.split(r'\s*', r['Classification     Visual Abs']) #Split at whitespace (\s)
                    , index=['Classification','Visual','Abs']), axis=1) #Will use Abs for size later
     , stars.apply(cart, axis=1)  # the Cartesian coordinates; this returns a dataframe.
    ], axis=1    #concatenate along columns, not rows.
    )
stars['Abs'] = stars['Abs'].map(float) #A

#Colors that will be assigned to certain stars.  Others are yellow.
col = {'k':['Sun','Alpha Canis Majoris']
      , 'b':['Alpha Centauri']}
colinv = {v:k for k,l in col.items() for v in l} #map from star to colors, could go directly to this.
stars['color'] = pd.Series({_i:colinv.get(_i, 'y') for _i in stars.index})

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.scatter3D(stars['x'] ,stars['y'], stars['z'], s=stars['Abs']**2
             , c=stars['color'], marker='o', edgecolor='', depthshade=True)
stars.apply(lambda s: ax.plot3D(s.x*np.ones(2), s.y*np.ones(2), [0, s.z]
              , c='b', alpha=0.3, linestyle={True:'solid',False:'dotted'}[s.z>0])
         , axis=1) #draw lines for each star to the x-y plane, solid from above, dashed from below
for _i in colinv.keys(): #Show names of special-colored stars
    s = stars.loc[_i] #for convenience below
    ax.text3D(s.x, s.y, s.z, _i) #the name

#x, y axes (positive) to 50 light-years
ax.plot3D([0,50], [0,0], [0,0], c='k', alpha=0.5)
ax.plot3D([0,0], [0,50], [0,0], c='k', alpha=0.5)

#distance rings, @ 10ly radii
grad = pd.Series(np.arange(0,1.01,0.01) * 2. * math.pi)
cx = grad.map(math.cos)
cy = grad.map(math.sin)
cz = np.zeros(len(cx))
for r in np.arange(10,60,10):
    ax.plot3D(cx*r, cy*r, cz*r, c='k', alpha=0.3)
ax.set_axis_off()

plt.show()




