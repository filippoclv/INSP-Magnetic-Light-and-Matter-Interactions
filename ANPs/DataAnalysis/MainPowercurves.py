from FileReader import *
from Plotter import *
from Analyzer import *
from DataAnalysis import *
from DataAnalysisNF import *
import warnings
import json

warnings.simplefilter("ignore", np.RankWarning)
plt.close("all")

with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\powercurves_metadata.json", "r") as powercurves:

    powercurves_datasets = json.load(powercurves)

background_subtraction_range = (875, 900)
int_start = 770
int_end = 835

selected_dataset = powercurves_datasets[1]
all_spectra_dict = all_spectra_dataframe_dict(selected_dataset["folder"],
                                              background_subtraction_range=background_subtraction_range)

# plot_all_spectra(all_spectra_dict,
#                  integration_time=selected_dataset["integration_time"],
#                  ratio_start=selected_dataset["ratio_start"],
#                  ratio_stop=selected_dataset["ratio_stop"],
#                  data_label=selected_dataset,
#                  integration_range=(int_start, int_end)
#                 )

plot_all_spectra_with_zoom(all_spectra_dict,
                           integration_time=selected_dataset["integration_time"],
                           ratio_start=selected_dataset["ratio_start"],
                           ratio_stop=selected_dataset["ratio_stop"],
                           data_label=selected_dataset,
                           zoom_wl_min=630,
                           zoom_wl_max=760,
                           integration_range=(int_start, int_end)
                          )

powercurve = integrate_all_spectra(all_spectra_dict, wl_min=int_start, wl_max=int_end, integration_time=selected_dataset["integration_time"])
plot_powercurve(powercurve, selected_dataset, wl_min=int_start, wl_max=int_end)

plot_all_powercurves_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end)

derivative_powercurve, s_value, s_power = calculate_single_derivative(powercurve)
plot_single_derivative_powercurve(derivative_powercurve, selected_dataset, wl_min=int_start, wl_max=int_end)

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

# with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\scanZ_metadata.json", "r") as NF_spectra_scanZ:
#
#     NF_spectra_scanZ_datasets = json.load(NF_spectra_scanZ)
#
# selected_dataset = NF_spectra_scanZ_datasets[-1]
# all_spectra_dict = read_all_spectraNF(selected_dataset["folder"])
# ref_df = read_spectrum_txt_to_dataframe(Path(selected_dataset["folder"]) / "ref.txt")
# background_region = ref_df[(ref_df["Wavelength_nm"] >= 843) & (ref_df["Wavelength_nm"] <= 844)]
# background_mean = background_region["Intensity_counts"].mean()
# ref_df["Intensity_counts"] -= background_mean
# ref_df["Intensity_counts"] = ref_df["Intensity_counts"].clip(lower=0)
#
# print(all_spectra_dict)
#
# plot_spectra_heights(all_spectra_dict, integration_time=selected_dataset["integration_time"], data=selected_dataset, fig=None, ax=None)
# plt.show()
#
# plot_single_spectrum(ref_df)
#
# heights, wl_bins, intensity_map = integral_map_different_heights(
#     spectra_dict=all_spectra_dict,
#     integration_time=selected_dataset["integration_time"],
#     wl_start=759,
#     wl_stop=844,
#     ref_df=ref_df
# )
#
# plt.figure(figsize=(12, 7))
# pcm = plt.pcolormesh(
#     wl_bins,
#     heights,
#     intensity_map,
#     shading='auto',
#     cmap='jet',
#     vmin=1,  # Minimum value for color mapping (e.g., for ratios)
#     vmax=1.5   # Maximum value
# )
#
# # Add colorbar with extensions for values outside vmin/vmax
# cbar = plt.colorbar(pcm, extend='both')
# cbar.set_label("$L_A / L_0$", fontsize=16)
# cbar.ax.tick_params(labelsize=14)
#
# # Axis labels
# plt.xlabel("Wavelength [nm]", fontsize=16)
# plt.ylabel("Height (SensZ) [mV]", fontsize=16)
#
# # Title
# plt.title("2D map: integrated counts per 1 nm bin", fontsize=18, pad=15)
#
# # Ticks font size
# plt.xticks(fontsize=14)
# plt.yticks(fontsize=14)
#
# plt.grid(False)
# plt.tight_layout()
# plt.show()

# NF analysis:

# selected_data = power_curvers_datasets[-1]
# all_spectra = read_all_spectraNF(selected_data["folder"])
#
# plot_spectra_heights(all_spectra, integration_time=selected_data["integration_time"], data=selected_data, fig=None, ax=None)
# plt.show()
#
# plot_spectra_heights_norm(all_spectra, integration_time=selected_data["integration_time"], data=selected_data, fig=None, ax=None)
# plt.show()
#
# heights, wl_bins, intensity_map = integral_map_different_heights(all_spectra, integration_time=2, wl_start=760, wl_stop=840)
# plt.figure(figsize=(12, 7))  # Slightly larger figure for better spacing
# pcm = plt.pcolormesh(
#     wl_bins,
#     heights,
#     intensity_map,
#     shading='auto',
#     cmap='jet'
# )
#
# # Axis labels
# plt.xlabel("Wavelength [nm]", fontsize=16)
# plt.ylabel("Height (SensZ) [mV]", fontsize=16)
#
# # Title
# plt.title("2D map: integrated counts per 1 nm bin", fontsize=18, pad=15)
#
# # Ticks font size
# plt.xticks(fontsize=14)
# plt.yticks(fontsize=14)
#
# # Add colorbar with label
# cbar = plt.colorbar(pcm)
# cbar.set_label("Luminescence [counts/s]", fontsize=16)
# cbar.ax.tick_params(labelsize=14)
#
# plt.grid(False)
# plt.tight_layout()
# plt.show()
#
# #plot_all_spectra_superimposed(datasets)
#
#
#
# # Attempt to plot luminescence enhancements (this is done to an emission experiment, it is more relevant to an excitation experiment):
#
# # Define integration range
# wl_min = 760
# wl_max = 840
# integration_time = selected_data["integration_time"]
#
# # Integrate each spectrum over the wavelength range
# lum_df = integrate_peakNF(all_spectra, wl_min=wl_min, wl_max=wl_max, integration_time=integration_time)
#
# # Sort the DataFrame by height in descending order
# lum_df = lum_df.sort_values("Height_mV", ascending=False)
#
# # Plot Luminescence vs Height
# plt.figure(figsize=(9, 6))
# plt.plot(
#    lum_df["Height_mV"],
#          lum_df["Luminescence_counts"],
#          marker='o',
#          markersize=8,
#          markerfacecolor='white',
#          markeredgewidth=2,
#          linestyle='-',
#          linewidth=2,
#          color='tab:blue'
#         )
#
# plt.xlabel("Height (SensZ) [mV]", fontsize=16)
# plt.ylabel("Luminescence [counts]", fontsize=16)
# plt.title(f"Luminescence vs height", fontsize=18)
# plt.xticks(fontsize=14)
# plt.yticks(fontsize=14)
# plt.grid(True, linestyle="--", alpha=0.3)
#
# # Optional: reverse x-axis if height decreases upward
# plt.gca().invert_xaxis()
#
# plt.tight_layout()
# plt.show()