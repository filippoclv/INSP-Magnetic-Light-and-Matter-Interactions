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