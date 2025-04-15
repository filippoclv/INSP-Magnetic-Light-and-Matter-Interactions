import numpy as np
import os
import sys
import time
import matplotlib.pyplot as plt

# Add the script folder to the module search path
ScriptFolder = 'C:\\Users\\User\\Desktop\\Filippo\\INSP-Magnetic-Light-and-Matter-Interactions\\ANP\\Interfacing'
if ScriptFolder not in sys.path: sys.path.append(ScriptFolder)

from FunctionsPowerControl import *
from SavingScript import *
#from FunctionsTipControl import *

WorkingFolder = 'C:\\Users\\User\\Desktop\\Benoit\\PythonConnection\\v2_20240318'; os.chdir(WorkingFolder)
TodayDateTime = time.strftime('%Y%m%d', time.gmtime())
SaveDataFolder = r'\Users\User\Desktop\Benoit\PythonConnection\v2_20240318\DATA' + '\\' + TodayDateTime

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

def fGetPowerCurve(RotorStage,
                   PowerMeter,
                   PowerStart,
                   PowerStop,
                   PowerNumberStep,
                   SaveDataFolder,
                   DensityInfo,
                   RatioStart,
                   RatioStop,
                   DelayIntegrationTime,
                   LinearPowerLogScale = True):

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
    FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\n')
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

        # NEW WAY TO SAVE DATA TO BE TESTED

        try:

            IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)

        except RuntimeError as e:

            print(f"[FATAL] Failed to save spectrum at P{Pi}: {e}")

            # Options:
            break  # Stop the loop entirely
            #continue   # Skip and move to next power
            #raise      # Crash and exit
            #retry logic here if you want

        with open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a') as FileInfo:
            FileInfo.write(
                f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')

#        IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
        
#        FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a')
#        FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')
#        FileInfo.close()

        print(f'{Pi+1}/{PowerNumberStep} Power done')
        
    return MyDataFolder

def fGetPowerCurve_BackAndForth(RotorStage, PowerMeter,
                                PowerStart, PowerStop,
                                PowerNumberStep, SaveDataFolder,
                                DensityInfo,
                                RatioStart, RatioStop, DelayIntegrationTime,
                                LinearPowerLogScale=True):

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
    FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\n')
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
        #plt.savefig('PowerCurve' + str(WLi) + '.png')

    #return PowerData, LumiData

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
            WL, Intensity = np.loadtxt(FileNamePath, dtype=float, delimiter=';', skiprows=3, converters=lambda x: x.replace(',', '.'), encoding=None, unpack=True)

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

# Let's add a way to automatically detect the slope and measure more points there

def fAutoRefinedPowerCurve(RotorStage, PowerMeter, SaveDataFolder, DensityInfo,
                          RatioStart=0.0001, RatioStop=0.9, DelayIntegrationTime=2,
                          CoarseSteps=25, FineSteps=50, LinearPowerLogScale=True):

    print("Running initial coarse scan...")
    PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
    PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

    MyDataFolderCoarse = fGetPowerCurve(
                                        RotorStage, PowerMeter,
                                        PowerStart, PowerStop,
                                        CoarseSteps, SaveDataFolder, DensityInfo,
                                        RatioStart, RatioStop,
                                        DelayIntegrationTime,
                                        LinearPowerLogScale
                                       )

    # Analyze the data
    print("Analyzing coarse data to find linear region...")
    FileSetInfoPath = MyDataFolderCoarse + '\\SetInfoPowerCurve.txt'
    PowerData = np.loadtxt(FileSetInfoPath, skiprows=1, usecols=3)
    LumiData = []

    for i in range(CoarseSteps):

        FilePath = MyDataFolderCoarse + f'\\P{i}.txt'
        WL, Intensity = np.loadtxt(FilePath, delimiter=';', skiprows=3, converters=lambda x: x.replace(',', '.'), unpack=True)
        idx_min = np.argmin(np.abs(WL - 700))
        idx_max = np.argmin(np.abs(WL - 720))
        LumiData.append(np.sum(Intensity[idx_min:idx_max]))

    PowerData = np.array(PowerData)
    LumiData = np.array(LumiData)

    # Log scale fit
    logP = np.log10(PowerData)
    logL = np.log10(LumiData)

    window_size = 5
    best_r2 = 0
    best_start = 0

    for i in range(len(logP) - window_size + 1):

        x = logP[i:i + window_size]
        y = logL[i:i + window_size]

        coeffs = np.polyfit(x, y, 1)
        fit = np.poly1d(coeffs)
        residuals = y - fit(x)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2 = 1 - (ss_res / ss_tot)

        if r2 > best_r2:

            best_r2 = r2
            best_start = i

    best_range_P = PowerData[best_start:best_start + window_size]
    print(f"Best linear region found between: {best_range_P[0]:.2e} – {best_range_P[-1]:.2e} W (R² = {best_r2:.4f})")

    # Fine scan
    MyDataFolderFine = fGetPowerCurve(
                                      RotorStage, PowerMeter,
                                      best_range_P[0], best_range_P[-1],
                                      FineSteps, SaveDataFolder, DensityInfo,
                             0, 0,  # Not relevant here
                                      DelayIntegrationTime,
                                      LinearPowerLogScale
                                     )

    return MyDataFolderCoarse, MyDataFolderFine

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
MyDataFolder = fGetPowerCurve(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, RatioStart, RatioStop, DelayIntegrationTime, LinearPowerLogScale = True)
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

RatioStart = 0.00001
RatioStop = 0.9
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 41 # Step number will be doubled
DelayIntegrationTime = 3 # [s]
MyDataFolder = fGetPowerCurve_BackAndForth(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, RatioStart, RatioStop, DelayIntegrationTime, LinearPowerLogScale = True)
time.sleep(0.5)

# WLRange = np.array([535, 550]) # [nm]
# WLRange = np.array([790, 810]) # [nm] 800 nm
# WLRange = np.array([680, 710]) # [nm] 700 nm
# WLRange = np.array([730, 750]) # [nm] 740 nm
WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])
fProcessPowerCurveBackAndForth(MyDataFolder, WLRangeAll)

fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

print('\nSetup back to the initial ratio of max power: ', Ratio)

#%% fAutoRefinedPowerCurve

RatioStart = 0.00001
RatioStop = 0.9
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStepCoarse = 25  # Coarse scan step count
PowerNumberStepFine = 80    # Refined scan step count
DelayIntegrationTime = 3    # [s]

MyDataFolderCoarse, MyDataFolderFine = fAutoRefinedPowerCurve(
                                                             RotorStage, PowerMeter,
                                                             SaveDataFolder, DensityInfo,
                                                             RatioStart, RatioStop,
                                                             DelayIntegrationTime,
                                                             CoarseSteps=PowerNumberStepCoarse,
                                                             FineSteps=PowerNumberStepFine,
                                                             LinearPowerLogScale=True
                                                            )

# Wavelength ranges for integration
WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])

# Process the final fine scan results
fProcessPowerCurve(MyDataFolderFine, WLRangeAll)

# Reset to chosen power level
SetPointPower = PowerRangeMin + Ratio * (PowerRangeMax - PowerRangeMin)
fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

print('\nSetup back to the initial ratio of max power:', Ratio)

#%% fScanAllHeightAllPower

RatioStart = 0.5
RatioStop = 0.5
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)
PowerNumberStep = 1
DelayIntegrationTime = 2 # [s]
SensZStep = - 60 # [mV] Must be an integer number, and negative to move back
HeightNumberStep = 31

fScanAllHeightAllPower()

#%% fScanHeight

DelayIntegrationTime = 2 # [s]
SensZStep = - 50 # [mV] Must be an integer number, and negative to move back
HeightNumberStep = 31
DoRefSpectrum = True

fScanHeight(DoRefSpectrum)

#%% fStudyLaserStabilityPower

SetPointPower = PowerRange[1]
TimeTotal = 60 # (s)
TimeStep = 1 # (s)
fStudyLaserStabilityPower(RotorStage, PowerMeter, SetPointPower, TimeTotal, TimeStep, *PowerRangeFitParameters)

#%% Disconnection rotor stage

RotorStage.close()

#%% Disconnection powermeter

PowerMeter.disconnect_device() # To disconnect the device