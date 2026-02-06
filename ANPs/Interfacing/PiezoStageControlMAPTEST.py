import serial
import time
import tkinter as tk
from tkinter import ttk
import threading

class Piezoconcept:
    """
    Robust Driver for FOC100.
    - Adds 'move_rel' for Relative Mapping.
    - Filters Echoes and 'Ok' responses.
    """
    def __init__(self, port='COM9'):
        self.port = port
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5,
                xonxoff=False, rtscts=False, dsrdtr=False
            )
            self.ser.reset_input_buffer()
            print(f"[Piezo] Connected on {port}")
        except Exception as e:
            print(f"[Piezo] Connection Error: {e}")

    def _send(self, cmd):
        self.ser.reset_input_buffer()
        self.ser.write(f"{cmd}\n".encode('ascii'))
        time.sleep(0.05) 

    def _read_float(self):
        """Smart Read: Ignores 'Ok' and Echoes."""
        start_time = time.time()
        while time.time() - start_time < 1.0:
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if not line or line == "Ok" or line.startswith("MOV") or line.startswith("GET"):
                    continue
                # Parse number
                clean = line.lower().replace('um','').replace('nm','').replace('u','').replace('n','').strip()
                return float(clean)
            except ValueError:
                continue
        return -999.0

    # --- RELATIVE MOVE (Crucial for your Map) ---
    def move_rel(self, axis, microns):
        """
        MOVRX / MOVRY
        Moves relative to CURRENT position. No jumps.
        """
        nm = int(microns * 1000)
        # Command is MOVRX, MOVRY, etc.
        cmd = f"MOVR{axis.upper()} {nm}n"
        self.ser.write(f"{cmd}\n".encode('ascii'))
        time.sleep(0.1) # Wait for move to finish

    # --- ABSOLUTE MOVE ---
    def move_x(self, microns):
        nm = int(microns * 1000)
        self.ser.write(f"MOVEX {nm}n\n".encode('ascii'))
        time.sleep(0.05)

    def move_y(self, microns):
        nm = int(microns * 1000)
        self.ser.write(f"MOVEY {nm}n\n".encode('ascii'))
        time.sleep(0.05)

    # --- GETTERS ---
    def get_x(self):
        self._send("GET_X")
        return str(self._read_float())

    def get_y(self):
        self._send("GET_Y")
        return str(self._read_float())
    
    def get_info(self):
        self.ser.reset_input_buffer()
        self.ser.write(b"INFOS\n")
        time.sleep(0.2)
        return self.ser.read(1024).decode('ascii', errors='ignore')

    def close(self):
        self.ser.close()
        print("[Piezo] Closed")