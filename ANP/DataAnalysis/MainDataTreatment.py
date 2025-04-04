from DataAnalysis import *

plt.close("all")

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

# Integration range

int_start = 770
int_end = 835

n = len(datasets)

# Plot all power curves in one figure
fig_all, ax_all = plt.subplots(figsize=(8, 6))

colors = plt.cm.viridis(np.linspace(0, 1, len(datasets)))

for i, data in enumerate(datasets):

    folder = data["folder"]
    power_info_file = Path(folder) / "SetInfoPowerCurve.txt"
    power_info = pd.read_csv(power_info_file, sep="\t")
    power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

    all_spectra = read_all_spectra(folder)
    results_df = integrate_peak(all_spectra, int_start, int_end)

    label = f"Int: {data['integration_time']:>4.1f} s    R: {data['ratio_start']:<7.4f} – {data['ratio_stop']:<4.2f}"

    ax_all.plot(
        results_df["Power_W"],
        results_df["Integrated intensity"],
        marker='o',
        markersize=6,
        markerfacecolor='none',
        linestyle='-',
        linewidth=2,
        label=label,
        color=colors[i]
    )

ax_all.set_xscale("log")
ax_all.set_yscale("log")
ax_all.set_title("Integrated intensity vs power", fontsize=14)
ax_all.set_xlabel("Power [W]")
ax_all.set_ylabel("Integrated intensity [a.u.]")
ax_all.grid(True, which='both', linestyle='--', alpha=0.3)
ax_all.legend(fontsize=9, loc="lower right")

plt.tight_layout()
plt.savefig("All_PowerCurves.png", dpi=300)
plt.show()

# For the specific spectra plot

selected_data = datasets[2]  # This is the third one

# Load power map
power_info_file = Path(selected_data["folder"]) / "SetInfoPowerCurve.txt"
power_info = pd.read_csv(power_info_file, sep="\t")
power_map = dict(zip(power_info["Pindex"], power_info["CurrentPower"]))

# Read spectra and plot
all_spectra = read_all_spectra(selected_data["folder"])

plot_spectra_with_zoom(
    all_spectra,
    integration_time=selected_data["integration_time"],
    ratio_start=selected_data["ratio_start"],
    ratio_stop=selected_data["ratio_stop"],
    zoom_wl_min=630,
    zoom_wl_max=760,
    integration_range=(int_start, int_end)
)

# 630 - 760 nm range is good to zoom on the smaller peaks

plt.show()