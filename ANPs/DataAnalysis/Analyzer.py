import pandas as pd
import numpy as np

def integrate_single_spectrum(spectrum_dataframe, wl_min, wl_max, integration_time, power=None):

    filtered_dataframe = spectrum_dataframe[(spectrum_dataframe["Wavelength_nm"] >= wl_min) &
                                            (spectrum_dataframe["Wavelength_nm"] <= wl_max)]

    integrated_counts = np.trapz(filtered_dataframe["Intensity_counts"], filtered_dataframe["Wavelength_nm"])
    luminescence = integrated_counts / integration_time

    power_str = f" at power {power} W" if power is not None else ""
    print(f"Luminescence within {wl_min}-{wl_max} nm{power_str}: {luminescence:.2f} counts/s")

def integrate_all_spectra(spectra_dict, wl_min, wl_max, integration_time):

    results = []

    for data in spectra_dict.items():

        power = data.attrs["Power_W"]
        filtered_dataframe = data[(data["Wavelength_nm"] >= wl_min) & (data["Wavelength_nm"] <= wl_max)]

        integrated_counts = np.trapz(filtered_dataframe["Intensity_counts"], filtered_dataframe["Wavelength_nm"])
        luminescence = integrated_counts / integration_time

        results.append((power, luminescence))

    pd.DataFrame(results, columns=["Power_W", "Luminescence_counts/s"])

    return powercurve_dataset