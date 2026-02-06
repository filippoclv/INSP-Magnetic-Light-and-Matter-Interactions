import numpy as np
import os
import sys
import time
import matplotlib.pyplot as plt

# Add the script folder to the module search path
ScriptFolder = 'C:\\Users\\User\\Desktop\\Filippo\\INSP-Magnetic-Light-and-Matter-Interactions\\ANPs\\Interfacing'
if ScriptFolder not in sys.path: sys.path.append(ScriptFolder)

from FunctionsPowerControl import *
from SavingScript import *
from FunctionsTipControl import *
from APD_Control import *

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
                   Pmin,
                   Pmax,
                   Ratio,
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
    FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\Ratio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')
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
                                DensityInfo, Pmin,
                                Pmax, Ratio,
                                RatioStart, RatioStop,
                                DelayIntegrationTime, LinearPowerLogScale=True):

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
    FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\Ratio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')
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
            
            BackgroundRef = np.mean(Intensity[-20:-1])
            Background = np.ones(Intensity.shape) * BackgroundRef
            
            Intensity_Corrected = Intensity - Background
            
            WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
            WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
            
            LumiData.append(np.sum(Intensity_Corrected[WLRangeIdxMin:WLRangeIdxMax]))

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

            BackgroundRef = np.mean(Intensity[-20:-1])
            Background = np.ones(Intensity.shape) * BackgroundRef
            Intensity_Corrected = Intensity - Background
            
            WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
            WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
            LumiData.append(np.sum(Intensity_Corrected[WLRangeIdxMin:WLRangeIdxMax]))

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

def fAdaptiveRefinedPowerCurve(RotorStage, PowerMeter,
                               SaveDataFolder, DensityInfo,
                               Pmin, Pmax,
                               Ratio, PowerStart,
                               PowerStop, PowerNumberStep,
                               RatioStart, RatioStop,
                               DelayIntegrationTime, SlopeThreshold,
                               MaxTotalExtraPoints, LuminescenceJumpThreshold,
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
        
        f.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\Ratio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')

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
    
    return MyDataFolder
               
def fProcessScanHeight(MyDataFolder, WLRangeAll, HeightNumberStep):
    FileSetInfoPath = MyDataFolder + '\\SetInfoScanHeight.txt'
    HeightData = np.loadtxt(FileSetInfoPath, dtype = float, skiprows = 1, usecols = 2, encoding = None, )
    for WLi in range(len(WLRangeAll)):
        WLRange = WLRangeAll[WLi]
        LumiData = []
        for i in range(HeightNumberStep):
            FileNamePath = MyDataFolder + '\\Z' + str(i) + '.txt'
            WL, Intensity = np.loadtxt(FileNamePath, dtype = float, delimiter = ';', skiprows = 3, converters =  lambda x: x.replace(',', '.'), encoding = None, unpack = True)
            
            BackgroundRef = np.mean(Intensity[-20:-1])
            Background = np.ones(Intensity.shape) * BackgroundRef
            Intensity_Corrected = Intensity - Background
            
            WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
            WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
            LumiData.append(np.sum(Intensity_Corrected[WLRangeIdxMin:WLRangeIdxMax]))
            
        LumiData = np.array(LumiData)

        fig, ax = plt.subplots()
        ax.scatter(HeightData, LumiData)
        ax.set_xlabel('Height (no corr) (mV)')
        ax.set_ylabel('Integrated Luminescence (u.a.)')
        plt.title(str(WLRange[0]) + 'to' + str(WLRange[1]) + ' nm')
        plt.grid(axis = 'both', which = 'both')
        plt.show()
        


# Added functions for APD measurements :

def fGetAPDflux(IntegrationTime, dt):
    total_samples, times = set_param(PicoScope, Channel_PicoScope, IntegrationTime, dt)
    CountRates = run_scope(PicoScope, times, total_samples, Channel_PicoScope, IntegrationTime, dt, plot = False)
    return CountRates
   
def fGetPowerCurve_APD(RotorStage,
                       PowerMeter,
                       PowerStart,
                       PowerStop,
                       PowerNumberStep,
                       SaveDataFolder,
                       DensityInfo,
                       Pmin,
                       Pmax,
                       Ratio,
                       RatioStart,
                       RatioStop,
                       IntegrationTime,
                       dt,
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
        
    FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve_APD.txt', 'w')
    FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\tCountRates\tRatio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {IntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')
    FileInfo.close()

    NumberOfMeasurement = 0
    
    LumiData = []

    for Pi in range(len(PowerScan)):

        NumberOfMeasurement += 1

        SetPointPower = PowerScan[Pi]
        fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)
        
        CountRates = fGetAPDflux(IntegrationTime, dt)
        CountRateToWrite = CountRates[Channel_PicoScope[0]]
        LumiData.append(CountRateToWrite)
        
        CurrentPower = fMeasurePower(PowerMeter)
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())

        with open(MyDataFolder + '\\' + 'SetInfoPowerCurve_APD.txt', 'a') as FileInfo:
            
            FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\t{CountRateToWrite}\n')

        print(f'{Pi+1}/{PowerNumberStep} Power done')
    
        
    LumiData = np.array(LumiData)
    
    fig, ax = plt.subplots()
    ax.scatter(PowerScan, LumiData)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Power (W)')
    ax.set_ylabel('Integrated Luminescence (u.a.)')
    plt.title('APD')
    plt.grid(axis = 'both', which = 'both')
    plt.show()
    
def fGetPowerCurve_BackAndForth_APD(RotorStage,
                                PowerMeter,
                                PowerStart,
                                PowerStop,
                                PowerNumberStep,
                                SaveDataFolder,
                                DensityInfo,
                                Pmin,
                                Pmax,
                                Ratio,
                                RatioStart,
                                RatioStop,
                                IntegrationTime,
                                dt,
                                LinearPowerLogScale = True):

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

    FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve_APD.txt', 'w')
    FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\tCountRates\tRatio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {IntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')
    FileInfo.close()

    NumberOfMeasurement = 0
    LumiData = []
    set_trigger(PicoScope, Channel_PicoScope, trigger = False)
    
    for Pi, SetPointPower in enumerate(FullPowerScan):

        NumberOfMeasurement += 1

        fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

        CountRates = fGetAPDflux(IntegrationTime, dt)
        CountRateToWrite = CountRates[Channel_PicoScope[0]]
        LumiData.append(CountRateToWrite)
        
        CurrentPower = fMeasurePower(PowerMeter)
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())

        with open(MyDataFolder + '\\' + 'SetInfoPowerCurve_APD.txt', 'a') as FileInfo:
            
            FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\t{CountRateToWrite}\n')

        print(f'{Pi+1}/{len(FullPowerScan)} Power done')
    

    LumiData = np.array(LumiData)
    PowerData = FullPowerScan
    
    Half = NumberOfMeasurement // 2
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
    ax.set_ylabel('Counts rate [/s]')
    ax.set_title('PC - BF - APD')
    ax.grid(True, which='both')
    ax.legend()
    plt.show()

def fScanHeight_APD(DoRefSpectrum, RepeatCount):

    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
    os.makedirs(MyDataFolder)
    print(f'New folder created in {MyDataFolder}')

    FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanHeight_APD.txt', 'w')
    FileInfo.write('N\tZindex\tHeight\tTime\tIntegrationTime\tCountRate\n')
    FileInfo.close()

    NumberOfMeasurement = 0
    set_trigger(PicoScope, Channel_PicoScope, trigger = False)
    LumiData = []
    HeightData = []
    

    SensZStart = FromPhaseToSenZ()
    SetPointHeight = SensZStart
    
    for Zi in range(HeightNumberStep):

        NumberOfMeasurement += 1
        
        Measurements = []  # Liste pour stocker les N mesures
        for _ in range(RepeatCount):
            CountRates = fGetAPDflux(IntegrationTime, dt)
            CountRate = CountRates[Channel_PicoScope[0]]
            Measurements.append(CountRate)
            time.sleep(0.01)  # Petite pause pour stabiliser, optionnelle
        CountRateMean = np.mean(Measurements)
        
        CountRateToWrite = CountRateMean
        LumiData.append(CountRateToWrite)
        HeightData.append(SetPointHeight)
        
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        
        FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanHeight_APD.txt', 'a')
        FileInfo.write(f'{NumberOfMeasurement}\t{Zi}\t{SetPointHeight}\t{CurrentTime}\t{IntegrationTime}\t{CountRateToWrite}\n')
        FileInfo.close()
        
        print(f'{Zi +1}/{HeightNumberStep} Height done')
            
        OldSenZ_mV, NewSenZ_mV = ChangeSetPointV(SensZStep)
        SetPointHeight = NewSenZ_mV
        
    if DoRefSpectrum == True:

        FeedBackOff = True
        FromSenZToPhase(FeedBackOff)
        time.sleep(3)
        
        Measurements = []  # Liste pour stocker les N mesures
        for _ in range(RepeatCount):
            CountRates = fGetAPDflux(IntegrationTime, dt)
            CountRate = CountRates[Channel_PicoScope[0]]
            Measurements.append(CountRate)
            time.sleep(0.01)  # Petite pause pour stabiliser, optionnelle
        CountRateMean = np.mean(Measurements)
        
        CountRateToWrite = CountRateMean
        LumiDataRef = np.array(CountRateToWrite)
        
        CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
        
        FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanHeight_APD.txt', 'a')
        FileInfo.write(f'ref\tref\tref\t{CurrentTime}\t{IntegrationTime}\t{CountRateToWrite}\n')
        FileInfo.close()
        
        print(f'Reference done')
    
    LumiData = np.array(LumiData)
    HeightData = np.array(HeightData)
    
    fig, ax = plt.subplots()
    ax.scatter(HeightData, LumiData)
    ax.set_xlabel('Height (no corr) (mV)')
    ax.set_ylabel('Luminescence (a.u)')
    plt.title('ScanZ via APD')
    plt.grid(axis = 'both', which = 'both')
    plt.show()    
    
    return MyDataFolder

def fMapPowerCurves_Verified(PiezoStage, RotorStage, PowerMeter, 
                             X_Rel_List, Y_Rel_List, 
                             PowerStart, PowerStop, PowerNumberStep, 
                             PowerRangeFitParameters, 
                             SaveDataFolder, 
                             IntegrationTime=0.1, dt=4e-9, LinearPowerLogScale=True):
    """
    Verified Map (Corrected for Barebone Driver):
    1. Reads CURRENT piezo position as the "Anchor" (Origin).
    2. Moves relative to Anchor using move_x/move_y.
    3. VERIFIES position by reading it back.
    """
    
    print('\n--- Verified Power Map (Auto-Anchored) ---')

    # 1. Create Map Folder
    FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    MapFolder = os.path.join(SaveDataFolder, FolderTimeName + '_VerifiedMap')
    os.makedirs(MapFolder)
    print(f'Data stored in: {MapFolder}')

    # 2. AUTO-ANCHOR: Read Current Position as Origin
    try:
        print("Reading current position to set as Anchor...")
        
        # --- FIX: Use get_x() instead of get_pos('X') ---
        raw_x = PiezoStage.get_x()
        raw_y = PiezoStage.get_y()
        
        # --- FIX: Parse string "25.123 um" -> Float 25.123 ---
        # Checks if 'um' or 'nm' is in string, removes it, then converts to float
        OriginX = float(raw_x.lower().replace('um','').replace('nm','').strip())
        OriginY = float(raw_y.lower().replace('um','').replace('nm','').strip())
        
        print(f" -> ANCHOR ESTABLISHED: X={OriginX:.4f} um, Y={OriginY:.4f} um")
        
    except Exception as e:
        print(f"\n!!! CRITICAL ERROR !!! Could not set Anchor. Driver returned: X='{raw_x}', Y='{raw_y}'")
        print(f"Error details: {e}")
        return 

    # 3. Generate Power Scan List
    if LinearPowerLogScale:
        PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))
    else:
        PowerScan = np.linspace(PowerStart, PowerStop, PowerNumberStep)
    
    # 4. Master Loop
    TotalPixels = len(X_Rel_List) * len(Y_Rel_List)
    PixelCount = 0

    # Go to Safe Min Power before moving Piezo
    SafeMinPower = PowerRangeFitParameters[2] 
    fMoveToPower(RotorStage, PowerMeter, SafeMinPower, *PowerRangeFitParameters)

    for iY, Y_Offset in enumerate(Y_Rel_List):
        
        # Calculate Absolute Target Y based on ANCHOR
        TargetY = OriginY + Y_Offset
        
        # --- FIX: Use move_y instead of move_abs ---
        PiezoStage.move_y(TargetY)
        
        for iX, X_Offset in enumerate(X_Rel_List):
            
            # Calculate Absolute Target X
            TargetX = OriginX + X_Offset
            
            # --- FIX: Use move_x instead of move_abs ---
            PiezoStage.move_x(TargetX)
            
            # --- THE "TRUST BUT VERIFY" STEP ---
            time.sleep(0.5) 
            
            # Read REAL position from hardware
            # --- FIX: Use get_x() and clean the string ---
            real_x_str = PiezoStage.get_x().strip()
            real_y_str = PiezoStage.get_y().strip()
            
            print(f"\nPx {PixelCount+1}/{TotalPixels} | Target Offset: ({X_Offset:.1f}, {Y_Offset:.1f}) | READ: X={real_x_str}, Y={real_y_str}")

            # Create Pixel File
            PixelFileName = f"Pixel_{iX}_{iY}.txt"
            PixelFilePath = os.path.join(MapFolder, PixelFileName)
            
            # Write Header
            with open(PixelFilePath, 'w') as FileInfo:
                FileInfo.write(f"N\tPindex\tSetPointPower\tCurrentPower\tTime\tCounts\tTargetX={TargetX}\tTargetY={TargetY}\tREAL_X={real_x_str}\tREAL_Y={real_y_str}\n")

            LumiData = []
            RealPowerData = []
            
            # --- POWER CURVE LOOP ---
            for Pi, SetPointPower in enumerate(PowerScan):
                
                # A. Set Laser Power
                fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)
                
                # B. Measure APD
                CountRates = fGetAPDflux(IntegrationTime, dt)
                CountRateToWrite = CountRates[Channel_PicoScope[0]]
                
                # C. Measure Real Power
                CurrentPower = fMeasurePower(PowerMeter)
                CurrentTime = time.strftime("%H%M%S", time.gmtime())
                
                # D. Save Data
                with open(PixelFilePath, 'a') as FileInfo:
                    FileInfo.write(f"{Pi+1}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{CurrentTime}\t{CountRateToWrite}\n")
                
                LumiData.append(CountRateToWrite)
                RealPowerData.append(CurrentPower)
            
            # Reset Power for safety before next move
            fMoveToPower(RotorStage, PowerMeter, SafeMinPower, *PowerRangeFitParameters)
            
            PixelCount += 1

    print("\n--- MAP FINISHED ---")
    print(f"Returning to Anchor ({OriginX:.4f}, {OriginY:.4f})...")
    PiezoStage.move_x(OriginX)
    PiezoStage.move_y(OriginY)

def fScanPiezoRange(PiezoStage):
    """
    Moves X and Y to 0 and 100 um to find the PHYSICAL limits.
    Returns the valid span for mapping.
    """
    print("\n--- STARTING PIEZO RANGE SCAN ---")
    print("Warning: This will move the stage to its limits!")
    
    # --- SCAN X ---
    print("\n[X-AXIS] Finding bounds...")
    
    # Go to 0
    PiezoStage.move_x(0)
    time.sleep(1.0)
    raw_x_min = PiezoStage.get_x()
    
    # Go to Max (Sending 100um is safe; controller will just stop at its limit)
    PiezoStage.move_x(100) 
    time.sleep(1.0)
    raw_x_max = PiezoStage.get_x()
    
    # --- SCAN Y ---
    print("[Y-AXIS] Finding bounds...")
    
    # Go to 0
    PiezoStage.move_y(0)
    time.sleep(1.0)
    raw_y_min = PiezoStage.get_y()
    
    # Go to Max
    PiezoStage.move_y(100) 
    time.sleep(1.0)
    raw_y_max = PiezoStage.get_y()
    
    # --- REPORT ---
    print("-" * 40)
    print("PHYSICAL RANGE RESULTS:")
    print(f"X Axis: {raw_x_min}  <-->  {raw_x_max}")
    print(f"Y Axis: {raw_y_min}  <-->  {raw_y_max}")
    print("-" * 40)
    
    # Return to center (safe spot)
    print("Returning to origin (0, 0)...")
    PiezoStage.move_x(0)
    PiezoStage.move_y(0)
    
#%% Connection RotorStage

RotorStage = fConnectRotorStage()

#%% Connection PowerMeter

PowerMeter = fConnectPowerMeter()

#%% fScanPowerRange

AngleStart = 0
AngleStop = 90
AngleNumberStep = 31
DensityInfo = 0

AngleAll, PowerAll, PowerRange, PowerRangeFitParameters = fScanPowerRange(RotorStage, PowerMeter, fBeamSplitterCubeLawTheta2Power, AngleStart, AngleStop, AngleNumberStep)


PowerRangeMax = PowerRange[0]
PowerRangeMin = PowerRange[1]

Pmin = np.min(PowerAll)
Pmax = np.max(PowerAll)

#%% Connection PicoScope

Channel_PicoScope = ['A'] # Select the channel of the PicoScope to monitor (['A', 'B', ...]). Pour l'instant, en utiliser qu'UNE A LA FOIS
PicoScope = connexion_pico(Channel_PicoScope)

#%% Mesure UNIQUE avec APD x PicoScope

IntegrationTime = 0.1 # Duration [s]
dt = 4e-9 # TimeStep for the APD behaviour [s] DO NOT CHANGE
set_trigger(PicoScope, Channel_PicoScope, trigger=False)
CountRates = fGetAPDflux(IntegrationTime, dt)

#%% Stream avec APD x PicoScope

IntegrationTime = 0.1 # Duration [s]
dt = 4e-9 # TimeStep for the APD behaviour [s] DO NOT CHANGE

set_trigger(PicoScope, Channel_PicoScope, trigger = False)
total_samples, times = set_param(PicoScope, Channel_PicoScope, IntegrationTime, dt)
stream(PicoScope, times, total_samples, Channel_PicoScope, IntegrationTime, dt, plot = False)

#%% fScanPowerRange_APD

RatioStart = 0.0001
RatioStop =  0.03
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 61
IntegrationTime = 0.1 # [s]
fGetPowerCurve_APD(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, Pmin, Pmax, Ratio, RatioStart, RatioStop, IntegrationTime, dt, LinearPowerLogScale = True)

#%% fGetPowerCurve_BackAndForth_APD

RatioStart = 0.0001
RatioStop =  0.0070
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 101 # Step number will be doubled for back and forth
IntegrationTime = 0.1 # [s]
fGetPowerCurve_BackAndForth_APD(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, Pmin, Pmax, Ratio, RatioStart, RatioStop, IntegrationTime, dt, LinearPowerLogScale = True)

#%% fScanHeight_APD

DelayIntegrationTime = 0.1 # [s]
SensZStep = - 50 # [mV] Must be an integer number, and negative to move the tip back
HeightNumberStep = 61
DoRefSpectrum = True
RepeatCount = 3

MyDataFolder = fScanHeight_APD(DoRefSpectrum, RepeatCount)

#%% HARDWARE CONNECTION (Piezo) & VERIFICATION

# 1. Connect Piezo Stage
from PiezoStageControlMAPTEST import Piezoconcept 
try:
    if 'PiezoStage' not in locals() or PiezoStage is None:
        PiezoStage = Piezoconcept(port="COM9")
        print("PiezoStage connected on COM9.")
    else:
        print("PiezoStage is already connected.")
        
    # 2. Quick Health Check
    # FIXED: Changed .get_infos() to .get_info() to match your driver
    info_response = PiezoStage.get_info()
    print(f"Device Info: {info_response}") 
    
except Exception as e:
    print(f"!!! Piezo Connection Failed: {e}")
    PiezoStage = None

#%% fScanPiezoRange EXECUTION (Run this first to check 7um vs 50um limit)

if PiezoStage is not None:
    fScanPiezoRange(PiezoStage)
else:
    print("Connect Piezo first!")

#%% fMapPowerCurves_Verified EXECUTION

# --- PRE-FLIGHT CHECKS ---
if PiezoStage is None:
    print("CRITICAL STOP: Piezo not connected.")
elif 'PowerRangeFitParameters' not in locals():
    print("CRITICAL STOP: Please run fScanPowerRange (Laser Calibration) first!")
else:
    # 1. Define Grid (Microns relative to current position)
    X_Rel = np.linspace(0, 2.0, 3)   # 0 to 2 um
    Y_Rel = np.linspace(0, 2.0, 3)   # 0 to 2 um

    # 2. Define Power Scan (Ratios of Laser Calibration)
    PowerRangeMax = PowerRange[0]
    PowerRangeMin = PowerRange[1]
    
    RatioStart = 0.001 
    RatioStop  = 0.03
    
    MapPowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
    MapPowerStop  = PowerRangeMin + RatioStop  * (PowerRangeMax - PowerRangeMin)
    MapPowerSteps = 3 

    print(f"Map Configured: {len(X_Rel)}x{len(Y_Rel)} Pixels.")

    # 3. RUN
    fMapPowerCurves_Verified(
        PiezoStage, 
        RotorStage, 
        PowerMeter, 
        X_Rel, 
        Y_Rel, 
        MapPowerStart, 
        MapPowerStop, 
        MapPowerSteps, 
        PowerRangeFitParameters, 
        SaveDataFolder,
        IntegrationTime=0.1,
        dt=4e-9,
        LinearPowerLogScale=True
    )
    
#%% fMoveToPower

#Desired ratio of the max power
Ratio = 0.3

SetPointPower = PowerRangeMin + Ratio * (PowerRangeMax - PowerRangeMin)
fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

#%% ChangeAngle

Angle = 50
RotorStage.move_to(Angle)

#%% fGetPowerCurve

RatioStart = 0.0001
RatioStop =  0.03
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 21
DelayIntegrationTime = 1 # [s]
MyDataFolder = fGetPowerCurve(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, Pmin, Pmax, Ratio, RatioStart, RatioStop, DelayIntegrationTime, LinearPowerLogScale = True)
time.sleep(0.5)

# WLRange = np.array([535, 550]) # (nm)
WLRange = np.array([780, 820]) # (nm) 800 nm
# WLRange = np.array([680, 710]) # (nm) 700 nm
# WLRange = np.array([730, 750]) # (nm) 740 nm
WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])
fProcessPowerCurve(MyDataFolder, WLRangeAll)

fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

print('\nSetup back to the initial ratio of max power: ', Ratio)

#%% fGetPowerCurve_BackAndForth

RatioStart = 0.0005
RatioStop =  0.0050
PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

PowerNumberStep = 21 # Step number will be doubled
DelayIntegrationTime = 1 # [s]
MyDataFolder = fGetPowerCurve_BackAndForth(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, Pmin, Pmax, Ratio, RatioStart, RatioStop, DelayIntegrationTime, LinearPowerLogScale = True)
time.sleep(0.5)

# WLRange = np.array([535, 550]) # [nm]
WLRange = np.array([780, 820]) # [nm] 800 nm
# WLRange = np.array([680, 710]) # [nm] 700 nm
# WLRange = np.array([730, 750]) # [nm] 740 nm
WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])
fProcessPowerCurveBackAndForth(MyDataFolder, WLRangeAll)

fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

print('\nSetup back to the initial ratio of max power: ', Ratio)


#%% fScanHeight

DelayIntegrationTime = 2 # [s]
SensZStep = - 50 # [mV] Must be an integer number, and negative to move back
HeightNumberStep = 31
DoRefSpectrum = True

MyDataFolder = fScanHeight(DoRefSpectrum)

WLRangeAll = np.array([[780,820]])
fProcessScanHeight(MyDataFolder, WLRangeAll, HeightNumberStep)

#%% fAdaptiveRefinedPowerCurve

# RatioStart = 0.0001
# RatioStop = 0.9
# PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
# PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

# PowerNumberStep = 31
# DelayIntegrationTime = 3    # [s]

# MyDataFolder = fAdaptiveRefinedPowerCurve(
#                                           RotorStage=RotorStage,
#                                           PowerMeter=PowerMeter,
#                                           SaveDataFolder=SaveDataFolder,
#                                           DensityInfo=DensityInfo,
#                                           Pmin=Pmin,
#                                           Pmax=Pmax,
#                                           Ratio=Ratio,
#                                           PowerStart=PowerStart,
#                                           PowerStop=PowerStop,
#                                           PowerNumberStep=PowerNumberStep,
#                                           RatioStart=RatioStart,
#                                           RatioStop=RatioStop,
#                                           DelayIntegrationTime=3,
#                                           SlopeThreshold=4, # Slope threshold to be chosen, 4 seems too high
#                                           MaxTotalExtraPoints=5,
#                                           LuminescenceJumpThreshold=1.05, # Percentage of luminescence difference to trigger fine measurement
#                                           WLRange=[790, 810]
#                                          )

# fProcessRefinedPowerCurve(MyDataFolder, WLRangeAll=[[790, 810]])


# fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

# print('\nSetup back to the initial ratio of max power:', Ratio)

#%% fScanAllHeightAllPower

# RatioStart = 0.5
# RatioStop = 0.5
# PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
# PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)
# PowerNumberStep = 1
# DelayIntegrationTime = 2 # [s]
# SensZStep = - 60 # [mV] Must be an integer number, and negative to move back
# HeightNumberStep = 31

# fScanAllHeightAllPower()


#%% fStudyLaserStabilityPower

# SetPointPower = PowerRange[1]
# TimeTotal = 60 # (s)
# TimeStep = 1 # (s)
# fStudyLaserStabilityPower(RotorStage, PowerMeter, SetPointPower, TimeTotal, TimeStep, *PowerRangeFitParameters)

#%% Disconnection rotor stage

RotorStage.close()

#%% Disconnection powermeter

PowerMeter.disconnect_device() # To disconnect the device

#%% Disconnection PicoScope

PicoScope.close() # Properly close the PicoScope connection
print("PicoScope closed") 
PicoScope = None  # Reset global scope variable










#%% ???




# import numpy as np
# import os
# import sys
# import time
# import matplotlib.pyplot as plt

# # Add the script folder to the module search path
# ScriptFolder = 'C:\\Users\\User\\Desktop\\Filippo\\INSP-Magnetic-Light-and-Matter-Interactions\\ANP\\Interfacing'
# if ScriptFolder not in sys.path: sys.path.append(ScriptFolder)

# from FunctionsPowerControl import *
# from SavingScript import *
# from FunctionsTipControl import *

# WorkingFolder = 'C:\\Users\\User\\Desktop\\Benoit\\PythonConnection\\v2_20240318'; os.chdir(WorkingFolder)
# TodayDateTime = time.strftime('%Y%m%d', time.gmtime())
# SaveDataFolder = r'\Users\User\Desktop\Benoit\PythonConnection\v2_20240318\DATA' + '\\' + TodayDateTime

# def fScanAllHeightAllPower(LinearPowerLogScale = True):

#     FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
#     MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
#     os.makedirs(MyDataFolder)
#     print(f'New folder created in {MyDataFolder}')

#     if LinearPowerLogScale == True:

#         PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))

#     else:

#         PowerScan = np.linspace(PowerStart, PowerStop, PowerNumberStep)
        
#     FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanAllHeightAllPower.txt', 'w')
#     FileInfo.write('N\tZindex\tPindex\tHeight\tSetPointPower\tCurrentPower\tTime\n')

#     NumberOfMeasurement = 0

#     SensZStart = FromPhaseToSenZ()
#     SetPointHeight = SensZStart
#     IsFolderChecked  = False

#     for Zi in range(HeightNumberStep):

#         for Pi in range(len(PowerScan)):

#             NumberOfMeasurement += 1

#             SetPointPower = PowerScan[Pi]
#             fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)
#             GetASpectrum(DelayIntegrationTime)
#             CurrentPower = fMeasurePower(PowerMeter)
#             CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
#             FileName = f'Z{Zi}P{Pi}'
#             IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
            
#             FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanAllHeightAllPower.txt', 'a')
#             FileInfo.write(f'{NumberOfMeasurement}\t{Zi}\t{Pi}\t{SetPointHeight}\t{SetPointPower}\t{CurrentPower}\t{CurrentTime}\n')
#             FileInfo.close()
#             print(f'{Zi +1}/{HeightNumberStep} Height done \n{Pi +1}/{PowerNumberStep} Power done')
            
#         OldSenZ_mV, NewSenZ_mV = ChangeSetPointV(SensZStep)
#         SetPointHeight = NewSenZ_mV
        
#     FromSenZToPhase()

# def fGetPowerCurve(RotorStage,
#                    PowerMeter,
#                    PowerStart,
#                    PowerStop,
#                    PowerNumberStep,
#                    SaveDataFolder,
#                    DensityInfo,
#                    Pmin,
#                    Pmax,
#                    Ratio,
#                    RatioStart,
#                    RatioStop,
#                    DelayIntegrationTime,
#                    LinearPowerLogScale = True):

#     print('Power curve is running ...')
    
#     FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
#     MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
#     os.makedirs(MyDataFolder)
#     print(f'New folder created in {MyDataFolder}')
    
#     if LinearPowerLogScale == True:

#         PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))

#     else:

#         PowerScan = np.linspace(PowerStart, PowerStop, PowerNumberStep)
        
#     FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'w')
#     FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\Ratio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')
#     FileInfo.close()

#     NumberOfMeasurement = 0
#     IsFolderChecked = False

#     for Pi in range(len(PowerScan)):

#         NumberOfMeasurement += 1

#         SetPointPower = PowerScan[Pi]
#         fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)
        
#         GetASpectrum(DelayIntegrationTime) # New
#         #GetASpectrum(DelayIntegrationTime)
        
#         CurrentPower = fMeasurePower(PowerMeter)
#         CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
#         FileName = f'P{Pi}'

#         try:

#             IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)

#         except RuntimeError as e:

#             print(f"[FATAL] Failed to save spectrum at P{Pi}: {e}")

#             # Options:
#             break  # Stop the loop entirely
#             #continue   # Skip and move to next power
#             #raise      # Crash and exit
#             #retry logic here if you want

#         with open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a') as FileInfo:
            
#             FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')

# #        IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
        
# #        FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a')
# #        FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')
# #        FileInfo.close()

#         print(f'{Pi+1}/{PowerNumberStep} Power done')
        
#     return MyDataFolder

# def fGetPowerCurve_BackAndForth(RotorStage, PowerMeter,
#                                 PowerStart, PowerStop,
#                                 PowerNumberStep, SaveDataFolder,
#                                 DensityInfo, Pmin,
#                                 Pmax, Ratio,
#                                 RatioStart, RatioStop,
#                                 DelayIntegrationTime, LinearPowerLogScale=True):

#     print('Power curve (back and forth) is running ...')

#     FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
#     MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
#     os.makedirs(MyDataFolder)
#     print(f'New folder created in {MyDataFolder}')

#     # Generate the power scan
#     if LinearPowerLogScale:

#         PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))

#     else:

#         PowerScan = np.linspace(PowerStart, PowerStop, PowerNumberStep)

#     # Combine forward and backward sweeps
#     FullPowerScan = np.concatenate((PowerScan, PowerScan[::-1]))

#     FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'w')
#     FileInfo.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\Ratio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')
#     FileInfo.close()

#     NumberOfMeasurement = 0
#     IsFolderChecked = False

#     for Pi, SetPointPower in enumerate(FullPowerScan):

#         NumberOfMeasurement += 1

#         fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

#         GetASpectrum(DelayIntegrationTime) # New
#         #GetASpectrum(DelayIntegrationTime)
        
#         CurrentPower = fMeasurePower(PowerMeter)
#         CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
#         FileName = f'P{Pi}'

#         try:

#             IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)

#         except RuntimeError as e:

#             print(f"[FATAL] Failed to save spectrum at P{Pi}: {e}")

#             # Options:
#             break  # Stop the loop entirely
#             #continue   # Skip and move to next power
#             #raise      # Crash and exit
#             #retry logic here if you want

#         with open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a') as FileInfo:
            
#             FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')

# #        IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
        
# #        FileInfo = open(MyDataFolder + '\\' + 'SetInfoPowerCurve.txt', 'a')
# #        FileInfo.write(f'{NumberOfMeasurement}\t{Pi}\t{SetPointPower}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n')
# #        FileInfo.close()

#         print(f'{Pi+1}/{len(FullPowerScan)} Power done')

#     return MyDataFolder

# def fProcessPowerCurve(MyDataFolder, WLRangeAll):
#     FileSetInfoPath = MyDataFolder + '\\SetInfoPowerCurve.txt'
#     PowerData = np.loadtxt(FileSetInfoPath, dtype = float, skiprows = 1, usecols = 3, encoding = None, )

#     for WLi in range(len(WLRangeAll)):

#         WLRange = WLRangeAll[WLi]
#         LumiData = []

#         for i in range(PowerNumberStep):

#             FileNamePath = MyDataFolder + '\\P' + str(i) + '.txt'
#             WL, Intensity = np.loadtxt(FileNamePath, dtype = float, delimiter = ';', skiprows = 3, converters =  lambda x: x.replace(',', '.'), encoding = None, unpack = True)
            
#             WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
#             WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
            
#             LumiData.append(np.sum(Intensity[WLRangeIdxMin:WLRangeIdxMax]))

#         LumiData = np.array(LumiData)

#         fig, ax = plt.subplots()
#         ax.scatter(PowerData, LumiData)
#         ax.set_xscale('log')
#         ax.set_yscale('log')
#         ax.set_xlabel('Power (W)')
#         ax.set_ylabel('Integrated Luminescence (u.a.)')
#         plt.title(str(WLRange[0]) + 'to' + str(WLRange[1]) + ' nm')
#         plt.grid(axis = 'both', which = 'both')
#         plt.show()
#         #plt.savefig('PowerCurve' + str(WLi) + '.png')

#     #return PowerData, LumiData

# def fProcessPowerCurveBackAndForth(MyDataFolder, WLRangeAll):

#     FileSetInfoPath = MyDataFolder + '\\SetInfoPowerCurve.txt'

#     # Read the full power data (now points are doubled)
#     PowerData = np.loadtxt(FileSetInfoPath, dtype=float, skiprows=1, usecols=3, encoding=None)
#     TotalMeasurements = len(PowerData)

#     for WLi in range(len(WLRangeAll)):

#         WLRange = WLRangeAll[WLi]
#         LumiData = []

#         for i in range(TotalMeasurements):

#             FileNamePath = MyDataFolder + '\\P' + str(i) + '.txt'
#             WL, Intensity = np.loadtxt(FileNamePath, dtype=float, delimiter=';', skiprows=3, converters=lambda x: x.replace(',', '.'), encoding=None, unpack=True)

#             WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
#             WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
#             LumiData.append(np.sum(Intensity[WLRangeIdxMin:WLRangeIdxMax]))

#         LumiData = np.array(LumiData)

#         # Separate forward and backward
#         Half = TotalMeasurements // 2
#         LumiFwd = LumiData[:Half]
#         LumiBwd = LumiData[Half:]
#         PowerFwd = PowerData[:Half]
#         PowerBwd = PowerData[Half:]

#         fig, ax = plt.subplots()
#         ax.plot(PowerFwd, LumiFwd, 'o-', label='Forward sweep')
#         ax.plot(PowerBwd, LumiBwd, 'o-', label='Backward sweep')
#         ax.set_xscale('log')
#         ax.set_yscale('log')
#         ax.set_xlabel('Power (W)')
#         ax.set_ylabel('Integrated Luminescence (counts)')
#         ax.set_title(f'{WLRange[0]}–{WLRange[1]} nm')
#         ax.grid(True, which='both')
#         ax.legend()
#         plt.show()

# # Let's add a way to automatically detect the slope and measure more points there

# def fAdaptiveRefinedPowerCurve(RotorStage, PowerMeter,
#                                SaveDataFolder, DensityInfo,
#                                Pmin, Pmax,
#                                Ratio, PowerStart,
#                                PowerStop, PowerNumberStep,
#                                RatioStart, RatioStop,
#                                DelayIntegrationTime, SlopeThreshold,
#                                MaxTotalExtraPoints, LuminescenceJumpThreshold,
#                                WLRange
#                               ):

#     print("[INFO] Adaptive power scan starting...")

#     FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
#     MyDataFolder = os.path.join(SaveDataFolder, FolderTimeName)
#     os.makedirs(MyDataFolder)
#     print(f"[INFO] New folder created at: {MyDataFolder}")

#     PowerScan = np.power(10, np.linspace(np.log10(PowerStart), np.log10(PowerStop), PowerNumberStep))
#     PowerQueue = list(PowerScan)
#     InsertedBetween = set()

#     SetInfoPath = os.path.join(MyDataFolder, 'SetInfoPowerCurve.txt')
    
#     with open(SetInfoPath, 'w') as f:
        
#         f.write(f'N\tPindex\tSetPointPower\tCurrentPower\tDensityInfo\tTime\Ratio = {Ratio}\tRatio_start = {RatioStart}\tRatio_stop = {RatioStop}\tInt. time = {DelayIntegrationTime}\tP_min = {Pmin}\tP_max = {Pmax}\n')

#     LumiList = []
#     IsFolderChecked = False
#     i = 0
#     P_index = 0
#     ExtraPointsAdded = 0
#     OriginalPowers = set(PowerQueue)

#     while i < len(PowerQueue):
        
#         P = PowerQueue[i]

#         fMoveToPower(RotorStage, PowerMeter, P, *PowerRangeFitParameters)
#         GetASpectrum(DelayIntegrationTime)
#         CurrentPower = fMeasurePower(PowerMeter)
#         CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
#         FileName = f'P{P_index}'

#         try:
            
#             IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
            
#         except RuntimeError as e:
            
#             print(f"[FATAL] Failed to save spectrum at {FileName}: {e}")
            
#             break

#         FilePath = os.path.join(MyDataFolder, f"{FileName}.txt")
#         WL, Intensity = np.loadtxt(FilePath, delimiter=';', skiprows=3,
#                                    converters={
#                                        0: lambda x: float(x.decode('latin1').replace(',', '.')),
#                                        1: lambda x: float(x.decode('latin1').replace(',', '.'))
#                                    },
#                                    unpack=True
#                                   )

#         idx_min = np.argmin(np.abs(WL - WLRange[0]))
#         idx_max = np.argmin(np.abs(WL - WLRange[1]))
#         Lumi = np.sum(Intensity[idx_min:idx_max])
#         LumiList.append(Lumi)

#         with open(SetInfoPath, 'a') as f:
            
#             f.write(f"{P_index+1}\t{P_index}\t{P}\t{CurrentPower}\t{DensityInfo}\t{CurrentTime}\n")

#         print(f"[INFO] {P_index+1}/{len(PowerQueue)} power steps done")

#         if i < len(PowerQueue) - 1 and (
#                                         P in OriginalPowers and
#                                         PowerQueue[i + 1] in OriginalPowers and
#                                         (MaxTotalExtraPoints is None or ExtraPointsAdded < MaxTotalExtraPoints)
#                                        ):
            
#             P_next = PowerQueue[i + 1]
            
#             if len(LumiList) >= 2:
                
#                 L_current = LumiList[-1]
#                 L_prev = LumiList[-2]
#                 dP = P_next - P
#                 dL = L_current - L_prev
#                 slope = abs(dL / dP) if dP != 0 else 0
#                 ratio_increase = L_current / L_prev if L_prev > 0 else 0
        
#                 pair_id = (round(P, 10), round(P_next, 10))
#                 midpoint = (P + P_next) / 2.0
#                 midpoint_rounded = round(midpoint, 10)
        
#                 existing_rounded = set(round(p, 10) for p in PowerQueue)
        
#                 if (
#                     slope > SlopeThreshold and
#                     ratio_increase > LuminescenceJumpThreshold and
#                     pair_id not in InsertedBetween and
#                     midpoint_rounded not in existing_rounded
#                    ):
                    
#                     PowerQueue.insert(i + 1, midpoint)
#                     InsertedBetween.add(pair_id)
#                     ExtraPointsAdded += 1
#                     print(f"[INFO] Inserting 1 point after {P:.5f} due to high slope and luminescence jump.")

#         i += 1
#         P_index += 1

#     return MyDataFolder

# def fProcessRefinedPowerCurve(MyDataFolder, WLRangeAll):
    
#     FileSetInfoPath = os.path.join(MyDataFolder, 'SetInfoPowerCurve.txt')
#     PowerData = np.loadtxt(FileSetInfoPath, dtype=float, skiprows=1, usecols=3, encoding=None)

#     NumberOfFiles = len(PowerData) # Variable number of spectra

#     for WLi in range(len(WLRangeAll)):

#         WLRange = WLRangeAll[WLi]
#         LumiData = []

#         for i in range(NumberOfFiles):
            
#             FileNamePath = os.path.join(MyDataFolder, f'P{i}.txt')

#             try:
                
#                 WL, Intensity = np.loadtxt(
#                                            FileNamePath, dtype=float, delimiter=';', skiprows=3,
#                                            converters=lambda x: x.replace(',', '.'), encoding=None, unpack=True
#                                           )
                
#             except Exception as e:
                
#                 print(f"[WARNING] Could not read file {FileNamePath}: {e}")
                
#                 continue

#             WLRangeIdxMin = np.argmin(np.abs(WL - WLRange[0]))
#             WLRangeIdxMax = np.argmin(np.abs(WL - WLRange[1]))
#             LumiData.append(np.sum(Intensity[WLRangeIdxMin:WLRangeIdxMax]))

#         LumiData = np.array(LumiData)

#         fig, ax = plt.subplots()
#         ax.scatter(PowerData[:len(LumiData)], LumiData)
#         ax.set_xscale('log')
#         ax.set_yscale('log')
#         ax.set_xlabel('Power (W)')
#         ax.set_ylabel('Integrated Luminescence (a.u.)')
#         ax.set_title(f'{WLRange[0]} to {WLRange[1]} nm')
#         ax.grid(True, which='both')
#         plt.show()

# def fScanHeight(DoRefSpectrum):

#     FolderTimeName = time.strftime('%Y%m%d%H%M%S', time.gmtime())
#     MyDataFolder = SaveDataFolder + '\\' + FolderTimeName
#     os.makedirs(MyDataFolder)
#     print(f'New folder created in {MyDataFolder}')

#     FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanHeight.txt', 'w')
#     FileInfo.write('N\tZindex\tHeight\tTime\n')
#     FileInfo.close()

#     NumberOfMeasurement = 0

#     SensZStart = FromPhaseToSenZ()
#     SetPointHeight = SensZStart
#     IsFolderChecked  = False

#     for Zi in range(HeightNumberStep):

#         NumberOfMeasurement += 1
#         GetASpectrum(DelayIntegrationTime)
#         CurrentTime = time.strftime("%Y%m%d%H%M%S", time.gmtime())
#         FileName = f'Z{Zi}'

#         if IsFolderChecked == False:

#             time.sleep(1)

#         IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
        
#         FileInfo = open(MyDataFolder + '\\' + 'SetInfoScanHeight.txt', 'a')
#         FileInfo.write(f'{NumberOfMeasurement}\t{Zi}\t{SetPointHeight}\t{CurrentTime}\n')
#         FileInfo.close()
#         print(f'{Zi +1}/{HeightNumberStep} Height done')
            
#         OldSenZ_mV, NewSenZ_mV = ChangeSetPointV(SensZStep)
#         SetPointHeight = NewSenZ_mV
        
#     if DoRefSpectrum == True:

#         FeedBackOff = True
#         FromSenZToPhase(FeedBackOff)
#         time.sleep(2)
#         GetASpectrum(DelayIntegrationTime)
#         SaveASpectrum(MyDataFolder, 'ref', IsFolderChecked)
    
# #%% Connection RotorStage

# RotorStage = fConnectRotorStage()

# #%% Connection PowerMeter

# PowerMeter = fConnectPowerMeter()

# #%% fScanPowerRange

# AngleStart = 0
# AngleStop = 90
# AngleNumberStep = 19
# DensityInfo = 0

# AngleAll, PowerAll, PowerRange, PowerRangeFitParameters = fScanPowerRange(RotorStage, PowerMeter, fBeamSplitterCubeLawTheta2Power, AngleStart, AngleStop, AngleNumberStep)

# PowerRangeMax = PowerRange[0]
# PowerRangeMin = PowerRange[1]

# Pmin = np.min(PowerAll)
# Pmax = np.max(PowerAll)

# #%% fMoveToPower

# #Desired ratio of the max power
# Ratio = 0.8

# SetPointPower = PowerRangeMin + Ratio * (PowerRangeMax - PowerRangeMin)
# fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

# #%% ChangeAngle

# Angle = 50
# RotorStage.move_to(Angle)

# #%% fGetPowerCurve

# RatioStart = 0.08
# RatioStop = 0.99
# PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
# PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

# PowerNumberStep = 31
# DelayIntegrationTime = 1 # [s]
# MyDataFolder = fGetPowerCurve(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, Pmin, Pmax, Ratio, RatioStart, RatioStop, DelayIntegrationTime, LinearPowerLogScale = True)
# time.sleep(0.5)

# # WLRange = np.array([535, 550]) # (nm)
# # WLRange = np.array([790, 810]) # (nm) 800 nm
# # WLRange = np.array([680, 710]) # (nm) 700 nm
# # WLRange = np.array([730, 750]) # (nm) 740 nm
# WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])
# fProcessPowerCurve(MyDataFolder, WLRangeAll)

# fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

# print('\nSetup back to the initial ratio of max power: ', Ratio)

# #%% fGetPowerCurve_BackAndForth

# RatioStart = 0.01
# RatioStop = 0.8
# PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
# PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

# PowerNumberStep = 5 # Step number will be doubled
# DelayIntegrationTime = 3 # [s]
# MyDataFolder = fGetPowerCurve_BackAndForth(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, SaveDataFolder, DensityInfo, Pmin, Pmax, Ratio, RatioStart, RatioStop, DelayIntegrationTime, LinearPowerLogScale = True)
# time.sleep(0.5)

# # WLRange = np.array([535, 550]) # [nm]
# # WLRange = np.array([790, 810]) # [nm] 800 nm
# # WLRange = np.array([680, 710]) # [nm] 700 nm
# # WLRange = np.array([730, 750]) # [nm] 740 nm
# WLRangeAll = np.array([[645, 650], [655, 665], [680, 710], [730, 750], [790, 810]])
# fProcessPowerCurveBackAndForth(MyDataFolder, WLRangeAll)

# fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

# print('\nSetup back to the initial ratio of max power: ', Ratio)

# #%% fAdaptiveRefinedPowerCurve

# RatioStart = 0.0001
# RatioStop = 0.9
# PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
# PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)

# PowerNumberStep = 31
# DelayIntegrationTime = 3    # [s]

# MyDataFolder = fAdaptiveRefinedPowerCurve(
#                                           RotorStage=RotorStage,
#                                           PowerMeter=PowerMeter,
#                                           SaveDataFolder=SaveDataFolder,
#                                           DensityInfo=DensityInfo,
#                                           Pmin=Pmin,
#                                           Pmax=Pmax,
#                                           Ratio=Ratio,
#                                           PowerStart=PowerStart,
#                                           PowerStop=PowerStop,
#                                           PowerNumberStep=PowerNumberStep,
#                                           RatioStart=RatioStart,
#                                           RatioStop=RatioStop,
#                                           DelayIntegrationTime=3,
#                                           SlopeThreshold=4, # Slope threshold to be chosen, 4 seems too high
#                                           MaxTotalExtraPoints=5,
#                                           LuminescenceJumpThreshold=1.05, # Percentage of luminescence difference to trigger fine measurement
#                                           WLRange=[790, 810]
#                                          )

# fProcessRefinedPowerCurve(MyDataFolder, WLRangeAll=[[790, 810]])


# fMoveToPower(RotorStage, PowerMeter, SetPointPower, *PowerRangeFitParameters)

# print('\nSetup back to the initial ratio of max power:', Ratio)

# #%% fScanAllHeightAllPower

# RatioStart = 0.5
# RatioStop = 0.5
# PowerStart = PowerRangeMin + RatioStart * (PowerRangeMax - PowerRangeMin)
# PowerStop = PowerRangeMin + RatioStop * (PowerRangeMax - PowerRangeMin)
# PowerNumberStep = 1
# DelayIntegrationTime = 2 # [s]
# SensZStep = - 60 # [mV] Must be an integer number, and negative to move back
# HeightNumberStep = 31

# fScanAllHeightAllPower()

# #%% fScanHeight

# DelayIntegrationTime = 2 # [s]
# SensZStep = - 80 # [mV] Must be an integer number, and negative to move back
# HeightNumberStep = 31
# DoRefSpectrum = True

# fScanHeight(DoRefSpectrum)

# #%% fStudyLaserStabilityPower

# SetPointPower = PowerRange[1]
# TimeTotal = 60 # (s)
# TimeStep = 1 # (s)
# fStudyLaserStabilityPower(RotorStage, PowerMeter, SetPointPower, TimeTotal, TimeStep, *PowerRangeFitParameters)

# #%% Disconnection rotor stage

# RotorStage.close()

# #%% Disconnection powermeter

# PowerMeter.disconnect_device() # To disconnect the device