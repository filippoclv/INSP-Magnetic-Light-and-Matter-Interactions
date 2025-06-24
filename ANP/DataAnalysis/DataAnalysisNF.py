import pandas as pd
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pathlib import Path
import re

# If some data importing/displaying doesn't work, check the formatting of the digits in the functions!

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

    # Load power map locally per folder
    height_info_file = folder / "SetInfoScanHeight.txt"
    height_info = pd.read_csv(height_info_file, sep="\t")
    height_map = dict(zip(height_info["Zindex"], height_info["Height"]))

    spectra = {} # Dictionary to store the power labels of each dataframe

    # To sort the labels
    files = sorted(
        folder.glob("Z*.txt"),
        key=lambda f: int(re.search(r"Z(\d+)", f.name).group(1))
    )

    for file_path in files:

        try:

            df = read_dataNF(file_path, height_map)
            spectra[df.attrs["Height_label"]] = df

        except Exception as e:

            print(f"Error, skipping {file_path.name}: {str(e)}")

    # Background subtraction, average of Z0
    background_df = spectra.get("Z0")

    if background_df is not None:

        # Choose a wavelength region where there's clearly no signal
        background_region = background_df[
                                          (background_df["Wavelength_nm"] >= 840) &
                                          (background_df["Wavelength_nm"] <= 845)
                                         ]

        if not background_region.empty:

            background_value = background_region["Intensity_counts"].mean()
            #print(f"\nBackground counts (Z0 average in 840–845 nm) in dataset '{file_path.parent.name}': {background_value:.2f} counts")

            for label, df in spectra.items():

                df["Intensity_counts"] -= background_value
                df["Intensity_counts"] = df["Intensity_counts"].clip(lower=0)

        else:

            print(f"\nWarning: No data in 840–845 nm for Z0 in dataset '{file_path.parent.name}', skipping background subtraction.")

    return spectra

def plot_spectra_heights(spectra_dict, integration_time, data, fig=None, ax=None):

    if fig is None or ax is None:

        fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    heights = [df.attrs["Height"] for df in spectra_dict.values()]
    norm = LogNorm(vmin=min(heights), vmax=max(heights))
    colormap = cm.turbo

    # Main curve
    for label, df in spectra_dict.items():

        height = df.attrs["Height"]
        color = colormap(norm(height))
        ax.plot(df["Wavelength_nm"], df["Intensity_counts"], label=label, color=color)

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
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

    parameters_text = (f"Type: {measurement_type}\n"
                       f"Integration time: {integration_time} s\n"
                      )

    ax.text(0.72, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    return fig, ax