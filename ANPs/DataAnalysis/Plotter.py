import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def plot_all_spectra(spectra_dict,
                     integration_time,
                     ratio_start,
                     ratio_stop,
                     data_label,
                     integration_range=None):

    fig, ax = plt.subplots(figsize=(12, 7))

    power_values = [data.attrs["Power_W"] for data in spectra_dict.values()]
    color_normalization = LogNorm(vmin=min(power_values), vmax=max(power_values))
    colormap = cm.jet

    for label, data in spectra_dict.items():

        power = data.attrs["Power_W"]
        color = colormap(color_normalization(power))
        ax.plot(data["Wavelength_nm"], data["Intensity_counts"], label=label, color=color)

    if integration_range is not None:

        wl_min, wl_max = integration_range
        line1 = plt.axvline(x=wl_min, color="grey", linestyle="--", linewidth=1.2)
        line2 = plt.axvline(x=wl_max, color="grey", linestyle="--", linewidth=1.2)

        legend = ax.legend([line1], ["Integration region"],
                           loc="upper right",
                           fontsize=14,
                           frameon=True)

    sm = plt.cm.ScalarMappable(cmap=colormap, norm=color_normalization)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Power [W] (log scale)", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=16)

    ax.set_title("Intensity counts vs wavelength", fontsize=18)
    ax.set_xlabel("Wavelength [nm]", fontsize=16)
    ax.set_ylabel("Intensity [counts]", fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=14)

    measurement_label = data_label.get('label', 'Unknown')
    parameters_text = (f"Type: {measurement_label}\n"
                       f"Integration time: {integration_time} s\n"
                       f"Power ratio start: {ratio_start}\n"
                       f"Power ratio stop: {ratio_stop}")

    ax.text(0.03, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=16,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    plt.tight_layout()
    plt.show()

def plot_all_spectra_with_zoom(spectra_dict,
                               integration_time,
                               ratio_start,
                               ratio_stop,
                               data_label,
                               zoom_wl_min,
                               zoom_wl_max,
                               integration_range=None):

    fig, ax = plt.subplots(figsize=(12, 7))

    power_values = [data.attrs["Power_W"] for data in spectra_dict.values()]
    color_normalization = LogNorm(vmin=min(power_values), vmax=max(power_values))
    colormap = cm.jet

    for label, data in spectra_dict.items():

        power = data.attrs["Power_W"]
        color = colormap(color_normalization(power))
        ax.plot(data["Wavelength_nm"], data["Intensity_counts"], label=label, color=color)

    if integration_range is not None:
        wl_min, wl_max = integration_range
        line1 = plt.axvline(x=wl_min, color="grey", linestyle="--", linewidth=1.2)
        line2 = plt.axvline(x=wl_max, color="grey", linestyle="--", linewidth=1.2)

        legend = ax.legend([line1], ["Integration region"],
                           loc="upper right",
                           fontsize=14,
                           frameon=True)

    sm = plt.cm.ScalarMappable(cmap=colormap, norm=color_normalization)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("Power [W] (log scale)", fontsize=16, labelpad=5)
    cbar.ax.tick_params(labelsize=16)

    ax_inset = inset_axes(ax, width="45%", height="45%",
                          loc="lower left",
                          bbox_to_anchor=(0.1, 0.25, 1, 1),
                          bbox_transform=ax.transAxes,
                          borderpad=0)

    for label, data in spectra_dict.items():

        power = data.attrs["Power_W"]
        color = colormap(color_normalization(power))
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
    parameters_text = (f"Type: {measurement_label}\n"
                       f"Integration time: {integration_time} s\n"
                       f"Power ratio start: {ratio_start}\n"
                       f"Power ratio stop: {ratio_stop}")

    ax.text(0.03, 0.95, parameters_text,
            transform=ax.transAxes,
            fontsize=16,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    plt.tight_layout()
    plt.show()