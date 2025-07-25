# GaussianFitterAllSpectra.py
# Script for multi-Gaussian decomposition of Tm3+ 800 nm emission band in NaYF4 nanoparticles
# Based on literature: The ~800 nm band (3H4 -> 3H6 transition) is often decomposed into 3-4 overlapping Gaussians
# due to Stark splitting in the crystal field. Typical centers: ~785-795 nm, 800-805 nm, 810-815 nm (sometimes a 4th at ~820 nm).
# Sigmas (widths): 5-8 nm (FWHM ~12-19 nm). References: Various papers on Tm3+ in fluorides show 3-5 sub-peaks;
# e.g., deconvolution into 3 Gaussians in high-pressure studies (ACS Nano 2020), or high-res spectra showing sub-structure.

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import re


def multi_gaussian(x, *params):
    """
    Multi-Gaussian function: sum of individual Gaussians + baseline.
    Params: [baseline, amp1, center1, sigma1, amp2, center2, sigma2, ...]
    """
    y = params[0]  # Baseline (constant)
    for i in range(1, len(params), 3):
        amp = params[i]
        ctr = params[i + 1]
        wid = params[i + 2]
        y += amp * np.exp(-((x - ctr) ** 2) / (2 * wid ** 2))
    return y


def fit_spectrum(spectrum_df, wl_min=760, wl_max=840, num_gaussians=3, initial_guesses=None, bounds=None,
                 bg_mean=0.0, dark_rate=0.0003, read_noise=3.0, integration_time=3.0):
    """
    Fit the spectrum dataframe to num_gaussians Gaussians in the given wavelength range.

    Parameters:
    - spectrum_df: pd.DataFrame with 'Wavelength_nm' and 'Intensity_counts' columns.
    - wl_min, wl_max: Wavelength range for fitting.
    - num_gaussians: Number of Gaussian components (3-4 recommended for Tm3+ band).
    - initial_guesses: List of [amp1, ctr1, sig1, ...]; if None, auto-generates based on data and literature.
    - bounds: Tuple of (lower, upper) lists; if None, defaults to positive amps, centers in range, sigmas 1-20 nm.
    - bg_mean: Mean background counts per wavelength bin (from subtraction range, e.g., 843-844 nm).
    - dark_rate: Dark current rate in counts/pixel/second (typical 0.01-0.1 for cooled CCDs).
    - read_noise: Read noise in counts (typical 5-10 for CCD spectrometers).
    - integration_time: Exposure time in seconds (e.g., 3 s from your measurements).

    Returns:
    - popt: Optimized parameters [amp1, ctr1, sig1, ...]
    - perr: Standard errors from covariance matrix.
    """
    # Subtract background from the entire dataframe (clip to 0 to avoid negative values)
    spectrum_df['Intensity_counts'] = np.clip(spectrum_df['Intensity_counts'] - bg_mean, 0, None)

    filtered_df = spectrum_df[(spectrum_df['Wavelength_nm'] >= wl_min) & (spectrum_df['Wavelength_nm'] <= wl_max)]
    x_data = filtered_df['Wavelength_nm'].values
    y_data = filtered_df['Intensity_counts'].values

    if initial_guesses is None:
        # Auto initial guesses: based on literature and data max
        max_y = y_data.max()
        centers = [780.0, 800.0, 815.0]  # Literature-based: ~780, 800, 815 nm
        sigmas = [6.0, 6.0, 6.0]  # Typical sigma ~5-8 nm
        amps = [max_y / num_gaussians] * num_gaussians  # Equal initial amplitudes
        initial_guesses = [0.0]  # Initial baseline = 0
        for a, c, s in zip(amps, centers, sigmas):
            initial_guesses.extend([a, c, s])

    if bounds is None:
        # Tight bounds based on literature and supervisor input
        lower = [0.0] + [0, 778.0, 3.0, 0, 798.0, 3.0, 0, 813.0, 3.0]  # Per Gaussian: amp>=0, center±2 nm, sigma>=3 nm
        upper = [10.0] + [300.0, 782.0, 15.0, 300.0, 802.0, 15.0, 300.0, 817.0,
                          15.0]  # Amp<=300, center±2 nm, sigma<=15 nm
        bounds = (lower, upper)

    # Compute variance for each data point (use subtracted y_data)
    dark_counts = dark_rate * integration_time
    variance = y_data + 2 * bg_mean + dark_counts + read_noise ** 2  # Account for subtraction variance
    sigma = np.sqrt(variance)
    sigma = np.clip(sigma, 1e-6, None)  # Prevent zero or negative sigma

    try:
        popt, pcov = curve_fit(multi_gaussian, x_data, y_data, p0=initial_guesses, bounds=bounds, sigma=sigma,
                               absolute_sigma=True, maxfev=10000)
        perr = np.sqrt(np.diag(pcov))
    except Exception as e:
        print(f"Fitting failed: {e}")
        return None, None

    # Compute goodness of fit (reduced chi-squared)
    y_fit = multi_gaussian(x_data, *popt)
    residuals = y_data - y_fit
    chi2 = np.sum((residuals / sigma) ** 2)
    dof = len(x_data) - len(popt)
    reduced_chi2 = chi2 / dof
    print(f"Reduced chi-squared: {reduced_chi2:.2f}")

    return popt, perr


def plot_fit(spectrum_df, popt, wl_min=760, wl_max=840, num_gaussians=3, title="Gaussian Fit"):
    """
    Plot the data, total fit, and individual Gaussian components.
    """
    filtered_df = spectrum_df[(spectrum_df['Wavelength_nm'] >= wl_min) & (spectrum_df['Wavelength_nm'] <= wl_max)]
    x_data = filtered_df['Wavelength_nm'].values
    y_data = filtered_df['Intensity_counts'].values

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # Main plot
    ax1.plot(x_data, y_data, 'b-', label='Data')
    y_fit = multi_gaussian(x_data, *popt)
    ax1.plot(x_data, y_fit, 'r--', label='Total Fit')

    colors = plt.cm.viridis(np.linspace(0, 1, num_gaussians))
    baseline = popt[0]
    ax1.axhline(baseline, color='gray', linestyle=':', label=f'Baseline: {baseline:.1f}')
    for i in range(num_gaussians):
        start = 1 + i * 3  # Skip baseline
        amp, ctr, wid = popt[start:start + 3]
        y_comp = multi_gaussian(x_data, 0, amp, ctr, wid)  # Individual without baseline
        ax1.plot(x_data, y_comp, '--', color=colors[i], label=f'G{i + 1}: μ={ctr:.1f} nm, σ={wid:.1f} nm')

    ax1.set_ylabel('Intensity [counts]', fontsize=16)
    ax1.set_title(title, fontsize=18)
    ax1.legend(fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=14)

    # Residuals
    residuals = y_data - y_fit
    ax2.plot(x_data, residuals, 'k.', label='Residuals')
    ax2.axhline(0, color='r', linestyle='--')
    ax2.set_xlabel('Wavelength [nm]', fontsize=16)
    ax2.set_ylabel('Residuals', fontsize=16)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=14)

    plt.tight_layout()
    plt.show()


def load_spectrum_txt(file_path):
    """
    Load a spectrum .txt file into a Pandas DataFrame.
    Handles wavelength with comma as decimal separator.
    """
    wavelengths = []
    intensities = []
    with open(file_path, 'r') as f:
        for line in f:
            if '=' in line or not ';' in line:  # Skip headers
                continue
            wl_str, int_str = line.strip().split(';')
            wl = float(wl_str.replace(',', '.'))
            intensity = int(int_str.strip())
            wavelengths.append(wl)
            intensities.append(intensity)
    df = pd.DataFrame({'Wavelength_nm': wavelengths, 'Intensity_counts': intensities})
    return df


def all_spectra_dataframe_dict_nearfield_heights(folder_path):
    folder = Path(folder_path)

    height_info_file = folder / "SetInfoScanHeight.txt"
    height_info = pd.read_csv(height_info_file, sep="\t")
    height_map = dict(zip(height_info["Zindex"], height_info["Height"]))

    spectra_dict = {}

    files = sorted(folder.glob("Z*.txt"), key=lambda f: int(re.search(r"Z(\d+)", f.name).group(1)))

    for file_path in files:
        data = load_spectrum_txt(file_path)
        height_label_extracted = re.search(r"Z(\d+)", file_path.name)
        if height_label_extracted:
            height_label = height_label_extracted.group(1)
            height_index = int(height_label)
            data.attrs = {}
            data.attrs["Height_label"] = f"Z{height_label}"
            data.attrs["Height_mV"] = height_map.get(height_index)
        spectra_dict[data.attrs["Height_label"]] = data

    return spectra_dict


def fit_all_heights(spectra_dict, wl_min=760, wl_max=840, num_gaussians=3, dark_rate=0.0003, read_noise=3.0,
                    integration_time=3.0):
    """
    Fit Gaussians to all heights in spectra_dict.
    Returns dict of height: {'popt': array, 'perr': array, 'areas': list}.
    """
    results = {}
    for label, df in spectra_dict.items():
        # Calculate bg_mean from 843-844 nm range for each spectrum
        bg_region = df[(df['Wavelength_nm'] >= 843) & (df['Wavelength_nm'] <= 844)]
        bg_mean = bg_region['Intensity_counts'].mean() if not bg_region.empty else 0.0
        print(f"Calculated bg_mean for {label}: {bg_mean:.2f}")

        height = df.attrs.get("Height_mV", "Unknown")
        popt, perr = fit_spectrum(df, wl_min, wl_max, num_gaussians, bg_mean=bg_mean, dark_rate=dark_rate,
                                  read_noise=read_noise, integration_time=integration_time)
        if popt is not None:
            areas = [popt[start] * popt[start + 2] * np.sqrt(2 * np.pi) for start in
                     range(1, len(popt), 3)]  # Area = amp * sigma * sqrt(2pi)
            results[height] = {'popt': popt, 'perr': perr, 'areas': areas}
            plot_fit(df, popt, wl_min, wl_max, num_gaussians,
                     title=f"Gaussian fit to {label} spectrum, P=90%, t=3s, height {height} mV")

    # Save to CSV and plot amps/areas vs height
    if results:
        df_results = pd.DataFrame.from_dict(results, orient='index')
        df_results.to_csv('fit_results.csv')
        heights = sorted(results.keys())
        for g in range(num_gaussians):
            amps = [results[h]['popt'][1 + 3 * g] for h in heights]  # Amp for Gaussian g
            areas = [results[h]['areas'][g] for h in heights]
            fig, ax1 = plt.subplots()
            ax1.plot(heights, amps, 'b-o', label='Amp')
            ax1.set_xlabel('Height (mV)')
            ax1.set_ylabel('Amplitude (counts)', color='b')
            ax2 = ax1.twinx()
            ax2.plot(heights, areas, 'g--o', label='Area')
            ax2.set_ylabel('Area', color='g')
            plt.title(f'Gaussian {g + 1} Amp and Area vs Height')
            plt.grid(True)
            plt.show()

    return results


# Example usage (integrate with your project by passing a spectrum dataframe from all_spectra_dict)
if __name__ == "__main__":
    folder_path = r"C:\Users\Filippo Calavaro\Documents\Filippo Calavaro\Data\20250722\20250722142045"  # Update to your folder path
    spectra_dict = all_spectra_dataframe_dict_nearfield_heights(folder_path)
    fit_results = fit_all_heights(spectra_dict)