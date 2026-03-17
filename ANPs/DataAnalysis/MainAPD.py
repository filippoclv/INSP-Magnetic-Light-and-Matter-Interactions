import json
from FileReader import *
from Plotter import *
from Analyzer import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
import glob
import os
import numpy as np
import re

spectrum = read_spectrum_txt_to_dataframe(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260223_samplestudy\2025Asample10power_1s.txt")

bg_min, bg_max = 875, 900
bg_region = spectrum[(spectrum["Wavelength_nm"] >= bg_min) & (spectrum["Wavelength_nm"] <= bg_max)]

if not bg_region.empty:

    bg_mean = bg_region["Intensity_counts"].mean()
    print(f"Calculated background mean ({bg_min}-{bg_max} nm): {bg_mean:.2f} counts")
    spectrum["Intensity_counts"] = spectrum["Intensity_counts"] - bg_mean
    spectrum["Intensity_counts"] = spectrum["Intensity_counts"].clip(lower=0)

else:

    print(f"Warning: no data found in background range {bg_min}-{bg_max} nm. Skipping subtraction.")

plot_single_spectrum(spectrum, "Layer spectrum, 10% power, 1 s integration time, background subtracted")

spectrum = read_spectrum_txt_to_dataframe(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260223_samplestudy\2025Asample10power2_1s.txt")

bg_region = spectrum[(spectrum["Wavelength_nm"] >= bg_min) & (spectrum["Wavelength_nm"] <= bg_max)]

if not bg_region.empty:

    bg_mean = bg_region["Intensity_counts"].mean()
    print(f"Calculated background mean ({bg_min}-{bg_max} nm): {bg_mean:.2f} counts")
    spectrum["Intensity_counts"] = spectrum["Intensity_counts"] - bg_mean
    spectrum["Intensity_counts"] = spectrum["Intensity_counts"].clip(lower=0)

else:

    print(f"Warning: no data found in background range {bg_min}-{bg_max} nm. Skipping subtraction.")

plot_single_spectrum(spectrum, "Layer spectrum with vortex exc, 10% power, 1 s integration time, background subtracted")

def plot_map_from_txt(filepath, scan_size_um=2.0):

    df = pd.read_csv(filepath, sep="\t", header=None, names=["x", "y", "intensity"])
    image_data = df.pivot(index='y', columns='x', values='intensity').values
    fig, ax = plt.subplots(figsize=(8, 7))
    extent = [0, scan_size_um, 0, scan_size_um]

    im = ax.imshow(image_data,
                   origin='lower',
                   cmap='viridis',
                   extent=extent)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.15)
    cbar = plt.colorbar(im, cax=cax)

    fmt = ticker.ScalarFormatter(useMathText=True)
    fmt.set_powerlimits((3, 3))
    cbar.ax.yaxis.set_major_formatter(fmt)

    cbar.ax.tick_params(labelsize=14)
    cbar.ax.yaxis.get_offset_text().set_fontsize(14)
    cbar.ax.yaxis.get_offset_text().set_horizontalalignment('center')
    cbar.ax.yaxis.get_offset_text().set_x(2.0)

    cbar.set_label("Intensity [counts]", fontsize=16, labelpad=15)

    # Axis labels with padding
    ax.set_xlabel("x position [µm]", fontsize=16, labelpad=10)
    ax.set_ylabel("y position [µm]", fontsize=16, labelpad=10)
    ax.tick_params(labelsize=14)

    ax.set_title(f"Hyperspectral map of the agglomerate,\n 40% power, 1 s integration time", fontsize=16, pad=15)

    plt.tight_layout()
    plt.show()

# plot_map_from_txt(
#     r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\hyperspectral40P1s770to830.txt",
#     scan_size_um=2.0)

def plot_map_data(image_data, scan_size_um=2.0, title=None):

    fig, ax = plt.subplots(figsize=(8, 7))
    extent = [0, scan_size_um, 0, scan_size_um]

    im = ax.imshow(image_data,
                   origin='lower',
                   cmap='viridis',
                   extent=extent)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.15)
    cbar = plt.colorbar(im, cax=cax)

    fmt = ticker.ScalarFormatter(useMathText=True)
    fmt.set_powerlimits((3, 3))
    cbar.ax.yaxis.set_major_formatter(fmt)

    cbar.ax.tick_params(labelsize=14)
    cbar.ax.yaxis.get_offset_text().set_fontsize(14)
    cbar.ax.yaxis.get_offset_text().set_horizontalalignment('center')
    cbar.ax.yaxis.get_offset_text().set_x(2.0)

    cbar.set_label("Integrated intensity [counts]", fontsize=16, labelpad=15)

    ax.set_xlabel("x position [µm]", fontsize=16, labelpad=10)
    ax.set_ylabel("y position [µm]", fontsize=16, labelpad=10)
    ax.tick_params(labelsize=14)

    if title:
        ax.set_title(title, fontsize=16, pad=15)

    plt.tight_layout()
    plt.show()

filepath = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\hyperspectral40P1s770to830.txt"
df = pd.read_csv(filepath, sep="\t", header=None, names=["x", "y", "intensity"])

# Identify the row corresponding to 2 microns (assuming max y index is the top row)
max_y = df['y'].max()
print(f"Max y index found: {max_y}")

# Calculate average of the top row
top_row_mean = df[df['y'] == max_y]['intensity'].mean()
print(f"Average counts at 2 microns (row y={max_y}): {top_row_mean:.2f}")

# Subtract this average from the entire map and clip negative values
df['intensity'] = df['intensity'] - top_row_mean
df['intensity'] = df['intensity'].clip(lower=0)

# Pivot to 2D matrix
image_data = df.pivot(index='y', columns='x', values='intensity').values

# plot_map_data(image_data,
#               scan_size_um=2.0,
#               title="Hyperspectral map, background subtracted,\n40% power")

def plot_all_powercurves_from_folder(folder_path):

    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['xtick.major.width'] = 1.5
    plt.rcParams['ytick.major.width'] = 1.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    files = sorted(glob.glob(os.path.join(folder_path, "*.txt")))

    if not files:

        print(f"No .txt files found in {folder_path}")

        return

    print(f"Found {len(files)} files. Plotting...")

    fig, ax = plt.subplots(figsize=(10, 8))

    for filepath in files:

        try:

            df = pd.read_csv(filepath, sep="\t")

            if "ReadPower" in df.columns and "Counts" in df.columns:

                ax.plot(df["ReadPower"], df["Counts"],
                        marker='o', markersize=4, linestyle='-', linewidth=1,
                        alpha=0.3, color='teal')

            else:

                print(f"Skipping {os.path.basename(filepath)}: missing 'ReadPower' or 'Counts' columns.")

        except Exception as e:

            print(f"Error reading {os.path.basename(filepath)}: {e}")

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel("Power [W]", fontsize=18)
    ax.set_ylabel("Counts", fontsize=18)
    ax.set_title(f"Powercurves, all pixels, \n{len(files)} files processed", fontsize=18, pad=15)

    ax.grid(True, which="both", linestyle='--', alpha=0.3)
    ax.tick_params(labelsize=16)

    plt.tight_layout()
    plt.show()

folder_to_scan = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\20260217165040_RelativeMap"

# plot_all_powercurves_from_folder(folder_to_scan)

def calculate_max_slope_discrete(x_data, y_data):
    """
    Calcola la pendenza (derivata discreta) segmento per segmento.
    Restituisce la pendenza massima e gli indici dei due punti che la generano.
    """
    valid_mask = (x_data > 0) & (y_data > 0)
    x_valid, y_valid = x_data[valid_mask], y_data[valid_mask]

    if len(x_valid) < 2:
        return None, None, None, None

    log_x = np.log10(x_valid)
    log_y = np.log10(y_valid)

    # Derivata discreta: (y_i+1 - y_i) / (x_i+1 - x_i)
    delta_x = np.diff(log_x)
    delta_y = np.diff(log_y)

    # Evita la divisione per zero in caso di punti con la stessa potenza letta
    valid_diff = delta_x != 0
    if not np.any(valid_diff):
        return None, None, None, None

    slopes = np.zeros_like(delta_x)
    slopes[valid_diff] = delta_y[valid_diff] / delta_x[valid_diff]

    max_idx = np.argmax(slopes)
    max_slope = slopes[max_idx]

    # Coordinate per plottare il segmento specifico
    segment_x = [x_valid[max_idx], x_valid[max_idx + 1]]
    segment_y = [y_valid[max_idx], y_valid[max_idx + 1]]

    return max_slope, segment_x, segment_y, log_x.min()

# --- Main Plotting and Analysis Workflow ---
def analyze_and_plot_curves(file_paths, labels):
    fig, ax = plt.subplots(figsize=(10, 8))

    colors = ['teal', 'darkorange', 'crimson', 'purple']

    print("--- Extracted Avalanche Slopes (Point-by-Point) ---")

    for filepath, label, color in zip(file_paths, labels, colors):
        try:
            df = pd.read_csv(filepath, sep="\t")

            if "CurrentPower" not in df.columns or "CountRates" not in df.columns:
                print(f"Skipping {label}: missing 'CurrentPower' or 'CountRates' columns.")
                continue

            p_arr = np.array(df["CurrentPower"].values, dtype=float)
            c_arr = np.array(df["CountRates"].values, dtype=float)

            # Sort data by power to ensure sequential discrete differences make sense
            sort_idx = np.argsort(p_arr)
            p_arr = p_arr[sort_idx]
            c_arr = c_arr[sort_idx]

            # Extract slope point-by-point
            max_slope, seg_x, seg_y, _ = calculate_max_slope_discrete(p_arr, c_arr)

            # Print result
            slope_str = f"{max_slope:.2f}" if max_slope is not None else "Failed"
            print(f"{label:<40}: s_max = {slope_str}")

            # Plot Raw Data (Lines and markers to see the point-to-point jumps)
            ax.plot(p_arr, c_arr, '-o', color=color, alpha=0.5, markersize=4, linewidth=1, label=f"{label}")

            # Highlight the segment with the maximum slope
            if max_slope is not None:
                ax.plot(seg_x, seg_y, '-', color=color, linewidth=5, solid_capstyle='round')

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    # Formatting
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Current Power [W]", fontsize=18)
    ax.set_ylabel("Count Rates", fontsize=18)
    ax.set_title("Photon Avalanche Curves (Discrete Derivatives)", fontsize=18, pad=15)

    ax.grid(True, which="both", linestyle='--', alpha=0.3)
    ax.legend(fontsize=12, loc='best')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    files = [
        r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260223_samplestudy\powercurves\powercurve1.txt",
        r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260223_samplestudy\powercurves\powercurve2optimizedpathandfocus.txt",
        r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260223_samplestudy\powercurves\farawaydot.txt",
        r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260223_samplestudy\powercurves\farawaynothing.txt"
    ]

    labels = [
        "Curve 1 (Initial)",
        "Curve 2 (Optimized Focus/Path)",
        "Far Away Dot",
        "Far Away Nothing (Background)"
    ]

    analyze_and_plot_curves(files, labels)