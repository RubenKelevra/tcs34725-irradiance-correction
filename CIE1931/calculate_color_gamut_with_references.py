import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

# Load CIE 1931 color-matching functions
cie_file = 'CIE_xyz_1931_2deg.csv'
cie_data = pd.read_csv(cie_file, header=None, names=['Wavelength', 'x_bar', 'y_bar', 'z_bar'])

# Load sensor responsivity curves
sensor_file = 'TCS34725_spectral_responsivity.csv'
sensor_data = pd.read_csv(sensor_file)

# Create a 1 nm wavelength grid (360 nm to 830 nm) for the interpolation
wavelengths = np.arange(360, 831, 1)  # Target range in nm

# Interpolation function to resample the sensor data to the 1nm CIE wavelength grid
def interpolate_sensor(sensor_data, channel):
    interpolator = PchipInterpolator(sensor_data['Wavelength'], sensor_data[channel], extrapolate=False)
    return interpolator(wavelengths)

# Interpolated values for each channel on the 1 nm grid
interpolated_responsivity = {}
for channel in ['Clear', 'Red', 'Blue', 'Green']:
    interpolated_responsivity[channel] = interpolate_sensor(sensor_data, channel)

# Calculate FWHM for each channel (Red, Green, Blue)
def calculate_fwhm(responsivity, wavelengths):
    peak_value = np.max(responsivity)
    half_max = peak_value / 2
    left_idx = np.where(responsivity >= half_max)[0][0]
    right_idx = np.where(responsivity >= half_max)[0][-1]
    left_wavelength = wavelengths[left_idx]
    right_wavelength = wavelengths[right_idx]
    return left_wavelength, right_wavelength

# FWHM wavelengths for Red, Green, and Blue channels
fwhm_red = calculate_fwhm(interpolated_responsivity['Red'], wavelengths)
fwhm_green = calculate_fwhm(interpolated_responsivity['Green'], wavelengths)
fwhm_blue = calculate_fwhm(interpolated_responsivity['Blue'], wavelengths)

# Interpolate CIE matching functions to match wavelength ranges
def interpolate_cie(cie_data, wavelength_range):
    interp_x = PchipInterpolator(cie_data['Wavelength'], cie_data['x_bar'])(wavelength_range)
    interp_y = PchipInterpolator(cie_data['Wavelength'], cie_data['y_bar'])(wavelength_range)
    interp_z = PchipInterpolator(cie_data['Wavelength'], cie_data['z_bar'])(wavelength_range)
    return interp_x, interp_y, interp_z

# Calculate XYZ for the FWHM edges of each channel
def calculate_xyz_for_wavelengths(wavelength_range, cie_data):
    interp_x, interp_y, interp_z = interpolate_cie(cie_data, wavelength_range)
    X = np.trapz(interp_x, wavelength_range)
    Y = np.trapz(interp_y, wavelength_range)
    Z = np.trapz(interp_z, wavelength_range)
    return X, Y, Z

# Generate wavelength ranges based on FWHM
wavelength_range_red = np.linspace(fwhm_red[0], fwhm_red[1], int(fwhm_red[1] - fwhm_red[0]))
wavelength_range_green = np.linspace(fwhm_green[0], fwhm_green[1], int(fwhm_green[1] - fwhm_green[0]))
wavelength_range_blue = np.linspace(fwhm_blue[0], fwhm_blue[1], int(fwhm_blue[1] - fwhm_blue[0]))

XYZ_red = calculate_xyz_for_wavelengths(wavelength_range_red, cie_data)
XYZ_green = calculate_xyz_for_wavelengths(wavelength_range_green, cie_data)
XYZ_blue = calculate_xyz_for_wavelengths(wavelength_range_blue, cie_data)

# Normalize and calculate chromaticity coordinates (x, y) for each channel
def calculate_chromaticity(X, Y, Z):
    total = X + Y + Z
    if total == 0:
        return 0, 0  # Avoid division by zero
    x = X / total
    y = Y / total
    return x, y

xy_red = calculate_chromaticity(*XYZ_red)
xy_green = calculate_chromaticity(*XYZ_green)
xy_blue = calculate_chromaticity(*XYZ_blue)

# Plotting the sensor's calculated FWHM chromaticity coordinates
sensor_gamut_x = [xy_red[0], xy_green[0], xy_blue[0], xy_red[0]]
sensor_gamut_y = [xy_red[1], xy_green[1], xy_blue[1], xy_red[1]]

# Predefined color gamuts (NTSC, sRGB, AdobeRGB, DCI-P3, Rec. 2020)
gamuts = {
    'NTSC': {'R': (0.67, 0.33), 'G': (0.21, 0.71), 'B': (0.14, 0.08)},
    'sRGB': {'R': (0.64, 0.33), 'G': (0.30, 0.60), 'B': (0.15, 0.06)},
    'AdobeRGB': {'R': (0.64, 0.33), 'G': (0.21, 0.71), 'B': (0.15, 0.06)},
    'DCI-P3': {'R': (0.680, 0.320), 'G': (0.265, 0.690), 'B': (0.150, 0.060)},
    'Rec. 2020': {'R': (0.708, 0.292), 'G': (0.170, 0.797), 'B': (0.131, 0.046)}
}

# Plot the CIE 1931 color space and the color gamuts
def plot_cie_1931():
    cie_x = cie_data['x_bar'] / (cie_data['x_bar'] + cie_data['y_bar'] + cie_data['z_bar'])
    cie_y = cie_data['y_bar'] / (cie_data['x_bar'] + cie_data['y_bar'] + cie_data['z_bar'])
    plt.plot(cie_x, cie_y, label='CIE 1931 spectrum', color='black', linewidth=0.5)

plot_cie_1931()

# Plot sensor gamut
plt.plot(sensor_gamut_x, sensor_gamut_y, 'r-', label='Sensor Gamut')
plt.fill(sensor_gamut_x, sensor_gamut_y, 'r', alpha=0.2)

# Plot each predefined gamut with labels
colors = ['blue', 'green', 'orange', 'purple', 'cyan']
for i, (gamut_name, coords) in enumerate(gamuts.items()):
    gamut_x = [coords['R'][0], coords['G'][0], coords['B'][0], coords['R'][0]]
    gamut_y = [coords['R'][1], coords['G'][1], coords['B'][1], coords['R'][1]]
    plt.plot(gamut_x, gamut_y, label=gamut_name, color=colors[i])
    plt.fill(gamut_x, gamut_y, color=colors[i], alpha=0.1)

# Add labels
plt.xlabel('x')
plt.ylabel('y')
plt.title('CIE 1931 Chromaticity Diagram with Reference Color Gamuts')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
