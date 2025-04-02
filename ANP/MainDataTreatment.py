import pandas as pd
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pathlib import Path
import re
from DataAnalysis import read_data
from DataAnalysis import read_all_spectra
from DataAnalysis import plot_spectra
from DataAnalysis import print_power_values
from DataAnalysis import plot_spectra_with_zoom


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