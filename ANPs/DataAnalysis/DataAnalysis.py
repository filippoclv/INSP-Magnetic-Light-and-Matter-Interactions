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