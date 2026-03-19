import matplotlib

# Force a native interactive window (Bypasses IDE static plot panes like PyCharm SciView)
try:
    matplotlib.use('TkAgg')
except Exception:
    pass

import os
import glob
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d


# --- 1. Core Physics & Extraction Logic ---

def analyze_pixel_savgol(power, counts_raw, bg_baseline, bg_noise_floor,
                         snr_threshold=3, min_consecutive=3, savgol_window=15, savgol_poly=3):
    """
    Performs the SavGol analysis. Returns a dictionary with all the curves needed for plotting,
    or None for the s_max if it fails the noise threshold.
    """
    counts_corrected = counts_raw - bg_baseline
    raw_valid_mask = counts_corrected > (snr_threshold * bg_noise_floor)

    avalanche_start_idx = len(raw_valid_mask)
    for i in range(len(raw_valid_mask) - min_consecutive + 1):
        if np.all(raw_valid_mask[i: i + min_consecutive]):
            avalanche_start_idx = i
            break

    final_valid_mask = np.copy(raw_valid_mask)
    final_valid_mask[:avalanche_start_idx] = False

    power_valid = power[final_valid_mask]
    counts_valid = counts_corrected[final_valid_mask]

    result = {
        "power_raw": power,
        "counts_raw": counts_raw,
        "power_valid": power_valid,
        "counts_valid": counts_valid,
        "s_max": None
    }

    if len(power_valid) < max(4, savgol_window):
        return result  # Fails noise check, return raw data only

        # THE FIX 4: The Physical Explosion Criteria (Dynamic Range)
        # A true avalanche must produce a massive macroscopic jump in signal.
        # If the maximum raw signal isn't at least 2.5x the background, it is just scatter/drift.
    min_fold_increase = 2.5
    if np.max(counts_raw[final_valid_mask]) < (min_fold_increase * bg_baseline):
        return result  # (or 'return None' in the simple script)

    log_power = np.log10(power_valid)
    log_counts = np.log10(counts_valid)

    log_power, unique_idx = np.unique(log_power, return_index=True)
    log_counts = log_counts[unique_idx]

    if len(log_power) < savgol_window:
        return result

    # Interpolate onto a dense grid
    num_fine_points = 300
    log_p_fine = np.linspace(log_power.min(), log_power.max(), num_fine_points)
    interp_func = interp1d(log_power, log_counts, kind='linear')
    log_c_interp = interp_func(log_p_fine)

    # THE FIX: Scale the SavGol window from the raw data density to the interpolated grid density
    points_ratio = num_fine_points / len(log_power)
    wl_fine = int(savgol_window * points_ratio)
    wl_fine = wl_fine if wl_fine % 2 != 0 else wl_fine + 1
    wl_fine = min(wl_fine, num_fine_points - 1)

    if wl_fine <= savgol_poly:
        savgol_poly = wl_fine - 1

    # Apply filter on the scaled window
    log_c_fine = savgol_filter(log_c_interp, window_length=wl_fine, polyorder=savgol_poly)
    dx = log_p_fine[1] - log_p_fine[0]
    slopes_fine = savgol_filter(log_c_interp, window_length=wl_fine, polyorder=savgol_poly, deriv=1, delta=dx)

    # THE FIX 2: Hard Array Truncation to permanently destroy edge artifacts
    clip_idx = wl_fine // 2

    if len(slopes_fine) > 2 * clip_idx:
        log_p_fine = log_p_fine[clip_idx:-clip_idx]
        log_c_fine = log_c_fine[clip_idx:-clip_idx]
        slopes_fine = slopes_fine[clip_idx:-clip_idx]

    s_idx = np.argmax(slopes_fine)
    s_max = slopes_fine[s_idx]

    result.update({
        "s_max": s_max,
        "p_at_s_max": 10 ** (log_p_fine[s_idx]),
        "log_p_fine": log_p_fine,
        "log_c_fine": log_c_fine,
        "slopes_fine": slopes_fine,
        "wl": wl_fine,
        "poly": savgol_poly
    })

    return result


# --- 2. Interactive Map Generation ---

def process_interactive_map(folder_path, scan_width_um=10.0, scan_height_um=10.0, bg_points_to_average=10,
                            snr_threshold=3, savgol_window=15, savgol_poly=3):
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    files = glob.glob(os.path.join(folder_path, "Pixel_*.txt"))
    if not files:
        print(f"No Pixel_X_Y.txt files found in {folder_path}")
        return

    print("Establishing global background...")
    lowest_bg = np.inf
    global_bg = 0
    global_noise = 0

    all_pixel_data = {}

    # 1. Read Data and Find Background
    for filepath in files:
        match = re.search(r"Pixel_(\d+)_(\d+)\.txt", os.path.basename(filepath))
        if not match: continue
        x_idx, y_idx = int(match.group(1)), int(match.group(2))

        try:
            df = pd.read_csv(filepath, sep="\t")
            p_col = "ReadPower" if "ReadPower" in df.columns else "CurrentPower"
            c_col = "Counts" if "Counts" in df.columns else "CountRates"

            p_arr, c_arr = df[p_col].values, df[c_col].values
            sort_idx = np.argsort(p_arr)
            p_arr, c_arr = p_arr[sort_idx], c_arr[sort_idx]

            all_pixel_data[(x_idx, y_idx)] = {"p": p_arr, "c": c_arr}

            local_bg = np.mean(c_arr[:bg_points_to_average])
            if local_bg < lowest_bg:
                lowest_bg = local_bg
                global_bg = local_bg
                global_noise = max(np.std(c_arr[:bg_points_to_average]), np.sqrt(local_bg))
        except Exception as e:
            pass

    print(f"Global Baseline: {global_bg:.1f} counts/s | Noise Floor (1σ): {global_noise:.1f} counts/s")

    # 2. Extract s_max and build Matrix
    nx = max(k[0] for k in all_pixel_data.keys()) + 1
    ny = max(k[1] for k in all_pixel_data.keys()) + 1

    s_matrix = np.full((ny, nx), np.nan)

    for (x, y), data in all_pixel_data.items():
        res = analyze_pixel_savgol(data["p"], data["c"], global_bg, global_noise,
                                   snr_threshold, 3, savgol_window, savgol_poly)

        # Only plot the pixel if the math succeeded AND it physically represents an avalanche
        if res["s_max"] is not None and res["s_max"] > 3.0:
            s_matrix[y, x] = res["s_max"]

    # 3. Create Main Heatmap Figure
    fig_map, ax_map = plt.subplots(figsize=(8, 7))
    extent = [0, scan_width_um, 0, scan_height_um]
    cmap = plt.cm.inferno.copy()
    cmap.set_bad(color='#222222')

    im = ax_map.imshow(s_matrix, origin='lower', cmap=cmap, extent=extent, interpolation='nearest')

    divider = make_axes_locatable(ax_map)
    cax = divider.append_axes("right", size="5%", pad=0.15)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label("Max nonlinearity ($s_{max}$)", fontsize=16, labelpad=15)

    ax_map.set_xlabel("x position [µm]", fontsize=16)
    ax_map.set_ylabel("y position [µm]", fontsize=16)
    ax_map.set_title("Interactive PA map (click a pixel)", fontsize=16, pad=15)

    # 4. Interactive Click Handler
    detail_fig = [None]

    def on_click(event):
        if event.inaxes != ax_map: return

        x_click_idx = int(event.xdata * (nx / scan_width_um))
        y_click_idx = int(event.ydata * (ny / scan_height_um))

        x_click_idx = max(0, min(nx - 1, x_click_idx))
        y_click_idx = max(0, min(ny - 1, y_click_idx))

        if (x_click_idx, y_click_idx) not in all_pixel_data:
            print(f"No data for pixel ({x_click_idx}, {y_click_idx})")
            return

        print(f"Plotting Pixel ({x_click_idx}, {y_click_idx})...")

        data = all_pixel_data[(x_click_idx, y_click_idx)]
        res = analyze_pixel_savgol(data["p"], data["c"], global_bg, global_noise,
                                   snr_threshold, 3, savgol_window, savgol_poly)

        if detail_fig[0] is None or not plt.fignum_exists(detail_fig[0].number):
            detail_fig[0], (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 9), sharex=True,
                                                     gridspec_kw={'height_ratios': [2, 1]})
            detail_fig[0].canvas.manager.set_window_title('Pixel detail')
            plt.show(block=False)
        else:
            ax1, ax2 = detail_fig[0].axes
            ax1.clear()
            ax2.clear()

        # Plot Panel 1: Powercurve
        ax1.plot(res["power_raw"], res["counts_raw"], 'o', color='gray', alpha=0.5, label='Raw total counts')

        if res["s_max"] is not None:
            ax1.plot(res["power_valid"], res["counts_valid"] + global_bg, 'o', color='teal', markersize=7,
                     label='Avalanche signal')
            ax1.plot(10 ** res["log_p_fine"], (10 ** res["log_c_fine"]) + global_bg, '-', color='crimson', linewidth=2,
                     label=f'SavGol fit')

            ax2.plot(10 ** res["log_p_fine"], res["slopes_fine"], '-', color='teal', linewidth=2)
            ax2.plot(res["p_at_s_max"], res["s_max"], 'o', color='crimson', markersize=8,
                     label=f's_max = {res["s_max"]:.2f}')
            ax2.axvline(res["p_at_s_max"], color='crimson', linestyle='--', alpha=0.5)

            title_str = f'Pixel ({x_click_idx}, {y_click_idx}) | $s_{{max}} = {res["s_max"]:.2f}$'
        else:
            title_str = f'Pixel ({x_click_idx}, {y_click_idx}) | No avalanche detected'

        ax1.axhline(global_bg, color='gray', linestyle='--', alpha=0.5, label='Global BG')

        ax1.axhline(global_bg + (snr_threshold * global_noise), color='orange', linestyle=':',
                    label=f'{snr_threshold}σ limit')

        ax1.set_yscale('log')
        ax1.set_xscale('log')
        ax1.set_ylabel('Luminescence [counts/s]', fontsize=14)
        ax1.set_title(title_str, fontsize=16)
        ax1.grid(True, which='both', linestyle='--', alpha=0.3)
        ax1.legend(loc='upper left', fontsize=11)

        ax2.axhline(1, color='black', linestyle=':', alpha=0.5)
        ax2.set_xscale('log')
        ax2.set_xlabel('Power [W]', fontsize=14)
        ax2.set_ylabel('Slope $s$', fontsize=14)
        ax2.grid(True, which='both', linestyle='--', alpha=0.3)
        if res["s_max"] is not None: ax2.legend(loc='upper right', fontsize=12)

        detail_fig[0].tight_layout()
        detail_fig[0].canvas.draw_idle()

    fig_map.canvas.mpl_connect('button_press_event', on_click)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    target_folder = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\20260318\20260318173630_RelativeMap"

    process_interactive_map(
        folder_path=target_folder,
        scan_width_um=10.0 / 2.0,
        scan_height_um=10.0,
        bg_points_to_average=10,
        snr_threshold=3,
        savgol_window=5,
        savgol_poly=3
    )