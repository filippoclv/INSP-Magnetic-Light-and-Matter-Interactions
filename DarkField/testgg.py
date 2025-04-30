
# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data_bead = pd.read_csv('SIO2_Au_30nm_bead_spectrum_0,1s.csv', sep=';')
data_background=  pd.read_csv('SIO2_Au_30nm_lamp_spectrum_1s.csv', sep=';')



bead_wavelenght = data_bead['wave length (nm)']
bead_counts = data_bead['counts']

bg_wavelenght = data_background['wave length (nm)']
bg_counts = data_background['counts']

#--------------plot du silicat et du background de cette boîte à 30nm----------------------

# plt.figure(figsize=(8,5))
# plt.scatter(bg_wavelenght,bg_counts, label = "background not normalized", s=2 , alpha =0.6)
# plt.xlabel(r"$\lambda$ (nm)")
# plt.ylabel(r"Intensity")
#plt.legend()
# plt.plot()
# plt.show()

# plt.figure(figsize=(8,5))
# plt.scatter(bead_wavelenght,bead_counts,label = "bead not normalized",s=2 , alpha =0.6)
# plt.xlabel(r"$\lambda$ (nm)")
# plt.ylabel(r"Intensity")
#plt.legend()
# plt.plot()
# plt.show()


#-------------------------------plots normalisés------------------------------------

bead_wl_normalized = bead_wavelenght / np.max(bead_wavelenght)
bead_counts_normalized = bead_counts / np.max(bead_counts)

bg_wl_normalized = bg_wavelenght / np.max(bg_wavelenght)
bg_counts_normalized = bg_counts / np.max(bg_counts)

# plt.figure(figsize=(8,5))
# plt.scatter(bead_wl_normalized,bead_counts_normalized,label = "bead normalized",s=2 , alpha =0.6)
# plt.xlabel(r"$\lambda$ (nm)")
# plt.ylabel(r"Intensity")
# plt.legend()
# plt.plot()
# plt.show()

# plt.figure(figsize=(8,5))
# plt.scatter(bg_wl_normalized,bg_counts_normalized,label = "background normalized", s=2 , alpha =0.6)
# plt.xlabel(r"$\lambda$ (nm)")
# plt.ylabel(r"Intensity")
# plt.legend()
# plt.plot()
# plt.show()


#-----------comparaison des 2 plots bof ---------------



plt.figure(figsize=(8,5))
plt.scatter(bead_wavelenght,bead_counts,label = "bead not normalized",s=2 , alpha =0.6)
plt.scatter(bg_wavelenght,bg_counts,label = "background not normalized", s=2 , alpha =0.6)
plt.xlabel(r"$\lambda$ (nm)")
plt.ylabel(r"Intensity")
plt.legend()
plt.plot()
plt.show()






















