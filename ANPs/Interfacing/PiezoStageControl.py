from __future__ import print_function
from builtins import str
import serial
import nplab.instrument.serial_instrument as si
import time
import tkinter as tk
import keyboard
from threading import Thread

# Could be necessary:
# pip install keyboard
# pip install serial
# pip install nplab

class Piezoconcept(si.SerialInstrument):
    """A simple class for the Piezo concept FOC100 nanopositioning system."""
    
    def __init__(self, position=None, port=None):

        self.position = position
        self.termination_character = '\n'
        self.port_settings = {
                    "baudrate":115200,
                    "bytesize":serial.EIGHTBITS,
                    "parity":serial.PARITY_NONE,
                    "stopbits":serial.STOPBITS_ONE,
                    "timeout": 1, # Wait at most one second for a response
                    #"writeTimeout":1, #similarly, fail if writing takes >1s
                    #"xonxoff":False, 'rtscts':False, 'dsrdtr':False,
                    }

        si.SerialInstrument.__init__(self, port=port)
        #self.recenter()
        
    def move_relX(self, value, unit="n"):
        """A command for relative movement, where the default units is nm."""

        if unit == "n":

            multiplier=1

        if unit == "u":

            multiplier=1E3
             
        if (value*multiplier+self.position) > 1E5 or (value*multiplier+self.position) < 0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (X)")

        elif (value*multiplier+self.position) < 1E5 and (value*multiplier+self.position) >= 0:

            self.write("MOVRX "+str(value)+unit)
            self.position=(value*multiplier+self.position)

    def move_relY(self, value, unit="n"):
        """A command for relative movement, where the default units is nm."""

        if unit == "n":
            multiplier = 1

        if unit == "u":
            multiplier = 1E3

        if (value * multiplier + self.position) > 1E5 or (value * multiplier + self.position) < 0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (X)")

        elif (value * multiplier + self.position) < 1E5 and (value * multiplier + self.position) >= 0:

            self.write("MOVRY " + str(value) + unit)
            self.position = (value * multiplier + self.position)

    def move_relZ(self, value, unit="n"):
        """A command for relative movement, where the default units is nm."""

        if unit == "n":
            multiplier = 1

        if unit == "u":
            multiplier = 1E3

        if (value * multiplier + self.position) > 1E5 or (value * multiplier + self.position) < 0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (X)")

        elif (value * multiplier + self.position) < 1E5 and (value * multiplier + self.position) >= 0:

            self.write("MOVRZ " + str(value) + unit)
            self.position = (value * multiplier + self.position)
    
    def MOVEX(self, value, unit="n"):
        """An absolute movement command, will print an error to the console
        if you move outside of the range(100um) default unit is nm"""

        if unit == "n":

            multiplier=1

        if unit == "u":

            multiplier=1E3
            
        if value*multiplier >1E5 or value*multiplier <0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (X)")
            
        elif value*multiplier < 1E5 and value*multiplier >=0:

            self.write("MOVEX "+str(value)+unit)
            self.position = value*multiplier

    def MOVEY(self, value, unit="n"):
        """An absolute movement command, will print an error to the console
        if you move outside of the range(100um) default unit is nm"""

        if unit == "n":

            multiplier=1

        if unit == "u":

            multiplier=1E3
            
        if value*multiplier >1E5 or value*multiplier <0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (Y)")
            
        elif value*multiplier < 1E5 and value*multiplier >=0:

            self.write("MOVEY "+str(value)+unit)
            self.position = value*multiplier

    def recenter(self):
        """Moves the stage to the center position."""

        self.move(50,unit = "u")
        self.position = 50E3
        
    def INFOS(self):
        """Read full device information as raw text."""
        
        self.write("INFOS")
        time.sleep(3)  # Let it respond fully
        
        try:
            
            raw = self.ser.read(1024)  # Read up to 1024 bytes
            
            return raw.decode("latin1").strip()
        
        except UnicodeDecodeError as e:
            
            return f"[Decode error] {e}"

    def GET_X(self):

        return self.query("GET_X", multiline=False, timeout=0.1).strip()
    
    def GET_Y(self):

        return self.query("GET_Y", multiline=False, timeout=0.1).strip()
    
    def GET_Z(self):

        return self.query("GET_Z", multiline=False, timeout=0.1).strip()
    
    def GET_XYZ(self):

        return {
                "X": self.GET_X(),
                "Y": self.GET_Y(),
                "Z": self.GET_Z()
               }

# Move by steps with arrow keys:

def move_x(direction):

    PiezoStage.move_relX(direction * step_size, "n")
    print(f"Moved X: {direction * step_size} nm")

def move_y(direction):

    PiezoStage.move_relY(direction * step_size, "n")
    print(f"Moved Y: {direction * step_size} nm")

def move_z(direction):

    PiezoStage.move_relZ(direction * step_size, "n")
    print(f"Moved Z: {direction * step_size} nm")

def keyboard_input():

    print("[INFO] Use arrow keys to move in the X/Y direction, ESC to exit.")

    while True:

        try:

            if keyboard.is_pressed('right'):

                move_x(1)
                time.sleep(0.1)

            elif keyboard.is_pressed('left'):

                move_x(-1)
                time.sleep(0.1)

            elif keyboard.is_pressed('up'):

                move_y(1)
                time.sleep(0.1)

            elif keyboard.is_pressed('down'):

                move_y(-1)
                time.sleep(0.1)

            elif keyboard.is_pressed('esc'):

                print("[INFO] Exiting...")

                break

        except:

            break

def launch_gui():

    root = tk.Tk()
    root.title("Piezostage keyboard controller")
    root.geometry("300x100")
    label = tk.Label(root, text="Use arrow keys to move.\nESC to exit.", font=("Arial", 12))
    label.pack(pady=20)
    root.mainloop()

#%% Connection PiezoStage

#PiezoStage = Piezoconcept(port = "COM9")

#%%

#PiezoStage.MOVEX(3, "u")

#%%

#PiezoStage.MOVEY(15, "u")

#%%

#print(PiezoStage.INFOS())

#%%

#print(f'\nX position: {PiezoStage.GET_X()}')

#%%

#print(f'\nY position: {PiezoStage.GET_Y()}')

#%%

#print(f'\nXYZ position: {PiezoStage.GET_XYZ()}')

#%%

#PiezoStage.recenter()
#print(f'\nXYZ position: {PiezoStage.GET_XYZ()}')

#%%

PiezoStage.move_relX(5, "u")
print(f'\nXYZ position: {PiezoStage.GET_XYZ()}')

#%%

PiezoStage.move_relY(5, "u")
print(f'\nXYZ position: {PiezoStage.GET_XYZ()}')

#%%

#PiezoStage.move_relZ(50, "n")
#print(f'\nXYZ position: {PiezoStage.GET_XYZ()}')

#%% Manual step movement:

#step_size = 100 # Nanometers by default

#move_x(1) # Forward

#%%

#step_size = 100 # Nanometers by default

#move_x(-1) # Backwards

#%%

#step_size = 100 # Nanometers by default

#move_y(1)

#%%

#step_size = 100 # Nanometers by default

#move_y(-1)

#%% GUI to move with arrow keys

#step_size = 100 # Nanometers by default

#Thread(target=keyboard_input, daemon=True).start()
#launch_gui()

#%%

#PiezoStage.close()