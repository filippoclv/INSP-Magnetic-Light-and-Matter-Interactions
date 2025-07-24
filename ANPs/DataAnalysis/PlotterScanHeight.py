import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize, ListedColormap, BoundaryNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def plot_single_spectrum(data, title=None):

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(data["Wavelength_nm"], data["Intensity_counts"], color="teal")

    if title:
        ax.set_title(title, fontsize=18)
    else:
        ax.set_title("Spectrum", fontsize=18)

    ax.set_xlabel("Wavelength [nm]", fontsize=16)
    ax.set_ylabel("Intensity [counts]", fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=14)

    plt.tight_layout()
    plt.show()

def plot_all_spectra_nearfield_heights(spectra_dict, integration_time, data_label, integration_range=None):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    height_values = [data.attrs["Height_mV"] for label, data in spectra_dict.items() if label != "Reference"]
    sorted_heights = np.sort(np.unique(height_values))

    colormap = cm.jet
    colors = colormap(np.linspace(0, 1, len(sorted_heights)))
    height_to_color = dict(zip(sorted_heights, colors))

    for label, data in spectra_dict.items():
        if label == "Reference":
            continue
        height = data.attrs["Height_mV"]
        color = height_to_color[height]
        ax.plot(data["Wavelength_nm"], data["Intensity_counts"], label=label, color=color, linewidth=0.6, alpha=0.8)

    cmap = ListedColormap(colors)
    boundaries = np.append(sorted_heights, sorted_heights[-1] + 1)
    norm = BoundaryNorm(boundaries=boundaries, ncolors=len(colors))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, ticks=sorted_heights[::max(1, len(sorted_heights) // 10)])
    cbar.set_label("Height (SensZ) [mV]", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=14)

    if integration_range is not None:
        wl_min, wl_max = integration_range
        plt.axvline(x=wl_min, color="grey", linestyle="--", linewidth=1.2)
        plt.axvline(x=wl_max, color="grey", linestyle="--", linewidth=1.2)

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
    sorted_heights = np.sort(np.unique(height_values))

    colormap = cm.jet
    colors = colormap(np.linspace(0, 1, len(sorted_heights)))
    height_to_color = dict(zip(sorted_heights, colors))

    for label, data in spectra_dict.items():
        if label == "Reference":
            continue
        height = data.attrs["Height_mV"]
        color = height_to_color[height]
        ax.plot(data["Wavelength_nm"], data["Intensity_counts"]/data["Intensity_counts"].max(), label=label, color=color, linewidth=1, alpha=0.8)

    cmap = ListedColormap(colors)
    boundaries = np.append(sorted_heights, sorted_heights[-1] + 1)
    norm = BoundaryNorm(boundaries=boundaries, ncolors=len(colors))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, ticks=sorted_heights[::max(1, len(sorted_heights) // 10)])
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

def plot_all_spectra_nearfield_heights_with_zoom(spectra_dict, integration_time, data_label, zoom_wl_min, zoom_wl_max, integration_range=None):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    height_values = [data.attrs["Height_mV"] for label, data in spectra_dict.items() if label != "Reference"]
    sorted_heights = np.sort(np.unique(height_values))

    colormap = cm.jet
    colors = colormap(np.linspace(0, 1, len(sorted_heights)))
    height_to_color = dict(zip(sorted_heights, colors))

    for label, data in spectra_dict.items():
        if label == "Reference":
            continue
        height = data.attrs["Height_mV"]
        color = height_to_color[height]
        ax.plot(data["Wavelength_nm"], data["Intensity_counts"], label=label, color=color, linewidth=0.6, alpha=0.8)

    cmap = ListedColormap(colors)
    boundaries = np.append(sorted_heights, sorted_heights[-1] + 1)
    norm = BoundaryNorm(boundaries=boundaries, ncolors=len(colors))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, ticks=sorted_heights[::max(1, len(sorted_heights) // 10)])
    cbar.set_label("Height (SensZ) [mV]", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=14)

    if integration_range is not None:
        wl_min, wl_max = integration_range
        plt.axvline(x=wl_min, color="grey", linestyle="--", linewidth=1.2)
        plt.axvline(x=wl_max, color="grey", linestyle="--", linewidth=1.2)

    ax_inset = inset_axes(ax, width="45%", height="45%",
                          loc="lower left",
                          bbox_to_anchor=(0.1, 0.21, 1, 1),
                          bbox_transform=ax.transAxes,
                          borderpad=0)

    for label, data in spectra_dict.items():
        if label == "Reference":
            continue
        height = data.attrs["Height_mV"]
        color = height_to_color[height]
        zoomed_region = data[(data["Wavelength_nm"] >= zoom_wl_min) & (data["Wavelength_nm"] <= zoom_wl_max)]
        if not zoomed_region.empty:
            ax_inset.plot(zoomed_region["Wavelength_nm"], zoomed_region["Intensity_counts"], color=color)

    ax_inset.set_xlim(zoom_wl_min, zoom_wl_max)
    ax_inset.set_title(f"Zoomed region: {zoom_wl_min}–{zoom_wl_max} nm", fontsize=16)
    ax_inset.tick_params(labelsize=12)
    ax_inset.grid(True, alpha=0.3)
    ax_inset.set_xlabel("Wavelength [nm]", fontsize=14)
    ax_inset.set_ylabel("Intensity [counts]", fontsize=14)
    ax_inset.patch.set_edgecolor('black')
    ax_inset.patch.set_linewidth(1.2)

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

def plot_integral_map_nearfield_heights(heights, wl_bins, intensity_map):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    pcm = ax.pcolormesh(wl_bins, heights, intensity_map, shading='auto', cmap='jet', vmin=1, vmax=1.5)

    cbar = plt.colorbar(pcm, ax=ax)
    cbar.set_label("L_A / L_0", fontsize=16)
    cbar.ax.tick_params(labelsize=14)

    ax.set_xlabel("Wavelength [nm]", fontsize=16)
    ax.set_ylabel("Height (SensZ) [mV]", fontsize=16)
    ax.set_title("2D map: integrated counts per 1 nm bin", fontsize=18)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.grid(False)

    plt.show()