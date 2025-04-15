import pyautogui as pyGUI
import pyperclip
import time
from gui_helpers import safe_click, safe_type, wait_for_image

def safe_click(image_path, confidence=0.9, max_attempts=5, delay=1, click_offset=(0, 0)):
    """Try clicking a UI element by image, with retries and optional offset."""

    for attempt in range(max_attempts):

        location = pyGUI.locateOnScreen(image_path, confidence=confidence, grayscale=True)

        if location:

            x, y = pyGUI.center(location)
            x += click_offset[0]
            y += click_offset[1]
            pyGUI.click(x, y)

            return True

        print(f"Retrying... ({attempt+1}/{max_attempts})")
        time.sleep(delay)

    raise RuntimeError(f"[ERROR] Could not find image: {image_path}")

def safe_type(text, use_clipboard=True):
    """Type text safely, optionally using clipboard (more reliable for special characters)."""

    if use_clipboard:

        pyperclip.copy(text)
        pyGUI.hotkey('ctrl', 'v')

    else:

        pyGUI.write(text)

def wait_for_image(image_path, confidence=0.9, timeout=10):
    """Wait until a UI element appears on screen (with timeout)."""

    start = time.time()

    while time.time() - start < timeout:

        if pyGUI.locateOnScreen(image_path, confidence=confidence):

            return True

        time.sleep(0.5)

    raise TimeoutError(f"[ERROR] Timed out waiting for image: {image_path}")

def SaveASpectrum(FolderName, FileName, IsFolderChecked=False):
    """Improved and safe version of spectrum saving using UI automation."""

    print(f"[INFO] Saving spectrum as: {FileName}")

    try:
        # Step 1: Click 'Save' button
        safe_click('SaveSpectrumButton.PNG', confidence=0.9)

        time.sleep(0.5)  # Give time for the dialog to open

        # Step 2: Change the folder only once
        if not IsFolderChecked:

            safe_click('FolderButton2.PNG', confidence=0.9, click_offset=(-5, 0))
            safe_type(FolderName)
            pyGUI.press('enter')
            time.sleep(0.5)
            IsFolderChecked = True

        # Step 3: Enter filename
        safe_click('SaveSpectrumFileNameLoc.PNG', confidence=0.8, click_offset=(+120, 0))
        safe_type(str(FileName))
        pyGUI.press('enter')

        time.sleep(0.5)  # Let save finish
        print(f"Spectrum '{FileName}' saved successfully.")

        return IsFolderChecked

    except Exception as e:

        print(f"Failed to save spectrum '{FileName}': {e}")
        # optionally retry or skip depending on context

        raise


'''

then, instead of: IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
let's use the following

try:
    IsFolderChecked = SaveASpectrum(MyDataFolder, FileName, IsFolderChecked)
except RuntimeError as e:
    print(f"[FATAL] Aborting measurement at File: {FileName}")
    # Optionally break or skip

'''