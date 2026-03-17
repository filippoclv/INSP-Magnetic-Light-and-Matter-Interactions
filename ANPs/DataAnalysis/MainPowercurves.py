import json
from FileReader import *
from Plotter import *
from Analyzer import *

with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\20260317\powercurves_metadata.json", "r") as powercurves:

    powercurves_datasets = json.load(powercurves)

background_subtraction_range = (875, 900)
background_subtraction_range_narrower_grating = (842, 844)
background_subtraction_range = background_subtraction_range_narrower_grating
int_start = 770
int_end = 835
degree = 5

selected_dataset = powercurves_datasets[0]

# all_spectra_dict = all_spectra_dataframe_dict(selected_dataset["folder"])
all_spectra_dict = all_spectra_dataframe_dict(selected_dataset["folder"],
                                              background_subtraction_range=background_subtraction_range)

plot_all_spectra(all_spectra_dict,
                 integration_time=selected_dataset["integration_time"],
                 ratio_start=selected_dataset["ratio_start"],
                 ratio_stop=selected_dataset["ratio_stop"],
                 data_label=selected_dataset,
                 integration_range=(int_start, int_end))

# plot_all_spectra_with_zoom(all_spectra_dict,
#                            integration_time=selected_dataset["integration_time"],
#                            ratio_start=selected_dataset["ratio_start"],
#                            ratio_stop=selected_dataset["ratio_stop"],
#                            data_label=selected_dataset,
#                            zoom_wl_min=630,
#                            zoom_wl_max=760,
#                            integration_range=(int_start, int_end))

powercurve = integrate_all_spectra(all_spectra_dict, wl_min=int_start, wl_max=int_end, integration_time=selected_dataset["integration_time"])
# plot_powercurve(powercurve, selected_dataset, wl_min=int_start, wl_max=int_end)

# plot_all_powercurves_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end)

# derivative_powercurve, s_value, s_power = calculate_single_derivative(powercurve)
# plot_single_derivative_powercurve(derivative_powercurve, selected_dataset, wl_min=int_start, wl_max=int_end)

plot_single_powercurve_with_s(powercurve, selected_dataset, wl_min=int_start, wl_max=int_end)

# plot_all_derivatives_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end)

# plot_all_powercurves_with_s_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end)

powercurve, polynomial_fit, log_power_fine_points, power_fine_points, luminescence_fine_points = fit_powercurve(powercurve, degree=degree)
powercurve, s_value, s_power = calculate_derivative_of_fit(powercurve, polynomial_fit, log_power_fine_points, degree=degree)

# plot_single_powercurve_fit(powercurve, polynomial_fit, log_power_fine_points, selected_dataset, int_start, int_end, degree=degree)

derivative_fine_points = np.polyder(polynomial_fit)(log_power_fine_points)
# plot_single_derivative_of_fit(powercurve, log_power_fine_points, derivative_fine_points, s_value, s_power, selected_dataset, int_start, int_end, degree=degree)

plot_single_powercurve_with_s_fitted(powercurve, polynomial_fit, log_power_fine_points, s_value, s_power, selected_dataset, int_start, int_end, degree=degree)

# plot_all_powercurves_fitted_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end, degree=degree)
# plot_all_derivatives_of_fits_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end, degree=degree)

# plot_all_fitted_powercurves_with_s_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end, degree=degree)

# plot_powercurve_forward_and_backward_sweep(folder_path=r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410125446",
#                                            int_start=770,
#                                            int_end=835,
#                                            integration_time=1,
#                                            ratio_start=0.0001,
#                                            ratio_stop=0.7,
#                                            background_subtraction_range=background_subtraction_range,
#                                            title_note="non near-field, TIR")

# plot_powercurve_forward_and_backward_sweep(folder_path=r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410132709",
#                                            int_start=770,
#                                            int_end=835,
#                                            integration_time=1,
#                                            ratio_start=0.0001,
#                                            ratio_stop=0.7,
#                                            background_subtraction_range=background_subtraction_range,
#                                            title_note="non near-field, normal incidence")

def plot_txt_powercurve_with_s(filepath, data_label, wl_min, wl_max):
    # Read the text file
    df = pd.read_csv(filepath, sep="\t")

    # Rename the columns so they perfectly match what Analyzer.py and Plotter.py expect
    df = df.rename(columns={
        "CurrentPower": "Power_W",
        "CountRates": "Luminescence_counts/s"
    })

    # Call your exact existing function (which internally calculates the derivative)
    plot_single_powercurve_with_s(df, data_label, wl_min, wl_max)

    df, polynomial_fit, log_power_fine_points, power_fine_points, luminescence_fine_points = fit_powercurve(df, degree=degree)
    df, s_value, s_power = calculate_derivative_of_fit(df, polynomial_fit, log_power_fine_points, degree=degree)

    # plot_single_powercurve_fit(df, polynomial_fit, log_power_fine_points, selected_dataset, int_start, int_end, degree=degree)

    derivative_fine_points = np.polyder(polynomial_fit)(log_power_fine_points)
    # plot_single_derivative_of_fit(df, log_power_fine_points, derivative_fine_points, s_value, s_power, selected_dataset, int_start, int_end, degree=degree)

    plot_single_powercurve_with_s_fitted(df, polynomial_fit, log_power_fine_points, s_value, s_power, selected_dataset, int_start, int_end, degree=degree)

# Create the metadata dictionary expected by Plotter.py
apd_data_label = {
    "label": "APD agglomerate",
    "integration_time": 1,      # From your txt header
    "ratio_start": 0.001,       # From your txt header
    "ratio_stop": 0.1           # From your txt header
}

# Call the function (update the path if necessary)
txt_filepath = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\20260317\20260317162933\SetInfoPowerCurve_APD.txt"
plot_txt_powercurve_with_s(txt_filepath, apd_data_label, wl_min=int_start, wl_max=int_end)

apd_data_label = {
    "label": "APD monolayer",
    "integration_time": 0.1,      # From your txt header
    "ratio_start": 0.001,       # From your txt header
    "ratio_stop": 0.1           # From your txt header
}


txt_filepath = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\20260317\20260317160929\SetInfoPowerCurve_APD.txt"
plot_txt_powercurve_with_s(txt_filepath, apd_data_label, wl_min=int_start, wl_max=int_end)

apd_data_label = {
    "label": "APD agglomerate",
    "integration_time": 1,      # From your txt header
    "ratio_start": 0.001,       # From your txt header
    "ratio_stop": 0.1           # From your txt header
}



txt_filepath = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\20260317\20260317163246\SetInfoPowerCurve_APD.txt"
plot_txt_powercurve_with_s(txt_filepath, apd_data_label, wl_min=int_start, wl_max=int_end)