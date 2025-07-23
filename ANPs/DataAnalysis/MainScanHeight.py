import warnings
import json
from FileReader import *
from Plotter import *
from Analyzer import *
from DataAnalysis import *
from DataAnalysisNF import *

warnings.simplefilter("ignore", np.RankWarning)
plt.close("all")

with open(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250722\scanZ_metadata.json", "r") as NF_spectra_scanZ:

    NF_spectra_scanZ_datasets = json.load(NF_spectra_scanZ)

selected_dataset = NF_spectra_scanZ_datasets[5]
all_spectra_dict = read_all_spectraNF(selected_dataset["folder"])

ref_df = read_spectrum_txt_to_dataframe(Path(selected_dataset["folder"]) / "ref.txt")
background_region = ref_df[(ref_df["Wavelength_nm"] >= 843) & (ref_df["Wavelength_nm"] <= 844)]
background_mean = background_region["Intensity_counts"].mean()
ref_df["Intensity_counts"] -= background_mean
ref_df["Intensity_counts"] = ref_df["Intensity_counts"].clip(lower=0)


plot_spectra_heights(all_spectra_dict, integration_time=selected_dataset["integration_time"], data=selected_dataset, fig=None, ax=None)

whitelight_df = read_spectrum_txt_to_dataframe(Path(selected_dataset["folder"]).parent / "whitelightref.txt")
plot_single_spectrum(whitelight_df)

plot_single_spectrum(ref_df, title="Reference spectrum")

heights, wl_bins, intensity_map = integral_map_different_heights(spectra_dict=all_spectra_dict,
                                                                 integration_time=selected_dataset["integration_time"],
                                                                 wl_start=759,
                                                                 wl_stop=844,
                                                                 ref_df=ref_df)

plt.figure(figsize=(12, 7))
pcm = plt.pcolormesh(wl_bins,
                     heights,
                     intensity_map,
                     shading='auto',
                     cmap='jet',
                     vmin=1,
                     vmax=1.5)

cbar = plt.colorbar(pcm)
cbar.set_label("$L_A / L_0$", fontsize=16)
cbar.ax.tick_params(labelsize=14)
plt.xlabel("Wavelength [nm]", fontsize=16)
plt.ylabel("Height (SensZ) [mV]", fontsize=16)
plt.title("2D map: integrated counts per 1 nm bin", fontsize=18, pad=15)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.grid(False)
plt.tight_layout()
plt.show()