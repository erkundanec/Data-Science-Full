# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 11:37:13 2020

@author: Sumanshu
"""

import numpy as np
import random as rnd
import matplotlib.pyplot as plt

r=3
fig_sz=(3,3)
fig1=plt.figure(figsize=fig_sz)
ax1=plt.axes([0.125,0.125,0.75,0.75])
d_tot=1000
d_circ=0
area_square=(2*r)**2
pi=np.pi
plt.xlim([-r,r])
plt.ylim([-r,r])
plt.axis('square')
k=0
theta=np.arange(0,2*pi,0.01)

for jj in range(d_tot):
    k +=1
    x=rnd.uniform(-r,r)
    y=rnd.uniform(-r,r)
    dist=np.sqrt(x**2+y**2)
    
    if dist<=r: 
        d_circ += 1
        ax1.plot(x,y,'r.')
    else:
        ax1.plot(x,y,'b.')
    pr=d_circ/k
    area=pr*area_square
    # print(area)


plt.xticks(np.linspace(-r, r,2*r+1))
plt.yticks(np.linspace(-r, r,2*r+1))
ax1.plot(r*np.cos(theta),r*np.sin(theta),'k-',linewidth=2.0)

print('Calculated area of circle from simulation:', area)
area_circ=pi*r**2
print('Calculated area of circle using equation:',area_circ)
fig1.savefig('monte-carlo.png',dpi=300)