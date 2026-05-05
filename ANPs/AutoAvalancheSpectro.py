import numpy as np
import os
import sys
import time
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import simpson
from scipy.stats import linregress

def GetPointSpectro(Power, 
                    SpectrumName, 
                    MyDataFolder,
                    IsFolderChecked = False, 
                    DelayIntegrationTime = 3, 
                    WLRange = np.array([780, 820])):
    #input RotorStage, PowerMeter, SaveDataFolder
    #Move to power
    fMoveToPower(RotorStage, PowerMeter, Power, *PowerRangeFitParameters)
    
    #Take a measurement with integration time
    GetASpectrum(DelayIntegrationTime)
    CurrentPower = fMeasurePower(PowerMeter)
    CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
    
    #Saving spectrum
    IsFolderChecked = SaveASpectrum(MyDataFolder, SpectrumName, False)
        
    #Integrate the spectrum
    FileNamePath =  MyDataFolder + "\\" + SpectrumName + ".txt"
    WL, Intensity = np.loadtxt(FileNamePath, dtype = float, delimiter = ';', skiprows = 3, converters =  lambda x: x.replace(',', '.'), encoding = None, unpack = True)
    
    BackgroundRef = np.mean(Intensity[-20:-1])
    Background = np.ones(Intensity.shape) * BackgroundRef   
    Intensity_Corrected = Intensity - Background
    
    WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
    WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
    
    Lum = np.sum(Intensity_Corrected[WLRangeIdxMin:WLRangeIdxMax])
    #Save point

    with open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a') as FileInfo:
        FileInfo.write(f'{Power}\t{CurrentPower}\t{CurrentTime}\t{Lum}\n')
    plt.plot(CurrentPower, Lum, 'r+')
    return CurrentPower, Lum

def FindAvalanche(
            SaveDataFolder,
            Pmin,
            Pmax,
            Ratio,
            integration_time = 3):
    
    print("Autodetection is running ...")
    rough_step_gap = (Pmax - Pmin) / 100 #First measurement and gap between measurements
    fine_step_gap = rough_step_gap /10 #Resolution of the avalanche
    PowerLimit = Pmax / 5 #Safety
    LumQueueSize =  int(2 * rough_step_gap // fine_step_gap)
    SlopeQueueSize = 3
    
    #Create the output folder and files
    
    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
    os.makedirs(MyDataFolder)
    
    FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'w')
    FileInfo.write(f'Power\tCurrentPower\tTime\tLuminosity\tInt. time = {integration_time}\tP_min = {Pmin}\tP_max = {Pmax}\n')
    FileInfo.close()
    
    print(f'New folder and file created in {MyDataFolder}')
    
    #Dark noise measurement (6 points)
    Power = Pmin
    noise_lum_list = np.zeros(6)
    
    for l in range(6):
        SpectrumName = f"Dark{l}"
        noise_lum_list[l] = GetPointSpectro(Power, SpectrumName, MyDataFolder)[1]
        
    noise = [np.mean(noise_lum_list), np.max(noise_lum_list)]
    print("\n\n\nNoise calibrated")
    
    #Avalanche find (noise exit)
    InNoise = True
    LumNoiseExit = [0, 0]
    PowNoiseExit = [0, 0]
    index = 5
    
    while InNoise and Power < PowerLimit:
        index += 1
        Power += rough_step_gap
        SpectrumName = f"Noise{index}"
        pump, measure = GetPointSpectro(Power, SpectrumName, MyDataFolder)
        
        if (measure - noise[1] > noise[0]):
            #Ensure true noise exit
            LumNoiseExit[0] = measure
            PowNoiseExit[0] = pump
            SpectrumName = f"Try{index}"
            pump, measure = GetPointSpectro(Power, SpectrumName, MyDataFolder)
            if (measure - noise[1] > noise[0] * 2):
                LumNoiseExit[1] = measure
                PowNoiseExit[1] = pump
                InNoise = False
                print("\n\n\nNoise exit found")
          
    #Area scan -> looking for the avalanche slow-down
    Searching = True

    #Creation of the queue that computes the luminescence slope
    LastNPump = np.zeros(LumQueueSize)
    LastNLum = np.zeros(LumQueueSize)
    
    LastNPump[-2] = PowNoiseExit[0]
    LastNPump[-1] = PowNoiseExit[1]
    LastNLum[-2] = LumNoiseExit[0]
    LastNLum[-1] = LumNoiseExit[1]    
    for j in range(LumQueueSize - 2):
        index += 1 
        SpectrumName = f"Avalanche{index}"
        LastNPump[j], LastNLum[j] = GetPointSpectro(Power + (2 - LumQueueSize + j) * fine_step_gap, SpectrumName, MyDataFolder)
    
    Power += fine_step_gap #Highest power used in a measurement and last in queue

    #Creation of the queue that computes the max avalanche region
    SlopeQueue = np.ones(SlopeQueueSize) * (-1)
    AllTimeMaxMinOfQueue = -1
    MaxOfQueue = 0
    MinOfQueue = -1
    
    Avalanche = (0, 0)
    
    #Computing the avalanche peak (max slope)
    
    #First slope
    fit_params = linregress(np.log10(LastNPump), np.log10(LastNLum))
    slope_ini = fit_params.slope
    SlopeQueue[-1] = slope_ini
    
    #Loop
    
    while Power < PowerLimit: #TEMPORARY
        index += 1 
        SpectrumName = f"Avalanche{index}"
        #Update power and the queue of measures then find the slope
        Power += fine_step_gap
        for i in range(LumQueueSize - 1):
            LastNLum[i] = LastNLum[i + 1]
            LastNPump[i] = LastNPump[i + 1]
        LastNPump[-1], LastNLum[-1] = GetPointSpectro(Power, SpectrumName, MyDataFolder)

        fit_params = linregress(np.log10(LastNPump), np.log10(LastNLum))
        slope_next = fit_params.slope
        
        
        #Update the slope queue
        for k in range(SlopeQueueSize - 1):
            SlopeQueue[k] = SlopeQueue[k + 1]
        SlopeQueue[-1] = slope_next
        
        MaxOfQueue = max(SlopeQueue)
        MinOfQueue = min(SlopeQueue)
        
        if Searching and MinOfQueue > AllTimeMaxMinOfQueue:
            AllTimeMaxMinOfQueue = MinOfQueue
            #Mark the spot
            adjust = (LumQueueSize - SlopeQueueSize) // 2 - LumQueueSize // 10 - 1
            tempx, tempy = [LastNPump[adjust], LastNLum[adjust]]
            Avalanche = tempx, tempy
        elif not Searching:
            Power += rough_step_gap - fine_step_gap
        
        #Check if Max avalanche was reached
        
        if AllTimeMaxMinOfQueue > MaxOfQueue and Searching:
            Searching = False
            plt.plot(Avalanche[0], Avalanche[1], "bo")
            print("\n\n\nAvalanche found")
        slope_ini = np.copy(slope_next)
    
    fMoveToPower(RotorStage, PowerMeter, Pmin + Ratio * (Pmax - Pmin), *PowerRangeFitParameters)

    return LumQueueSize
        
        
LumQueueSize = FindAvalanche(
            SaveDataFolder,
            Pmin,
            Pmax,
            0.001,
            integration_time = 3)
plt.yscale("log")
plt.xscale("log")
plt.title("Acquired data{}".format(LumQueueSize))
plt.show()

    

