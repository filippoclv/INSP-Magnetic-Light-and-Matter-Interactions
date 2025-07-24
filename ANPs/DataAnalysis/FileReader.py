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

def all_spectra_dataframe_dict(folder_path, background_subtraction_range=None):

    folder = Path(folder_path)

    power_info_file = folder / "SetInfoPowerCurve.txt"
    power_info = pd.read_csv(power_info_file, sep="\t")
    power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

    spectra_dict = {}

    files = sorted(folder.glob("P*.txt"), key=lambda f: int(re.search(r"P(\d+)", f.name).group(1)))

    for file_path in files:

        data = read_spectrum_txt_to_dataframe(file_path, power_map)
        spectra_dict[data.attrs["Power_label"]] = data

    if background_subtraction_range is not None:

        first_spectrum = spectra_dict.get("P0")

        if first_spectrum is not None:

            bg_min, bg_max = background_subtraction_range

            background_region = first_spectrum[(first_spectrum["Wavelength_nm"] >= bg_min) &
                                               (first_spectrum["Wavelength_nm"] <= bg_max)]

            if not background_region.empty:

                background_mean = background_region["Intensity_counts"].mean()
                #print(f"\nBackground counts (P0 average in {bg_min}–{bg_max} nm) in dataset '{file_path.parent.name}': {background_mean:.2f} counts")

                for label, data in spectra_dict.items():

                    data["Intensity_counts"] -= background_mean
                    data["Intensity_counts"] = data["Intensity_counts"].clip(lower=0)

            else:

                print(f"\nWarning: No data in {bg_min}–{bg_max} nm for P0 in dataset '{file_path.parent.name}', skipping background subtraction.")
        else:

            print(f"\nWarning: No P0 spectrum found in dataset '{file_path.parent.name}', skipping background subtraction.")

    return spectra_dict

def read_spectrum_txt_to_dataframe_nearfield_heights(spectrum_path, height_map=None):

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

    if height_map is not None:

        height_label_extracted = re.search(r"Z(\d+)", spectrum_path.name)

        if height_label_extracted:

            height_label = height_label_extracted.group(1)
            height_index = int(height_label)

            spectrum.attrs["Height_label"] = f"Z{height_label}"
            spectrum.attrs["Height_mV"] = height_map.get(height_index)

    return spectrum


def all_spectra_dataframe_dict_nearfield_heights(folder_path, reference_background_subtraction_range=None):
    folder = Path(folder_path)

    height_info_file = folder / "SetInfoScanHeight.txt"
    height_info = pd.read_csv(height_info_file, sep="\t")
    height_map = dict(zip(height_info["Zindex"], height_info["Height"]))

    spectra_dict = {}

    files = sorted(folder.glob("Z*.txt"), key=lambda f: int(re.search(r"Z(\d+)", f.name).group(1)))

    for file_path in files:
        data = read_spectrum_txt_to_dataframe_nearfield_heights(file_path, height_map)
        spectra_dict[data.attrs["Height_label"]] = data

    reference_path = folder / "ref.txt"

    if reference_path.exists():

        reference_spectrum = read_spectrum_txt_to_dataframe_nearfield_heights(reference_path)

        if reference_background_subtraction_range is not None:

            bg_min, bg_max = reference_background_subtraction_range

            background_region = reference_spectrum[(reference_spectrum["Wavelength_nm"] >= bg_min) &
                                                   (reference_spectrum["Wavelength_nm"] <= bg_max)]

            if not background_region.empty:

                background_mean = background_region["Intensity_counts"].mean()

                reference_spectrum["Intensity_counts"] -= background_mean
                reference_spectrum["Intensity_counts"] = reference_spectrum["Intensity_counts"].clip(lower=0)

                for label, data in spectra_dict.items():
                    data["Intensity_counts"] -= background_mean
                    data["Intensity_counts"] = data["Intensity_counts"].clip(lower=0)

            else:

                print(f"\nWarning: No data in {bg_min}–{bg_max} nm for reference in dataset '{folder.name}', skipping background subtraction.")

        spectra_dict["Reference"] = reference_spectrum

    return spectra_dict