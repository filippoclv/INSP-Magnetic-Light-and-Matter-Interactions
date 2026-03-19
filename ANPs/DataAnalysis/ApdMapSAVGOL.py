import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d


# --- 1. Core Physics & Extraction Logic ---

def extract_smax_savgol(power, counts_raw, bg_baseline, bg_noise_floor,
                        snr_threshold=3, min_consecutive=3, savgol_window=15, savgol_poly=3):
    """
    Extracts the maximum non-linearity (s_max) using a global background and local SavGol filter.
    Returns None if no avalanche is detected above the noise floor.
    """
    counts_corrected = counts_raw - bg_baseline

    # SNR Mask
    raw_valid_mask = counts_corrected > (snr_threshold * bg_noise_floor)

    # Contiguity Filter
    avalanche_start_idx = len(raw_valid_mask)
    for i in range(len(raw_valid_mask) - min_consecutive + 1):
        if np.all(raw_valid_mask[i: i + min_consecutive]):
            avalanche_start_idx = i
            break

    final_valid_mask = np.copy(raw_valid_mask)
    final_valid_mask[:avalanche_start_idx] = False

    power_valid = power[final_valid_mask]
    counts_valid = counts_corrected[final_valid_mask]

    # If the pixel is dark or doesn't have enough points to fit, reject it physically
    if len(power_valid) < max(4, savgol_window):
        return None

    min_fold_increase = 0.5
    if np.max(counts_raw[final_valid_mask]) < (min_fold_increase * bg_baseline):
        return result  # (or 'return None' in the simple script)

    # Log-Log Transform
    log_power = np.log10(power_valid)
    log_counts = np.log10(counts_valid)

    # Remove duplicates for interpolation
    log_power, unique_idx = np.unique(log_power, return_index=True)
    log_counts = log_counts[unique_idx]

    if len(log_power) < savgol_window:
        return None

    # Uniform Grid Interpolation
    num_fine_points = 300
    log_p_fine = np.linspace(log_power.min(), log_power.max(), num_fine_points)
    interp_func = interp1d(log_power, log_counts, kind='linear')
    log_c_interp = interp_func(log_p_fine)

    # THE FIX: Scale the SavGol window from the raw data density to the interpolated grid density
    points_ratio = num_fine_points / len(log_power)
    wl_fine = int(savgol_window * points_ratio)
    wl_fine = wl_fine if wl_fine % 2 != 0 else wl_fine + 1
    wl_fine = min(wl_fine, num_fine_points - 1)

    if wl_fine <= savgol_poly:
        savgol_poly = wl_fine - 1

    # Apply filter on the scaled window
    log_c_fine = savgol_filter(log_c_interp, window_length=wl_fine, polyorder=savgol_poly)
    dx = log_p_fine[1] - log_p_fine[0]
    slopes_fine = savgol_filter(log_c_interp, window_length=wl_fine, polyorder=savgol_poly, deriv=1, delta=dx)

    # THE FIX 2: Hard Array Truncation to permanently destroy edge artifacts
    clip_idx = wl_fine // 2

    if len(slopes_fine) > 2 * clip_idx:
        slopes_fine = slopes_fine[clip_idx:-clip_idx]

    return np.max(slopes_fine)


# --- 2. Map Generation Workflow ---

def process_spatial_map(folder_path, scan_width_um=10.0, bg_points_to_average=15,
                        snr_threshold=3, savgol_window=15, savgol_poly=3):
    # Setup Aesthetics
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    files = glob.glob(os.path.join(folder_path, "Pixel_*.txt"))
    if not files:
        print(f"No Pixel_X_Y.txt files found in {folder_path}")
        return

    print(f"Found {len(files)} pixels. Establishing global background...")

    # --- Step A: Find the Global Background ---
    # Scan all files to find the "darkest" pixel (lowest average in the first N points)
    lowest_bg = np.inf
    global_bg_baseline = 0
    global_bg_noise_floor = 0
    darkest_pixel_name = ""

    all_pixel_data = []  # Store raw data to avoid reading files twice

    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.search(r"Pixel_(\d+)_(\d+)\.txt", filename)
        if not match: continue

        x_idx, y_idx = int(match.group(1)), int(match.group(2))

        try:
            df = pd.read_csv(filepath, sep="\t")
            if "ReadPower" in df.columns:
                power_col = "ReadPower"
            elif "CurrentPower" in df.columns:
                power_col = "CurrentPower"
            else:
                continue

            p_arr = df[power_col].values
            c_arr = df["Counts" if "Counts" in df.columns else "CountRates"].values

            # Sort just in case
            sort_idx = np.argsort(p_arr)
            p_arr, c_arr = p_arr[sort_idx], c_arr[sort_idx]

            all_pixel_data.append({"x": x_idx, "y": y_idx, "p": p_arr, "c": c_arr})

            # Check background level of this pixel
            local_bg = np.mean(c_arr[:bg_points_to_average])
            if local_bg < lowest_bg:
                lowest_bg = local_bg
                global_bg_baseline = local_bg

                std_emp = np.std(c_arr[:bg_points_to_average])
                std_poi = np.sqrt(local_bg)
                global_bg_noise_floor = max(std_emp, std_poi)
                darkest_pixel_name = filename

        except Exception as e:
            pass

    print(f"Global Baseline set by {darkest_pixel_name}: {global_bg_baseline:.1f} counts/s")
    print(f"Global Noise Floor (1σ): {global_bg_noise_floor:.1f} counts/s")
    print("-" * 50)

    # --- Step B: Extract s_max for every pixel ---
    results = []

    for px in all_pixel_data:
        s_max = extract_smax_savgol(px["p"], px["c"],
                                    global_bg_baseline, global_bg_noise_floor,
                                    snr_threshold=snr_threshold,
                                    savgol_window=savgol_window,
                                    savgol_poly=savgol_poly)

        # THE FIX 3: Apply physical threshold to reject linear scattering
        if s_max is not None and s_max <= 3.0:
            s_max = None

        results.append({"x": px["x"], "y": px["y"], "s_max": s_max})

    # --- Step C: Build the 2D Matrix ---
    df_results = pd.DataFrame(results)

    # Calculate grid aspect ratio to ensure physical map dimensions are correct
    nx = df_results['x'].max() + 1
    ny = df_results['y'].max() + 1
    scan_height_um = scan_width_um * (ny / nx)
    scan_width_um = scan_width_um / 2.0  # Because of the scan error!
    # Pivot to matrix
    matrix_df = df_results.pivot(index='y', columns='x', values='s_max')

    # Reindex to ensure the grid is perfectly square/rectangular even if some files were corrupted
    matrix_df = matrix_df.reindex(index=range(ny), columns=range(nx))
    s_matrix = matrix_df.values

    # --- Step D: Plot the Map ---
    fig, ax = plt.subplots(figsize=(8, 7))
    extent = [0, scan_width_um, 0, scan_height_um]

    # Set up colormap. Use a 'bad' color (e.g., dark grey) for NaN pixels (no avalanche)
    cmap = plt.cm.inferno.copy()
    cmap.set_bad(color='#222222')

    im = ax.imshow(s_matrix, origin='lower', cmap=cmap, extent=extent, interpolation='nearest')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.15)
    cbar = plt.colorbar(im, cax=cax)

    cbar.ax.tick_params(labelsize=14)
    cbar.set_label("Max nonlinearity ($s_{max}$)", fontsize=16, labelpad=15)

    ax.set_xlabel("x position [µm]", fontsize=16, labelpad=10)
    ax.set_ylabel("y position [µm]", fontsize=16, labelpad=10)
    ax.tick_params(labelsize=14)
    ax.set_title("PA nonlinearity map", fontsize=16, pad=15)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Update this to point to the folder containing your Pixel_X_Y.txt files
    # For a 10x10 micron map (5x5 pixels), scan_width_um = 10.0
    target_folder = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\20260318\20260318173630_RelativeMap"

    process_spatial_map(
        folder_path=target_folder,
        scan_width_um=10.0,  # The physical width of your scan in microns
        bg_points_to_average=10,  # Points to average for the global background
        snr_threshold=3,  # Sigma threshold
        savgol_window=5,  # Length of the SavGol smoothing window
        savgol_poly=3  # Degree of the local polynomial (cubic is optimal)
    )