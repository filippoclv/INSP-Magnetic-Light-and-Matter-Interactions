import serial
import time

# SETTINGS
PORT = "COM9"
BAUD = 115200

def spy_on_piezo():
    print(f"--- OPENING SERIAL SPY ON {PORT} ---")
    try:
        # Open raw connection
        ser = serial.Serial(PORT, BAUD, timeout=1)
        
        # 1. FLUSH AND LISTEN
        # See if there is any 'trash' or error messages waiting
        print("Checking for pending messages...")
        time.sleep(0.5)
        pending = ser.read_all()
        if pending:
            print(f"Found in buffer: {pending}")
        else:
            print("Buffer is empty.")

        # 2. ASK FOR STATUS
        # The manual mentions 'INFOS'. Let's see if it replies.
        print("\n[TX] INFOS")
        ser.write(b"INFOS\n")
        time.sleep(0.5)
        print(f"[RX] {ser.read_all()}")

        # 3. CHECK POSITION
        print("\n[TX] GET_X")
        ser.write(b"GET_X\n")
        time.sleep(0.2)
        pos_response = ser.read_all()
        print(f"[RX] {pos_response}")

        # 4. TRY MOVE (Format A: Integer Microns)
        # We try '25u' instead of '25.00u' to see if decimals are the enemy
        print("\n[TX] MOVEX 25u (Trying Integer Format)")
        ser.write(b"MOVEX 25u\n")
        time.sleep(1.0)
        
        # Check result
        ser.write(b"GET_X\n")
        time.sleep(0.2)
        print(f"[RX CHECK] {ser.read_all()}")

        # 5. TRY MOVE (Format B: Integer Nanometers)
        # Manual says: MOVEX 200000n
        print("\n[TX] MOVEX 25000n (Trying Nanometer Format)")
        ser.write(b"MOVEX 25000n\n")
        time.sleep(1.0)
        
        ser.write(b"GET_X\n")
        time.sleep(0.2)
        print(f"[RX CHECK] {ser.read_all()}")

        ser.close()
        print("\n--- SPY CLOSED ---")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    spy_on_piezo()