import json
from FileReader import *
from Plotter import *
from Analyzer import *

spectrum = read_spectrum_txt_to_dataframe(r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\APD\20260217\spectra1s40P.txt")

bg_min, bg_max = 875, 900
bg_region = spectrum[(spectrum["Wavelength_nm"] >= bg_min) & (spectrum["Wavelength_nm"] <= bg_max)]

if not bg_region.empty:

    bg_mean = bg_region["Intensity_counts"].mean()
    print(f"Calculated background mean ({bg_min}-{bg_max} nm): {bg_mean:.2f} counts")

    spectrum["Intensity_counts"] = spectrum["Intensity_counts"] - bg_mean
    spectrum["Intensity_counts"] = spectrum["Intensity_counts"].clip(lower=0)

else:

    print(f"Warning: no data found in background range {bg_min}-{bg_max} nm. Skipping subtraction.")

plot_single_spectrum(spectrum, "Agglomerate spectrum, 40% power, 1 s integration time, background subtracted")