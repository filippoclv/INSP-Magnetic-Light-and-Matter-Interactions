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


def fit_powercurve(powercurve_dataset, degree=10, fine_points=500):

    power = powercurve_dataset["Power_W"].values
    luminescence = powercurve_dataset["Luminescence_counts/s"].values

    positive_luminescence_mask = luminescence > 0

    if np.sum(positive_luminescence_mask) < degree + 1:

        raise ValueError("Not enough points for fitting.")

    log_power = np.log(power[positive_luminescence_mask])
    log_luminescence = np.log(luminescence[positive_luminescence_mask])

    fit_coefficients = np.polyfit(log_power, log_luminescence, deg=degree)
    polynomial_fit = np.poly1d(fit_coefficients)

    log_luminescence_original_values = polynomial_fit(np.log(power))
    log_luminescence_original_values = np.clip(log_luminescence_original_values, None, 700)
    powercurve_dataset["Fitted_luminescence_counts/s"] = np.exp(log_luminescence_original_values)

    log_power_fine_points = np.linspace(log_power.min(), log_power.max(), fine_points)
    power_fine_points = np.exp(log_power_fine_points)
    log_luminescence_fine_points = polynomial_fit(log_power_fine_points)
    log_luminescence_fine_points = np.clip(log_luminescence_fine_points, None, 700)
    luminescence_fine_points = np.exp(log_luminescence_fine_points)

    return powercurve_dataset, polynomial_fit, log_power_fine_points, power_fine_points, luminescence_fine_points

def calculate_derivative_of_fit(powercurve_dataset, polynomial_fit, log_power_fine_points, degree=10):

    polynomial_fit_derivative = np.polyder(polynomial_fit)
    derivative_fine_points = polynomial_fit_derivative(log_power_fine_points)

    log_power_original_values = np.log(powercurve_dataset["Power_W"].values)
    derivative_original_values = np.interp(log_power_original_values, log_power_fine_points, derivative_fine_points)
    powercurve_dataset["Derivative_values"] = derivative_original_values

    s_index = np.argmax(derivative_fine_points)
    s_value = derivative_fine_points[s_index]
    s_power = np.exp(log_power_fine_points[s_index])

    closest_index = np.argmin(np.abs(powercurve_dataset["Power_W"] - s_power))
    powercurve_dataset["Non-linearity s parameter"] = False
    powercurve_dataset.loc[closest_index, "Non-linearity s parameter"] = True

    return powercurve_dataset, s_value, s_power