import pandas as pd
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pathlib import Path
import re

# If some data importing/displaying doesn't work, check the formatting of the digits in the functions!

def read_spectrum(file_path):

    wavelengths = [] # In nm
    intensities = [] # Counts

    with open(file_path, "r") as file:

        # To read the file line by line, ignoring non data lines and removing spaces
        for line in file:

            if "=" in line or not (";" in line and "," in line):

                continue

            line = line.strip()

            if line:

                # Splitting wavelengths and intensities
                wavelength_only, intensity_only = line.split(";")

                # Converting comma to dots
                wavelength = float(wavelength_only.replace(",", "."))
                intensity = int(intensity_only.strip())

                wavelengths.append(wavelength)
                intensities.append(intensity)

    # Let's use pandas dataframes

    df = pd.DataFrame({
        "Wavelength_nm": wavelengths,
        "Intensity_counts": intensities
    })

    return df

def read_dataNF(file_path, height_map):

    height_label_check = re.search(r'Z(\d+)', file_path.name)

    if not height_label_check:

        raise ValueError(f"Filename {file_path.name} is not labeled correctly.")

    height_label = height_label_check.group(1)
    height_index = int(height_label)

    wavelengths = [] # In nm
    intensities = [] # Counts

    with open(file_path, "r") as file:

        # To read the file line by line, ignoring non data lines and removing spaces
        for line in file:

            if "=" in line or not (";" in line and "," in line):

                continue

            line = line.strip()

            if line:

                # Splitting wavelengths and intensities
                wavelength_only, intensity_only = line.split(";")

                # Converting comma to dots
                wavelength = float(wavelength_only.replace(",", "."))
                intensity = int(intensity_only.strip())

                wavelengths.append(wavelength)
                intensities.append(intensity)

    # Let's use pandas dataframes

    df = pd.DataFrame({
        "Wavelength_nm": wavelengths,
        "Intensity_counts": intensities
    })

    df.attrs["Height_label"] = f"Z{height_label}"  # To identify the spectrum to its label
    df.attrs["Height"] = height_map.get(height_index)

    return df

def read_all_spectraNF(folder_path):
    folder = Path(folder_path)

    # Load power map
    height_info_file = folder / "SetInfoScanHeight.txt"
    height_info = pd.read_csv(height_info_file, sep="\t")
    height_map = dict(zip(height_info["Zindex"], height_info["Height"]))

    spectra = {}

    # Load reference spectrum
    ref_df = read_spectrum(folder_path + "/ref.txt")
    ref_intensity = ref_df["Intensity_counts"].values

    # Compute background from a fixed wavelength window in the reference
    background_region = ref_df[(ref_df["Wavelength_nm"] >= 843) & (ref_df["Wavelength_nm"] <= 844)]
    background_mean = background_region["Intensity_counts"].mean()

    # Load spectra files
    files = sorted(
        folder.glob("Z*.txt"),
        key=lambda f: int(re.search(r"Z(\d+)", f.name).group(1))
    )

    for file_path in files:
        df = read_dataNF(file_path, height_map)

        # Subtract background (same value for all spectra)
        df["Intensity_counts"] -= background_mean
        df["Intensity_counts"] = df["Intensity_counts"].clip(lower=0)

        spectra[df.attrs["Height_label"]] = df

    return spectra

def plot_spectra_heights(spectra_dict, integration_time, data, fig=None, ax=None):

    if fig is None or ax is None:

        fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    heights = [df.attrs["Height"] for df in spectra_dict.values()]
    sorted_heights = np.sort(np.unique(heights))

    colormap = cm.jet
    colors = colormap(np.linspace(0, 1, len(sorted_heights)))
    height_to_color = dict(zip(sorted_heights, colors))

    for label, df in spectra_dict.items():

        height = df.attrs["Height"]
        color = height_to_color[height]
        ax.plot(df["Wavelength_nm"], df["Intensity_counts"], label=label, color=color, linewidth=1, alpha=0.8)

    cmap = ListedColormap(colors)
    boundaries = np.append(sorted_heights, sorted_heights[-1] + 1)
    norm = BoundaryNorm(boundaries=boundaries, ncolors=len(colors))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, ticks=sorted_heights[::max(1, len(sorted_heights) // 10)])
    cbar.set_label("Height (SensZ) [mV]", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=14)

    # Main plot layout
    ax.set_title("Intensity counts vs wavelength", fontsize=16)
    ax.set_xlabel("Wavelength [nm]", fontsize=14)
    ax.set_ylabel("Intensity [counts]", fontsize=14)
    ax.grid(True, alpha=0.3)

    # Get the first dataset to check if it's TIR or NO TIR
    first_df = next(iter(spectra_dict.values()))
    measurement_type = data.get('label', 'Unknown')  # Gets 'TIR' or 'NO TIR' from the data dictionary
    power_percentage = data.get('power_percentage', 'Unknown')
    stepZ = data.get('stepZ_mV', 'Unknown')

    parameters_text = (f"Type: {measurement_type}\n"
                       f"Integration time: {integration_time} s\n"
                       f"Power: {power_percentage}%\n"
                       f"StepZ size: {stepZ} mV"
                      )

    ax.text(0.72, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    ax.set_ylim(bottom=0)

    return fig, ax

def plot_spectra_heights_norm(spectra_dict, integration_time, data, fig=None, ax=None):

    if fig is None or ax is None:

        fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    heights = [df.attrs["Height"] for df in spectra_dict.values()]
    sorted_heights = np.sort(np.unique(heights))

    colormap = cm.jet
    colors = colormap(np.linspace(0, 1, len(sorted_heights)))
    height_to_color = dict(zip(sorted_heights, colors))

    for label, df in spectra_dict.items():

        height = df.attrs["Height"]
        color = height_to_color[height]
        ax.plot(df["Wavelength_nm"], df["Intensity_counts"]/max(df["Intensity_counts"]), label=label, color=color, linewidth=1, alpha=0.8)

    cmap = ListedColormap(colors)
    boundaries = np.append(sorted_heights, sorted_heights[-1] + 1)
    norm = BoundaryNorm(boundaries=boundaries, ncolors=len(colors))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, ticks=sorted_heights[::max(1, len(sorted_heights) // 10)])
    cbar.set_label("Height (SensZ) [mV]", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=14)

    # Main plot layout
    ax.set_title("Intensity counts vs wavelength", fontsize=16)
    ax.set_xlabel("Wavelength [nm]", fontsize=14)
    ax.set_ylabel("Intensity [counts]", fontsize=14)
    ax.grid(True, alpha=0.3)

    # Get the first dataset to check if it's TIR or NO TIR
    first_df = next(iter(spectra_dict.values()))
    measurement_type = data.get('label', 'Unknown')  # Gets TIR or NO TIR from the data dictionary
    power_percentage = data.get('power_percentage', 'Unknown')
    stepZ = data.get('stepZ', 'Unknown')

    parameters_text = (f"Type: {measurement_type}\n"
                       f"Integration time: {integration_time} s\n"
                       f"Power: {power_percentage}%\n"
                       f"StepZ size: {stepZ} mV"
                      )

    ax.text(0.72, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    ax.set_ylim(bottom=0)

    return fig, ax

def integrate_peakNF(spectra_dict, wl_min, wl_max, integration_time):
    # Integrating with trapeizoidal method

    results = []

    for label, df in spectra_dict.items():

        height = df.attrs["Height"]
        filtered_dataframe = df[(df["Wavelength_nm"] >= wl_min) & (df["Wavelength_nm"] <= wl_max)]

        if filtered_dataframe.empty:

            print(f"Warning: {label} has no data in range {wl_min}-{wl_max} nm")

            continue

        integrated_counts = np.trapz(filtered_dataframe["Intensity_counts"], filtered_dataframe["Wavelength_nm"])
        luminescence = integrated_counts / integration_time

        results.append((height, luminescence, integrated_counts))

    return pd.DataFrame(results, columns=["Height_mV", "Luminescence_counts", "Integrated_counts"])

def integral_map_different_heights(spectra_dict, integration_time, wl_start, wl_stop, wl_step=1.0, ref_df=None):
    heights = []
    wl_centers = np.arange(wl_start, wl_stop, wl_step)
    data_matrix = []

    ref_integrated = None
    if ref_df is not None:
        ref_integrated = []
        for wl in wl_centers:
            ref_window = ref_df[(ref_df["Wavelength_nm"] >= wl) & (ref_df["Wavelength_nm"] < wl + wl_step)]
            val = np.trapz(ref_window["Intensity_counts"], ref_window["Wavelength_nm"]) / integration_time
            ref_integrated.append(val)
        ref_integrated = np.array(ref_integrated)

    for label, df in sorted(spectra_dict.items(), key=lambda x: x[1].attrs["Height"]):
        height = df.attrs["Height"]
        heights.append(height)
        intensities = []

        for wl in wl_centers:
            window = df[(df["Wavelength_nm"] >= wl) & (df["Wavelength_nm"] < wl + wl_step)]
            val = np.trapz(window["Intensity_counts"], window["Wavelength_nm"]) / integration_time
            intensities.append(val)

        intensities = np.array(intensities)

        if ref_integrated is not None:
            # Set NaN where numerator is 0
            with np.errstate(divide='ignore', invalid='ignore'):
                intensities = np.where(intensities >= 500, intensities / ref_integrated, np.nan)

        data_matrix.append(intensities)

    return np.array(heights), wl_centers + wl_step / 2, np.array(data_matrix)

