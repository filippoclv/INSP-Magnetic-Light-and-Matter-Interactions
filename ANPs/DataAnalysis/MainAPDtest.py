import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.lines import Line2D
import glob
import os
import re

# Assume these exist from your local environment
from FileReader import read_spectrum_txt_to_dataframe
from Plotter import plot_single_spectrum

# --- 1. Configuration ---
CONFIG = {
    # Physical Scan Widths (X-axis size in microns)
    "HYPERSPECTRAL_WIDTH_UM": 2.0,
    "APD_MAP_WIDTH_UM": 4.0,

    "BG_RANGE_NM": (875, 900),
    "POLY_DEGREE": 4,
    "EDGE_CROP_PERCENT": 10,

    "PATHS": {
        "SPECTRUM_AGGLOMERATE": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\spectra1s40P.txt",
        "SPECTRUM_VORTEX": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\spectra1s40Pvortex.txt",
        "MAP_INTENSITY": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\hyperspectral40P1s770to830.txt",
        "PIXEL_FOLDER": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\20260217165040_RelativeMap"
    }
}


def set_plot_style():
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['xtick.major.width'] = 1.5
    plt.rcParams['ytick.major.width'] = 1.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'


# --- 2. Computationally Rigorous Analysis ---

def load_and_correct_spectrum(filepath, bg_range):
    try:
        spectrum = read_spectrum_txt_to_dataframe(filepath)
        bg_min, bg_max = bg_range
        bg_region = spectrum[(spectrum["Wavelength_nm"] >= bg_min) & (spectrum["Wavelength_nm"] <= bg_max)]

        if not bg_region.empty:
            bg_mean = bg_region["Intensity_counts"].mean()
            print(f"[{os.path.basename(filepath)}] BG Mean ({bg_min}-{bg_max} nm): {bg_mean:.2f} counts")
            spectrum["Intensity_counts"] = spectrum["Intensity_counts"] - bg_mean
            spectrum["Intensity_counts"] = spectrum["Intensity_counts"].clip(lower=0)
        else:
            print(f"Warning: No data in BG range for {os.path.basename(filepath)}")
        return spectrum
    except Exception as e:
        print(f"Error loading spectrum {filepath}: {e}")
        return None


def calculate_max_slope_polyfit(x_data, y_data, degree=4, crop_percent=10):
    valid_mask = (x_data > 0) & (y_data > 0)
    x_valid, y_valid = x_data[valid_mask], y_data[valid_mask]

    if len(x_valid) <= degree + 2:
        return None, None, None, None

    log_x = np.log10(x_valid)
    log_y = np.log10(y_valid)

    try:
        coeffs = np.polyfit(log_x, log_y, degree)
    except np.linalg.LinAlgError:
        return None, None, None, None

    poly_func = np.poly1d(coeffs)
    deriv_func = np.polyder(poly_func)

    # Dense evaluation with edge cropping
    x_dense = np.linspace(log_x.min(), log_x.max(), 500)
    idx_start = int(len(x_dense) * (crop_percent / 100))
    idx_end = int(len(x_dense) * (1 - crop_percent / 100))
    x_search = x_dense[idx_start:idx_end]

    if len(x_search) == 0: return None, None, None, None

    slopes = deriv_func(x_search)
    max_idx = np.argmax(slopes)
    return slopes[max_idx], poly_func, 10 ** (x_search[max_idx]), log_x


def load_all_pixel_data(folder_path, degree):
    files = glob.glob(os.path.join(folder_path, "Pixel_*.txt"))
    data_store = []
    print(f"--- Loading {len(files)} pixel files ---")

    for filepath in files:
        filename = os.path.basename(filepath)
        match = re.search(r"Pixel_(\d+)_(\d+)\.txt", filename)
        if not match: continue

        x_idx, y_idx = int(match.group(1)), int(match.group(2))

        try:
            df = pd.read_csv(filepath, sep="\t")
            if "ReadPower" not in df.columns or "Counts" not in df.columns: continue

            p_arr = np.array(df["ReadPower"].values, dtype=float)
            c_arr = np.array(df["Counts"].values, dtype=float)

            max_slope, poly_func, p_at_max, log_x_data = calculate_max_slope_polyfit(
                p_arr, c_arr, degree, CONFIG["EDGE_CROP_PERCENT"]
            )

            entry = {
                "x": x_idx, "y": y_idx,
                "power": p_arr, "counts": c_arr,
                "max_slope": max_slope, "poly_func": poly_func,
                "log_x_min": log_x_data.min() if log_x_data is not None else 0,
                "log_x_max": log_x_data.max() if log_x_data is not None else 0
            }
            data_store.append(entry)
        except Exception:
            pass
    return data_store


def create_matrix_from_coords(df, x_col, y_col, z_col):
    """
    Robustly converts physical coordinates (floats) or indices (ints) to a grid matrix.
    Returns: Matrix (numpy array), Aspect Ratio (height/width)
    """
    # 1. Identify unique coordinate steps
    x_unique = sorted(df[x_col].unique())
    y_unique = sorted(df[y_col].unique())

    # 2. Map coordinates to integer rank (0, 1, 2...)
    x_map = {val: i for i, val in enumerate(x_unique)}
    y_map = {val: i for i, val in enumerate(y_unique)}

    df['x_idx'] = df[x_col].map(x_map)
    df['y_idx'] = df[y_col].map(y_map)

    # 3. Pivot using the integer indices
    pivot_df = df.pivot(index='y_idx', columns='x_idx', values=z_col)

    # 4. Reindex to ensure full rectangular grid (fills missing pixels with NaN)
    # This handles cases where data might be sparse
    nx, ny = len(x_unique), len(y_unique)
    pivot_df = pivot_df.reindex(index=range(ny), columns=range(nx))

    # 5. Calculate Grid Aspect Ratio (Rows / Cols)
    # If the scan is 10x20 pixels, aspect is 0.5 (or 2.0 depending on convention).
    # Matplotlib extent handles the stretching, we just need to provide the physical box.
    # Aspect ratio logic: Height / Width
    grid_aspect_ratio = ny / nx if nx > 0 else 1.0

    return pivot_df.values, grid_aspect_ratio


# --- 3. Plotting ---

def plot_heatmap(matrix, scan_width_um, grid_aspect_ratio, title, label, force_scientific=False, cmap='viridis'):
    if matrix is None: return

    # Physical Height depends on the number of pixels in Y vs X
    scan_height_um = scan_width_um * grid_aspect_ratio

    fig, ax = plt.subplots(figsize=(8, 7))
    extent = [0, scan_width_um, 0, scan_height_um]

    im = ax.imshow(matrix, origin='lower', cmap=cmap, extent=extent, interpolation='nearest')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.15)
    cbar = plt.colorbar(im, cax=cax)

    if force_scientific:
        fmt = ticker.ScalarFormatter(useMathText=True)
        fmt.set_powerlimits((3, 3))
        cbar.ax.yaxis.set_major_formatter(fmt)

    cbar.ax.tick_params(labelsize=14)
    cbar.set_label(label, fontsize=16, labelpad=15)
    ax.set_xlabel("x position [µm]", fontsize=16)
    ax.set_ylabel("y position [µm]", fontsize=16)
    ax.set_title(title, fontsize=16, pad=15)
    plt.tight_layout()
    plt.show()


def plot_all_curves_and_fits(pixel_data):
    fig, ax = plt.subplots(figsize=(10, 8))

    for px in pixel_data:
        # Raw data
        ax.plot(px["power"], px["counts"], 'o', color='teal', alpha=0.05, markersize=2)
        # Fits
        if px["poly_func"] is not None:
            x_plot = np.logspace(px["log_x_min"], px["log_x_max"], 100)
            y_plot = 10 ** (px["poly_func"](np.log10(x_plot)))
            ax.plot(x_plot, y_plot, '-', color='crimson', linewidth=1, alpha=0.3)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Read Power [W]", fontsize=18)
    ax.set_ylabel("Counts", fontsize=18)
    ax.set_title(f"Power Curves & PolyFits (deg={CONFIG['POLY_DEGREE']})", fontsize=18)

    # FIX: Explicitly pass handles list to legend
    legend_handles = [
        Line2D([0], [0], marker='o', color='teal', lw=0, label='Raw Data'),
        Line2D([0], [0], color='crimson', lw=2, label='Polynomial Fit')
    ]
    ax.legend(handles=legend_handles, loc='best', fontsize=14)
    plt.tight_layout()
    plt.show()


def plot_slope_stats(pixel_data):
    slopes = [p["max_slope"] for p in pixel_data if p["max_slope"] is not None and np.isfinite(p["max_slope"])]
    if not slopes: return

    fig, ax = plt.subplots(figsize=(8, 6))
    mean_s = np.mean(slopes)

    filtered_slopes = [s for s in slopes if 0 < s < 15]  # Filter extreme outliers
    ax.hist(filtered_slopes, bins=25, color='teal', edgecolor='black', alpha=0.7)
    ax.axvline(mean_s, color='crimson', linestyle='--', linewidth=2, label=f"Mean: {mean_s:.2f}")

    ax.set_xlabel("Max Slope $s_{max}$", fontsize=16)
    ax.set_ylabel("Frequency", fontsize=16)
    ax.set_title("Distribution of Avalanche Slopes", fontsize=18)
    ax.legend(fontsize=14)
    plt.tight_layout()
    plt.show()


# --- 4. Workflow ---

def main():
    set_plot_style()

    # A. Spectra
    print("--- Spectra Analysis ---")
    s1 = load_and_correct_spectrum(CONFIG["PATHS"]["SPECTRUM_AGGLOMERATE"], CONFIG["BG_RANGE_NM"])
    if s1 is not None: plot_single_spectrum(s1, "Agglomerate Spectrum")

    s2 = load_and_correct_spectrum(CONFIG["PATHS"]["SPECTRUM_VORTEX"], CONFIG["BG_RANGE_NM"])
    if s2 is not None: plot_single_spectrum(s2, "Vortex Spectrum")

    # B. Hyperspectral Map
    print("\n--- Hyperspectral Map ---")
    try:
        # Use simple pandas read first
        df_map = pd.read_csv(CONFIG["PATHS"]["MAP_INTENSITY"], sep="\t", header=None, names=["x", "y", "intensity"])

        # We need to map physical coords to matrix rows/cols BEFORE assuming integer subtraction
        # But for subtraction, we just need the max Y coordinate
        max_y_val = df_map['y'].max()

        # Row Subtraction (Background Correction)
        top_row_bg = df_map[df_map['y'] == max_y_val]['intensity'].mean()
        print(f"Subtracting top row mean: {top_row_bg:.2f}")
        df_map['intensity'] = (df_map['intensity'] - top_row_bg).clip(lower=0)

        # Robust Matrix Creation (Handles Floats)
        matrix, aspect = create_matrix_from_coords(df_map, "x", "y", "intensity")

        plot_heatmap(matrix, CONFIG["HYPERSPECTRAL_WIDTH_UM"], aspect,
                     "Hyperspectral Intensity Map", "Intensity [counts]", force_scientific=True)
    except Exception as e:
        print(f"Hyperspectral error: {e}")

    # C. APD Slope Map
    print("\n--- APD Slope Analysis ---")
    pixel_data = load_all_pixel_data(CONFIG["PATHS"]["PIXEL_FOLDER"], CONFIG["POLY_DEGREE"])

    if pixel_data:
        plot_all_curves_and_fits(pixel_data)
        plot_slope_stats(pixel_data)

        # Convert Pixel List to DataFrame for mapping
        df_pixels = pd.DataFrame(pixel_data)
        matrix, aspect = create_matrix_from_coords(df_pixels, "x", "y", "max_slope")

        plot_heatmap(matrix, CONFIG["APD_MAP_WIDTH_UM"], aspect,
                     "Map of Max Slopes (s-factor)", "Slope $s_{max}$", cmap='inferno')


if __name__ == "__main__":
    main()