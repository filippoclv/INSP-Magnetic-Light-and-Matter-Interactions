import numpy as np
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt

path_P0 = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144818\P0.txt"

def read_data(file_path):

    wavelengths = [] # In nm
    intensities = [] # Counts

    with open(file_path, 'r') as file:

        # To read the file line by line, ignoring non data lines and removing spaces
        for line in file:

            if '=' in line or not (';' in line and ',' in line):

                continue

            line = line.strip()

            if line:

                # Splitting wavelengths and intensities
                wavelength_only, intensity_only = line.split(';')

                # Converting comma to dots
                wavelength = float(wavelength_only.replace(',', '.'))
                intensity = int(intensity_only.strip()) # Maybe the counts even if they are integers should be considered floats as well?

                wavelengths.append(wavelength)
                intensities.append(intensity)

    # Let's use pandas dataframes

    df = pd.DataFrame({
        'Wavelength_nm': wavelengths,
        'Intensity_counts': intensities
    })

    return df

# Let's test this

spectrum_P0 = read_data(path_P0)

print("Summary:")
print(spectrum_P0.info())
print("\nFirst 5 rows:")
print(spectrum_P0.head())

display(spectrum_P0)

spectrum_P0.plot(x="Wavelength_nm", y="Intensity_counts", legend=False)
plt.title("Intensity counts vs Wavelength")
plt.xlabel('Wavelength [nm]')
plt.ylabel('Intensity [counts]')
plt.grid()
plt.tight_layout()
plt.show()