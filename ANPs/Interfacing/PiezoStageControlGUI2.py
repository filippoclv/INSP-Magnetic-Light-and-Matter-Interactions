from __future__ import print_function
import serial
import time
import sys
import threading
import tkinter as tk
from tkinter import ttk
import keyboard

# Dependencies: pip install pyserial keyboard

class Piezoconcept:
    """
    BAREBONE DRIVER - NO SAFETY CHECKS
    - Sends raw commands directly from the Manual.
    - Uses Integer Nanometers ('n') as requested.
    - Flushes buffers to keep connection stable.
    """
    
    def __init__(self, port="COM9"):
        self.port = port
        self.settings = {
            "baudrate": 115200, "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE, "stopbits": serial.STOPBITS_ONE,
            "timeout": 0.5, "xonxoff": False, "rtscts": False
        }
        try:
            self.ser = serial.Serial(port, **self.settings)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            print(f"[Piezo] Raw Connection Open on {port}")
        except Exception as e:
            print(f"[Piezo] FAILED: {e}")
            sys.exit(1)

    # --- RAW COMMS ---

    def _send(self, cmd):
        """Flush and Send. No logic."""
        self.ser.reset_input_buffer()
        self.ser.write(f"{cmd}\n".encode('ascii'))
        time.sleep(0.02) # Min hardware wait

    def _read(self):
        """Read until a number appears."""
        start = time.time()
        while time.time() - start < 0.5:
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if not line or "ok" in line.lower() or "move" in line.lower(): continue
                
                # Parse "12.34 um" or "12340 nm"
                clean = line.lower().replace('um','').replace('u','').replace('nm','').replace('n','').strip()
                val = float(clean)
                if 'nm' in line.lower() or line.lower().endswith('n'):
                    return val / 1000.0 # Convert nm to um
                return val
            except:
                continue
        return -999.0

    # --- MANUAL COMMANDS (Raw) ---

    def move_abs(self, axis, microns):
        """Sends MOVEX/Y/Z with integer nanometers."""
        nm = int(round(microns * 1000))
        self._send(f"MOVE{axis} {nm}n")

    def move_rel(self, axis, microns):
        """Sends MOVRX/Y/Z with integer nanometers."""
        nm = int(round(microns * 1000))
        self._send(f"MOVR{axis} {nm}n")

    def get_pos(self, axis):
        """Sends GET_X/Y/Z."""
        self.ser.reset_input_buffer()
        self.ser.write(f"GET_{axis}\n".encode('ascii'))
        return self._read()

    def get_infos(self):
        """Sends INFOS."""
        self.ser.reset_input_buffer()
        self.ser.write(b"INFOS\n")
        time.sleep(0.5)
        return self.ser.read_all().decode('ascii', errors='ignore')

    def close(self):
        self.ser.close()
        print("[Piezo] Closed.")

# --- GUI CLASS ---

class PiezoGUI:
    def __init__(self, root, piezo):
        self.piezo = piezo
        self.root = root
        self.root.title("Piezo Control Dashboard")
        self.root.geometry("400x350")

        # Styles
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Arial", 10, "bold"))

        # 1. Info Section
        frame_info = ttk.LabelFrame(root, text="Device Info")
        frame_info.pack(pady=5, padx=10, fill="x")
        
        self.btn_info = ttk.Button(frame_info, text="Get INFOS", command=self.show_infos)
        self.btn_info.pack(pady=5)
        
        self.lbl_info = tk.Text(frame_info, height=4, width=40, font=("Consolas", 8))
        self.lbl_info.pack(pady=5, padx=5)

        # 2. Position Section
        frame_pos = ttk.LabelFrame(root, text="Live Position (um)")
        frame_pos.pack(pady=5, padx=10, fill="x")

        self.lbl_x = ttk.Label(frame_pos, text="X: ---", style="Bold.TLabel")
        self.lbl_x.pack(anchor="w", padx=10)
        self.lbl_y = ttk.Label(frame_pos, text="Y: ---", style="Bold.TLabel")
        self.lbl_y.pack(anchor="w", padx=10)
        self.lbl_z = ttk.Label(frame_pos, text="Z: ---", style="Bold.TLabel")
        self.lbl_z.pack(anchor="w", padx=10)

        self.btn_read = ttk.Button(frame_pos, text="Read Position", command=self.update_pos)
        self.btn_read.pack(pady=5)

        # 3. Control Section
        frame_ctrl = ttk.LabelFrame(root, text="Manual Control")
        frame_ctrl.pack(pady=5, padx=10, fill="x")

        ttk.Label(frame_ctrl, text="Step Size (um):").grid(row=0, column=0, padx=5)
        self.ent_step = ttk.Entry(frame_ctrl, width=10)
        self.ent_step.insert(0, "0.5")
        self.ent_step.grid(row=0, column=1, padx=5)

        self.btn_center = ttk.Button(frame_ctrl, text="Recenter (25um)", command=self.recenter)
        self.btn_center.grid(row=0, column=2, padx=10)

        ttk.Label(frame_ctrl, text="(Use Arrow Keys to Move X/Y)").grid(row=1, column=0, columnspan=3, pady=10)

        # Bind Keys
        root.bind('<Left>', lambda e: self.move('X', -1))
        root.bind('<Right>', lambda e: self.move('X', 1))
        root.bind('<Up>', lambda e: self.move('Y', 1))
        root.bind('<Down>', lambda e: self.move('Y', -1))
        root.bind('<Prior>', lambda e: self.move('Z', 1)) # Page Up
        root.bind('<Next>', lambda e: self.move('Z', -1)) # Page Down

    def show_infos(self):
        info = self.piezo.get_infos()
        self.lbl_info.delete("1.0", tk.END)
        self.lbl_info.insert(tk.END, info)

    def update_pos(self):
        x = self.piezo.get_pos('X')
        y = self.piezo.get_pos('Y')
        z = self.piezo.get_pos('Z')
        self.lbl_x.config(text=f"X: {x:.4f}")
        self.lbl_y.config(text=f"Y: {y:.4f}")
        self.lbl_z.config(text=f"Z: {z:.4f}")

    def recenter(self):
        print("Recentering...")
        self.piezo.move_abs('X', 25.0)
        self.piezo.move_abs('Y', 25.0)
        self.update_pos()

    def move(self, axis, direction):
        try:
            step = float(self.ent_step.get())
            self.piezo.move_rel(axis, direction * step)
            # Optional: Auto-update pos (can slow things down, uncomment if desired)
            # self.update_pos() 
        except ValueError:
            print("Invalid Step Size")

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    
    # 1. Connect
    PiezoStage = Piezoconcept(port="COM9") # <--- CHECK PORT
    
    # 2. Launch GUI
    root = tk.Tk()
    app = PiezoGUI(root, PiezoStage)
    
    # Handle Close
    def on_closing():
        PiezoStage.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()