import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def process_apd_avalanche_data(filepath, bg_points_to_average=15, snr_threshold=3, min_consecutive_valid=3,
                               poly_degree=4):
    """
    Physically correct APD power curves by subtracting the baseline and
    applying a strict contiguity filter to remove isolated noise spikes.
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

    if len(power_valid) <= poly_degree:
        raise ValueError(f"Not enough contiguous signal points above {snr_threshold}σ noise floor to perform fit.")

    # 6. Fit the Clean Avalanche Region
    log_power = np.log10(power_valid)
    log_counts = np.log10(counts_valid)

    fit_coeffs = np.polyfit(log_power, log_counts, deg=poly_degree)
    poly_func = np.poly1d(fit_coeffs)
    deriv_func = np.polyder(poly_func)

    # Generate fine points for smooth plotting
    log_p_fine = np.linspace(log_power.min(), log_power.max(), 300)
    log_c_fine = poly_func(log_p_fine)
    slopes_fine = deriv_func(log_p_fine)

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
             label=f'Polynomial fit (deg={poly_degree})')

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
        # I bumped bg_points_to_average to 15, since you have 100 points and the first chunk is beautifully flat.
        process_apd_avalanche_data(file_path, bg_points_to_average=15, snr_threshold=3, min_consecutive_valid=3,
                                   poly_degree=4)
    except Exception as e:
        print(f"Error processing data: {e}")