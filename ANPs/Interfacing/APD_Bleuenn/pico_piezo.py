# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 14:53:14 2025

@author: bleue
"""
import sys
import matplotlib.pyplot as plt
import numpy as np
import time

#tous les codes sont là
sys.path.append(r"C:\Users\User\Desktop\APD")

from PiezoStageControl import Piezoconcept
from pico3000 import*
from pico3000 import  dt




   
    
def connect_Piezo_Ps(channel):
    """
    Connects to both the PiezoConcept stage and the PicoScope.

    Parameters
    ----------
    channel : list
        List of channels to initialize on the PicoScope (e.g., ['A', 'B']).

    Returns
    -------
    tuple
        (PiezoStage, scope) where:
        - PiezoStage : instance of the Piezoconcept class (stage controller)
        - scope : PicoScope instance initialized via `connexion_pico(channel)`
    """
    # Connect to the PiezoConcept stage via serial port COM9
    PiezoStage = Piezoconcept(port='COM9')
    print(PiezoStage.ser.isOpen())
    
    # Display device information
    infos = PiezoStage.INFOS()
    print("=== Infos PiezoStage ===")
    print(infos)
    
    # Connect to PicoScope with the given channels
    scope = connexion_pico(channel)
    return PiezoStage, scope



def recenterPiezo(PizoStage):
    """
    Recenters the PiezoStage to its middle positions along X and Y axes.

    Parameters
    ----------
    PiezoStage : object
        Instance of the PiezoConcept stage controller.
    """
    # Move X axis to its center position (25 µm)
    PiezoStage.MOVEX(25,unit="u") 
    
    # Move Y axis to its center position (12.5 µm)
    PiezoStage.MOVEY(12.5, unit="u") #the middle for y position is 12.5



def CountRate_xy(x, y, scope, PiezoStage, channel, duration, total_samples, plot=False, unit="u"): 
    """
    Measures the count rate at a given (x, y) position of the PiezoStage.

    Parameters
    ----------
    x : float
        Target position along the X-axis.
    y : float
        Target position along the Y-axis.
    scope : object
        PicoScope instance used for acquisition.
    PiezoStage : object
        Instance of the PiezoConcept stage controller.
    channel : list
        List of channels to be acquired from the PicoScope.
    duration : float
        Acquisition duration in seconds.
    total_samples : int
        Number of samples to acquire.
    plot : bool, optional
        If True, plot the acquired waveforms (default is False).
    unit : str, optional
        Unit for the PiezoStage movement (default is "u" for microns).

    Returns
    -------
    count_rate : array-like
        Measured count rate from the PicoScope.
    """

    # Configure acquisition parameters (sampling, time axis, etc.)
    total_samples, times = set_param(scope, channel, duration, dt)   
    
    # Move the PiezoStage to the given (x, y) position

    PiezoStage.MOVEX(x,unit=unit)    
    PiezoStage.MOVEY(y,unit=unit)
    
    # Wait for the stage to stabilize before measurement
    time.sleep(duration)
        
    # Measure photon count rate at the given (x, y) position
    count_rate = run_scope(scope, times, total_samples, channel, duration, dt, plot=plot) #count rate A and countrate B
    
    
    return count_rate
    

        
def scan(size, npoints, scope, PiezoStage, channel, duration, total_samples, plot_scan=True):
    """
    2D scan with the PiezoStage and measure photon count rates.
    /!\ PiezoStage moves are weird. Move(1um) moves 0.5um in reality
    
    Parameters
    ----------
    size : float
        size of the scan (in microns)
    npoints : int
        Number of points along one axis (grid will be npoints x npoints).
    scope : object
        PicoScope instance.
    PiezoStage : object
        PiezoConcept stage instance.
    channel : list
        Channels to measure from the PicoScope.
    duration : float
        Acquisition time for each pixel (in sec).
    total_samples : int
        Number of samples acquired per measurement.
    plot_scan : bool, optional
        If True, plot the 2D scan maps. Default is True.
    
    Returns
    -------
    A_map, B_map : 2D numpy.ndarray
        2D photon count maps for channels A and B.
    """
    
    # Prevent too large scans (> 10 µm piezostage limit)
    if size>=10:
        print("Too large scan : size < 10um")
        return
    
    # Step size in scan grid (in microns)
    step = 2*size/(npoints-1) 
    
    # If the step size is very small, switch to nanometers
    #/!\ DISCLAIMER : this part doesn't works : the piezo stage doesn't moove if the step is too small. To be updated.
    if step<=0.1:
        unit = "n"
        step = step*1e3 # convert to nm
        
        x_init = (25-size)*1e3  # initial x position (nm) for the scan start
        y_init = (12.5 - size)*1e3  # initial y position (nm) for the scan start
    
    else : 
        unit = "u"
        x_init = (25-size) # initial x position (µm)
        y_init = (12.5 - size) # initial y position (µm)
        
    # Initialize 2D arrays for photon count maps
    A_map = np.zeros((npoints, npoints))
    B_map = np.zeros((npoints, npoints))
    
    
    # Loop over scan positions
    for j in range(npoints):
        x = x_init+ j*step
        for i in range(npoints):
            y = y_init + i*step
            
            # Measure photon count rate at (x, y)
            count_rate = CountRate_xy(x, y, scope, PiezoStage, channel, duration, total_samples, unit=unit)
            
            A_map[i, j] = count_rate["A"]
            B_map[i, j] = count_rate["B"]
            
            
    # Move Piezo back to center position   
    PiezoStage.MOVEX(25,unit="u")   
    PiezoStage.MOVEY(12.5,unit="u")
            
    # Normalize color scale between the two channels    
    common_min = 0
    common_max = max(A_map.max(), B_map.max())
        

    
    # Plot scan maps if requested
    if plot_scan:
        x_vals = (step/2) * np.linspace(-(npoints-1)/2, (npoints-1)/2, npoints)
        y_vals = (step/2)* np.linspace(-(npoints-1)/2, (npoints-1)/2, npoints)

        fig, axs = plt.subplots(1, 2, figsize=(10, 4))

        im1 = axs[0].imshow(A_map, extent=[x_vals[0], x_vals[-1], y_vals[0], y_vals[-1]],origin="lower", aspect='auto',vmin=common_min, vmax=common_max)
        axs[0].set_title("Channel A")
        axs[0].set_xlabel("x (um)")
        axs[0].set_ylabel("y (um)")
        cbar1 = fig.colorbar(im1, ax=axs[0])
        cbar1.set_label('ph/s')

        im2 = axs[1].imshow(B_map, extent=[x_vals[0], x_vals[-1], y_vals[0], y_vals[-1]],origin="lower", aspect='auto',vmin=common_min, vmax=common_max)
        axs[1].set_title(" Channel B")
        axs[1].set_xlabel("x (um)")
        axs[1].set_ylabel("y (um)")
        cbar2 = fig.colorbar(im2, ax=axs[1])
        cbar2.set_label('ph/s')
    
        plt.tight_layout()
        plt.show()
        
     

    return A_map, B_map


# #%% param pico

# channel=["A","B"]
# duration=0.01
# #dt = 4e-9
    
    
    
# #%%connexionPicoPiezo

# PiezoStage, scope = connect_Piezo_Ps(channel)

# #%%picoparams

# total_samples, times= set_param(scope, channel, duration, dt) 

# #%%2D scan
# size = 1 #1 um
# npoints = 5


# scan(size, npoints, scope, PiezoStage, channel, duration, total_samples, plot_scan=True)

# #%%close
# PiezoStage.close()
# scope.close()  




#============OTHER TESTS===============================
#%%
# PiezoStage.MOVEX(100, unit="n")
# #%%
# PiezoStage.MOVEY(32, unit="n")
#%%move piezo scan w/o count rate
# step = 0.1
# for j in range(10):
#     print("j",j)
#     for i in range(10):
#         y = 12.5 + step
#         x = 25 + step
#         z=0
#         PiezoStage.MOVEX(x, unit="u")
#         PiezoStage.MOVEY(y, unit="u")
#         time.sleep(0.5)
#         print("i",i)
        

#%%
# #print(PiezoStage.INFOS())
# print(f'\nX position: {PiezoStage.GET_X()}')

# #%%move relatif ?

# PiezoStage.move_relX(10, unit="u")



# #%%
# print(f'\nY position: {PiezoStage.GET_Y()}')

    
#%%test position / mesure de flux
# x=50
# y=25

# CountRate_xy(x, y, scope, PiezoStage, channel, duration, total_samples, plot=False, unit="u")


 
    
    
    