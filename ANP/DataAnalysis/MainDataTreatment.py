from DataAnalysis import *
from DataAnalysisNF import *
import warnings

warnings.simplefilter('ignore', np.RankWarning)

plt.close("all")

# Each dictionary element defines one dataset (this is for a standard, only forward power sweep)

datasets = [
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623101016",
        "integration_time": 2,
        "ratio_start": 0.001,
        "ratio_stop": 0.6,
        "label": "NO TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0,
        "spectrometer_hole_diameter": 0.05  # In mm
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623101700",
        "integration_time": 3,
        "ratio_start": 0.001,
        "ratio_stop": 0.9,
        "label": "NO TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0,
        "spectrometer_hole_diameter": 0.05  # In mm
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623113319",
        "integration_time": 3,
        "ratio_start": 0.001,
        "ratio_stop": 0.09,
        "label": "NO TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0,
        "spectrometer_hole_diameter": 0.05  # In mm
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623122015",
        "integration_time": 5,
        "ratio_start": 0.001,
        "ratio_stop": 0.09,
        "label": "TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0,
        "spectrometer_hole_diameter": 0.05  # In mm
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623131010",
        "integration_time": 4,
        "ratio_start": 0.05,
        "ratio_stop": 0.9,
        "label": "TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0,
        "spectrometer_hole_diameter": 0.05  # In mm
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623131703",
        "integration_time": 2,
        "ratio_start": 0.01,
        "ratio_stop": 0.99,
        "label": "TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0,
        "spectrometer_hole_diameter": 0.05  # In mm
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623133235",
        "integration_time": 1,
        "ratio_start": 0.05,
        "ratio_stop": 0.99,
        "label": "TIR",
        "power_shift_factor": 1.0,
        "luminescence_shift_factor": 1.0,
        "spectrometer_hole_diameter": 0.05  # In mm
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\20250623154507",
        "integration_time": 2,
        "power_percentage": 60,
        "stepZ": -80, # In mV
        "label": "TIR",
    },
    # {
    #     "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250618\20250618122307",
    #     "integration_time": 3,
    #     "ratio_start": 0.0003,
    #     "ratio_stop": 0.003,
    #     "label": "NO TIR",
    #     "Z": -50,  # In mV
    #     "power_shift_factor": 1.0,
    #     "luminescence_shift_factor": 1.0,
    #     "spectrometer_hole_diameter": 0.05  # In mm
    # },
]

# datasets_back_and_forth = [
#     {
#         "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410125446",
#         "integration_time": 1,
#         "ratio_start": 0.0001,
#         "ratio_stop": 0.7,
#         "label": "TIR",
#         "power_shift_factor": 1.0,
#         "luminescence_shift_factor": 1.0
#     },
#     {
#         "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410132709",
#         "integration_time": 1,
#         "ratio_start": 0.0001,
#         "ratio_stop": 0.7,
#         "label": "NO TIR",
#         "power_shift_factor": 1.0,
#         "luminescence_shift_factor": 1.0
#     },
# ]

# int_start = 770
# int_end = 835

# For a specific spectra plot

# selected_data = datasets[-1]
# all_spectra = read_all_spectra(selected_data["folder"])

# Load power map
# Check its use
# power_info_file = Path(selected_data["folder"]) / "SetInfoPowerCurve.txt"
# power_info = pd.read_csv(power_info_file, sep="\t")
# power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

# Integration range, just for visualizing

# plot_spectra_with_zoom(all_spectra,
#                       integration_time=selected_data["integration_time"],
#                       ratio_start=selected_data["ratio_start"],
#                       ratio_stop=selected_data["ratio_stop"],
#                       data=selected_data,
#                       zoom_wl_min=630,
#                       zoom_wl_max=760,
#                       integration_range=(int_start, int_end)
#                      )

# plot_spectra_no_zoom(all_spectra,
#                      integration_time=selected_data["integration_time"],
#                      ratio_start=selected_data["ratio_start"],
#                      ratio_stop=selected_data["ratio_stop"],
#                      data=selected_data,
#                      integration_range=(int_start, int_end)
#                     )

# 630 - 760 nm range is good to zoom on the smaller peaks

# Multiple dataset's spectra:

# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 12))
#
# selected_data = datasets[0] # First dataset
# power_info_file = Path(selected_data["folder"]) / "SetInfoPowerCurve.txt"
# power_info = pd.read_csv(power_info_file, sep="\t")
# power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))
# all_spectra = read_all_spectra(selected_data["folder"])
#
# plot_spectra_with_zoom(all_spectra,
#                       integration_time=selected_data["integration_time"],
#                       ratio_start=selected_data["ratio_start"],
#                       ratio_stop=selected_data["ratio_stop"],
#                       data=selected_data,
#                       zoom_wl_min=630,
#                       zoom_wl_max=760,
#                       integration_range=(int_start, int_end),
#                       fig=fig,
#                       ax=ax1)
#
# selected_data = datasets[1] # Second dataset
# power_info_file = Path(selected_data["folder"]) / "SetInfoPowerCurve.txt"
# power_info = pd.read_csv(power_info_file, sep="\t")
# power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))
# all_spectra = read_all_spectra(selected_data["folder"])
#
# plot_spectra_with_zoom(all_spectra,
#                       integration_time=selected_data["integration_time"],
#                       ratio_start=selected_data["ratio_start"],
#                       ratio_stop=selected_data["ratio_stop"],
#                       data=selected_data,
#                       zoom_wl_min=630,
#                       zoom_wl_max=760,
#                       integration_range=(int_start, int_end),
#                       fig=fig,
#                       ax=ax2)

# plot_all_power_curves(datasets, int_start, int_end) # Check this function

# The derivative method is just a simple slope calculation between two points

# selected_data = datasets[0]
# all_spectra = read_all_spectra(selected_data["folder"])

# results_df = integrate_peak(all_spectra, wl_min=755, wl_max=860, integration_time=integration_time)
# derivative_df, s_value, s_power = calculate_derivative(results_df)
# print(f"s ≈ {s_value:.2f} at power {s_power:.8f} W")
# plot_derivative(derivative_df)

# plot_all_derivatives(datasets, int_start, int_end)

# plot_all_power_curves_with_s(datasets, int_start, int_end)

# Fitting instead of a simple derivative:

# Degree of 100 gets a very smooth fit, but 10 seems good enough

# check_all_fits(datasets, int_start=770, int_end=835, degree=10) # Fitted powercurve
# plot_all_derivatives_fit(datasets, int_start, int_end, degree=10) # Fitted derivative

# Forward and backward sweep plotting:

# plot_power_curves_back_and_forth(folder=r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410125446",
#                                 int_start=770,
#                                 int_end=835,
#                                 integration_time=selected_data["integration_time"],
#                                 title_note="- TIR configuration"
#                                )
#
# plot_power_curves_back_and_forth(folder=r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\TIRvsNOTIR_20250410\20250410132709",
#                                 int_start=770,
#                                 int_end=835,
#                                 integration_time=selected_data["integration_time"],
#                                 title_note="- NO TIR configuration, same parameters"
#                                )

# Gaussian study, single ANP exporting:

#results_df = integrate_peak(all_spectra, wl_min=755, wl_max=860, integration_time=integration_time)
#single_anp = results_df.drop(columns=["Luminescence_counts"])
#display(single_anp)
#single_anp.to_csv("fake_single_anp.csv", index=True)

# Peak ratio study:

# fig, ax = plt.subplots(figsize=(12, 8))
#
# # Process first dataset (NO TIR)
# selected_data = datasets[0]
# all_spectra = read_all_spectra(selected_data["folder"])
# ratios_df_no_tir = analyze_peak_ratios(all_spectra,
#                                        peak1_range=(680, 720),
#                                        peak2_range=(780, 820)
#                                       )
#
# # Plot first dataset
# ax.plot(ratios_df_no_tir["Power_W"], ratios_df_no_tir["Peak_ratio"],
#         "o-", markerfacecolor="none",
#         color="teal", label="NO TIR, ratio max(780,820) / max(680,720)"
#        )
#
# # Process second dataset (TIR)
# selected_data = datasets[1]
# all_spectra = read_all_spectra(selected_data["folder"])
# ratios_df_tir = analyze_peak_ratios(all_spectra,
#                                     peak1_range=(680, 720),
#                                     peak2_range=(780, 820)
#                                    )
#
# # Plot second dataset
# ax.plot(ratios_df_tir["Power_W"], ratios_df_tir["Peak_ratio"],
#         "o-", markerfacecolor="none",
#         color="coral", label="TIR, ratio max(780,820) / max(680,720)"
#        )
#
# # Configure plot
# ax.set_xscale('log')
# #ax.set_yscale('log')
# ax.set_xlabel("Power [W]", fontsize=12)
# ax.set_ylabel("Peak ratio", fontsize=12)
# ax.set_title("Ratio of peak intensities vs power", fontsize=14)
# ax.grid(True, which='both', linestyle='--', alpha=0.3)
# ax.legend(fontsize=12)
#
# plt.tight_layout()
# plt.show()
#
# print("\nNO TIR data:")
# print(ratios_df_no_tir)
# print("\nTIR data:")
# print(ratios_df_tir)

# NF analysis:

selected_data = datasets[-1]
all_spectra = read_all_spectraNF(selected_data["folder"])

plot_spectra_heights(all_spectra, integration_time=selected_data["integration_time"], data=selected_data, fig=None, ax=None)
plt.show()