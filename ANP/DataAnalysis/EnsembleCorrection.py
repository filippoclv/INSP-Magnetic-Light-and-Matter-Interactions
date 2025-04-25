import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.constants as const
from scipy.integrate import quad
import warnings

warnings.simplefilter('ignore', np.RankWarning)

# Estimating the total excitation power from studying the power reflected and transmitted by the glass panel

theta = np.array([30.0, 35.0, 40.0, 45.0]) # In degrees

power_reflected = np.array([0.26, 0.73, 4.08, 10.00]) #In mW, truncated
uncertainty_reflected = np.array([0.01, 0.01, 0.01, 0.01])

power_transmitted = np.array([2.93, 11.21, 69.50, 172.20]) # In mW
uncertainty_transmitted = np.array([0.01, 0.01, 0.01, 0.01])

data = pd.DataFrame({'theta': theta, 'power_reflected': power_reflected, 'uncertainty_reflected': uncertainty_reflected, 'power_transmitted': power_transmitted, 'uncertainty_transmitted': uncertainty_transmitted})

# Calculate the linear fit
slope, intercept = np.polyfit(data['power_reflected'], data['power_transmitted'], 1)
fit_line = slope * data['power_reflected'] + intercept

plt.plot(data['power_reflected'], data['power_transmitted'], 'o', markerfacecolor='none', label='Data')
plt.plot(data['power_reflected'], fit_line, '-', color='coral', label=f'Linear fit: Pt = ({slope:.4f}) Pr + ({intercept:.4f})')

plt.xlabel('Reflected power [mW]')
plt.ylabel('Transmitted power [mW]')
plt.title('Power transmitted vs power reflected on the glass panel')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print(f'\nPr / Pt = {1/slope:.2f}\n')

conversion_factor = 1/slope # Obtain power on the sample by dividing the measured power with this factor

single_anp = pd.read_csv('fake_single_anp.csv')
single_anp.drop(single_anp.columns[0], axis=1, inplace=True)
integration_time = 3 # In seconds

#print(single_anp)

single_anp['Power_W'] = single_anp['Power_W'] / conversion_factor
single_anp['Luminescence_counts'] = single_anp['Integrated_counts'] / integration_time
single_anp.drop(single_anp.columns[1], axis=1, inplace=True)

#print(single_anp)

plt.loglog(single_anp['Power_W'], single_anp['Luminescence_counts'], '-o', markerfacecolor='none',
           color='coral', markeredgecolor='teal', label='Single ANP power curve')
plt.xlabel('Power [W]')
plt.ylabel('Luminescence [counts/s]')
plt.title('Power curve of a single ANP sample (arbitrary measurement)')

plt.grid(True, which='both', linestyle='--', alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()

wavelength = 1064 * 1e-9 # 1064 nm

# Luminescence must be counts/s

# Gaussian beam:

# Spectrometer hole is 0.05 mm so 50 um.
# ASSUMPTION: beam radius is 532 nm, assumed half of the wavelength. So FWHM is 1.18*532 nm

FWHM = 1.18 * 532 * 1e-9
#print(f'\nFWHM = {FWHM} m')

# nu = c/lambda
# 1 W = 1 J/s

nu = const.c / wavelength
#print(f'\nnu = {nu} Hz')

hnu = const.h * nu
#print(f'\nhnu = {hnu} J') # Or W*s

#test_flux = 1.0 / hnu / (np.pi * FWHM**2 * 4)
#print(f'\nTest flux = {test_flux} 1/s/m^2')

#single_anp['NOTIR_phi_exc'] = single_anp['Power_W'] / hnu / (np.pi * FWHM**2 * 4)

# TIR case:

# ASSUMPTION: power density of the oval beam spot on the sample is constant
# ASSUMPTION: laser spot is of the same dimension in a direction and around 3 times in the other

TIR_FWHM = 3 * FWHM

#single_anp['TIR_phi_exc'] = single_anp['Power_W'] / hnu / (np.pi * TIR_FWHM*FWHM * 4)

# Flux:

single_anp['Phi_exc'] = single_anp['Power_W'] / hnu / (np.pi * FWHM**2 * 4) # NO TIR, single anp or not is irrelevant
single_anp['Phi_peak'] = single_anp['Phi_exc'] * 1.47 # Taken from the paper

plt.loglog(single_anp['Phi_peak'], single_anp['Luminescence_counts'], '-o', markerfacecolor='none',
           color='coral', markeredgecolor='teal', label='Single ANP power curve')
plt.xlabel('Phi_peak [1/s/m^2]')
plt.ylabel('Luminescence [counts/s]')
plt.title('Power curve of a single ANP sample (arbitrary measurement),\nluminescence vs flux')

plt.grid(True, which='both', linestyle='--', alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()


print(single_anp)

# I need the power curve single ANP function

power = single_anp['Power_W'].values
lum = single_anp['Luminescence_counts'].values

logP = np.log(power)
logL = np.log(lum)

degree = 20
coeffs = np.polyfit(logP, logL, degree)
poly = np.poly1d(coeffs)

power_fit = np.linspace(min(power), max(power), 500)
logP_fit = np.log(power_fit)
logL_fit = poly(logP_fit)
lum_fit = np.exp(logL_fit)

# Plot
plt.loglog(power, lum, 'o', markerfacecolor='none', label='Data', color='teal')
plt.loglog(power_fit, lum_fit, '-', color='coral', label=f'Poly fit (deg {degree})')
plt.xlabel('Power [W]')
plt.ylabel('Luminescence [counts/s]')
plt.title('Luminescence vs power, polynomial fit')
plt.grid(True, which='both', linestyle='--', alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()

#print(poly)

def powercurve_singleANP(power):

    log_power = np.log(power)
    log_lum = poly(log_power)

    return np.exp(log_lum)

P_min = power.min()
P_max = power.max()

result, error = quad(powercurve_singleANP, P_min, P_max)
print(f'\nIntegrated luminescence = {result}')