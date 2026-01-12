# -*- coding: utf-8 -*-
"""
Created on Fri Jul 18 16:59:16 2025

@author: bleue
"""
import sys
import os
import csv
import datetime 
import customtkinter as ctk
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #pour mettre les plot dans une fenêtre
from collections import deque #pour les données de taille lim et visualisation dynamique

#path for codes
sys.path.append(r"C:\Users\User\Desktop\APD")


from pico3000 import *
from pico3000 import dt
from PiezoStageControl import *
from pico_piezo import *


#=====================
#variables globales
#=====================
running = False
scope = None
plot_window = None
plot_visible = False
PiezoStage = None


#here we create the first window where will be start button; stop button, connexion etc...


#==================================
#Graphical User Interface (GUI) appearence
#==================================
ctk.set_appearance_mode("dark")  # dark mode
ctk.set_default_color_theme("green")  #  bleu theme




# ==============================
# Main window 
# ==============================
root = ctk.CTk()  # create the main window
root.title("Pico Interface")  # name of the window
root.geometry("700x500")  # size of the window

# ==============================
# Main frame
# ==============================
main_frame = ctk.CTkFrame(root)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)




## ==============================
# Channels selection (A and B)
# ==============================

selected_A = ctk.BooleanVar(value=True)  # Create a boolean variable for Channel A, default checked (True)
selected_B = ctk.BooleanVar(value=True)  # Create a boolean variable for Channel B, default checked (True)

# Checkboxes for selecting the channels

checkbox_A = ctk.CTkCheckBox(main_frame, text="Channel A", variable=selected_A)  # Create checkbox for Channel A linked to selected_A variable
checkbox_A.grid(row=1, column=0, padx=10, pady=5)  # Place Channel A checkbox in grid at row 1, column 0 with padding

checkbox_B = ctk.CTkCheckBox(main_frame, text="Channel B", variable=selected_B)  # Create checkbox for Channel B linked to selected_B variable
checkbox_B.grid(row=2, column=0, padx=10, pady=5)  # Place Channel B checkbox in grid at row 2, column 0 with padding


# ==============================
# Conexion and close button for picoscope
# ==============================


# PicoScope connect button
connect_btn = ctk.CTkButton(
    main_frame,
    text="Connect PicoScope",                      # Button text
    command=lambda: connect_picoscope(),           # Function to call when clicked
    fg_color="#3399FF",                            # Default bright blue color
    hover_color="#66B2FF",                         # Light blue on hover
    text_color="white"                             # White text color
)
connect_btn.grid(row=0, column=0, padx=10, pady=5, sticky="w")  # Place button at row 0, column 0, left aligned with padding


# PicoScope close button
close_btn = ctk.CTkButton(
    main_frame,
    text="Close PicoScope",                        # Button text
    command=lambda: close_picoscope(),             # Function to call when clicked
    fg_color="#990000",                            # Dark red color
    hover_color="#CC3333",                         # Bright red on hover
    text_color="white"                             # White text color
)
close_btn.grid(row=0, column=3, padx=10, pady=5, sticky="e")  # Place button at row 0, column 3, right aligned with padding



# ==============================
# Start and stop button acquisition picoscope
# ==============================


# Start button
start_btn = ctk.CTkButton(main_frame, text="Start",
    command=lambda: start_pico_acquisition(),   # Starts acquisition when button is pressed
    fg_color="#1F6AA5",                    # Blue button color
    hover_color="#66FF99",                 # Light green on hover
    text_color="white",                    # White text color
    corner_radius=10)                      # Rounded corners
start_btn.grid(row=1, column=1, padx=5, pady=(30,10), sticky="w")  # Place at row 1, col 1, left aligned with padding


# Stop button (below Start)
stop_btn = ctk.CTkButton(main_frame, text="Stop",
    command=lambda: stop_pico_acquisition(),    # Stops acquisition when pressed
    fg_color="#1F6AA5",                     # Blue button color
    hover_color="#FF6666",                  # Light red on hover
    text_color="white",                     # White text color
    state="disabled",                       # Disabled initially (can’t stop if not started)
    corner_radius=10)                       # Rounded corners
stop_btn.grid(row=1, column=2, padx=5, pady=(30,10), sticky="w")  # Place at row 1, col 2, left aligned with padding


# ==============================
# Direct photon count rate update
# ==============================
    
#texte area
label_A = ctk.CTkLabel(main_frame, text="Channel A : --- ph/s", font=ctk.CTkFont(size=16)) 
label_A.grid(row=2, column=1, padx=10, pady=(30,10), sticky='w')

label_B = ctk.CTkLabel(main_frame, text="Channel B : --- ph/s", font=ctk.CTkFont(size=16))
label_B.grid(row=3, column=1, padx=10, pady=(30,10), sticky='w')


# ==============================
# Field to enter desired integration time 
# ==============================

# Field to enter the integration time (in seconds)
duration_label = ctk.CTkLabel(main_frame, text="Integration time (s):")
duration_label.grid(row=3, column=0, padx=5, pady=(2,0), sticky="n")  # Place label at row 3, col 0, aligned top with padding

duration_entry = ctk.CTkEntry(main_frame, width=50)               # Entry widget to input integration time, width 50
duration_entry.insert(0, "0.1")                                  # Insert default value "0.1" seconds
duration_entry.grid(row=4, column=0, padx=5, pady=(0,10), sticky="n")  # Place entry at row 4, col 0, aligned top with padding


# ==============================
# Functions to link button to an action
# ==============================


def get_selected_channels():
    """
    Returns a list of the channels selected by the user in the GUI.

    The function checks the state of the checkboxes for Channel A and Channel B.
    If a channel is selected (checkbox ticked), its identifier ("A" or "B") is 
    added to the list. The resulting list may contain:
        - ["A"] if only Channel A is selected
        - ["B"] if only Channel B is selected
        - ["A", "B"] if both channels are selected
        - [] if none are selected
    """
    
    # Create an empty list to store the selected channels
    channels = []
    
    # If the checkbox for Channel A is ticked, add "A" to the list
    if selected_A.get():
        channels.append("A")
        
    # If the checkbox for Channel B is ticked, add "B" to the list
    if selected_B.get():
        channels.append("B")
        
    # Return the list of selected channels
    return channels

def connect_picoscope():
    """
    Connects to the PicoScope using the channels selected in the GUI.
    
    This function:
    1. Retrieves the list of selected channels from the checkboxes.
    2. Attempts to establish a connection to the PicoScope using the 
       'connexion_pico' function.
    3. If successful, disables the "Connect" button in the GUI so the 
       user cannot try to reconnect.
    4. If an error occurs, prints the error message in the console.
    """
    global scope, total_samples, times # Declare global variables to store scope object and acquisition info
    # Get the channels currently selected in the GUI
    channels = get_selected_channels()
    
    
    try:
        # Attempt to connect to the PicoScope using the selected channels
        scope = connexion_pico(channels)
        
        # Disable the "Connect" button after a successful connection
        connect_btn.configure(state="disabled")  # désactivé une fois connecté
        
    except Exception as e:
        # If something goes wrong, display the error message
        print(" Erreur de connexion :", e)
        
        
def connect_pico_piezo():
    """
    Connects both the PicoScope and the Piezo stage. For the 2D map part
    
    This function:
    1. Retrieves the list of channels selected by the user in the GUI.
    2. Attempts to establish a connection to both the Piezo stage and 
       the PicoScope using the 'connect_Piezo_Ps' function.
    3. Stores the connected devices in the global variables 'PiezoStage' 
       and 'scope'.
    4. If an error occurs, prints the error message in the console.
    """
    global scope, PiezoStage, total_samples, times # Global variables to store devices and acquisition parameters
    
    # Get the channels currently selected in the GUI
    channels = get_selected_channels()
    try:
        # Attempt to connect to both Piezo stage and PicoScope
        PiezoStage, scope = connect_Piezo_Ps(channels)
        
        
    except Exception as e:
        # Print error message if connection fails
        print(" Erreur de connexion :", e)
        
    

def start_pico_acquisition():
    """
    Starts the acquisition process. Create a background thread. It doesn't acquire anything as acquisition_pico_loop function below.
    
    This function:
    1. Sets the 'running' flag to True so the acquisition loop will run.
    2. Disables the 'Start' button and enables the 'Stop' button in the GUI.
    3. Retrieves the channels selected by the user.
    4. Reads the integration time from the entry field (defaults to 0.1s if invalid).
    5. Launches the acquisition loop in a separate thread to avoid freezing the GUI.
    """
    global running
    running = True # Acquisition is now running
    
    # Update button states: disable Start, enable Stop
    start_btn.configure(state="disabled")
    stop_btn.configure(state="normal")

    # Get the channels selected in the GUI
    channels = get_selected_channels()
    
    # Read integration time from input field
    try:
        duration = float(duration_entry.get())# Convert entry text to float
    except ValueError:
        print("Valeur invalide, utilisation de 0.1s par défaut.")
        duration = 0.1  # Default duration
    
    # Create a separate thread for acquisition to keep GUI responsive (so the interface doesn't freeze while running)
    thread = threading.Thread(target=acquisition_pico_loop, args=(channels, duration))    

    thread.daemon = True  # Daemon thread ends automatically when main program exits or when the window is closed
    thread.start()        # Start acquisition loop in background


def acquisition_pico_loop(channels,duration):
    """
    Acquisition loop for PicoScope data. 
    
    This function continuously acquires photon count rates from the PicoScope
    on the specified channels during a given duration. 
    It updates both the GUI labels and a live plot in real time.
    The loop runs until the global variable "running" is set to False.
    """
    global scope, running

    # If no PicoScope is connected, exit the function
    if scope is None:
        print("Picoscope not connected.")
        return


    #dt = 4e-9
    # Configure acquisition parameters (number of samples, time array, etc.)
    total_samples, times = set_param(scope, channel=channels, duration=duration, dt=dt)
    # Configure the trigger (disabled here)
    set_trigger(scope, channel=channels, trigger=False)

    # Start a timer to measure elapsed time for plotting
    t0 = time.time()  # point de départ du chrono
    try:
        # Main acquisition loop: runs as long as "running" is True
        while running:
            # Acquire photon count rates from the PicoScope
            CountRates = run_scope(scope, times, total_samples, channel=channels, duration=duration, dt=dt, plot=False)
            
            # Function to update the GUI labels and the live plot
            def update_labels_and_plot():
                # Update label for Channel A
                if "A" in CountRates:
                    label_A.configure(text=f"Channel A : {CountRates['A']:.3e} ph/s")
                else:
                    label_A.configure(text="Channel A : --- ph/s")
                
                # Update label for Channel B
            
                if "B" in CountRates:
                    label_B.configure(text=f"Channel B : {CountRates['B']:.3e} ph/s")
                else:
                    label_B.configure(text="Channel B : --- ph/s")
            
                # Update the live plot if it is visible
                if plot_visible and plot_window is not None:
                    # Add current time and new data points
                    time_data.append(time.time()-t0)
                    if "A" in CountRates:
                        a_data.append(CountRates["A"])
                    else:
                        a_data.append(0)
            
                    if "B" in CountRates:
                        b_data.append(CountRates["B"])
                    else:
                        b_data.append(0)
            
                    # Update the plot lines
                    line_a.set_data(time_data, a_data)
                    line_b.set_data(time_data, b_data)
                    
                    # Rescale the plot to fit new data
                    ax.relim()
                    ax.autoscale_view()
                    canvas.draw()
            # Schedule the GUI update in the main thread
            root.after(0, update_labels_and_plot)  # met à jour l’UI et le graphe

            # Wait before next acquisition cycle
            time.sleep(duration)
    # If any error occurs during acquisition
    except Exception as e:
        print("Erreur dans l’acquisition :", e)
    # When loop ends, stop the PicoScope properly
    finally:
        if scope is not None:
            scope.stop()
            
            
def open_or_close_plot_window():
    """
    Opens or closes the dynamic plot window.
    
    - If the plot window is already open (`plot_visible = True`), it closes the window.
    - If the plot window is not open (`plot_visible = False`), it creates a new window
      with a Matplotlib figure embedded inside Tkinter.
    - Initializes empty data buffers for time and channels A & B.
    - Adds a "Save Data" button to export the recorded values.
    """
    global plot_window, plot_visible, fig, ax, canvas, line_a, line_b
    if plot_visible:
        # Close the existing plot window if it's open
        if plot_window is not None:
            plot_window.destroy()
            plot_window = None
        plot_visible = False
    else:
        # Create a new top-level window for the plot


        plot_window = ctk.CTkToplevel(root)
        plot_window.title("Dynamic view")
        plot_window.geometry("500x400")
        
        # Create a Matplotlib figure and axes
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.set_title("Dynamic view" )
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("ph/s")
        ax.grid(True)

        # Initialize plot lines for channels A and B
        line_a, = ax.plot([], [], label="channel A", marker='o', linestyle='-', color='lime')
        line_b, = ax.plot([], [], label="Fchannel B", marker='s', linestyle='-', color='orange')
        ax.legend()
        
        # Embed the Matplotlib figure inside the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # # Add a button to save the collected data /!\ TO BE UPDATED
        # save_btn = ctk.CTkButton(plot_window, text="Save Data", command=save_plot_data)
        # save_btn.pack(pady=5)

        # Initialize data buffers (fixed maximum size to avoid memory overload) You can go up if needed
        global time_data, a_data, b_data
        time_data = deque(maxlen=100_000)
        a_data = deque(maxlen=100_000)
        b_data = deque(maxlen=100_000)
        
        # Mark the plot as visible
        plot_visible = True
        

# file = None
# writer = None
# buffer = []
# buffer_size = 100
# saving_streaming = False

# buffer= []
# def start_streaming_save():
#     global file, writer, saving_streaming, buffer

#     now = datetime.datetime.now()
#     filename = f"photon_stream_{now.strftime('%Y%m%d%H%M%S')}.csv"

#     file = open(filename, mode='w', newline='')
#     writer = csv.writer(file)
#     writer.writerow(["Time (s)", "Channel A (ph/s)", "Channel B (ph/s)"])

#     buffer = []
#     saving_streaming = True
#     print(f"Started streaming save to {filename}")

# def streaming_save_point(t, a, b):
#     global time_data_buffer, a_data_buffer, b_data_buffer, writer, saving_streaming, file

#     if not saving_streaming:
#         return

#     buffer.append([t, a, b])

#     if len(buffer) >= buffer_size:
#         writer.writerows(buffer)
#         file.flush()
#         buffer.clear()

# def stop_streaming_save():
#     global file, writer, saving_streaming, buffer

#     if not saving_streaming:
#         return

#     if buffer:
#         writer.writerows(buffer)
#         file.flush()
#         buffer.clear()

#     file.close()
#     saving_streaming = False
#     print("Stopped streaming save and closed file")     
        
    
    





        
def stop_pico_acquisition():
    """
    Stop the pico acquisition process.
    
    - Sets the global flag 'running' to False, which will stop the acquisition loop.
    - Re-enables the 'Start' button so the user can launch a new acquisition.
    - Disables the 'Stop' button since the acquisition is no longer running.
    """
    global running
    running = False # Signal to stop the acquisition loop
    start_btn.configure(state="normal") # Enable the Start button again
    stop_btn.configure(state="disabled") # Disable the Stop button
    
    
def close_picoscope():
    """
    Safely close the PicoScope connection.
    
    - Re-enables the 'Connect' button so the user can connect again later.
    - If a PicoScope is currently connected:
        * Attempts to close the connection properly.
        * Prints a confirmation message.
        * Resets the global variable 'scope' to None.
    - If no PicoScope is connected:
        * Prints a message indicating that no device was connected.
    """
    global scope
    connect_btn.configure(state="normal") # Re-enable the 'Connect' button
    if scope is not None:
        try:
            scope.close() # Properly close the PicoScope connection
            print("PicoScope closed") 
            scope=None  # Reset global scope variable
        except Exception as e:
            print("Erreur lors de la fermeture :", e)
    else:
        print(" PicoScope non connecté.")    
        
def close_all():
    """
    Safely close all connected instruments (PiezoStage and PicoScope).
    
    - Closes the PiezoStage connection (if it exists), sets it to None, and prints confirmation.
    - Closes the PicoScope connection (if it exists), sets it to None, and prints confirmation.
    - Ensures both instruments are properly released to avoid resource conflicts.
    """
    global PiezoStage, scope
    PiezoStage.close() # Close PiezoStage 
    PiezoStage = None
    print("PiezoStage closed")
     
    scope.close() # Close PicoScope 
    scope = None
    print("PicoScope closed")
        
        

def open_map_window():
    """
    Open a new window for 2D mapping configuration and control.
    
    - Creates a secondary window for map acquisition settings.
    - Provides connection button for PicoScope + PiezoStage.
    - Allows the user to enter map parameters (size, number of points, integration time).
    - Provides a button to start the mapping process.
    - Provides a button to close both instruments safely.
    """
    global size_entry, points_entry, duration_entry
    
    

    # Secondary window for map control
    map_window = ctk.CTkToplevel(root)
    map_window.title("2D map")
    map_window.geometry("700x600")

    # Connection button (PicoScope + PiezoStage)
    connect_pico_piezo_btn = ctk.CTkButton(
        map_window, 
        text="Connect PicoScope + PiezoStage", 
        command=connect_pico_piezo
    )
    connect_pico_piezo_btn.pack(pady=10)

    # Frame for user inputs
    frame_inputs = ctk.CTkFrame(map_window)
    frame_inputs.pack(pady=10)

    # Map size (in micrometers)
    size_label = ctk.CTkLabel(frame_inputs, text="Size (µm) :")
    size_label.grid(row=0, column=0, padx=5, pady=5)
    size_entry = ctk.CTkEntry(frame_inputs, placeholder_text="e.g: 5")
    size_entry.grid(row=0, column=1, padx=5, pady=5)

    # Number of points in the scan
    points_label = ctk.CTkLabel(frame_inputs, text="Points :")
    points_label.grid(row=1, column=0, padx=5, pady=5)
    points_entry = ctk.CTkEntry(frame_inputs, placeholder_text="e.g: 20")
    points_entry.grid(row=1, column=1, padx=5, pady=5)

    # Integration time (per pixel)
    duration_label = ctk.CTkLabel(frame_inputs, text="Integration time (s) :")
    duration_label.grid(row=2, column=0, padx=5, pady=5)
    duration_entry = ctk.CTkEntry(frame_inputs, placeholder_text="e.g: 0.1")
    duration_entry.grid(row=2, column=1, padx=5, pady=5)


    # Start mapping button
    start_btn = ctk.CTkButton(map_window, text="Start Map", command=start_map)
    start_btn.pack(pady=10)
    
    
    # Button to close both instruments safely
    close_all_btn = ctk.CTkButton(
        map_window,
        text="Close Picoscope and PiezoStage",
        fg_color="#990000",
        hover_color="#CC3333",
        text_color="white",
        command=close_all
    )
    close_all_btn.pack(pady=10)

def start_map():
    """
    Start a 2D map acquisition using PicoScope and PiezoStage.
    
    - Retrieves scan parameters (size, number of points, integration time).
    - Configures acquisition parameters on the PicoScope.
    - Disables trigger for free acquisition.
    - Calls the scan function to perform the 2D scan and plot the results.
    """
    size = float(size_entry.get())
    points = int(points_entry.get())
    # dt = 4e-9
    duration = float(duration_entry.get())
    channels = get_selected_channels()

    total_samples, times = set_param(scope, channel=channels, duration=duration, dt=dt)
    set_trigger(scope, channel=channels, trigger=False)

    #Run the scan 
    scan(size, points, scope, PiezoStage, channel=channels,
         duration=duration, total_samples=total_samples)




# Button to open or close the live plot window picoscope acquisition
plot_btn = ctk.CTkButton(main_frame,
    text="Live view",
    command=open_or_close_plot_window,
    fg_color="#444444",
    hover_color="#888888",
    text_color="white")
plot_btn.grid(row=5, column=0, padx=5, pady=(10,10), sticky="w")



# bouton to open "Map" window
map_btn = ctk.CTkButton(
    main_frame,
    text="Map",
    command=open_map_window, 
    fg_color="#444444",
    hover_color="#888888",
    text_color="white")
map_btn.grid(row=6, column=0, padx=5, pady=(10,10), sticky="w")


    
    
def on_closing():
    """
    Handle the closing event of the main Tkinter window.
    
    - Stops any running acquisition loop.
    - Closes the live plot window if it is open.
    - Closes the PicoScope connection if still active.
    - Gracefully shuts down Tkinter and exits the program.
    """
    global running, scope, PiezoStage, plot_window


    # Stop acquisition loop
    running = False

    # Close the live plot window if still open
    if plot_window is not None:
        plot_window.destroy()
        plot_window = None

    # Close PicoScope connection if active
    if scope is not None:
        try:
            scope.close()
            print("PicoScope closed.")
        except Exception as e:
            print("Error closing PicoScope :", e)

    if PiezoStage is not None:
        try:
            PiezoStage.close()
            print("Piezo closed.")
        except Exception as e:
            print("Error closing Piezo :", e)    
    # Ferme proprement Tkinter et arrête Python
    root.quit()
    root.destroy()
    print("End")


    
    
# Bind this function to the window close (X button) event
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()  # Start the Tkinter main event loop (keeps the User interface running)



#%%
#scope.close()
