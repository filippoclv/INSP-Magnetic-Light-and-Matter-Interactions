import warnings
import json
from FileReader import *
from Plotter import *
from Analyzer import *
from DataAnalysis import *
from DataAnalysisNF import *

warnings.simplefilter("ignore", np.RankWarning)
plt.close("all")

with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250623\powercurves_metadata.json", "r") as powercurves:

    powercurves_datasets = json.load(powercurves)

background_subtraction_range = (875, 900)
background_subtraction_range_narrower_grating = (842, 844)
int_start = 770
int_end = 835

selected_dataset = powercurves_datasets[-2]

# all_spectra_dict = all_spectra_dataframe_dict(selected_dataset["folder"])
# all_spectra_dict = all_spectra_dataframe_dict(selected_dataset["folder"],
#                                               background_subtraction_range=background_subtraction_range_narrower_grating)
all_spectra_dict = all_spectra_dataframe_dict(selected_dataset["folder"],
                                              background_subtraction_range=background_subtraction_range)

plot_all_spectra(all_spectra_dict,
                 integration_time=selected_dataset["integration_time"],
                 ratio_start=selected_dataset["ratio_start"],
                 ratio_stop=selected_dataset["ratio_stop"],
                 data_label=selected_dataset,
                 integration_range=(int_start, int_end)
                )

# plot_all_spectra_with_zoom(all_spectra_dict,
#                            integration_time=selected_dataset["integration_time"],
#                            ratio_start=selected_dataset["ratio_start"],
#                            ratio_stop=selected_dataset["ratio_stop"],
#                            data_label=selected_dataset,
#                            zoom_wl_min=630,
#                            zoom_wl_max=760,
#                            integration_range=(int_start, int_end)
#                           )

powercurve = integrate_all_spectra(all_spectra_dict, wl_min=int_start, wl_max=int_end, integration_time=selected_dataset["integration_time"])
plot_powercurve(powercurve, selected_dataset, wl_min=int_start, wl_max=int_end)

# plot_all_powercurves_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end)

derivative_powercurve, s_value, s_power = calculate_single_derivative(powercurve)
plot_single_derivative_powercurve(derivative_powercurve, selected_dataset, wl_min=int_start, wl_max=int_end)

# plot_all_derivatives_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end)

# plot_all_powercurves_with_s_from_json(powercurves_datasets, background_subtraction_range, int_start, int_end)



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



# with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250722\scanZ_metadata.json", "r") as NF_spectra_scanZ:
#
#     NF_spectra_scanZ_datasets = json.load(NF_spectra_scanZ)
#
# selected_dataset = NF_spectra_scanZ_datasets[5]
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
# whitelight_df = read_spectrum_txt_to_dataframe(Path(selected_dataset["folder"]).parent / "whitelightref.txt")
# plot_single_spectrum(whitelight_df)
#
# plot_single_spectrum(ref_df, title="Reference spectrum")
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
# cbar = plt.colorbar(pcm)
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