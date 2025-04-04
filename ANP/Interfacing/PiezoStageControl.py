# -*- coding: utf-8 -*-
"""
Created on Thu Oct 01 11:52:44 2015

@author: benre
"""
from __future__ import print_function
from builtins import str
import serial
import nplab.instrument.serial_instrument as si

class Piezoconcept(si.SerialInstrument):
    '''A simple class for the Piezo concept FOC100 nanopositioning system'''
    
    def __init__(self, port=None):

        self.termination_character = '\n'
        self.port_settings = {
                    'baudrate':115200,
                    'bytesize':serial.EIGHTBITS,
                    'parity':serial.PARITY_NONE,
                    'stopbits':serial.STOPBITS_ONE,
                    'timeout': 1, #wait at most one second for a response
          #          'writeTimeout':1, #similarly, fail if writing takes >1s
          #         'xonxoff':False, 'rtscts':False, 'dsrdtr':False,
                    }

        si.SerialInstrument.__init__(self,port=port)
        # self.recenter()
        
    def move_rel(self,value,unit="n"):
        '''A command for relative movement, where the default units is nm'''
        if unit == "n":

            multiplier=1

        if unit == "u":

            multiplier=1E3
             
        if (value*multiplier+self.position) > 1E5 or (value*multiplier+self.position) < 0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (X)")

        elif (value*multiplier+self.position) < 1E5 and (value*multiplier+self.position) >= 0:

            self.write("MOVRX "+str(value)+unit)
            self.position=(value*multiplier+self.position)
    
    def MOVEX(self,value,unit="n"):
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range(100um) default unit is nm'''

        if unit == "n":

            multiplier=1
        if unit == "u":

            multiplier=1E3
            
        if value*multiplier >1E5 or value*multiplier <0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (X)")
            
        elif value*multiplier < 1E5 and value*multiplier >=0:

            self.write("MOVEX "+str(value)+unit)
            self.position = value*multiplier

    def MOVEY(self,value,unit="n"):
        '''An absolute movement command, will print an error to the console 
        if you moveoutside of the range(100um) default unit is nm'''

        if unit == "n":

            multiplier=1
        if unit == "u":

            multiplier=1E3
            
        if value*multiplier >1E5 or value*multiplier <0:

            print("The value is out of range! 0-100 um (0-1E8 nm) (Y)")
            
        elif value*multiplier < 1E5 and value*multiplier >=0:

            self.write("MOVEY "+str(value)+unit)
            self.position = value*multiplier
            
    def move_step(self,direction):

        self.move_rel(direction*self.stepsize)
        
    def recenter(self):
        ''' Moves the stage to the center position'''

        self.move(50,unit = "u")
        self.position = 50E3
        
    def INFOS(self):

        return self.query("INFOS", multiline = True, timeout = .1,)
    
    def GET_X(self):

        print(self.query("GET_X", multiline = True, termination_line = "\n \n \n \n", timeout = .1,))
    
    def GET_Y(self):

        print(self.query("GET_Y", multiline = True, termination_line = "\n \n \n \n", timeout = .1,))
    
    def GET_Z(self):

        print(self.query("GET_Z", multiline = True, termination_line = "\n \n \n \n", timeout = .1,))
    
    def GEXYZ(self):

        self.GET_X()
        self.GET_Y()
        self.GET_Z()
        
        
#%% Connection PiezoStage

PiezoStage = Piezoconcept(port = "COM9")

#%% Let's play!

Piezoconcept.MOVEX(PiezoStage, 20, "u")

#%% Let's play!

Piezoconcept.MOVEY(PiezoStage, 25, "u")

#%%

# Piezoconcept.INFOS(PiezoStage)
Piezoconcept.GET_X(PiezoStage)

#%%

Piezoconcept.GET_Y(PiezoStage)

#%%

Piezoconcept.GEXYZ(PiezoStage)

#%%

PiezoStage.close()