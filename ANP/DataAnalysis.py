import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
from pathlib import Path
import re

def read_data(file_path):

    # To extract the P label of the data files
    power_label_check = re.search(r'P(\d+)', file_path.name)

    if not power_label_check:
        raise ValueError(f"Filename {file_path.name} is not labeled correctly.")

    power_label = power_label_check.group(1)

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

    return spectra

def plot_spectra(spectra_dict):

    plt.figure(figsize=(12, 7))

    for label, df in spectra_dict.items():

        plt.plot(df["Wavelength_nm"],
                 df["Intensity_counts"],
                 label=label)

    plt.title("Intensity counts vs wavelength, different powers", fontsize=14)
    plt.xlabel("Wavelength [nm]", fontsize=12)
    plt.ylabel("Intensity [counts]", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(title="Power label", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=10, ncol=2)
    plt.tight_layout()
    plt.show()

data_folder = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144818"

all_spectra = read_all_spectra(data_folder)

file_label = "P5" # Choose which spectrum to display
print(f"\nSpectrum ({file_label}):")
display(all_spectra[file_label])

plot_spectra(all_spectra)