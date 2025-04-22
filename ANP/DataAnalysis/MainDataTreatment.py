from DataAnalysis import *
import warnings

warnings.simplefilter('ignore', np.RankWarning)

plt.close("all")

# Each dictionary defines one dataset (this is for standard, only forward power sweep)
datasets = [
#    {
#        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410124848",
#        "integration_time": 1,
#        "ratio_start": 0.0001,
#        "ratio_stop": 0.7,
#        "label": "TIR",
#        "power_shift_factor": 1.0, # 0.13 to superimpose
#        "luminescence_shift_factor": 1.0 # 0.05 to superimpose
#    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TestAutoRefined_20250417\20250417165039",
        "integration_time": 3,
        "ratio_start": 0.0001,
        "ratio_stop": 0.9,
        "label": "NO TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0
    },
#    {
#        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410135717",
#        "integration_time": 3,
#        "ratio_start": 0.00001,
#        "ratio_stop": 0.9,
#        "power_shift_factor": 1.0,
#        "luminescence_shift_factor": 1.0
#    },
]

datasets_back_and_forth = [
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410125446",
        "integration_time": 1,
        "ratio_start": 0.0001,
        "ratio_stop": 0.7,
        "label": "TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410132709",
        "integration_time": 1,
        "ratio_start": 0.0001,
        "ratio_stop": 0.7,
        "label": "NO TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0
    },
#    {
#        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410140605",
#        "integration_time": 3,
#        "ratio_start": 0.00001,
#        "ratio_stop": 0.9,
#        "power_shift_factor": 1.0,
#        "luminescence_shift_factor": 1.0
#    },
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

#plot_spectra_with_zoom(all_spectra,
#                       integration_time=selected_data["integration_time"],
#                       ratio_start=selected_data["ratio_start"],
#                       ratio_stop=selected_data["ratio_stop"],
#                       zoom_wl_min=630,
#                       zoom_wl_max=760,
#                       integration_range=(int_start, int_end)
#                      )

# 630 - 760 nm range is good to zoom on the smaller peaks

#plot_all_power_curves(datasets, int_start, int_end)

# The derivative method is just a simple slope calculation between two points
#derivative_df, s_value, s_power = calculate_derivative(results_df)
#print(f"s ≈ {s_value:.2f} at power {s_power:.8f} W")

#plot_derivative(derivative_results)

#plot_all_derivatives(datasets, int_start, int_end)

plot_all_power_curves_with_s(datasets, int_start, int_end)

# Degree of 100 gets a very smooth fit, but 10 seems good enough

#check_all_fits(datasets, int_start=770, int_end=835, degree=10)

#plot_all_derivatives_fit(datasets, int_start, int_end, degree=10)

#plot_power_curves_back_and_forth(folder=r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410125446",
#                                 int_start=770,
#                                 int_end=835,
#                                 integration_time=selected_data["integration_time"],
#                                 title_note="- TIR configuration"
#                                )

#plot_power_curves_back_and_forth(folder=r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410132709",
#                                 int_start=770,
#                                 int_end=835,
#                                 integration_time=selected_data["integration_time"],
#                                 title_note="- NO TIR configuration, same parameters"
#                                )

#plot_power_curves_back_and_forth(folder=r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410140605",
#                                 int_start=770,
#                                 int_end=835,
#                                 integration_time=selected_data["integration_time"],
#                                 title_note="- NO TIR configuration, different parameters"
#                                )