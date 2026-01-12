# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 10:57:06 2025

@author: bleue
"""

import os
os.add_dll_directory("C:/Program Files/Pico Technology/SDK/lib")
# from picoscope import ps2000a
from picoscope import ps3000a
import time 
import numpy as np
from matplotlib import pyplot as plt
from numba import njit



__all__ = [
    "connexion_pico",
    "set_param",
    "set_trigger",
    "run_scope",
    #"start_pico_for_APD",
    "count_peaks",
    "check_ps",
    "stream"
]


#global variable
count_rate_saturation = 1/90e-9
dt=4e-9 #sample step fixed to 4ns to detecte all photon signal shape
#duration=0.1 #seconde
#channel=["A","B"]



def check_ps(ps, channel):
    """
    The function check if the scope works well with a short acquisiton

    Parameters
    ----------
    ps : picoscope instance
        
    channel : list
        list of the channel to be used

    Returns
    -------
    None.

    """
    try:

        
        #channel config
        for ch in channel :
            ps.setChannel(ch, #sets all used channels
                          coupling='DC', #DC mode
                          VRange=5.0) #voltage amplitude s
        ps.setSamplingInterval(1e-6, #sample interval = 1um for this test
                               0.01)  # 10 ms acquisition time
    
        
        # run acquisition
        ps.runBlock() #this functioni runs picoscope acquisition
        
        # waiting
        ps.waitReady()  #function to wait the runblock ends

            
        #print("info du picoscpe:", ps.getAllUnitInfo())
        print("PicoScope ",ps.getUnitInfo("VariantInfo"),"is  ready.") #print the serie number of the scope if it' ready
        
        ps.stop() #stop the picoscope
        
        
    except Exception as e:
        print("Error Picoscope connexion:", e)
        
def connexion_pico(channel): #on peut pas la mettre dans stream / un psq ps3000a.PS3000a ca bug si on le relance, il faut le faire qu'une fois ou bien faire scope.close
    """
    Initialize connection to PicoScope and configure channels.
    
    Parameters
    ----------
    channel : list
        List of channels to initialize (e.g., ['A', 'B']).
    
    Returns
    -------
    scope : ps3000a.PS3000a
        PicoScope instance, ready to use.
    """
    scope = ps3000a.PS3000a()  # open connection to PicoScope
    check_ps(scope, channel)   # configure channels
    return scope
        
        
def set_param(ps, channel, duration, dt):
    """
    Configure the PicoScope acquisition parameters.
    
    Parameters
    ----------
    ps : picoscope instance

    channel : list
        List of channels to be configured (e.g., ['A', 'B']).
    duration : float
        Total acquisition duration in seconds. (equiv. integration time, e.g 1sec total acquisition time)
    dt : float
        sampling interval in seconds.
    
    Returns
    -------
    total_samples : int
        Number of samples that will actually be acquired.
    times : numpy.ndarray
        Time axis corresponding to the acquisition, from 0 to duration.
    """
    
    # Initialize the selected channels with DC coupling and ±5 V range
    for ch in channel:
        ps.setChannel(ch, coupling='DC', VRange=5.0)
        
    # Set the sampling interval and duration.
    # The PicoScope may adjust dt to the closest valid value.
    actual_interval, total_samples,_ = ps.setSamplingInterval(sampleInterval= dt, duration=duration)
    
    # Build the time axis based on the actual sampling interval and number of samples
    times = np.linspace(0, actual_interval * total_samples, total_samples) 
    
    #print(f"dt reel : {actual_interval:.2e} s - samples : {total_samples}")
        
    return total_samples, times

def set_trigger(ps, channel, trigger=True):
    """
    Configure the PicoScope trigger settings. The trigger can only be set for one channel even if several are used

    Parameters
    ----------
    ps : object
        PicoScope instance.
    channel : list
        List of channels to be configured (e.g., ['A', 'B']).
    trigger : bool, optional
        If True, a trigger is enabled on channel 'A' at 1.5 V rising edge.
        If False, no trigger is used. Default is True.

    Returns
    -------
    None
    """    
    channel_trig='A' #trigger channel
    threshold = 1.5 # trigger threshold in volts
    
    
    #With trigger enabled
    if trigger:
        for ch in channel:
            # Configure each channel with DC coupling and ±5 V range
            ps.setChannel(ch, coupling='DC', VRange=5.0)
            
            # Configure trigger on channel A
            ps.setSimpleTrigger(
                trigSrc=channel_trig,      # Trigger source
                threshold_V=threshold,     # Threshold voltage (1.5 V to discriminate photons from noise)
                direction="Rising",        # Rising edge trigger
                delay=0,                   # No delay
                timeout_ms=5000            # Timeout of 5 s
            )
        
        
    # Without trigger
    else:
        for ch in channel:
            # Configure channels without trigger
            ps.setChannel(channel=ch, coupling="DC", VRange=5.0)
            print(f'channel {ch} set')
            ps.setSimpleTrigger(ch,enabled=False)  # Disable trigger

@njit    
def count_peaks(signal, threshold=2.0):
    """
    A function that counts how many peaks are in an array

    Parameters
    ----------
    signal : array_like
        Voltage data (e.g. output of ps.getDataV()).
    threshold : float, optional
        Voltage threshold above which a crossing is considered a peak.
        Default is 2.0. 

    Returns
    -------
    n_peaks : int
       Number of detected peaks.

    """
    signal = np.asarray(signal)  # convert NumPy array

    #Counts the threshold crossings on rising edges above 2V
    over = signal > threshold #above 2.0 V, it's a photon and not noise
    n_peaks = np.sum((~over[:-1]) & over[1:]) + int(over[0])    #number of peaks
        
    return n_peaks


def run_scope(ps, times, total_samples, channel, duration, dt, plot=True):
    """
    Perform a simple acquisition in block mode (runBlock) without trigger.

    Parameters
    ----------
    ps : object
        PicoScope instance.
    times : numpy.ndarray
        Time axis for the acquisition, generated beforehand.
    total_samples : int
        Number of samples to acquire.
    channel : list
        List of channels to be acquired (e.g., ['A', 'B']).
    duration : float
        Acquisition duration in seconds.
    dt : float
        Desired sampling interval in seconds (may differ from actual).
    plot : bool, optional
        If True, plot the acquired waveforms. Default is True.

    Returns
    -------
    count_rate_dict : dict
        Dictionary containing the photon count rate per channel (photons/s).
    """
    data = {}          # Dictionary to store acquired signals for each channel
    n_peaks = {}       # Dictionary to store number of detected peaks per channel
    count_rate_dict = {}  # Dictionary to store photon count rate per channel
    
    
    #start acquisition
    ps.runBlock()
    ps.waitReady()  # Wait until the acquisition is complete


    
    # get the data 
    if ps.isReady():
        for ch in channel:
            signal = ps.getDataV(ch, total_samples)   # Get voltage data for channel ch         
            n_peaks[ch] = count_peaks(signal)         # Count the number of peaks in the signal
            data[ch] = signal                         # Store the signal for later use
      
    # Compute count rate for each channel 
    for ch in channel:
        count_rate = n_peaks[ch]/duration # Photon count rate = counts / acquisition time
        
        count_rate_dict[ch] = count_rate  # Save result in dictionary
        
        # Print results
        print(f"Canal {ch} : {count_rate} ph/sec")
        
        
        # Check if count rate exceeds detector limit (saturation)
        if count_rate  >= count_rate_saturation : # APD maximum ~1e7 counts/s
            print(r"/!\ saturation ")
    
    print("=================================")

    
    # Plot acquired signals if requested
    if plot:
        for ch in channel: 
            plt.plot(times, data[ch], linewidth=0.5, label = f"Channel {ch}")  # Plot each channel
    
        plt.xlabel("Time (s)")
        plt.ylabel("Tension (V)")
        plt.title("runBlock (w/o trigger)")
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        plt.show()

    
    return count_rate_dict # Return dictionary of count rates per channel
 


    
    

def stream(ps, times, total_samples, channel, duration, dt, plot=False):
    """
    Continuous acquisition using run_scope in a loop.
    
    Parameters
    ----------
    ps : object
        PicoScope instance.
    times : numpy.ndarray
        Time axis for acquisition.
    total_samples : int
        Number of samples to acquire.
    channel : list
        List of channels to be acquired.
    duration : float
        Acquisition duration in seconds.
    dt : float
        Desired sampling interval in seconds.
    plot : bool, optional
        If True, plot the acquired waveforms. Default is False.
    """

    try:
        while True:
            run_scope(ps, times, total_samples,
                      channel, duration, dt, plot)

    except KeyboardInterrupt:
        print("\nStreaming stopped by user.")

    finally:
        ps.stop()   # stop acquisition properly
    
    

    
# def start_pico_for_APD(scope,channel, duration,dt):      
#     total_samples, times = set_param(scope,channel, duration, dt) #calcul du temps total    
#     set_trigger(scope, channel, trigger=False) #pas de trigger    
#     stream(scope, times, total_samples, channel, duration, dt, plot=False) #lancement du stream qui affiche le flux
    
    
    
    
    
    

