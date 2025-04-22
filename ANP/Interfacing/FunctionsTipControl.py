import pyautogui as pyGUI
# https://pyautogui.readthedocs.io/en/latest/install.html
# pip install pyautogui
# pip install opencv-python

import time
# https://docs.python.org/fr/3/library/time.html

import pyperclip
import os

'''

def GetASpectrum(DelayIntegrationTime):

    ButtonCoord = pyGUI.locateOnScreen('SingleScanButton.PNG', grayscale=True, confidence = 0.9)
    ButtonCoordCenter = pyGUI.center(ButtonCoord)
    pyGUI.click(ButtonCoordCenter)
    time.sleep(DelayIntegrationTime)
    time.sleep(0.5)

def SaveASpectrum(FolderName, FileName, IsFolderChecked = True):
    # Save the spectrum:
    
    ButtonCoord1 = pyGUI.locateOnScreen('SaveSpectrumButton.PNG', grayscale=True, confidence = 0.9)
    ButtonCoord1Center = pyGUI.center(ButtonCoord1)
    pyGUI.click(ButtonCoord1Center)
    time.sleep(0.7)
    
    # Check the folder:
    if IsFolderChecked == False:

        #pyGUI.click(pyGUI.locateOnScreen('FolderButton.PNG', grayscale=True, confidence = 0.9))
        
        ButtonCoord3 = pyGUI.locateOnScreen('FolderButton2.PNG', grayscale=True, confidence = 0.9)
        ButtonCoord3Center = pyGUI.center(ButtonCoord3)
        pyGUI.click(ButtonCoord3.left - 5, ButtonCoord3Center.y)
        #pyGUI.write(FolderName)
        pyperclip.copy(FolderName)
        pyGUI.hotkey('ctrl', 'V')
        pyGUI.press('enter')
        time.sleep(0.1)
        IsFolderChecked = True
    
    # Save File:
    ButtonCoord2 = pyGUI.locateOnScreen('SaveSpectrumFileNameLoc.PNG', grayscale=True, confidence = 0.8)
    ButtonCoord2Center = pyGUI.center(ButtonCoord2)
    pyGUI.click(ButtonCoord2.left + ButtonCoord2.width, ButtonCoord2Center.y)
    #pyGUI.write(str(FileName))
    pyperclip.copy(str(FileName))
    pyGUI.hotkey('ctrl', 'V')
    pyGUI.press('enter')
    #time.sleep(0.1)
    #pyGUI.click(pyGUI.locateOnScreen('SaveFileSpectrumButton.PNG', grayscale=True, confidence = 0.9))
    time.sleep(0.5)

    return IsFolderChecked
    
'''

def BoucleGetSpectra(NumberSpectra, DelayIntegrationTime, FolderName): # Boucle stands for looping

    for i in range(NumberSpectra):

        FileName = str(i)
        GetASpectrum(DelayIntegrationTime)
        SaveASpectrum(FolderName, FileName)

def ChangeSetPointV(MoveSenZ_mV):

    if MoveSenZ_mV > 0:

        print('SenZ must be negative!')

    ButtonCoord = pyGUI.locateOnScreen('SetPointVoltArea.PNG', grayscale=True, confidence = 0.95)
    ButtonCoordCenter = pyGUI.center(ButtonCoord)
    
    #pyGUI.click(ButtonCoordCenter.x, ButtonCoordCenter.y + 10)
    
    # Get the old value of SenZ:
    pyGUI.moveTo(ButtonCoord.left + ButtonCoord.width + 35, ButtonCoordCenter.y)
    pyGUI.mouseDown(button='left')
    pyGUI.move(-35, 0)
    pyGUI.mouseUp(button='left')
    pyGUI.click(button='right')
    pyGUI.move(35, 65)
    pyGUI.click()
    OldSenZ_mV = float(pyperclip.paste().replace(",", "."))
    time.sleep(0.5)
    
    # Set the new value of SenZ:
    pyGUI.click(ButtonCoord.left + ButtonCoord.width + 35, ButtonCoordCenter.y)

    if  MoveSenZ_mV >= 0:

        pyGUI.press('up', presses = abs(MoveSenZ_mV))

    elif MoveSenZ_mV < 0:

        pyGUI.press('down', presses = abs(MoveSenZ_mV))

    time.sleep(0.5)
    
    # Get the new value of SenZ:
    pyGUI.moveTo(ButtonCoord.left + ButtonCoord.width + 35, ButtonCoordCenter.y)
    pyGUI.mouseDown(button='left')
    pyGUI.move(-35, 0)
    pyGUI.mouseUp(button='left')
    pyGUI.click(button='right')
    pyGUI.move(35, 65)
    pyGUI.click()
    NewSenZ_mV = float(pyperclip.paste().replace(",", "."))
    time.sleep(0.5)
    
    return OldSenZ_mV, NewSenZ_mV

def BoucleChangeSetPointV(NumberStep, MoveSenZ_mV, DelayIntegrationTime, FolderName):

    for i in range(NumberStep):

        OldSenZ_mV, NewSenZ_mV = ChangeSetPointV(MoveSenZ_mV)
        
        #FileName = f"{i} {NewSenZ_mV} mV"
        FileName = f"{NewSenZ_mV} mV {DelayIntegrationTime} s"
        
        GetASpectrum(DelayIntegrationTime)
        SaveASpectrum(FolderName, FileName)

def FromPhaseToSenZ():

    # To save dZ:
    ButtonCoord = pyGUI.locateOnScreen('FeedbackLoopButtonOn.PNG', grayscale = True, confidence = 0.95)
    ButtonCoordCenter = pyGUI.center(ButtonCoord)
    pyGUI.moveTo(ButtonCoord.left + ButtonCoord.width + 15, ButtonCoordCenter.y)
    pyGUI.click()
    pyGUI.move(0, 90)
    pyGUI.click()
    time.sleep(0.1)

    # To give the phase to SenZ:
    ButtonCoord2 = pyGUI.locateOnScreen('PhaseButton.PNG', grayscale=True, confidence = 0.95)
    ButtonCoord2Center = pyGUI.center(ButtonCoord2)
    pyGUI.moveTo(ButtonCoord2.left + ButtonCoord2.width + 0, ButtonCoord2Center.y)
    pyGUI.click()
    pyGUI.move(0, 90)
    pyGUI.click()
    time.sleep(0.1)

    # Asking to enter the current value of SenZ and modify the SetPoint:
    CurrentSenZ_mV = pyGUI.prompt(text='What is the value of SenZ ?', title='Attention!' , default='')
    ButtonCoord3 = pyGUI.locateOnScreen('SetPointVoltArea.PNG', grayscale=True, confidence = 0.95)
    ButtonCoord3Center = pyGUI.center(ButtonCoord3)
    pyGUI.moveTo(ButtonCoord3.left + ButtonCoord3.width + 35, ButtonCoord3Center.y)
    pyGUI.mouseDown(button='left')
    pyGUI.move(-35, 0)
    pyGUI.mouseUp(button='left')
    pyGUI.write(str(CurrentSenZ_mV))
    pyGUI.press('enter')
    time.sleep(0.1)

    # Looping again:
    ButtonCoord4 = pyGUI.locateOnScreen('FeedbackLoopSavedZButton.PNG', grayscale=True, confidence = 0.95)
    ButtonCoord4Center = pyGUI.center(ButtonCoord4)
    pyGUI.moveTo(ButtonCoord4.left + ButtonCoord4.width + 5, ButtonCoord4Center.y)
    pyGUI.click()
    pyGUI.move(0, 45)
    pyGUI.click()
    time.sleep(0.1)
    return CurrentSenZ_mV

def FromSenZToPhase(FeedBackOff = False):

    # To save dZ:
    ButtonCoord = pyGUI.locateOnScreen('FeedbackLoopButtonOn.PNG', grayscale=True, confidence = 0.95)
    ButtonCoordCenter = pyGUI.center(ButtonCoord)
    pyGUI.moveTo(ButtonCoord.left + ButtonCoord.width + 20, ButtonCoordCenter.y)
    pyGUI.click()
    pyGUI.move(0, 90)
    pyGUI.click()
    time.sleep(0.3)

    # To give the phase to SenZ:
    ButtonCoord2 = pyGUI.locateOnScreen('SenZButton.PNG', grayscale=True, confidence = 0.9)
    ButtonCoord2Center = pyGUI.center(ButtonCoord2)
    pyGUI.moveTo(ButtonCoord2.left + ButtonCoord2.width + 5, ButtonCoord2Center.y)
    pyGUI.click()
    pyGUI.move(0, 45)
    pyGUI.click()
    time.sleep(0.3)

    # Looping again:
    ButtonCoord4 = pyGUI.locateOnScreen('FeedbackLoopSavedZButton.PNG', grayscale=True, confidence = 0.99)
    ButtonCoord4Center = pyGUI.center(ButtonCoord4)
    pyGUI.moveTo(ButtonCoord4.left + ButtonCoord4.width + 5, ButtonCoord4Center.y)
    pyGUI.click()
    pyGUI.move(0, 45)
    pyGUI.click()
    time.sleep(0.3)
    
    if FeedBackOff == True:

        time.sleep(1)
        ButtonCoord5 = pyGUI.locateOnScreen('FeedbackLoopButtonOn.PNG', grayscale=True, confidence = 0.95)
        ButtonCoord5Center = pyGUI.center(ButtonCoord5)
        pyGUI.moveTo(ButtonCoord5Center)
        pyGUI.click()
        time.sleep(0.3)

def RunSeveralSeries(NumberSeries, NumberStep, MoveSenZ_mV, DelayIntegrationTime, FolderName):

    for i in range(NumberSeries):

        NewFolderName = f'{FolderName}\{i}'

        if not os.path.exists(NewFolderName):

            os.mkdir(NewFolderName)
            print("Folder %s created!" % NewFolderName)

        FromPhaseToSenZ()
        BoucleChangeSetPointV(NumberStep, MoveSenZ_mV, DelayIntegrationTime, NewFolderName)
        FromSenZToPhase()