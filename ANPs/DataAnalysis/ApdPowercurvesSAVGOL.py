import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d


def process_apd_avalanche_data(filepath, bg_points_to_average=15, snr_threshold=3, min_consecutive_valid=3,
                               savgol_window=25, savgol_poly=3):
    """
    Physically correct APD power curves by subtracting the baseline and
    applying a strict contiguity filter to remove isolated noise spikes.
    Calculates the slope using a local Savitzky-Golay filter.
    """
    # 1. Aesthetics
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    # 2. Read Data
    df = pd.read_csv(filepath, sep="\t")
    if "CurrentPower" not in df.columns or "CountRates" not in df.columns:
        raise ValueError("File must contain 'CurrentPower' and 'CountRates' columns.")

    power = df["CurrentPower"].values
    counts_raw = df["CountRates"].values

    # 3. Physical Background Estimation
    # Averaging the first N points (pre-avalanche region) to get a stable baseline
    bg_baseline = np.mean(counts_raw[:bg_points_to_average])

    bg_std_empirical = np.std(counts_raw[:bg_points_to_average])
    bg_std_poisson = np.sqrt(bg_baseline)
    # The noise floor is bounded by Poisson physics or empirical jitter, whichever is worse
    bg_noise_floor = max(bg_std_empirical, bg_std_poisson)

    print("-" * 50)
    print(f"Physical Background Estimated: {bg_baseline:.1f} counts/s")
    print(f"Noise Floor (1 sigma):       {bg_noise_floor:.1f} counts/s")

    # 4. Background Subtraction
    counts_corrected = counts_raw - bg_baseline

    # 5. Strict Artifact Prevention (Signal-to-Noise & Contiguity)
    # First pass: Which points are above the noise threshold?
    raw_valid_mask = counts_corrected > (snr_threshold * bg_noise_floor)

    # Second pass: Remove isolated spikes (Contiguity Filter)
    # The avalanche is a runaway process; it must stay above threshold once it starts.
    avalanche_start_idx = len(raw_valid_mask)

    for i in range(len(raw_valid_mask) - min_consecutive_valid + 1):
        if np.all(raw_valid_mask[i: i + min_consecutive_valid]):
            avalanche_start_idx = i
            break

    # Create the final mask: discard everything before the continuous avalanche onset
    final_valid_mask = np.copy(raw_valid_mask)
    final_valid_mask[:avalanche_start_idx] = False

    power_valid = power[final_valid_mask]
    counts_valid = counts_corrected[final_valid_mask]

    if len(power_valid) < 4:
        raise ValueError(f"Not enough contiguous signal points above {snr_threshold}σ noise floor to perform fit.")

    # 6. Fit the Clean Avalanche Region using Savitzky-Golay
    log_power = np.log10(power_valid)
    log_counts = np.log10(counts_valid)

    # Remove duplicates if any exist (required for interpolation)
    log_power, unique_idx = np.unique(log_power, return_index=True)
    log_counts = log_counts[unique_idx]

    # Interpolate onto a dense, uniform grid (Savgol requires uniform spacing for derivatives)
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

    # Apply Savitzky-Golay filter to smooth the curve and calculate the derivative
    log_c_fine = savgol_filter(log_c_interp, window_length=wl_fine, polyorder=savgol_poly)

    dx = log_p_fine[1] - log_p_fine[0]
    slopes_fine = savgol_filter(log_c_interp, window_length=wl_fine, polyorder=savgol_poly, deriv=1, delta=dx)

    # THE FIX 2: Hard Array Truncation to permanently destroy edge artifacts
    clip_idx = wl_fine // 2
    if len(slopes_fine) > 2 * clip_idx:
        log_p_fine = log_p_fine[clip_idx:-clip_idx]
        log_c_fine = log_c_fine[clip_idx:-clip_idx]
        slopes_fine = slopes_fine[clip_idx:-clip_idx]

    # Extract maximum true slope
    s_idx = np.argmax(slopes_fine)
    s_max = slopes_fine[s_idx]
    p_at_s_max = 10 ** (log_p_fine[s_idx])

    print(f"Maximum Non-linearity (s):   {s_max:.2f} (at {p_at_s_max:.2e} W)")
    print("-" * 50)

    # --- 7. Plotting Results ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    # Panel 1: Power Curves
    ax1.plot(power, counts_raw, 'o', color='gray', alpha=0.5, label='Raw total APD counts')
    ax1.plot(power_valid, counts_valid, 'o', color='teal', markersize=7, label='Filtered avalanche signal')

    # Plot Fit
    ax1.plot(10 ** log_p_fine, 10 ** log_c_fine, '-', color='crimson', linewidth=2,
             label=f'Savitzky-Golay filter (points={wl_fine}, deg={savgol_poly})')

    # Plot Noise Floor Boundaries
    ax1.axhline(bg_baseline, color='gray', linestyle='--', alpha=0.5, label='Mean background')
    ax1.axhline(snr_threshold * bg_noise_floor, color='orange', linestyle=':',
                label=f'Detection limit ({snr_threshold}σ)')

    ax1.set_yscale('log')
    ax1.set_xscale('log')
    ax1.set_ylabel('Luminescence [counts/s]', fontsize=14)
    ax1.set_title('APD Powercurve with background removal', fontsize=16)
    ax1.grid(True, which='both', linestyle='--', alpha=0.3)
    ax1.legend(loc='upper left', fontsize=11)

    # Panel 2: Derivative (Slope)
    ax2.plot(10 ** log_p_fine, slopes_fine, '-', color='teal', linewidth=2)
    ax2.plot(p_at_s_max, s_max, 'o', color='crimson', markersize=8, label=f's_max = {s_max:.2f}')
    ax2.axvline(p_at_s_max, color='crimson', linestyle='--', alpha=0.5)

    # Reference line for linear behavior
    ax2.axhline(1, color='black', linestyle=':', alpha=0.5)

    ax2.set_xscale('log')
    ax2.set_xlabel('Power [W]', fontsize=14)
    ax2.set_ylabel('Slope $s$', fontsize=14)
    ax2.grid(True, which='both', linestyle='--', alpha=0.3)
    ax2.legend(loc='upper right', fontsize=12)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Point this to the txt file you uploaded
    file_path = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\PhD\Projects\Doughnut\20260317\20260317163246\SetInfoPowerCurve_APD.txt"

    try:
        # Note the new arguments for Savitzky-Golay: savgol_window and savgol_poly
        process_apd_avalanche_data(file_path, bg_points_to_average=15, snr_threshold=3, min_consecutive_valid=3,
                                   savgol_window=5, savgol_poly=3)
    except Exception as e:
        print(f"Error processing data: {e}")