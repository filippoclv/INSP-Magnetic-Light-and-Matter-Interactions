import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize

def plot_all_spectra_nearfield_heights(spectra_dict, integration_time, data_label, integration_range=None):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    height_values = [data.attrs["Height_mV"] for label, data in spectra_dict.items() if label != "Reference"]
    color_normalization = Normalize(vmin=min(height_values), vmax=max(height_values))
    colormap = cm.jet

    for label, data in spectra_dict.items():

        if label == "Reference":

            continue

        height = data.attrs["Height_mV"]
        color = colormap(color_normalization(height))
        ax.plot(data["Wavelength_nm"], data["Intensity_counts"], label=label, color=color, linewidth=0.6, alpha=0.8)

    sm = plt.cm.ScalarMappable(cmap=colormap, norm=color_normalization)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Height (SensZ) [mV]", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=14)

    if integration_range is not None:

        wl_min, wl_max = integration_range
        line1 = plt.axvline(x=wl_min, color="grey", linestyle="--", linewidth=1.2)
        line2 = plt.axvline(x=wl_max, color="grey", linestyle="--", linewidth=1.2)

        legend = ax.legend([line1], ["Integration region"],
                           loc="upper right",
                           fontsize=14,
                           frameon=True)

    ax.set_title("Intensity counts vs wavelength", fontsize=18)
    ax.set_xlabel("Wavelength [nm]", fontsize=16)
    ax.set_ylabel("Intensity [counts]", fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=14)

    measurement_label = data_label.get('label', 'Unknown')
    power_percentage = data_label.get('power_percentage', 'Unknown')
    stepZ = data_label.get('stepZ_mV', 'Unknown')

    parameters_text = (f"Type: {measurement_label}\n"
                       f"Integration time: {integration_time} s\n"
                       f"Power: {power_percentage}%\n"
                       f"StepZ size: {stepZ} mV")

    ax.text(0.03, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=16,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    ax.set_ylim(bottom=0)
    plt.show()

def plot_all_spectra_nearfield_heights_normalized(spectra_dict, integration_time, data_label):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    height_values = [data.attrs["Height_mV"] for label, data in spectra_dict.items() if label != "Reference"]
    color_normalization = Normalize(vmin=min(height_values), vmax=max(height_values))
    colormap = cm.jet

    for label, data in spectra_dict.items():

        if label == "Reference":

            continue

        height = data.attrs["Height_mV"]
        color = colormap(color_normalization(height))
        ax.plot(data["Wavelength_nm"], data["Intensity_counts"]/data["Intensity_counts"].max(), label=label, color=color, linewidth=1, alpha=0.8)

    sm = plt.cm.ScalarMappable(cmap=colormap, norm=color_normalization)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Height (SensZ) [mV]", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=14)

    ax.set_title("Normalized intensity counts vs wavelength", fontsize=18)
    ax.set_xlabel("Wavelength [nm]", fontsize=16)
    ax.set_ylabel("Normalized intensity", fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=14)

    measurement_label = data_label.get('label', 'Unknown')
    power_percentage = data_label.get('power_percentage', 'Unknown')
    stepZ = data_label.get('stepZ_mV', 'Unknown')

    parameters_text = (f"Type: {measurement_label}\n"
                       f"Integration time: {integration_time} s\n"
                       f"Power: {power_percentage}%\n"
                       f"StepZ size: {stepZ} mV")

    ax.text(0.03, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=16,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    ax.set_ylim(bottom=0)
    plt.show()

def plot_LDOS_map(heights, wl_bins, intensity_map, cb_min=1, cb_max=2):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    pcm = ax.pcolormesh(wl_bins, heights, intensity_map, shading='auto', cmap='jet', vmin=cb_min, vmax=cb_max)

    cbar = plt.colorbar(pcm, ax=ax)
    cbar.set_label("$L_A / L_0$", fontsize=16)
    cbar.ax.tick_params(labelsize=14)

    ax.set_xlabel("Wavelength [nm]", fontsize=16)
    ax.set_ylabel("Height (SensZ) [mV]", fontsize=16)
    ax.set_title("LDOS 2D map: integrated counts per 1 nm bin,\ndivided by reference signal (removed antenna)", fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)

    plt.show()