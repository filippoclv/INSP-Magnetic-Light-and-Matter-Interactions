import re
import pandas as pd
from pathlib import Path

def read_data(file_path, power_map):

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

    # Load power map locally per folder
    power_info_file = folder / "SetInfoPowerCurve.txt"
    power_info = pd.read_csv(power_info_file, sep="\t")
    power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

    spectra = {} # Dictionary to store the power labels of each dataframe

    # To sort the labels
    files = sorted(
        folder.glob("P*.txt"),
        key=lambda f: int(re.search(r"P(\d+)", f.name).group(1))
    )

    for file_path in files:

        try:

            df = read_data(file_path, power_map)
            spectra[df.attrs["Power_label"]] = df

        except Exception as e:

            print(f"Error, skipping {file_path.name}: {str(e)}")

    # Background subtraction, average of P0
    background_df = spectra.get("P0")

    if background_df is not None:
        # Choose a wavelength region where there's clearly no signal
        background_region = background_df[
            (background_df["Wavelength_nm"] >= 870) &
            (background_df["Wavelength_nm"] <= 900)
            ]

        if not background_region.empty:

            background_value = background_region["Intensity_counts"].mean()
            #print(f"\nBackground counts (P0 average in 870–900 nm) in dataset '{file_path.parent.name}': {background_value:.2f} counts")

            for label, df in spectra.items():

                df["Intensity_counts"] -= background_value
                df["Intensity_counts"] = df["Intensity_counts"].clip(lower=0)

        else:

            print(f"\nWarning: No data in 870–900 nm for P0 in dataset '{file_path.parent.name}' — skipping background subtraction.")

    return spectra