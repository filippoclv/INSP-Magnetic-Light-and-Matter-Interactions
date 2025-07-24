import pandas as pd
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from pathlib import Path
import re

def plot_all_power_curvesNF(datasets, int_start, int_end):

    fig, ax = plt.subplots(figsize=(14, 12), constrained_layout=True)

    # Use Z for color coding
    z_values = np.array([data.get("Z_mV", 0) for data in datasets])
    norm = plt.Normalize(vmin=-1000, vmax=0)
    cmap = plt.cm.jet
    colors = cmap(norm(z_values))

    for i, data in enumerate(datasets):

        folder = data["folder"]
        int_time = data["integration_time"]
        ratio_start = data["ratio_start"]
        ratio_stop = data["ratio_stop"]

        power_info_file = Path(folder) / "SetInfoPowerCurve.txt"
        power_info = pd.read_csv(power_info_file, sep="\t")
        power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

        all_spectra = read_all_spectra(folder)
        results_df = integrate_peak(all_spectra, int_start, int_end, integration_time=int_time)

        config_label = f"{data.get('label', ''):<6}"  # Empty if not present
        #label = f"{config_label} | Int. time: {int_time:.1f} s | R: {ratio_start:.4f}–{ratio_stop:.2f}"

        label = (
                 f"Int. time: {int_time:>1.2f} s | "
                 f"R: {ratio_start:>1.4f} – {ratio_stop:>1.3f} | "
                )

        ax.plot(
          results_df["Power_W"],
                results_df["Luminescence_counts"],
                marker="o",
                markersize=6,
                markerfacecolor="none",
                linestyle="-",
                linewidth=2,
                label=label,
                color=colors[i]
               )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(f"log-log scale: luminescence vs power\n({int_start}–{int_end} nm peak)", fontsize=14)
    ax.set_xlabel("Power [W]")
    ax.set_ylabel("Luminescence [counts]")
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    ax.legend(fontsize=10, loc="best", prop={"family": "DejaVu Sans Mono"})

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Z parameter [mV]", fontsize=12)

    plt.show()

def integrate_peakNF(spectra_dict, wl_min, wl_max, integration_time):

    results = []

    for label, df in spectra_dict.items():

        height = df.attrs["Height"]
        filtered_dataframe = df[(df["Wavelength_nm"] >= wl_min) & (df["Wavelength_nm"] <= wl_max)]

        if filtered_dataframe.empty:

            print(f"Warning: {label} has no data in range {wl_min}-{wl_max} nm")

            continue

        integrated_counts = np.trapz(filtered_dataframe["Intensity_counts"], filtered_dataframe["Wavelength_nm"])
        luminescence = integrated_counts / integration_time

        results.append((height, luminescence, integrated_counts))

    return pd.DataFrame(results, columns=["Height_mV", "Luminescence_counts", "Integrated_counts"])

def integral_map_different_heights(spectra_dict, integration_time, wl_start, wl_stop, wl_step=1.0, ref_df=None):

    heights = []
    wl_centers = np.arange(wl_start, wl_stop, wl_step)
    data_matrix = []

    ref_integrated = None

    if ref_df is not None:

        ref_integrated = []

        for wl in wl_centers:

            ref_window = ref_df[(ref_df["Wavelength_nm"] >= wl) & (ref_df["Wavelength_nm"] < wl + wl_step)]
            val = np.trapz(ref_window["Intensity_counts"], ref_window["Wavelength_nm"]) / integration_time
            ref_integrated.append(val)

        ref_integrated = np.array(ref_integrated)

    for label, df in sorted(spectra_dict.items(), key=lambda x: x[1].attrs["Height"]):

        height = df.attrs["Height"]
        heights.append(height)
        intensities = []

        for wl in wl_centers:

            window = df[(df["Wavelength_nm"] >= wl) & (df["Wavelength_nm"] < wl + wl_step)]
            val = np.trapz(window["Intensity_counts"], window["Wavelength_nm"]) / integration_time
            intensities.append(val)

        intensities = np.array(intensities)

        if ref_integrated is not None:

            min_signal_threshold = 7

            with np.errstate(divide='ignore', invalid='ignore'):
                ratio = intensities / ref_integrated
                mask = (intensities >= min_signal_threshold)
                ratio[~mask] = np.nan
                intensities = ratio

        data_matrix.append(intensities)

    return np.array(heights), wl_centers + wl_step / 2, np.array(data_matrix)