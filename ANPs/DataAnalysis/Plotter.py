import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from FileReader import *
from Analyzer import *

def plot_single_spectrum(data,
                         title=None):

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(data["Wavelength_nm"], data["Intensity_counts"], color="teal")

    if title:

        ax.set_title(title, fontsize=18)

    ax.set_title("Spectrum", fontsize=18)
    ax.set_xlabel("Wavelength [nm]", fontsize=16)
    ax.set_ylabel("Intensity [counts]", fontsize=16)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=14)

    plt.tight_layout()
    plt.show()

def plot_all_spectra(spectra_dict,
                     integration_time,
                     ratio_start,
                     ratio_stop,
                     data_label,
                     integration_range=None):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

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

    plt.show()

def plot_all_spectra_with_zoom(spectra_dict,
                               integration_time,
                               ratio_start,
                               ratio_stop,
                               data_label,
                               zoom_wl_min,
                               zoom_wl_max,
                               integration_range=None):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

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

    plt.show()

def plot_powercurve(powercurve_dataset, data_label, wl_min, wl_max):

    measurement_label = data_label["label"]
    integration_time = data_label["integration_time"]
    ratio_start = data_label["ratio_start"]
    ratio_stop = data_label["ratio_stop"]

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    ax.plot(powercurve_dataset["Power_W"],
            powercurve_dataset["Luminescence_counts/s"],
            marker='o',
            markersize=7,
            markerfacecolor='none',
            markeredgecolor='crimson',
            linestyle='-',
            linewidth=2,
            color='teal',
            label="Luminescence [counts/s]"
           )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Power [W]", fontsize=16)
    ax.set_ylabel("Luminescence [counts/s]", fontsize=16)
    ax.set_title(f"Luminescence vs power, log-scale\n({wl_min}–{wl_max} nm peak)", fontsize=18)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    ax.tick_params(axis='both', which='major', labelsize=14)

    parameters_text = (f"Type: {measurement_label}\nIntegration time: {integration_time} s\n"
                       f"Power ratio start: {ratio_start}\nPower ratio stop: {ratio_stop}")

    ax.text(0.6, 0.2, parameters_text,
            transform=ax.transAxes,
            fontsize=16,
            verticalalignment="top",
            horizontalalignment="left",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.7))

    plt.show()

def plot_all_powercurves_from_json(powercurves_datasets,
                                    background_subtraction_range,
                                    int_start,
                                    int_end):

    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)

    colors = plt.cm.jet(np.linspace(0, 1, len(powercurves_datasets)))

    for i, dataset in enumerate(powercurves_datasets):

        folder = dataset["folder"]
        int_time = dataset["integration_time"]
        ratio_start = dataset["ratio_start"]
        ratio_stop = dataset["ratio_stop"]

        all_spectra_dict = all_spectra_dataframe_dict(folder, background_subtraction_range=background_subtraction_range)
        powercurve = integrate_all_spectra(all_spectra_dict, wl_min=int_start, wl_max=int_end, integration_time=int_time)

        config_label = f"{dataset.get('label', ''):<6}"

        label = (f"Int. time: {int_time:>1.2f} s | "
                 f"R: {ratio_start:>1.4f} – {ratio_stop:>1.3f} |\n{config_label} "
                )

        ax.plot(powercurve["Power_W"],
                powercurve["Luminescence_counts/s"],
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
    ax.set_title(f"Luminescence vs power, log-scale\n({int_start}–{int_end} nm peak)", fontsize=18)
    ax.set_xlabel("Power [W]", fontsize=16)
    ax.set_ylabel("Luminescence [counts/s]", fontsize=16)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    ax.legend(fontsize=16, loc="best", bbox_to_anchor=(1, 0.85))
    ax.tick_params(axis='both', which='major', labelsize=14)

    plt.show()