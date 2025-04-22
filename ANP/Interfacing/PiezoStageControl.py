from __future__ import print_function
from builtins import str
import serial
import nplab.instrument.serial_instrument as si
import time

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
        
    def move_rel(self, value, unit="n"):
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
            
    def move_step(self, direction):

        self.move_rel(direction*self.stepsize)
        
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
    
#%% Connection PiezoStage

PiezoStage = Piezoconcept(port = "COM9")

#%% Testing:

PiezoStage.MOVEX(20, "u")

#%%

PiezoStage.MOVEY(25, "u")

#%%

print(PiezoStage.INFOS())

#%%

print(f'\nX position: {PiezoStage.GET_X()}')

#%%

print(f'\nY position: {PiezoStage.GET_Y()}')

#%%

print(f'\nXYZ position: {PiezoStage.GET_XYZ()}')

#%%

PiezoStage.close()