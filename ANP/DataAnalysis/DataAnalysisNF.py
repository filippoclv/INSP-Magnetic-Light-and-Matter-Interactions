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

            df = read_data(file_path, height_map)
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