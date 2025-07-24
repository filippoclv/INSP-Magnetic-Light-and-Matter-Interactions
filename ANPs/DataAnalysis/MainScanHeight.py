import json
from pathlib import Path
from FileReader import *
from Plotter import *
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
                                   data_label=selected_dataset)

# plot_all_spectra_nearfield_heights_normalized(all_spectra_dict,
#                                               integration_time=selected_dataset["integration_time"],
#                                               data_label=selected_dataset)

heights, wl_bins, intensity_map = calculate_LDOS_map_different_heights(all_spectra_dict,
                                                                       integration_time=selected_dataset["integration_time"],
                                                                       wl_start=759,
                                                                       wl_stop=844,
                                                                       minimum_luminescence_threshold=7)

plot_LDOS_map(heights, wl_bins, intensity_map, cb_min=1, cb_max=1.5)