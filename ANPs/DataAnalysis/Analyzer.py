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

    for label, data in spectra_dict.items():

        power = data.attrs["Power_W"]
        filtered_dataframe = data[(data["Wavelength_nm"] >= wl_min) & (data["Wavelength_nm"] <= wl_max)]

        if filtered_dataframe.empty:

            print(f"Warning: {label} has no data in range {wl_min}-{wl_max} nm")

            continue

        integrated_counts = np.trapz(filtered_dataframe["Intensity_counts"], filtered_dataframe["Wavelength_nm"])
        luminescence = integrated_counts / integration_time

        results.append((power, luminescence))

    powercurve_dataset = pd.DataFrame(results, columns=["Power_W", "Luminescence_counts/s"])

    return powercurve_dataset

def calculate_single_derivative(powercurve_dataset):

    power = powercurve_dataset["Power_W"].values
    luminescence = powercurve_dataset["Luminescence_counts/s"].values

    derivatives = np.gradient(np.log(luminescence), np.log(power))
    powercurve_dataset["Derivative_values"] = derivatives

    s_parameter_index = powercurve_dataset["Derivative_values"].idxmax()
    powercurve_dataset["Non-linearity s parameter"] = False
    powercurve_dataset.loc[s_parameter_index, "Non-linearity s parameter"] = True
    s_value = powercurve_dataset.loc[s_parameter_index, "Derivative_values"]
    s_power = powercurve_dataset.loc[s_parameter_index, "Power_W"]

    return powercurve_dataset, s_value, s_power