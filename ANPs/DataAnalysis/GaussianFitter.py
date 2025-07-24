# GaussianFitter.py
# Script for multi-Gaussian decomposition of Tm3+ 800 nm emission band in NaYF4 nanoparticles
# Based on literature: The ~800 nm band (3H4 -> 3H6 transition) is often decomposed into 3-4 overlapping Gaussians
# due to Stark splitting in the crystal field. Typical centers: ~785-795 nm, 800-805 nm, 810-815 nm (sometimes a 4th at ~820 nm).
# Sigmas (widths): 5-8 nm (FWHM ~12-19 nm). References: Various papers on Tm3+ in fluorides show 3-5 sub-peaks;
# e.g., deconvolution into 3 Gaussians in high-pressure studies (ACS Nano 2020), or high-res spectra showing sub-structure.

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd


def multi_gaussian(x, *params):
    """
    Multi-Gaussian function: sum of individual Gaussians.
    Params: [amp1, center1, sigma1, amp2, center2, sigma2, ...]
    """
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        amp = params[i]
        ctr = params[i + 1]
        wid = params[i + 2]
        y += amp * np.exp(-((x - ctr) ** 2) / (2 * wid ** 2))
    return y


def fit_spectrum(spectrum_df, wl_min=760, wl_max=840, num_gaussians=3, initial_guesses=None, bounds=None):
    """
    Fit the spectrum dataframe to num_gaussians Gaussians in the given wavelength range.

    Parameters:
    - spectrum_df: pd.DataFrame with 'Wavelength_nm' and 'Intensity_counts' columns.
    - wl_min, wl_max: Wavelength range for fitting.
    - num_gaussians: Number of Gaussian components (3-4 recommended for Tm3+ band).
    - initial_guesses: List of [amp1, ctr1, sig1, ...]; if None, auto-generates based on data and literature.
    - bounds: Tuple of (lower, upper) lists; if None, defaults to positive amps, centers in range, sigmas 1-20 nm.

    Returns:
    - popt: Optimized parameters [amp1, ctr1, sig1, ...]
    - perr: Standard errors from covariance matrix.
    """
    filtered_df = spectrum_df[(spectrum_df['Wavelength_nm'] >= wl_min) & (spectrum_df['Wavelength_nm'] <= wl_max)]
    x_data = filtered_df['Wavelength_nm'].values
    y_data = filtered_df['Intensity_counts'].values

    if initial_guesses is None:
        # Auto initial guesses: evenly spaced centers, sigmas ~6 nm, amps ~ max / num_gaussians
        max_y = y_data.max()
        centers = np.linspace(785, 815, num_gaussians)  # Literature-inspired: 785, ~800, 815 for 3
        sigmas = [6.0] * num_gaussians  # Typical sigma ~5-8 nm
        amps = [max_y / num_gaussians] * num_gaussians
        initial_guesses = []
        for a, c, s in zip(amps, centers, sigmas):
            initial_guesses.extend([a, c, s])

    if bounds is None:
        # Bounds to prevent unphysical fits
        lower = [0, wl_min, 1] * num_gaussians
        upper = [np.inf, wl_max, 20] * num_gaussians
        bounds = (lower, upper)

    try:
        popt, pcov = curve_fit(multi_gaussian, x_data, y_data, p0=initial_guesses, bounds=bounds, maxfev=5000)
        perr = np.sqrt(np.diag(pcov))
    except Exception as e:
        print(f"Fitting failed: {e}")
        return None, None

    # Compute goodness of fit (reduced chi-squared)
    y_fit = multi_gaussian(x_data, *popt)
    residuals = y_data - y_fit
    chi2 = np.sum(residuals ** 2 / y_fit)  # Approximate, assuming Poisson noise ~sqrt(y_fit) but simplified
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
    for i in range(num_gaussians):
        start = i * 3
        amp, ctr, wid = popt[start:start + 3]
        y_comp = multi_gaussian(x_data, amp, ctr, wid)
        ax1.plot(x_data, y_comp, '--', color=colors[i], label=f'G{i + 1}: μ={ctr:.1f} nm, σ={wid:.1f} nm')

    ax1.set_ylabel('Intensity (counts)')
    ax1.set_title(title)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Residuals
    residuals = y_data - y_fit
    ax2.plot(x_data, residuals, 'k.', label='Residuals')
    ax2.axhline(0, color='r', linestyle='--')
    ax2.set_xlabel('Wavelength (nm)')
    ax2.set_ylabel('Residuals')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# Example usage (integrate with your project by passing a spectrum dataframe from all_spectra_dict)
if __name__ == "__main__":
    # For testing: simulate a spectrum (replace with your data loading)
    wl = np.linspace(760, 840, 500)
    intensity = (100 * np.exp(-((wl - 785) ** 2) / (2 * 6 ** 2)) +
                 250 * np.exp(-((wl - 800) ** 2) / (2 * 7 ** 2)) +
                 180 * np.exp(-((wl - 810) ** 2) / (2 * 5 ** 2)) +
                 120 * np.exp(-((wl - 820) ** 2) / (2 * 6 ** 2)) + np.random.normal(0, 10, 500))
    test_df = pd.DataFrame({'Wavelength_nm': wl, 'Intensity_counts': intensity})

    # Fit with 4 Gaussians (adjust num_gaussians as needed)
    popt, perr = fit_spectrum(test_df, num_gaussians=4)
    if popt is not None:
        print("Fitted parameters (amp, center, sigma ± err):")
        for i in range(0, len(popt), 3):
            print(f"Gaussian {i // 3 + 1}: amp={popt[i]:.2f} ± {perr[i]:.2f}, "
                  f"center={popt[i + 1]:.2f} ± {perr[i + 1]:.2f} nm, "
                  f"sigma={popt[i + 2]:.2f} ± {perr[i + 2]:.2f} nm")
        plot_fit(test_df, popt, num_gaussians=4, title="Test Fit to Simulated Tm3+ Spectrum")