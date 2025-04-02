from DataAnalysis import *

# Each dictionary defines one dataset
datasets = [
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401133337",
        "integration_time": 1,
        "ratio_start": 0.001,
        "ratio_stop": 0.1
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401135220",
        "integration_time": 0.5,
        "ratio_start": 0.0005,
        "ratio_stop": 0.1
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401142947",
        "integration_time": 2,
        "ratio_start": 0.0005,
        "ratio_stop": 0.2
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144019",
        "integration_time": 0.8,
        "ratio_start": 0.0005,
        "ratio_stop": 0.9
    },
    {
        "folder": r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\Test_ANP_20250401\20250401144818",
        "integration_time": 3,
        "ratio_start": 0.0001,
        "ratio_stop": 0.08
    },
]

n = len(datasets)
fig, axes = plt.subplots(nrows=n, ncols=2, figsize=(16, 5 * n), constrained_layout=True)

# Looping through each dataset
for i, data in enumerate(datasets):

    print(f"\nProcessing Dataset {i}")
    print(f"Folder: {data['folder']}")

    # Load power info for the current dataset

    power_info_file = Path(data["folder"]) / "SetInfoPowerCurve.txt"
    power_info = pd.read_csv(power_info_file, sep="\t")
    power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

    # Read spectra and apply background correction
    all_spectra = read_all_spectra(data["folder"])

    # Integrate peak
    results_df = integrate_peak(all_spectra, wl_min=755, wl_max=860)

    powers = [df.attrs["Power_W"] for df in all_spectra.values()]
    norm = LogNorm(vmin=min(powers), vmax=max(powers))
    colormap = cm.turbo

    # Spectra plot
    ax_zoom = axes[i, 0]
    powers = [df.attrs["Power_W"] for df in all_spectra.values()]

    for label, df in all_spectra.items():

        power = df.attrs["Power_W"]
        color = colormap(norm(power))
        ax_zoom.plot(df["Wavelength_nm"], df["Intensity_counts"], color=color)

    ax_zoom.set_title("Intensity counts vs wavelength", fontsize=14)
    ax_zoom.set_xlabel("Wavelength [nm]")
    ax_zoom.set_ylabel("Intensity [counts]")
    ax_zoom.grid(True, alpha=0.3)

    # Zoomed plot
    ax_inset = inset_axes(ax_zoom, width="45%", height="45%", loc="upper left", borderpad=4)

    for label, df in all_spectra.items():

        power = df.attrs["Power_W"]
        color = colormap(norm(power))
        zoomed = df[(df["Wavelength_nm"] >= 630) & (df["Wavelength_nm"] <= 760)]

        if not zoomed.empty:

            ax_inset.plot(zoomed["Wavelength_nm"], zoomed["Intensity_counts"], color=color)

    ax_inset.set_xlim(630, 760)
    ax_inset.set_title("Zoomed in 630–760 nm range", fontsize=9)
    ax_inset.tick_params(labelsize=8)
    ax_inset.grid(True, alpha=0.3)
    ax_inset.patch.set_edgecolor('black')
    ax_inset.patch.set_linewidth(1)

    # Add parameter box on main subplot
    info_text = (
        f"Int. time: {data['integration_time']} s\n"
        f"R_start: {data['ratio_start']}\n"
        f"R_stop: {data['ratio_stop']}"
    )
    ax_zoom.text(0.8, 0.2, info_text,
                 transform=ax_zoom.transAxes,
                 fontsize=10,
                 verticalalignment="bottom",
                 horizontalalignment="left",
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="black", alpha=0.6))


    # Integrated intensity vs Power plot
    ax_int = axes[i, 1]
    ax_int.plot(
        results_df["Power_W"],
        results_df["Integrated intensity"],
        marker='o',
        markersize=6,
        markerfacecolor='none',
        markeredgecolor='crimson',
        linestyle='-',
        linewidth=2,
        color='teal'
    )
    ax_int.set_xscale("log")
    ax_int.set_yscale("log")
    ax_int.set_title("log-log scale: integrated intensity vs power", fontsize=14)
    ax_int.set_xlabel("Power [W]")
    ax_int.set_ylabel("Integrated intensity [a.u.]")
    ax_int.grid(True, which='both', linestyle='--', alpha=0.3)

plt.show()

fig.savefig("Spectra_and_powercurves.png", dpi=300, bbox_inches='tight')