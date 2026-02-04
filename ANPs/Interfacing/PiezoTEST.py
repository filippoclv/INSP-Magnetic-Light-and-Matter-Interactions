#%% VERIFY MOVEMENT (CENTERING)
from PiezoStageControlTEST import Piezoconcept
import time
import sys

print("--- PIEZO CENTERING TEST ---")
try:
    piezo = Piezoconcept("COM9")
except:
    sys.exit()

try:
    # 1. Start
    x0 = piezo.get_x()
    y0 = piezo.get_y()
    print(f"Start: X={x0}, Y={y0}")
    
    if x0 is None:
        print("CRITICAL: Cannot read position.")
        sys.exit()

    # 2. Move X to CENTER (25.0)
    # We move away from the 50um limit to prove control
    print(f"\nMoving X to 25.00 u ...")
    piezo.move_x(25.0)
    time.sleep(1.0)
    
    x1 = piezo.get_x()
    print(f"Result X: {x1}")
    
    if abs(x1 - 25.0) < 0.5:
        print(">>> X SUCCESS (Moved to Center)")
    else:
        print("!!! X FAILED (Stuck?)")

    # 3. Move Y to CENTER (25.0)
    print(f"\nMoving Y to 25.00 u ...")
    piezo.move_y(25.0)
    time.sleep(1.0)
    
    y1 = piezo.get_y()
    print(f"Result Y: {y1}")
    
    if abs(y1 - 25.0) < 0.5:
        print(">>> Y SUCCESS (Moved to Center)")
    else:
        print("!!! Y FAILED (Stuck?)")

finally:
    piezo.close()
    print("--- TEST COMPLETE ---")