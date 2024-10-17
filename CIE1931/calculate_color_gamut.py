import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt

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
    # Find the peak responsivity
    peak_value = np.max(responsivity)
    half_max = peak_value / 2

    # Find the wavelengths where responsivity crosses half max (both sides of peak)
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

# Output the results
print(f"Red channel FWHM: {fwhm_red}, Chromaticity (x, y): {xy_red}")
print(f"Green channel FWHM: {fwhm_green}, Chromaticity (x, y): {xy_green}")
print(f"Blue channel FWHM: {fwhm_blue}, Chromaticity (x, y): {xy_blue}")

# Plot the CIE 1931 color space with the sensor's color gamut triangle
# Helper function to load and plot CIE 1931 diagram
def plot_cie_1931():
    cie_x = cie_data['x_bar'] / (cie_data['x_bar'] + cie_data['y_bar'] + cie_data['z_bar'])
    cie_y = cie_data['y_bar'] / (cie_data['x_bar'] + cie_data['y_bar'] + cie_data['z_bar'])

    plt.plot(cie_x, cie_y, label='CIE 1931 spectrum', color='black', linewidth=0.5)

# Plot the CIE diagram
plot_cie_1931()

# Plot the color gamut triangle of the sensor
triangle_x = [xy_red[0], xy_green[0], xy_blue[0], xy_red[0]]
triangle_y = [xy_red[1], xy_green[1], xy_blue[1], xy_red[1]]

plt.plot(triangle_x, triangle_y, 'r-', label='Sensor Gamut')
plt.fill(triangle_x, triangle_y, 'r', alpha=0.2)

# Labels and show
plt.scatter([xy_red[0], xy_green[0], xy_blue[0]], [xy_red[1], xy_green[1], xy_blue[1]], color=['red', 'green', 'blue'])
plt.text(xy_red[0], xy_red[1], 'Red', color='red', fontsize=12)
plt.text(xy_green[0], xy_green[1], 'Green', color='green', fontsize=12)
plt.text(xy_blue[0], xy_blue[1], 'Blue', color='blue', fontsize=12)

plt.xlabel('x')
plt.ylabel('y')
plt.title('CIE 1931 Chromaticity Diagram')
plt.legend()
plt.grid(True)
plt.show()
