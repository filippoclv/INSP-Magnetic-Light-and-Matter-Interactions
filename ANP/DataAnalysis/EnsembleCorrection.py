import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
plt.plot(data['power_reflected'], fit_line, '-', color='red', label=f'Linear fit: Pt = ({slope:.4f}) Pr + ({intercept:.4f})')

plt.xlabel('Reflected power [mW]')
plt.ylabel('Transmitted power [mW]')
plt.title('Power transmitted vs power reflected on the glass panel')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print(f'\nPr / Pt = {1/slope:.2f}')