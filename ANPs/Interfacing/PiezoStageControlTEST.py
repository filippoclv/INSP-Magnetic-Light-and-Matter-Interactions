import serial
import time
import sys

class Piezoconcept:
    """
    Driver V4: Manual-Compliant (Micron Mode).
    - Uses 'u' units (e.g., 'MOVEX 25.00u').
    - Handles the 50um limit safely.
    - Aggressive buffer clearing.
    """
    
    def __init__(self, port):
        self.port_settings = {
            "baudrate": 115200,
            "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
            "timeout": 2.0 
        }
        try:
            self.ser = serial.Serial(port=port, **self.port_settings)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            print(f"[Piezo] Connected on {port}")
        except Exception as e:
            print(f"[Piezo] Connection Error: {e}")
            sys.exit(1)

    def _send(self, cmd_str):
        """Sends command with \\n."""
        self.ser.reset_input_buffer() 
        full_cmd = f"{cmd_str}\n"
        self.ser.write(full_cmd.encode('ascii'))
        time.sleep(0.1) # Wait for processing

    def _read_float(self):
        """Reads response and extracts the number."""
        try:
            # Read multiple lines to skip 'Ok' or echoes
            for _ in range(5):
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if not line or "ok" in line.lower():
                    continue
                
                # Check for digit
                if any(c.isdigit() for c in line):
                    # Clean: '50.0000 um' -> '50.0000'
                    clean = line.lower().replace('um','').replace('u','').strip()
                    return float(clean)
        except:
            pass
        return None

    # --- COMMANDS ---

    def move_x(self, microns):
        """Move X (0-50um). Uses 2 decimal places + 'u'."""
        if not (0 <= microns <= 50.0):
            print(f"[Piezo] WARNING: X={microns}um out of range (0-50).")
            return
        
        # Format: "MOVEX 25.00u"
        cmd = f"MOVEX {microns:.2f}u"
        self._send(cmd)

    def move_y(self, microns):
        """Move Y (0-50um). Uses 2 decimal places + 'u'."""
        if not (0 <= microns <= 50.0):
            print(f"[Piezo] WARNING: Y={microns}um out of range (0-50).")
            return
            
        cmd = f"MOVEY {microns:.2f}u"
        self._send(cmd)

    def get_x(self):
        self.ser.reset_input_buffer()
        self.ser.write(b"GET_X\n")
        return self._read_float()

    def get_y(self):
        self.ser.reset_input_buffer()
        self.ser.write(b"GET_Y\n")
        return self._read_float()
        
    def close(self):
        self.ser.close()
        print("[Piezo] Closed.")