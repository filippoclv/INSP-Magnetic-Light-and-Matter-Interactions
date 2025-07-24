# import json
# from FileReader import *
# from Plotter import *
# from Analyzer import *
# from DataAnalysisNF import *
#
# with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250722\scanZ_metadata.json", "r") as scan_height:
#
#     scan_height_datasets = json.load(scan_height)
#
# selected_dataset = scan_height_datasets[5]
# all_spectra_dict = read_all_spectraNF(selected_dataset["folder"])
#
# reference_spectrum = read_spectrum_txt_to_dataframe(Path(selected_dataset["folder"]) / "ref.txt")
# background_region = reference_spectrum[(reference_spectrum["Wavelength_nm"] >= 843) &
#                                        (reference_spectrum["Wavelength_nm"] <= 844)]
#
# background_mean = background_region["Intensity_counts"].mean()
# reference_spectrum["Intensity_counts"] -= background_mean
# reference_spectrum["Intensity_counts"] = reference_spectrum["Intensity_counts"].clip(lower=0)
#
# plot_spectra_heights(all_spectra_dict,
#                      integration_time=selected_dataset["integration_time"],
#                      data=selected_dataset)
#
# whitelight_df = read_spectrum_txt_to_dataframe(Path(selected_dataset["folder"]).parent / "whitelightref.txt")
# plot_single_spectrum(whitelight_df)
#
# plot_single_spectrum(reference_spectrum, title="Reference spectrum")
#
# heights, wl_bins, intensity_map = integral_map_different_heights(spectra_dict=all_spectra_dict,
#                                                                  integration_time=selected_dataset["integration_time"],
#                                                                  wl_start=759,
#                                                                  wl_stop=844,
#                                                                  ref_df=reference_spectrum)
#
# plt.figure(figsize=(12, 7))
# pcm = plt.pcolormesh(wl_bins,
#                      heights,
#                      intensity_map,
#                      shading='auto',
#                      cmap='jet',
#                      vmin=1,
#                      vmax=1.5)
#
# cbar = plt.colorbar(pcm)
# cbar.set_label("$L_A / L_0$", fontsize=16)
# cbar.ax.tick_params(labelsize=14)
# plt.xlabel("Wavelength [nm]", fontsize=16)
# plt.ylabel("Height (SensZ) [mV]", fontsize=16)
# plt.title("2D map: integrated counts per 1 nm bin", fontsize=18, pad=15)
# plt.xticks(fontsize=14)
# plt.yticks(fontsize=14)
# plt.grid(False)
# plt.tight_layout()
# plt.show()

import json
from pathlib import Path
from FileReader import *
from PlotterScanHeight import *
from Analyzer import *

with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250722\scanZ_metadata.json", "r") as scan_height:

    scan_height_datasets = json.load(scan_height)

reference_background_subtraction_range = (875, 900)
reference_background_subtraction_range_narrower_grating = (843, 844)
reference_background_subtraction_range = reference_background_subtraction_range_narrower_grating
int_start = 770
int_end = 835

selected_dataset = scan_height_datasets[5]
all_spectra_dict = all_spectra_dataframe_dict_nearfield_heights(selected_dataset["folder"], reference_background_subtraction_range=reference_background_subtraction_range)

# white_light_spectrum_path = Path(selected_dataset["folder"]).parent / "whitelightref.txt"

# if white_light_spectrum_path.exists():

#     white_light_spectrum_dataframe = read_spectrum_txt_to_dataframe_nearfield_heights(white_light_spectrum_path)
#     plot_single_spectrum(white_light_spectrum_dataframe, title="White light spectrum")

reference_spectrum = all_spectra_dict.get("Reference")

# if reference_spectrum is not None:

#     plot_single_spectrum(reference_spectrum, title="Reference spectrum")

plot_all_spectra_nearfield_heights(all_spectra_dict,
                                   integration_time=selected_dataset["integration_time"],
                                   data_label=selected_dataset,
                                   integration_range=(int_start, int_end))

plot_all_spectra_nearfield_heights_normalized(all_spectra_dict,
                                              integration_time=selected_dataset["integration_time"],
                                              data_label=selected_dataset)

heights, wl_bins, intensity_map = integral_map_different_heights(all_spectra_dict,
                                                                 integration_time=selected_dataset["integration_time"],
                                                                 wl_start=759,
                                                                 wl_stop=844)

plot_integral_map_nearfield_heights(heights, wl_bins, intensity_map)