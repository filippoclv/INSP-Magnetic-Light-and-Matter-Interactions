# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 17:09:11 2024

@author: benre
"""

import numpy as np
import os
import time
import matplotlib.pyplot as plt


WorkingFolder = 'C:\\Users\\User\\Desktop\\Benoit\\PythonConnection\\v2_20240318'; os.chdir(WorkingFolder)
TodayDateTime = time.strftime('%Y%m%d', time.gmtime())
SaveDataFolder = r'\Users\User\Desktop\Benoit\PythonConnection\v2_20240318\DATA' + '\\' + TodayDateTime

from FunctionsPowerControl import fConnectRotorStage, fConnectPowerMeter, fScanPowerRange, fMoveToPower, fBeamSplitterCubeLawTheta2Power, fStudyLaserStabilityPower, fMeasurePower
from FunctionsTipControl import FromPhaseToSenZ, FromSenZToPhase, ChangeSetPointV, GetASpectrum, SaveASpectrum

def fScanAllHeightAllPower(LinearPowerLogScale = True):
    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
    os.makedirs(MyDataFolder)
    print(f'New folder created in {MyDataFolder}')

    if LinearPowerLogScale == True:
        PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))
    else:
        PowerScan = np.linspace(PowerStart, PowerStop, PowerNumberStep)
        
    FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanAllHeightAllPower.txt', 'w')
    FileInfo.write('N\tZindex\tPindex\tHeight\tSetPointPower\tCurrentPower\tTime\n')

    NumberOfMeasurement = 0

    SensZStart = FromPhaseToSenZ()
    SetPointHeight = SensZStart
    IsFolderChecked  = False
    for Zi in range(HeightNumberStep):
        for Pi in range(len(PowerScan)):
            NumberOfMeasurement += 1

            SetPointPower = PowerScan[Pi]
            fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)
            GetASpectrum(DelayIntegrationTime)
            CurrentPower = fMeasurePower(PowerMeter)
            CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
            FileName = f'Z{Zi}P{Pi}'
            IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
            
            FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanAllHeightAllPower.txt', 'a')
            FileInfo.write(f'{NumberOfMeasurement}\t{Zi}\t{Pi}\t{SetPointHeight}\t{SetPointPower}\t{CurrentPower}\t{CurrentTime}\n')
            FileInfo.close()
            print(f'{Zi +1}/{HeightNumberStep} Height done \n{Pi +1}/{PowerNumberStep} Power done')
            
        OldSenZ_mV, NewSenZ_mV = ChangeSetPointV(SensZStep)
        SetPointHeight = NewSenZ_mV
        
    FromSenZToPhase()

def fGetPowerCurve(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, LinearPowerLogScale = True):
    print('Power curve is running ...')
    
    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
    os.makedirs(MyDataFolder)
    print(f'New folder created in {MyDataFolder}')
    
    if LinearPowerLogScale == True:
        PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))
    else:
        PowerScan = np.linspace(PowerStart, PowerStop, PowerNumberStep)
        
    FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'w')
    FileInfo.write('N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\n')
    FileInfo.close()

    NumberOfMeasurement = 0
    IsFolderChecked = False
    for Pi in range(len(PowerScan)):
        NumberOfMeasurement += 1

        SetPointPower = PowerScan[Pi]
        fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)
        GetASpectrum(DelayIntegrationTime)
        CurrentPower = fMeasurePower(PowerMeter)
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        FileName = f'P{Pi}'
        
        IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
        
        FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a')
        FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')
        FileInfo.close()
        print(f'{Pi+1}/{PowerNumberStep} Power done')
        
    return MyDataFolder

def fGetPowerCurve_BackAndForth(RotorStage, PowerMeter,
                                PowerStart, PowerStop,
                                PowerNumberStep, SaveDataFolder,
                                DensityInfo, LinearPowerLogScale=True):

    print('Power curve (back and forth) is running ...')

    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
    os.makedirs(MyDataFolder)
    print(f'New folder created in {MyDataFolder}')

    # Generate the power scan
    if LinearPowerLogScale:

        PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))

    else:

        PowerScan = np.linspace(PowerStart, PowerStop, PowerNumberStep)

    # Combine forward and backward sweeps
    FullPowerScan = np.concatenate((PowerScan, PowerScan[::-1]))

    FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'w')
    FileInfo.write('N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\n')
    FileInfo.close()

    NumberOfMeasurement = 0
    IsFolderChecked = False

    for Pi, SetPointPower in enumerate(FullPowerScan):

        NumberOfMeasurement += 1

        fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)
        GetASpectrum(DelayIntegrationTime)
        CurrentPower = fMeasurePower(PowerMeter)
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        FileName = f'P{Pi}'

        IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)

        FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a')
        FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')
        FileInfo.close()

        print(f'{Pi + 1}/{len(FullPowerScan)} Power done')

    fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

    print('\nSetup back to the initial ratio of max power: ', Ratio)

    return MyDataFolder

def fProcessPowerCurve(MyDataFolder, WLRangeAll):
    FileSetInfoPath = MyDataFolder + '\\SetInfoPowerCurve.txt'
    PowerData = np.loadtxt(FileSetInfoPath, dtype = float, skiprows = 1, usecols = 3, encoding = None, )
    for WLi in range(len(WLRangeAll)):
        WLRange = WLRangeAll[WLi]
        LumiData = []
        for i in range(PowerNumberStep):
            FileNamePath = MyDataFolder + '\\P' + str(i) + '.txt'
            WL, Intensity = np.loadtxt(FileNamePath, dtype = float, delimiter = ';', skiprows = 3, converters =  lambda x: x.replace(',', '.'), encoding = None, unpack = True)
            
            WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
            WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
            
            LumiData.append(np.sum(Intensity[WLRangeIdxMin:WLRangeIdxMax]))
        LumiData = np.array(LumiData)

        fig, ax = plt.subplots()
        ax.scatter(PowerData, LumiData)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Power (W)')
        ax.set_ylabel('Integrated Luminescence (u.a.)')
        plt.title(str(WLRange[0]) + 'to' + str(WLRange[1]) + ' nm')
        plt.grid(axis = 'both', which = 'both')
        plt.show()
        # plt.savefig('PowerCurve' + str(WLi) + '.png')
    # return PowerData, LumiData

def fProcessPowerCurveBackAndForth(MyDataFolder, WLRangeAll):
    FileSetInfoPath = MyDataFolder + '\\SetInfoPowerCurve.txt'

    # Read the full power data (now points are doubled)
    PowerData = np.loadtxt(FileSetInfoPath, dtype=float, skiprows=1, usecols=3, encoding=None)
    TotalMeasurements = len(PowerData)

    for WLi in range(len(WLRangeAll)):
        WLRange = WLRangeAll[WLi]
        LumiData = []

        for i in range(TotalMeasurements):
            FileNamePath = MyDataFolder + '\\P' + str(i) + '.txt'
            WL, Intensity = np.loadtxt(FileNamePath, dtype=float, delimiter=';', skiprows=3,
                                       converters=lambda x: x.replace(',', '.'), encoding=None, unpack=True)

            WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
            WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
            LumiData.append(np.sum(Intensity[WLRangeIdxMin:WLRangeIdxMax]))

        LumiData = np.array(LumiData)

        # Separate forward and backward
        Half = TotalMeasurements // 2
        LumiFwd = LumiData[:Half]
        LumiBwd = LumiData[Half:]
        PowerFwd = PowerData[:Half]
        PowerBwd = PowerData[Half:]

        fig, ax = plt.subplots()
        ax.plot(PowerFwd, LumiFwd, 'o-', label='Forward sweep')
        ax.plot(PowerBwd, LumiBwd, 'o-', label='Backward sweep')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Power (W)')
        ax.set_ylabel('Integrated Luminescence (counts)')
        ax.set_title(f'{WLRange[0]}–{WLRange[1]} nm')
        ax.grid(True, which='both')
        ax.legend()
        plt.show()

def fScanHeight(DoRefSpectrum):
    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
    os.makedirs(MyDataFolder)
    print(f'New folder created in {MyDataFolder}')

    FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanHeight.txt', 'w')
    FileInfo.write('N\tZindex\tHeight\tTime\n')
    FileInfo.close()

    NumberOfMeasurement = 0

    SensZStart = FromPhaseToSenZ()
    SetPointHeight = SensZStart
    IsFolderChecked  = False
    for Zi in range(HeightNumberStep):
        NumberOfMeasurement += 1
        GetASpectrum(DelayIntegrationTime)
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        FileName = f'Z{Zi}'
        if IsFolderChecked == False:
            time.sleep(1)
        IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
        
        FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanHeight.txt', 'a')
        FileInfo.write(f'{NumberOfMeasurement}\t{Zi}\t{SetPointHeight}\t{CurrentTime}\n')
        FileInfo.close()
        print(f'{Zi +1}/{HeightNumberStep} Height done')
            
        OldSenZ_mV, NewSenZ_mV = ChangeSetPointV(SensZStep)
        SetPointHeight = NewSenZ_mV
        
    if DoRefSpectrum == True:
        FeedBackOff = True
        FromSenZToPhase(FeedBackOff)
        time.sleep(2)
        GetASpectrum(DelayIntegrationTime)
        SaveASpectrum(MyDataFolder, 'ref', IsFolderChecked)
        
        
    
#%% Connection RotorStage

RotorStage = fConnectRotorStage()

#%% Connection PowerMeter

PowerMeter = fConnectPowerMeter()

#%% fScanPowerRange

AngleStart = 0
AngleStop = 90
AngleNumberStep = 19
DensityInfo = 0

_, _, PowerRange, PowerRangeFitParameters = fScanPowerRange(RotorStage, PowerMeter, fBeamSplitterCubeLawTheta2Power, AngleStart, AngleStop, AngleNumberStep)

PowerRangeMax = PowerRange[0]
PowerRangeMin = PowerRange[1]

#%% fMoveToPower

#Desired ratio of the max power
Ratio = 0.1

SetPointPower = PowerRangeMin + Ratio * (PowerRangeMax - PowerRangeMin)
fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

#%% ChangeAngle

Angle = 37
RotorStage.move_to(Angle)

#%% fGetPowerCurve

RatioStart = 0.00001
RatioStop = 0.9
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 41
DelayIntegrationTime = 3 # (s)
MyDataFolder = fGetPowerCurve(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, LinearPowerLogScale = True)
time.sleep(0.5)

# WLRange = np.array([535, 550]) # (nm)
# WLRange = np.array([790, 810]) # (nm) 800 nm
# WLRange = np.array([680, 710]) # (nm) 700 nm
# WLRange = np.array([730, 750]) # (nm) 740 nm
WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])
fProcessPowerCurve(MyDataFolder, WLRangeAll)

fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

print('\nSetup back to the initial ratio of max power: ', Ratio)

#%% fGetPowerCurve_BackAndForth

# Number of points is doubled, so to have good data treatment you need the base number to be even
# So (PowerNumberStep + 1) should be even

RatioStart = 0.00001
RatioStop = 0.9
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 41 # Step number will be doubled
DelayIntegrationTime = 3 # [s]
MyDataFolder = fGetPowerCurve_BackAndForth(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, LinearPowerLogScale = True)
time.sleep(0.5)

# WLRange = np.array([535, 550]) # [nm]
# WLRange = np.array([790, 810]) # [nm] 800 nm
# WLRange = np.array([680, 710]) # [nm] 700 nm
# WLRange = np.array([730, 750]) # [nm] 740 nm
WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])
fProcessPowerCurveBackAndForth(MyDataFolder, WLRangeAll)

fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

print('\nSetup back to the initial ratio of max power: ', Ratio)

#%% fScanAllHeightAllPower

RatioStart = 0.5
RatioStop = 0.5
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)
PowerNumberStep = 1
DelayIntegrationTime = 2 # (s)
SensZStep = - 60 # (mV) Doit être un nombre entier. Doit être un nombre négatif pour reculer.
HeightNumberStep = 31

fScanAllHeightAllPower()

#%% fScanHeight

DelayIntegrationTime = 2 # (s)
SensZStep = - 50 # (mV) Doit être un nombre entier. Doit être un nombre négatif pour reculer.
HeightNumberStep = 31
DoRefSpectrum = True

fScanHeight(DoRefSpectrum)

#%% fStudyLaserStabilityPower

SetPointPower = PowerRange[1]
TimeTotal = 60 # (s)
TimeStep = 1 # (s)
fStudyLaserStabilityPower(RotorStage, PowerMeter, SetPointPower, TimeTotal, TimeStep, *PowerRangeFitParameters)

#%% Deconnection
RotorStage.close()
#%%
PowerMeter.disconnect_device() #disconnect the device
 
