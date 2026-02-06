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
    BAREBONE DRIVER (Status: WORKING)
    - Protocol: Integer Nanometers ('n').
    - connection: Direct Serial with aggressive flushing.
    """
    
    def __init__(self, port="COM9"):
        self.port = port
        self.settings = {
            "baudrate": 115200, "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE, "stopbits": serial.STOPBITS_ONE,
            "timeout": 0.5, "xonxoff": False, "rtscts": False
        }
        self.lock = threading.Lock() # Thread-safe lock for serial port
        
        try:
            self.ser = serial.Serial(port, **self.settings)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            print(f"[Piezo] Connected on {port}")
        except Exception as e:
            print(f"[Piezo] FAILED: {e}")
            sys.exit(1)

    def _send(self, cmd):
        """Thread-safe send."""
        with self.lock:
            self.ser.reset_input_buffer()
            self.ser.write(f"{cmd}\n".encode('ascii'))
            time.sleep(0.02)

    def _read(self):
        """Thread-safe read float."""
        # Note: Caller should hold lock if strictly necessary, 
        # but for simple request/reply usually it's fine if _send took the lock.
        # We'll assume the caller methods handle the lock or we do it here.
        # To avoid lock recursion, we won't lock inside _read if called by locked methods.
        # Ideally, we lock at the public method level.
        pass 

    def _read_safe(self):
        """Internal read loop."""
        start = time.time()
        while time.time() - start < 0.5:
            
            
            
            
            
            try:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if not line: continue
                if "ok" in line.lower() or "move" in line.lower(): continue
                
                clean = line.lower().replace('um','').replace('u','').replace('nm','').replace('n','').strip()
                val = float(clean)
                if 'nm' in line.lower() or line.lower().endswith('n'):
                    return val / 1000.0
                return val
            except:
                continue
        return -999.0

    # --- PUBLIC COMMANDS (Thread-Safe) ---

    def move_rel(self, axis, microns):
        with self.lock:
            nm = int(round(microns * 1000))
            self.ser.reset_input_buffer()
            self.ser.write(f"MOVR{axis} {nm}n\n".encode('ascii'))
            time.sleep(0.02)

    def move_abs(self, axis, microns):
        with self.lock:
            nm = int(round(microns * 1000))
            self.ser.reset_input_buffer()
            self.ser.write(f"MOVE{axis} {nm}n\n".encode('ascii'))
            time.sleep(0.02)

    def get_pos(self, axis):
        with self.lock:
            self.ser.reset_input_buffer()
            self.ser.write(f"GET_{axis}\n".encode('ascii'))
            return self._read_safe()

    def get_infos(self):
        with self.lock:
            self.ser.reset_input_buffer()
            self.ser.write(b"INFOS\n")
            time.sleep(0.5)
            return self.ser.read_all().decode('ascii', errors='ignore')

    def close(self):
        with self.lock:
            self.ser.close()
            print("[Piezo] Closed.")

# --- ADVANCED DASHBOARD GUI ---

class PiezoDashboard:
    def __init__(self, root, piezo):
        self.root = root
        self.piezo = piezo
        self.root.title("Piezo Control Center")
        self.root.geometry("550x450")
        
        # State Variables
        self.start_pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
        self.curr_pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
        self.is_monitoring = False
        self.monitor_thread = None
        
        # --- LAYOUT ---
        
        # 1. Header & Controls
        ctrl_frame = ttk.LabelFrame(root, text="Control Panel")
        ctrl_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(ctrl_frame, text="Step (um):").pack(side="left", padx=5)
        self.ent_step = ttk.Entry(ctrl_frame, width=8)
        self.ent_step.insert(0, "0.5")
        self.ent_step.pack(side="left", padx=5)
        
        self.btn_monitor = ttk.Button(ctrl_frame, text="Start Monitor", command=self.toggle_monitor)
        self.btn_monitor.pack(side="left", padx=10)
        
        ttk.Button(ctrl_frame, text="Set New Start", command=self.capture_start_pos).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Recenter (25u)", command=self.recenter).pack(side="right", padx=5)

        # 2. Main Data Display (Grid)
        data_frame = ttk.LabelFrame(root, text="Real-Time Telemetry")
        data_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Columns: Axis | Start Pos | Current Pos | Delta | Visual
        ttk.Label(data_frame, text="Axis", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(data_frame, text="Start (um)", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(data_frame, text="Current (um)", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(data_frame, text="Delta (um)", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(data_frame, text="Range (0-50um)", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5)
        
        # X Row
        ttk.Label(data_frame, text="X", font=("Arial", 12, "bold"), foreground="red").grid(row=1, column=0)
        self.lbl_start_x = ttk.Label(data_frame, text="---")
        self.lbl_start_x.grid(row=1, column=1)
        self.lbl_curr_x = ttk.Label(data_frame, text="---", font=("Consolas", 12))
        self.lbl_curr_x.grid(row=1, column=2)
        self.lbl_delta_x = ttk.Label(data_frame, text="---")
        self.lbl_delta_x.grid(row=1, column=3)
        self.pb_x = ttk.Progressbar(data_frame, length=100, maximum=50)
        self.pb_x.grid(row=1, column=4, padx=5)

        # Y Row
        ttk.Label(data_frame, text="Y", font=("Arial", 12, "bold"), foreground="green").grid(row=2, column=0)
        self.lbl_start_y = ttk.Label(data_frame, text="---")
        self.lbl_start_y.grid(row=2, column=1)
        self.lbl_curr_y = ttk.Label(data_frame, text="---", font=("Consolas", 12))
        self.lbl_curr_y.grid(row=2, column=2)
        self.lbl_delta_y = ttk.Label(data_frame, text="---")
        self.lbl_delta_y.grid(row=2, column=3)
        self.pb_y = ttk.Progressbar(data_frame, length=100, maximum=50)
        self.pb_y.grid(row=2, column=4, padx=5)

        # Z Row
        ttk.Label(data_frame, text="Z", font=("Arial", 12, "bold"), foreground="blue").grid(row=3, column=0)
        self.lbl_start_z = ttk.Label(data_frame, text="---")
        self.lbl_start_z.grid(row=3, column=1)
        self.lbl_curr_z = ttk.Label(data_frame, text="---", font=("Consolas", 12))
        self.lbl_curr_z.grid(row=3, column=2)
        self.lbl_delta_z = ttk.Label(data_frame, text="---")
        self.lbl_delta_z.grid(row=3, column=3)
        self.pb_z = ttk.Progressbar(data_frame, length=100, maximum=50)
        self.pb_z.grid(row=3, column=4, padx=5)

        # 3. Log / Status
        self.lbl_status = ttk.Label(root, text="Ready. Use Arrow Keys to move.", relief="sunken")
        self.lbl_status.pack(side="bottom", fill="x")

        # Key Bindings
        root.bind('<Left>', lambda e: self.move_thread('X', -1))
        root.bind('<Right>', lambda e: self.move_thread('X', 1))
        root.bind('<Up>', lambda e: self.move_thread('Y', 1))
        root.bind('<Down>', lambda e: self.move_thread('Y', -1))
        root.bind('<Prior>', lambda e: self.move_thread('Z', 1)) # Page Up
        root.bind('<Next>', lambda e: self.move_thread('Z', -1)) # Page Down

        # Initialize
        self.capture_start_pos()
        self.update_display()

    # --- LOGIC ---

    def capture_start_pos(self):
        """Records initial position (t=0)."""
        self.start_pos['X'] = self.piezo.get_pos('X')
        self.start_pos['Y'] = self.piezo.get_pos('Y')
        self.start_pos['Z'] = self.piezo.get_pos('Z')
        
        # Update UI labels immediately
        self.lbl_start_x.config(text=f"{self.start_pos['X']:.3f}")
        self.lbl_start_y.config(text=f"{self.start_pos['Y']:.3f}")
        self.lbl_start_z.config(text=f"{self.start_pos['Z']:.3f}")
        
        # Also update current to match
        self.curr_pos = self.start_pos.copy()
        self.update_display()
        print(f"[GUI] Start Position Set: {self.start_pos}")

    def update_live_pos(self):
        """Reads hardware and updates variables."""
        x = self.piezo.get_pos('X')
        y = self.piezo.get_pos('Y')
        z = self.piezo.get_pos('Z')
        
        # Simple validation to filter -999 errors
        if x > -100: self.curr_pos['X'] = x
        if y > -100: self.curr_pos['Y'] = y
        if z > -100: self.curr_pos['Z'] = z
        
        # Use root.after to safely update GUI from this thread
        self.root.after(0, self.update_display)

    def update_display(self):
        """Updates Labels and Progress bars based on self.curr_pos."""
        # X
        x = self.curr_pos['X']
        dx = x - self.start_pos['X']
        self.lbl_curr_x.config(text=f"{x:.4f}")
        self.lbl_delta_x.config(text=f"{dx:+.4f}")
        self.pb_x['value'] = x

        # Y
        y = self.curr_pos['Y']
        dy = y - self.start_pos['Y']
        self.lbl_curr_y.config(text=f"{y:.4f}")
        self.lbl_delta_y.config(text=f"{dy:+.4f}")
        self.pb_y['value'] = y

        # Z
        z = self.curr_pos['Z']
        dz = z - self.start_pos['Z']
        self.lbl_curr_z.config(text=f"{z:.4f}")
        self.lbl_delta_z.config(text=f"{dz:+.4f}")
        self.pb_z['value'] = z

    # --- MOVEMENT ---

    def move_thread(self, axis, direction):
        """Runs movement in a thread so GUI doesn't freeze."""
        threading.Thread(target=self._move_worker, args=(axis, direction)).start()

    def _move_worker(self, axis, direction):
        try:
            step = float(self.ent_step.get())
            self.lbl_status.config(text=f"Moving {axis} by {direction*step}...")
            
            # 1. Move
            self.piezo.move_rel(axis, direction * step)
            
            # 2. Immediate Readback
            new_val = self.piezo.get_pos(axis)
            if new_val > -100:
                self.curr_pos[axis] = new_val
                self.root.after(0, self.update_display)
                self.root.after(0, lambda: self.lbl_status.config(text=f"Moved {axis}. Pos: {new_val:.4f}"))
            
        except ValueError:
            self.lbl_status.config(text="Invalid Step Size!")

    def recenter(self):
        threading.Thread(target=self._recenter_worker).start()

    def _recenter_worker(self):
        self.lbl_status.config(text="Recentering...")
        self.piezo.move_abs('X', 25.0)
        self.piezo.move_abs('Y', 25.0)
        self.update_live_pos()
        self.lbl_status.config(text="Recentered to 25.0, 25.0")

    # --- MONITORING LOOP ---

    def toggle_monitor(self):
        if self.is_monitoring:
            self.is_monitoring = False
            self.btn_monitor.config(text="Start Monitor")
            self.lbl_status.config(text="Monitoring Stopped.")
        else:
            self.is_monitoring = True
            self.btn_monitor.config(text="Stop Monitor")
            self.lbl_status.config(text="Monitoring Active...")
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()

    def _monitor_loop(self):
        while self.is_monitoring:
            self.update_live_pos()
            time.sleep(0.5) # Update every 500ms

# --- MAIN ---
if __name__ == "__main__":
    
    # 1. Connect
    PiezoStage = Piezoconcept(port="COM9") # <--- CHECK PORT
    
    # 2. Launch GUI
    root = tk.Tk()
    app = PiezoDashboard(root, PiezoStage)
    
    def on_closing():
        app.is_monitoring = False
        PiezoStage.close()
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()