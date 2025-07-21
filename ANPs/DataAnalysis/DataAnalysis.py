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

# def plot_all_power_curvesNF(datasets, int_start, int_end):
#
#     fig, ax = plt.subplots(figsize=(14, 12), constrained_layout=True)
#
#     # Use Z for color coding
#     z_values = np.array([data.get("Z_mV", 0) for data in datasets])
#     norm = plt.Normalize(vmin=-1000, vmax=0)
#     cmap = plt.cm.jet
#     colors = cmap(norm(z_values))
#
#     for i, data in enumerate(datasets):
#
#         folder = data["folder"]
#         int_time = data["integration_time"]
#         ratio_start = data["ratio_start"]
#         ratio_stop = data["ratio_stop"]
#
#         power_info_file = Path(folder) / "SetInfoPowerCurve.txt"
#         power_info = pd.read_csv(power_info_file, sep="\t")
#         power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))
#
#         all_spectra = read_all_spectra(folder)
#         results_df = integrate_peak(all_spectra, int_start, int_end, integration_time=int_time)
#
#         config_label = f"{data.get('label', ''):<6}"  # Empty if not present
#         #label = f"{config_label} | Int. time: {int_time:.1f} s | R: {ratio_start:.4f}–{ratio_stop:.2f}"
#
#         label = (
#                  f"Int. time: {int_time:>1.2f} s | "
#                  f"R: {ratio_start:>1.4f} – {ratio_stop:>1.3f} | "
#                 )
#
#         ax.plot(
#           results_df["Power_W"],
#                 results_df["Luminescence_counts"],
#                 marker="o",
#                 markersize=6,
#                 markerfacecolor="none",
#                 linestyle="-",
#                 linewidth=2,
#                 label=label,
#                 color=colors[i]
#                )
#
#     ax.set_xscale("log")
#     ax.set_yscale("log")
#     ax.set_title(f"log-log scale: luminescence vs power\n({int_start}–{int_end} nm peak)", fontsize=14)
#     ax.set_xlabel("Power [W]")
#     ax.set_ylabel("Luminescence [counts]")
#     ax.grid(True, which='both', linestyle='--', alpha=0.3)
#     ax.legend(fontsize=10, loc="best", prop={"family": "DejaVu Sans Mono"})
#
#     # Add colorbar
#     sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
#     sm.set_array([])
#     cbar = plt.colorbar(sm, ax=ax)
#     cbar.set_label("Z parameter [mV]", fontsize=12)
#
#     plt.show()

def plot_all_power_curves_with_s(datasets, int_start, int_end):

    fig, ax = plt.subplots(figsize=(14, 10), constrained_layout=True)
    colors = plt.cm.viridis(np.linspace(0, 1, len(datasets)))

    for i, data in enumerate(datasets):

        folder = data["folder"]
        int_time = data["integration_time"]
        ratio_start = data["ratio_start"]
        ratio_stop = data["ratio_stop"]
        spectrometer_hole_diameter = data["spectrometer_hole_diameter"]

        power_info_file = Path(folder) / "SetInfoPowerCurve.txt"
        power_info = pd.read_csv(power_info_file, sep="\t")
        power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

        all_spectra = read_all_spectra(folder)
        results_df = integrate_peak(all_spectra, int_start, int_end, integration_time=int_time)

        # If you want to shift the curves use this after integration:

        power_shift = data.get("power_shift_factor", 1.0)
        lum_shift = data.get("luminescence_shift_factor", 1.0)

        results_df["Power_W"] *= power_shift
        results_df["Luminescence_counts"] *= lum_shift

        # Compute s value and power
        derivative_df, s_value, s_power = calculate_derivative(results_df)

        from matplotlib.cm import get_cmap

        # Get a categorical colormap for more distinct colors
        cmap = get_cmap("tab10")  # You can also try "tab20", "Set1", etc.
        colors = [cmap(i % cmap.N) for i in range(len(datasets))]

        config_label = f"{data.get('label', ''):<7}"  # Empty if not present

        label = (
            f"{config_label:<7} | "
            f"Int. time: {int_time:>5.2f} s | "
            f"R: {ratio_start:.4f} - {ratio_stop:.3f} | "
            f"s ≈ {s_value:.2f} at {s_power:.6f} W"
        )

        # Plot curve
        ax.plot(
          results_df["Power_W"],
                results_df["Luminescence_counts"],
                marker="o",
                markersize=6,
                markerfacecolor="none",
                linestyle="-",
                linewidth=2,
                color=colors[i],
                label=label
               )

        # Vertical line at s_power
        ax.axvline(
                   x=s_power,
                   linestyle="--",
                   linewidth=1.6,
                   color=colors[i],
                   alpha=0.5
                  )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(f"log-log scale: luminescence vs power\n({int_start}–{int_end} nm peak)", fontsize=22)
    ax.set_xlabel("Power [W]", fontsize=22)
    ax.set_ylabel("Luminescence [counts]", fontsize=22)
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.grid(True, which="both", linestyle="--", alpha=0.3)

    legend = ax.legend(
        fontsize=22,
        loc="best",
        prop={"family": "DejaVu Sans Mono", "size": 22},
        frameon=True,
        fancybox=True
    )
    for text in legend.get_texts():
        text.set_fontsize(14)

    plt.show()

def calculate_derivative_fit(results_df, degree):

    power = results_df["Power_W"].values
    luminescence = results_df["Luminescence_counts"].values

    # Log-log transform
    log_power = np.log(power)
    log_luminescence = np.log(luminescence)

    # Polynomial fit
    coefficients = np.polyfit(log_power, log_luminescence, deg=degree)
    poly_fit = np.poly1d(coefficients)

    # Evaluate fitted curve and its gradient
    log_luminescence_fit = poly_fit(log_power)
    derivative = np.gradient(log_luminescence_fit, log_power)

    results_df["Fitted_logLuminescence"] = log_luminescence_fit
    results_df["Derivative"] = derivative

    # Identify max slope (s)
    s_idx = np.argmax(derivative)
    results_df["s parameter"] = False
    results_df.loc[s_idx, "s parameter"] = True

    s_value = derivative[s_idx]
    s_power = power[s_idx]

    return results_df, s_value, s_power

def plot_all_derivatives_fit(datasets, int_start, int_end, degree):

    fig, ax = plt.subplots(figsize=(14, 10), constrained_layout=True)
    colors = plt.cm.viridis(np.linspace(0, 1, len(datasets)))

    for i, data in enumerate(datasets):

        folder = data["folder"]
        int_time = data["integration_time"]
        ratio_start = data["ratio_start"]
        ratio_stop = data["ratio_stop"]

        # Read and integrate
        all_spectra = read_all_spectra(folder)
        results_df = integrate_peak(all_spectra, int_start, int_end, integration_time=int_time)

        # Derivative fit
        derivative_df, s_value, s_power = calculate_derivative_fit(results_df, degree=degree)

        # Compute FWHM
        x = np.log(derivative_df["Power_W"].values)
        y = derivative_df["Derivative"].values
        y_max = np.max(y)
        half_max = y_max / 2
        crossings = np.where(np.diff(np.sign(y - half_max)))[0]

        if len(crossings) >= 2:

            x1_idx, x2_idx = crossings[0], crossings[-1]

            def interp_x(idx):

                x0, x1 = x[idx], x[idx + 1]
                y0, y1 = y[idx], y[idx + 1]

                return x0 + (half_max - y0) * (x1 - x0) / (y1 - y0)

            x1 = interp_x(x1_idx)
            x2 = interp_x(x2_idx)
            fwhm_val = np.exp(x2) - np.exp(x1)
            fwhm_str = f"{fwhm_val:.8f} W"

        else:

            fwhm_str = "N/A"

        # Label
        config_label = f"{data.get('label', ''):<8}"  # Aligned
        label = (
                 f"{config_label}\n"
                 f"Int. time: {int_time:.1f} s\n"
                 f"R: {ratio_start:.4f}–{ratio_stop:.2f}\n"
                 f"s ≈ {s_value:.2f} at {s_power:.8f} W\n"
                 f"FWHM ≈ {fwhm_str}"
                )

        # Plot curve
        ax.plot(
          derivative_df["Power_W"],
                derivative_df["Derivative"],
                marker="o",
                markersize=6,
                markerfacecolor="none",
                linestyle="-",
                linewidth=2,
                color=colors[i],
                label=label
               )

        # Highlight max slope
        s_point = derivative_df[derivative_df["s parameter"]]

        ax.plot(
          s_point["Power_W"],
                s_point["Derivative"],
                marker="o",
                color=colors[i],
                markersize=8,
                markeredgecolor="black"
               )

        ax.axvline(
                   x=s_power,
                   linestyle="--",
                   linewidth=1.2,
                   color=colors[i],
                   alpha=0.5
                  )

    ax.set_xscale("log")
    ax.set_xlabel("Power [W]", fontsize=12)
    ax.set_ylabel("d(logL) / d(logP)", fontsize=12)
    ax.set_title(f"Derivative (fitted) of luminescence vs power\n({int_start}–{int_end} nm peak)", fontsize=14)
    ax.grid(True, which="both", linestyle="--", alpha=0.3)
    ax.legend(fontsize=10, loc="best", prop={"family": "DejaVu Sans Mono"})

    plt.show()

def check_all_fits(datasets, int_start, int_end, degree=3):

    fig, ax = plt.subplots(figsize=(14, 10), constrained_layout=True)
    colors = plt.cm.viridis(np.linspace(0, 1, len(datasets)))

    for i, data in enumerate(datasets):

        folder = data["folder"]
        int_time = data["integration_time"]

        # Read and integrate
        all_spectra = read_all_spectra(folder)
        results_df = integrate_peak(all_spectra, int_start, int_end, integration_time=int_time)

        # Raw data
        power = results_df["Power_W"].values
        luminescence = results_df["Luminescence_counts"].values
        log_power = np.log(power)
        log_luminescence = np.log(luminescence)

        # Fit
        coefficients = np.polyfit(log_power, log_luminescence, deg=degree)
        poly_fit = np.poly1d(coefficients)
        log_power_smooth = np.linspace(log_power.min(), log_power.max(), 300)
        log_luminescence_smooth = poly_fit(log_power_smooth)

        # Back to linear scale
        power_fit = np.exp(log_power_smooth)
        luminescence_fit = np.exp(log_luminescence_smooth)

        # Label

        config_label = f"{data.get('label', ''):<8}"  # Empty if not present

        label = f"{config_label} | Int. time {int_time:.1f}s | Fit degree={degree}"

        # Plot raw + fit
        ax.plot(power, luminescence, "o", color=colors[i], alpha=0.6, label=f"Data {i+1}")
        ax.plot(power_fit, luminescence_fit, "-", color=colors[i], label=label)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Power [W]", fontsize=12)
    ax.set_ylabel("Luminescence [counts]", fontsize=12)
    ax.set_title(f"Power curves and polynomial fits (deg={degree})", fontsize=14)
    ax.grid(True, which="both", linestyle="--", alpha=0.3)
    ax.legend(fontsize=10, loc="best", prop={"family": "DejaVu Sans Mono"})

    plt.show()

# Let's consider the possibility of measuring curves back and forth

def plot_power_curves_back_and_forth(folder, int_start, int_end, integration_time, title_note=""):

    spectra = read_all_spectra(folder)
    total_points = len(spectra)

    half = total_points // 2
    sorted_labels = sorted(spectra.keys(), key=lambda x: int(x[1:]))

    # Split the spectra
    spectra_fwd = {k: spectra[k] for k in sorted_labels[:half]}
    spectra_bwd = {k: spectra[k] for k in sorted_labels[half:]}

    # Fwd and bwd stands for forward and backward obviously

    df_fwd = integrate_peak(spectra_fwd, int_start, int_end, integration_time)
    df_bwd = integrate_peak(spectra_bwd, int_start, int_end, integration_time)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)

    ax.plot(df_fwd["Power_W"], df_fwd["Luminescence_counts"], 'o-', label="Forward sweep", color='tab:blue')
    ax.plot(df_bwd["Power_W"], df_bwd["Luminescence_counts"], 'o-', label="Backward sweep", color='tab:orange')

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Power [W]", fontsize=12)
    ax.set_ylabel("Luminescence [counts]", fontsize=12)
    ax.set_title(f"log-log scale: luminescence vs power - forward/backward power sweep\n({int_start}-{int_end} nm {title_note})", fontsize=14)
    ax.grid(True, which="both", linestyle="--", alpha=0.3)
    ax.legend(fontsize=11)

    plt.show()

# Let's analyze the peak ratios:

def analyze_peak_ratios(spectra_dict, peak1_range=(680, 720), peak2_range=(780, 820)):

    results = []

    for power_label, df in spectra_dict.items():

        # Find max value for peak 1 (around 700 nm)
        peak1_mask = (df["Wavelength_nm"] >= peak1_range[0]) & (df["Wavelength_nm"] <= peak1_range[1])
        peak1_max = df.loc[peak1_mask, "Intensity_counts"].max()

        # Find max value for peak 2 (around 800 nm)
        peak2_mask = (df["Wavelength_nm"] >= peak2_range[0]) & (df["Wavelength_nm"] <= peak2_range[1])
        peak2_max = df.loc[peak2_mask, "Intensity_counts"].max()

        # Calculate ratio and store with power value
        ratio = peak2_max / peak1_max
        power = df.attrs["Power_W"]

        results.append({
            "Power_W": power,
            "Peak1_max": peak1_max,
            "Peak2_max": peak2_max,
            "Peak_ratio": ratio
        })

    # Convert to DataFrame and sort by power
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("Power_W")

    return results_df

def plot_peak_ratios(results_df):

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.plot(results_df["Power_W"], results_df["Peak_ratio"],
            "o-", markerfacecolor="none", color="teal",
            label="Ratio between max(780,820) / max(680,720)"
           )

    ax.set_xscale('log')
    ax.set_xlabel("Power [W]", fontsize=12)
    ax.set_ylabel("Peak ratio", fontsize=12)
    ax.set_title("Ratio of peak values vs power", fontsize=14)
    ax.grid(True, which='both', linestyle='--', alpha=0.3)
    ax.legend(fontsize=12, loc="best")

    plt.tight_layout()
    plt.show()

    return fig, ax