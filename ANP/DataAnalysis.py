import pandas as pd
import numpy as np
#from IPython.display import display
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pathlib import Path
import re

power_info_file = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144818\SetInfoPowerCurve.txt"
power_info = pd.read_csv(power_info_file, sep="\t")
power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

def read_data(file_path):

    # To extract the P label of the data files
    power_label_check = re.search(r'P(\d+)', file_path.name)

    if not power_label_check:
        raise ValueError(f"Filename {file_path.name} is not labeled correctly.")

    power_label = power_label_check.group(1)
    power_index = int(power_label) # This is to use the "power index" stored in the info file for the colormap

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
                # Maybe the counts even if they are integers should be considered floats as well?

                wavelengths.append(wavelength)
                intensities.append(intensity)

    # Let's use pandas dataframes

    df = pd.DataFrame({
        "Wavelength_nm": wavelengths,
        "Intensity_counts": intensities
    })

    df.attrs["Power_label"] = f"P{power_label}"  # To identify the spectrum to its label
    df.attrs["Power_W"] = power_map.get(power_index)

    return df

def read_all_spectra(folder_path):

    folder = Path(folder_path)
    spectra = {} # Dictionary to store the power labels of each dataframe

    # To sort the labels
    files = sorted(
        folder.glob("P*.txt"),
        key=lambda f: int(re.search(r"P(\d+)", f.name).group(1))
    )

    for file_path in files:

        try:

            df = read_data(file_path)
            spectra[df.attrs["Power_label"]] = df

        except Exception as e:

            print(f"Error, skipping {file_path.name}: {str(e)}")

    # Background subtraction, average of P0
    background_df = spectra.get("P0")

    if background_df is not None:

        background_value = background_df["Intensity_counts"].mean()
        print(f"\nBackground counts (P0 average): {background_value:.2f} counts")

        for df in spectra.values():
            df["Intensity_counts"] -= background_value
            df["Intensity_counts"] = df["Intensity_counts"].clip(lower=0)

    return spectra

def plot_spectra(spectra_dict):

    fig, ax = plt.subplots(figsize=(12, 7))

    powers = [df.attrs["Power_W"] for df in spectra_dict.values()]
    norm = LogNorm(vmin=min(powers), vmax=max(powers)) # Needed for colormap
    colormap = cm.turbo

    for label, df in spectra_dict.items():

        power = df.attrs["Power_W"]
        color = colormap(norm(power))
        ax.plot(df["Wavelength_nm"], df["Intensity_counts"], label=label, color=color)

    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])

    ticks_values = np.linspace(min(powers), max(powers), 6)  # Choose number of ticks
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_ticks(ticks_values)
    cbar.set_ticklabels([f"{v:.1e}" for v in ticks_values])  # For scientific notation
    cbar.set_label("Power [W]", fontsize=12, labelpad=25)

    ax.set_title("Intensity counts vs wavelength at different powers", fontsize=14)
    ax.set_xlabel("Wavelength [nm]", fontsize=12)
    ax.set_ylabel("Intensity [counts]", fontsize=12)
    ax.grid(True, alpha=0.3)
    #ax.legend(title="Power label", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=10, ncol=2)

    plt.tight_layout()
    #plt.show()

def print_power_values():

    for label, df in all_spectra.items():
        print(f"{label}: {df.attrs['Power_W']:.6e} W")

data_folder = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144818"

#Specific parameters of this measurement!
integration_time = 3 # Integration time in s
ratio_start = 0.0001
ratio_stop = 0.08

all_spectra = read_all_spectra(data_folder)

#file_label = "P5" # Choose which spectrum to display
#print(f"\nSpectrum ({file_label}):")
#display(all_spectra[file_label])

#print_power_values()

#plot_spectra(all_spectra)

# Trying now to zoom into little peaks

def plot_spectra_with_zoom(spectra_dict, integration_time, ratio_start, ratio_stop):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    powers = [df.attrs["Power_W"] for df in spectra_dict.values()]
    norm = LogNorm(vmin=min(powers), vmax=max(powers))
    colormap = cm.turbo

    # Main curve
    for label, df in spectra_dict.items()\
            :
        power = df.attrs["Power_W"]
        color = colormap(norm(power))
        ax.plot(df["Wavelength_nm"], df["Intensity_counts"], label=label, color=color)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    #ticks_values = np.linspace(min(powers), max(powers), 6)  # Choose number of ticks
    #cbar.set_ticks(ticks_values)
    #cbar.set_ticklabels([f"{v:.1e}" for v in ticks_values])  # For scientific notation
    cbar.set_label("Power [W] (log scale)", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=14)

    # Zoomed curve
    ax_inset = inset_axes(ax, width="45%", height="45%", loc="upper left", borderpad=7)

    for label, df in spectra_dict.items():

        power = df.attrs["Power_W"]
        color = colormap(norm(power))
        zoomed = df[(df["Wavelength_nm"] >= 630) & (df["Wavelength_nm"] <= 760)]
        if not zoomed.empty:
            ax_inset.plot(zoomed["Wavelength_nm"], zoomed["Intensity_counts"], color=color)

    ax_inset.set_xlim(630, 760)
    ax_inset.set_title("Zoomed in 630–760 nm range", fontsize=12)
    ax_inset.tick_params(labelsize=12)
    ax_inset.grid(True, alpha=0.3)
    ax_inset.set_xlabel("Wavelength [nm]", fontsize=12)
    ax_inset.set_ylabel("Intensity [counts]", fontsize=12)

    ax_inset.patch.set_edgecolor('black')
    ax_inset.patch.set_linewidth(1.2)

    # Main plot layout
    ax.set_title("Intensity counts vs wavelength", fontsize=16)
    ax.set_xlabel("Wavelength [nm]", fontsize=14)
    ax.set_ylabel("Intensity [counts]", fontsize=14)
    ax.grid(True, alpha=0.3)
    #ax.legend(title="Power label", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=10, ncol=2)

    parameters_text = f"Integration time: {integration_time} s\nPower ratio start: {ratio_start}\nPower ratio stop: {ratio_stop}"
    ax.text(0.72, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    #plt.show()

# Let's try the same with spectra normalized by its max
# Not sure if the following function makes sense

def plot_normalized_spectra_with_zoom(spectra_dict, integration_time, ratio_start, ratio_stop):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    powers = [df.attrs["Power_W"] for df in spectra_dict.values()]
    norm = Normalize(vmin=min(powers), vmax=max(powers))
    colormap = cm.turbo

    # Main curves
    for label, df in spectra_dict.items():

        power = df.attrs["Power_W"]
        color = colormap(norm(power))
        max_value = df["Intensity_counts"].max()

        if max_value > 0:

            normalized_intensity = df["Intensity_counts"] / max_value

        else:

            normalized_intensity = np.zeros_like(df["Intensity_counts"])

        ax.plot(df["Wavelength_nm"], normalized_intensity, label=label, color=color)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Normalized power", fontsize=14, labelpad=10)
    cbar.ax.tick_params(labelsize=12)

    # Zoomed in normalized curves
    ax_inset = inset_axes(ax, width="45%", height="45%", loc="upper left", borderpad=7)

    for label, df in spectra_dict.items():

        power = df.attrs["Power_W"]
        color = colormap(norm(power))
        zoomed = df[(df["Wavelength_nm"] >= 630) & (df["Wavelength_nm"] <= 760)]

        if not zoomed.empty:

            max_zoomed_value = df["Intensity_counts"].max()

            if max_zoomed_value > 0:

                norm_intensity_zoomed = zoomed["Intensity_counts"] / max_zoomed_value

            else:

                norm_intensity_zoomed = np.zeros_like(zoomed["Intensity_counts"])

            ax_inset.plot(zoomed["Wavelength_nm"], norm_intensity_zoomed, color=color)

    ax_inset.set_xlim(630, 760)
    ax_inset.set_title("Zoom: 630–760 nm", fontsize=10)
    ax_inset.tick_params(labelsize=9)
    ax_inset.grid(True, alpha=0.3)
    ax_inset.set_xlabel("Wavelength [nm]", fontsize=10)
    ax_inset.set_ylabel("Normalized intensity counts", fontsize=10)
    ax_inset.patch.set_edgecolor('black')
    ax_inset.patch.set_linewidth(1.2)

    # Main plot layout
    ax.set_title("Normalized intensity vs Wavelength", fontsize=16)
    ax.set_xlabel("Wavelength [nm]", fontsize=14)
    ax.set_ylabel("Normalized intensity counts", fontsize=14)
    ax.grid(True, alpha=0.3)

    # Parameter box
    parameters_text = f"Integration time: {integration_time} s\nPower ratio start: {ratio_start}\nPower ratio stop: {ratio_stop}"
    ax.text(0.72, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=13,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    #plt.show()

plot_spectra_with_zoom(all_spectra,
                       integration_time=integration_time,
                       ratio_start=ratio_start,
                       ratio_stop=ratio_stop)

#plot_normalized_spectra_with_zoom(all_spectra,
#                                  integration_time=integration_time,
#                                  ratio_start=ratio_start,
#                                  ratio_stop=ratio_stop
#                                  )

# I should normalize each spectrum with its max value! Check previous function

# Let's now handle the data and integrate the big peak

def integrate_peak(spectra_dict, wl_min, wl_max):

    results = []

    for label, df in spectra_dict.items():

        power = df.attrs["Power_W"]
        filtered_dataframe = df[(df["Wavelength_nm"] >= wl_min) & (df["Wavelength_nm"] <= wl_max)]

        if filtered_dataframe.empty:

            print(f"Warning: {label} has no data in range {wl_min}-{wl_max} nm")

            continue

        luminescence = np.trapz(filtered_dataframe["Intensity_counts"], filtered_dataframe["Wavelength_nm"])
        results.append((power, luminescence))

    return pd.DataFrame(results, columns=["Power_W", "Integrated intensity"])

results_df = integrate_peak(all_spectra, wl_min=755, wl_max=860)

#display(results_df)

def plot_integrated_intensity_vs_power(results_df, wl_min, wl_max, integration_time, ratio_start, ratio_stop):

    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)

    ax.plot(
        results_df["Power_W"],
        results_df["Integrated intensity"],
        marker='o',
        markersize=7,
        markerfacecolor='none',
        markeredgecolor='crimson',
        linestyle='-',
        linewidth=2,
        color='teal',
        label="Integrated intensity"
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Power [W]", fontsize=12)
    ax.set_ylabel("Integrated intensity [a.u.]", fontsize=12)
    ax.set_title(f"log-log scale: integrated intensity vs power\n({wl_min}–{wl_max} nm peak)", fontsize=14)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)

    # Parameters box
    parameters_text = f"Integration time: {integration_time} s\nPower ratio start: {ratio_start}\nPower ratio stop: {ratio_stop}"
    ax.text(0.7, 0.2, parameters_text,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    #plt.show()

plot_integrated_intensity_vs_power(results_df,
                                   wl_min=755,
                                   wl_max=860,
                                   integration_time=integration_time,
                                   ratio_start=ratio_start,
                                   ratio_stop=ratio_stop
                                   )

# Remove the background, like P0, in the data (done). Then try again normalization
# If I do the derivative of the power spectra I should get the non linearity parameter s

