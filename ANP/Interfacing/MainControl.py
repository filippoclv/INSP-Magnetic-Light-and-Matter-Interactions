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
        
        GetASpectrum(DelayIntegrationTime) # New
        #GetASpectrum(DelayIntegrationTime)
        
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
            
            FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')

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

        GetASpectrum(DelayIntegrationTime) # New
        #GetASpectrum(DelayIntegrationTime)
        
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
            
            FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')

#        IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
        
#        FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a')
#        FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')
#        FileInfo.close()

        print(f'{Pi+1}/{len(FullPowerScan)} Power done')

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

def fAdaptiveRefinedPowerCurve(RotorStage, PowerMeter,
                               SaveDataFolder, DensityInfo,
                               PowerStart, PowerStop,
                               PowerNumberStep,
                               RatioStart,
                               RatioStop,
                               DelayIntegrationTime,
                               SlopeThreshold,
                               MaxTotalExtraPoints,
                               LuminescenceJumpThreshold,
                               WLRange
                              ):

    print("[INFO] Adaptive power scan starting...")

    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MyDataFolder = os.path.join(SaveDataFolder, FolderTimeName)
    os.makedirs(MyDataFolder)
    print(f"[INFO] New folder created at: {MyDataFolder}")

    PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))
    PowerQueue = list(PowerScan)
    InsertedBetween = set()

    SetInfoPath = os.path.join(MyDataFolder, 'SetInfoPowerCurve.txt')
    
    with open(SetInfoPath, 'w') as f:
        
        f.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\n')

    LumiList = []
    IsFolderChecked = False
    i = 0
    P_index = 0
    ExtraPointsAdded = 0
    OriginalPowers = set(PowerQueue)

    while i < len(PowerQueue):
        
        P = PowerQueue[i]

        fMoveToPower(RotorStage, PowerMeter, P, *PowerRangeFitParameters)
        GetASpectrum(DelayIntegrationTime)
        CurrentPower = fMeasurePower(PowerMeter)
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        FileName = f'P{P_index}'

        try:
            
            IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
            
        except RuntimeError as e:
            
            print(f"[FATAL] Failed to save spectrum at {FileName}: {e}")
            
            break

        FilePath = os.path.join(MyDataFolder, f"{FileName}.txt")
        WL, Intensity = np.loadtxt(FilePath, delimiter=';', skiprows=3,
                                   converters={
                                       0: lambda x: float(x.decode('latin1').replace(',', '.')),
                                       1: lambda x: float(x.decode('latin1').replace(',', '.'))
                                   },
                                   unpack=True
                                  )

        idx_min = np.argmin(np.abs(WL - WLRange[0]))
        idx_max = np.argmin(np.abs(WL - WLRange[1]))
        Lumi = np.sum(Intensity[idx_min:idx_max])
        LumiList.append(Lumi)

        with open(SetInfoPath, 'a') as f:
            
            f.write(f"{P_index+1}\t{P_index}\t{P}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n")

        print(f"[INFO] {P_index+1}/{len(PowerQueue)} power steps done")

        if i < len(PowerQueue) - 1 and (
                                        P in OriginalPowers and
                                        PowerQueue[i + 1] in OriginalPowers and
                                        (MaxTotalExtraPoints is None or ExtraPointsAdded < MaxTotalExtraPoints)
                                       ):
            
            P_next = PowerQueue[i + 1]
            
            if len(LumiList) >= 2:
                
                L_current = LumiList[-1]
                L_prev = LumiList[-2]
                dP = P_next - P
                dL = L_current - L_prev
                slope = abs(dL / dP) if dP != 0 else 0
                ratio_increase = L_current / L_prev if L_prev > 0 else 0
        
                pair_id = (round(P, 10), round(P_next, 10))
                midpoint = (P + P_next) / 2.0
                midpoint_rounded = round(midpoint, 10)
        
                existing_rounded = set(round(p, 10) for p in PowerQueue)
        
                if (
                    slope > SlopeThreshold and
                    ratio_increase > LuminescenceJumpThreshold and
                    pair_id not in InsertedBetween and
                    midpoint_rounded not in existing_rounded
                   ):
                    
                    PowerQueue.insert(i + 1, midpoint)
                    InsertedBetween.add(pair_id)
                    ExtraPointsAdded += 1
                    print(f"[INFO] Inserting 1 point after {P:.5f} due to high slope and luminescence jump.")

        i += 1
        P_index += 1

    return MyDataFolder

def fProcessRefinedPowerCurve(MyDataFolder, WLRangeAll):
    
    FileSetInfoPath = os.path.join(MyDataFolder, 'SetInfoPowerCurve.txt')
    PowerData = np.loadtxt(FileSetInfoPath, dtype=float, skiprows=1, usecols=3, encoding=None)

    NumberOfFiles = len(PowerData) # Variable number of spectra

    for WLi in range(len(WLRangeAll)):

        WLRange = WLRangeAll[WLi]
        LumiData = []

        for i in range(NumberOfFiles):
            
            FileNamePath = os.path.join(MyDataFolder, f'P{i}.txt')

            try:
                
                WL, Intensity = np.loadtxt(
                                           FileNamePath, dtype=float, delimiter=';', skiprows=3,
                                           converters=lambda x: x.replace(',', '.'), encoding=None, unpack=True
                                          )
                
            except Exception as e:
                
                print(f"[WARNING] Could not read file {FileNamePath}: {e}")
                
                continue

            WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
            WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
            LumiData.append(np.sum(Intensity[WLRangeIdxMin:WLRangeIdxMax]))

        LumiData = np.array(LumiData)

        fig, ax = plt.subplots()
        ax.scatter(PowerData[:len(LumiData)], LumiData)
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Power (W)')
        ax.set_ylabel('Integrated Luminescence (a.u.)')
        ax.set_title(f'{WLRange[0]} to {WLRange[1]} nm')
        ax.grid(True, which='both')
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
Ratio = 0.2

SetPointPower = PowerRangeMin + Ratio * (PowerRangeMax - PowerRangeMin)
fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

#%% ChangeAngle

Angle = 37
RotorStage.move_to(Angle)

#%% fGetPowerCurve

RatioStart = 0.0001
RatioStop = 0.9
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 21
DelayIntegrationTime = 3 # [s]
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

RatioStart = 0.01
RatioStop = 0.8
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 5 # Step number will be doubled
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

#%% fAdaptiveRefinedPowerCurve

RatioStart = 0.0001
RatioStop = 0.9
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 31
DelayIntegrationTime = 3    # [s]

MyDataFolder = fAdaptiveRefinedPowerCurve(
                                          RotorStage=RotorStage,
                                          PowerMeter=PowerMeter,
                                          SaveDataFolder=SaveDataFolder,
                                          DensityInfo=DensityInfo,
                                          PowerStart=PowerStart,
                                          PowerStop=PowerStop,
                                          PowerNumberStep=PowerNumberStep,
                                          RatioStart=RatioStart,
                                          RatioStop=RatioStop,
                                          DelayIntegrationTime=3,
                                          SlopeThreshold=4, # Slope threshold to be chosen, 4 seems too high
                                          MaxTotalExtraPoints=5,
                                          LuminescenceJumpThreshold=1.05, # Percentage of luminescence difference to trigger fine measurement
                                          WLRange=[790, 810]
                                         )

fProcessRefinedPowerCurve(MyDataFolder, WLRangeAll=[[790, 810]])


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