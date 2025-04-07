# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 17:15:56 2024

@author: benre
"""

# TO BE TESTED VERSION

import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pylablib.devices import Thorlabs # pip install pylablib
from pyThorlabsPM100x.driver import ThorlabsPM100x

def fConnectRotorStage():

    # print('Hello !')
    DetectedDevices = Thorlabs.list_kinesis_devices()
    print(DetectedDevices)
    RotorStage = Thorlabs.KinesisMotor(DetectedDevices[0][0], scale = 'stage')
    # print(RotorStage.get_scale())
    # print(RotorStage.get_scale_units())
    # print(RotorStage.get_velocity_parameters())
    RotorStage.setup_velocity(max_velocity = 20, scale = 'stage') # Max velocity = 25 deg/s but we set it at 20
    
    if RotorStage.is_homed() == False:

        print('Homing ...')
        RotorStage.home()
        RotorStage.wait_for_home()
        print('Stage well homed')

    else:

        print('Stage already homed')

    RotorStage.move_to(0, scale = True)
    RotorStage.wait_move()
    
    print('RotorStage connected')

    return RotorStage


def fConnectPowerMeter():

    PowerMeter = ThorlabsPM100x()
    available_devices = PowerMeter.list_devices() #Check which devices are available
    print(available_devices)

    if available_devices == []:

        print('Check if the Driver are PM100D. Use Thorlabs.PMDriverSwitcher.')

    PowerMeter.connect_device(device_addr = available_devices[0][0]) #Connect to the first available device
    # PowerMeter.wavelength(wavelength)
    # PowerMeter.auto_power_range(True)
    print('PowerMeter connected')

    return PowerMeter

def fMeasurePower(PowerMeter):

    CurrentPower = np.array(PowerMeter.power)

    if CurrentPower[1] == 'W':

        ReturnPower = float(CurrentPower[0])

    elif CurrentPower[1] == 'mW':

        ReturnPower = float(CurrentPower[0]) * 1e-3

    elif CurrentPower[1] == 'uW':

        ReturnPower = float(CurrentPower[0]) * 1e-6

    return ReturnPower

def fBeamSplitterCubeLawTheta2Power(theta, theta0, P0, P1):

    P = P0 * np.cos(2*(theta - theta0)*(np.pi/180)) * np.cos(2*(theta - theta0) *(np.pi/180)) + P1

    return P
 
def fBeamSplitterCubeLawPower2Theta(P, theta0, P0, P1):

    theta = ( np.arccos(np.sqrt((P - P1)/P0))/2 + (theta0*(np.pi/180)) ) * (180/np.pi)

    return theta
   
def fScanPowerRange(RotorStage, PowerMeter, fMalusLawTheta2Power, AngleStart = 0, AngleStop = 180, AngleNumberStep = 21):   
    
    # AngleAll = np.array(range(AngleStart, AngleStop, AngleStep))
    # AngleNumberStep = (AngleStop - AngleStart)/AngleStep + 1
    AngleAll = np.linspace(AngleStart, AngleStop, AngleNumberStep)
    PowerAll = []
    print('Power scan in progress ...')

    for i in range(0, len(AngleAll)):

        AngleNew = AngleAll[i]
        RotorStage.move_to(AngleNew, scale = True)
        RotorStage.wait_move()
        time.sleep(0.1)
        CurrentPower = fMeasurePower(PowerMeter)
        PowerAll.append(CurrentPower)
        CurrentPosition = RotorStage.get_position()
        print('theta = ', f'{CurrentPosition:.5f}', '° \t P = ', f'{CurrentPower:.5f}', 'W')

    PowerAll = np.array(PowerAll)
    print('Power scan over!')
    
    OptFitParameters, _ = curve_fit(fMalusLawTheta2Power, AngleAll, PowerAll)
    
    PowerRangeMax = OptFitParameters[2] # P0 ?
    PowerRangeMin = OptFitParameters[1] + OptFitParameters[2] # P0 + P1 ?
    PowerRange = np.array([PowerRangeMin, PowerRangeMax])
    
    print('The power range is', PowerRange, 'W')
    
    fig, ax = plt.subplots()
    ax.scatter(AngleAll, PowerAll)
    ax.plot(AngleAll, fMalusLawTheta2Power(AngleAll, *OptFitParameters))
    plt.axhline(PowerRange[0])
    plt.axhline(PowerRange[1])
    ax.set_xlabel('Angle [°]')
    ax.set_ylabel('Power [W]')
    # plt.ticklabel_format(axis='both', style='sci')
    plt.show()

    RotorStage.move_to(AngleAll[np.argmin(PowerAll)], scale=True)
    RotorStage.wait_move()
    time.sleep(0.1)
    print('Angle back to theta = ', f'{RotorStage.get_position():.5f}', '°, \t where P = ',
          f'{fMeasurePower(PowerMeter):.5f}', 'W, the minimum power value')

    return AngleAll, PowerAll, PowerRange, OptFitParameters

def fMoveToPower(RotorStage, PowerMeter, SetPointPower, *OptFitParameters):

    print('Power is changing ...')
    CorrespondingAngle = fBeamSplitterCubeLawPower2Theta(SetPointPower, *OptFitParameters)
    RotorStage.move_to(CorrespondingAngle, scale = True)
    RotorStage.wait_move()
    CurrentPower = fMeasurePower(PowerMeter)
    print('theta = ', f'{CorrespondingAngle:.5f}', '° \t P = ', f'{CurrentPower:.5f}', 'W')
    print('Done!')

def fLaunchPowerMeasurements(RotorStage, PowerMeter, PowerStart, PowerStop, PowerNumberStep, *OptFitParameters):

    PowerAll = np.linspace(PowerStart, PowerStop, PowerNumberStep)
    PowerData = []
    AngleData = []

    for i in range(0, len(PowerAll)):

        SetPointPower = PowerAll[i]
        fMoveToPower(RotorStage, PowerMeter, SetPointPower, *OptFitParameters)
        time.sleep(0.1)
        PowerData.append(fMeasurePower(PowerMeter))
        # print(RotorStage.get_position(scale = True))
        AngleData.append(RotorStage.get_position(scale = True))
        
    PowerData = np.array(PowerData)
    AngleData = np.array(AngleData)
    
    fig, ax = plt.subplots()
    # plt.ticklabel_format(axis = 'x', style = 'sci', scilimits = (4,4))
    ax.scatter(PowerData, AngleData)
    ax.set_xlabel('Power [W]')
    ax.set_ylabel('Angle [°]')
    plt.show()
    
    return PowerData, AngleData

def fStudyLaserStabilityPower(RotorStage, PowerMeter, SetPointPower, TimeTotal, TimeStep = 0.5, *OptFitParameters):

    fMoveToPower(RotorStage, PowerMeter, SetPointPower, *OptFitParameters)
    TimeAll = np.arange(0, TimeTotal, TimeStep)
    PowerAll = []
    print('Power acquisition ongoing ...')

    for i in range(0, len(TimeAll)):

        CurrentPower = fMeasurePower(PowerMeter)
        PowerAll.append(CurrentPower)
        # print(CurrentPower)
        time.sleep(TimeStep)

    print('Power acquisition done!')
        
    fig, ax = plt.subplots()
    # plt.ticklabel_format(axis = 'x', style = 'sci', scilimits = (4,4))
    ax.scatter(TimeAll, PowerAll)
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Power [W]')
    plt.show()