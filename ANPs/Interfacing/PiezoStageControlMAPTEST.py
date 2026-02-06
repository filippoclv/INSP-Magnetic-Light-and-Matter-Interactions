import serial
import time
import tkinter as tk
from tkinter import ttk
import threading

class Piezoconcept:
    """
    Barebone Driver for FOC100.
    - Direct Serial (No nplab)
    - No software safety limits (Hardware handles 0-100um)
    - Integer Nanometers ('n') protocol
    """
    def __init__(self, port='COM9'):
        self.port = port
        self.ser = serial.Serial(
            port=self.port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            xonxoff=False, rtscts=False, dsrdtr=False
        )
        # Flush buffers to avoid reading old data
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        print(f"[Piezo] Connected on {port}")

    def _send(self, cmd):
        """Send raw command terminated by newline."""
        self.ser.write(f"{cmd}\n".encode('ascii'))
        # Tiny delay to let controller process
        time.sleep(0.05) 

    def _read(self):
        """Read response line."""
        try:
            response = self.ser.readline().decode('ascii').strip()
            return response
        except Exception as e:
            return f"Error: {e}"

    # --- MOVEMENT (Raw integer nanometers) ---
    # Manual says: MOVEX 200000n [cite: 283]

    def move_x(self, microns):
        nm = int(microns * 1000)
        self._send(f"MOVEX {nm}n")

    def move_y(self, microns):
        nm = int(microns * 1000)
        self._send(f"MOVEY {nm}n")

    def move_z(self, microns):
        nm = int(microns * 1000)
        self._send(f"MOVEZ {nm}n")

    # --- GETTERS ---
    def get_x(self):
        self.ser.reset_input_buffer() # Clear old echoes
        self._send("GET_X")
        return self._read()

    def get_y(self):
        self.ser.reset_input_buffer()
        self._send("GET_Y")
        return self._read()

    def get_z(self):
        self.ser.reset_input_buffer()
        self._send("GET_Z")
        return self._read()
    
    def get_info(self):
        self.ser.reset_input_buffer()
        self._send("INFOS")
        time.sleep(0.2) # INFO needs more time
        return self.ser.read(1024).decode('ascii', errors='ignore')

    def close(self):
        self.ser.close()
        print("[Piezo] Closed")

# --- GUI DASHBOARD ---
def launch_dashboard(piezo):
    root = tk.Tk()
    root.title("Piezo Dashboard (Real-Time)")
    
    # Variables
    pos_x = tk.StringVar(value="---")
    pos_y = tk.StringVar(value="---")
    pos_z = tk.StringVar(value="---")
    step_size = tk.DoubleVar(value=1.0) # Microns

    # Update Function
    def refresh_positions():
        # Note: Querying too fast might slow down movement commands in main script
        # Use this button manually when verifying
        pos_x.set(piezo.get_x())
        pos_y.set(piezo.get_y())
        pos_z.set(piezo.get_z())

    # Manual Move Functions
    def move_manual(axis, direction):
        step = step_size.get() * direction
        # We need to know current pos to do relative move? 
        # Or use MOVRX (Relative) command if available. 
        # Manual [cite: 276] confirms MOVRX exists.
        nm = int(step * 1000)
        piezo._send(f"MOVR{axis} {nm}n")
        refresh_positions()

    # Layout
    frame = ttk.LabelFrame(root, text="Position Readout")
    frame.pack(padx=10, pady=10, fill="x")

    ttk.Label(frame, text="X:").grid(row=0, column=0)
    ttk.Label(frame, textvariable=pos_x).grid(row=0, column=1)
    ttk.Label(frame, text="Y:").grid(row=1, column=0)
    ttk.Label(frame, textvariable=pos_y).grid(row=1, column=1)
    ttk.Label(frame, text="Z:").grid(row=2, column=0)
    ttk.Label(frame, textvariable=pos_z).grid(row=2, column=1)
    
    btn_refresh = ttk.Button(frame, text="READ XYZ", command=refresh_positions)
    btn_refresh.grid(row=3, column=0, columnspan=2, pady=5)

    ctrl_frame = ttk.LabelFrame(root, text="Manual Control")
    ctrl_frame.pack(padx=10, pady=10, fill="x")
    
    ttk.Label(ctrl_frame, text="Step (um):").pack()
    ttk.Entry(ctrl_frame, textvariable=step_size).pack()

    # Arrows
    btn_frame = ttk.Frame(ctrl_frame)
    btn_frame.pack(pady=5)
    
    ttk.Button(btn_frame, text="Y+", command=lambda: move_manual('Y', 1)).grid(row=0, column=1)
    ttk.Button(btn_frame, text="Y-", command=lambda: move_manual('Y', -1)).grid(row=2, column=1)
    ttk.Button(btn_frame, text="X-", command=lambda: move_manual('X', -1)).grid(row=1, column=0)
    ttk.Button(btn_frame, text="X+", command=lambda: move_manual('X', 1)).grid(row=1, column=2)

    root.mainloop()

if __name__ == "__main__":
    # Test Mode
    stage = Piezoconcept(port='COM9')
    print(stage.get_info())
    launch_dashboard(stage)