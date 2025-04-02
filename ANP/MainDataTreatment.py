import pandas as pd
from DataAnalysis import *

# Write data folder path and power info file
data_folder = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144019"

power_info_file = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144019\SetInfoPowerCurve.txt"
power_info = pd.read_csv(power_info_file, sep="\t")
power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

#Specific parameters of this measurement!
integration_time = 0.8 # Integration time in s
ratio_start = 0.0005
ratio_stop = 0.09

all_spectra = read_all_spectra(data_folder)

#file_label = "P5" # Choose which spectrum to display
#print(f"\nSpectrum ({file_label}):")
#display(all_spectra[file_label])

plot_spectra_with_zoom(all_spectra)

results_df = integrate_peak(all_spectra, wl_min=755, wl_max=860)
plot_integrated_intensity_vs_power(results_df, wl_min=755, wl_max=860)