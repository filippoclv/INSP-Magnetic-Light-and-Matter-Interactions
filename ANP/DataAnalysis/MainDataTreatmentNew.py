import matplotlib.pyplot as plt

from DataAnalysis import *

plt.close("all")

# Each dictionary defines one dataset
datasets = [
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Refocusing_same_place_20250404\20250404143753",
        "integration_time": 2,
        "ratio_start": 0.0005,
        "ratio_stop": 0.2
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Refocusing_same_place_20250404\20250404144307",
        "integration_time": 2,
        "ratio_start": 0.0005,
        "ratio_stop": 0.2
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Refocusing_same_place_20250404\20250404144722",
        "integration_time": 2,
        "ratio_start": 0.0005,
        "ratio_stop": 0.2
    },
]

# For the specific spectra plot

selected_data = datasets[0]  # This is the first one

# Load power map
power_info_file = Path(selected_data["folder"]) / "SetInfoPowerCurve.txt"
power_info = pd.read_csv(power_info_file, sep="\t")
power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

# Read spectra and plot
all_spectra = read_all_spectra(selected_data["folder"])

# Integration range

int_start = 770
int_end = 835
'''
plot_spectra_with_zoom(
                       all_spectra,
                       integration_time=selected_data["integration_time"],
                       ratio_start=selected_data["ratio_start"],
                       ratio_stop=selected_data["ratio_stop"],
                       zoom_wl_min=630,
                       zoom_wl_max=760,
                       integration_range=(int_start, int_end)
                      )

# 630 - 760 nm range is good to zoom on the smaller peaks

plot_all_power_curves(datasets, int_start, int_end)

# The derivative method is just a simple slope calculation between two points
#derivative_df, s_value, s_power = calculate_derivative(results_df)
#print(f"s ≈ {s_value:.2f} at power {s_power:.8f} W")

#plot_derivative(derivative_results)

plot_all_derivatives(datasets, int_start, int_end)
'''
plot_all_power_curves_with_s(datasets, int_start, int_end)

check_all_fits(datasets, int_start=770, int_end=835, degree=100)

plot_all_derivatives_fit(datasets, int_start, int_end, degree=100)
