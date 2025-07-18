import re
import pandas as pd
from pathlib import Path

def read_spectrum_txt_to_dataframe(spectrum_path, power_map=None):

    wavelengths = [] # In nm
    intensities = [] # Counts

    with open(spectrum_path, "r") as file:

        for line in file:

            if "=" in line or not (";" in line and "," in line):

                continue

            line = line.strip()

            if line:

                wavelength_only, intensity_only = line.split(";")
                wavelength = float(wavelength_only.replace(",", "."))
                intensity = int(intensity_only.strip())

                wavelengths.append(wavelength)
                intensities.append(intensity)

    spectrum = pd.DataFrame({"Wavelength_nm": wavelengths,"Intensity_counts": intensities})

    if power_map is not None:

        power_label_extracted = re.search(r"P(\d+)", spectrum_path.name)
        power_label = power_label_extracted.group(1)
        power_index = int(power_label)

        spectrum.attrs["Power_label"] = f"P{power_label}"
        spectrum.attrs["Power_W"] = power_map.get(power_index)

    return spectrum

def all_spectra_dataframe_dict(folder_path):

    folder = Path(folder_path)

    power_info_file = folder / "SetInfoPowerCurve.txt"
    power_info = pd.read_csv(power_info_file, sep="\t")
    power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

    spectra_dict = {}

    files = sorted(folder.glob("P*.txt"), key=lambda f: int(re.search(r"P(\d+)", f.name).group(1)))

    for file_path in files:

        data = read_spectrum_txt_to_dataframe(file_path, power_map)
        spectra_dict[data.attrs["Power_label"]] = data


    # # Background subtraction, average of P0
    # background_df = spectra.get("P0")
    #
    # if background_df is not None:
    #     # Choose a wavelength region where there's clearly no signal
    #     background_region = background_df[
    #         (background_df["Wavelength_nm"] >= 870) &
    #         (background_df["Wavelength_nm"] <= 900)
    #         ]
    #
    #     if not background_region.empty:
    #
    #         background_value = background_region["Intensity_counts"].mean()
    #         #print(f"\nBackground counts (P0 average in 870–900 nm) in dataset '{file_path.parent.name}': {background_value:.2f} counts")
    #
    #         for label, df in spectra.items():
    #
    #             df["Intensity_counts"] -= background_value
    #             df["Intensity_counts"] = df["Intensity_counts"].clip(lower=0)
    #
    #     else:
    #
    #         print(f"\nWarning: No data in 870–900 nm for P0 in dataset '{file_path.parent.name}' — skipping background subtraction.")

    return spectra_dict