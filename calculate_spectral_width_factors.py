import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

# Read the CSV file
data = pd.read_csv('TCS34725_spectral_responsivity.csv')

# Define the wavelength range for interpolation
wavelength_range = np.arange(data['Wavelength'].min(), data['Wavelength'].max() + 1, 1)

# Function to interpolate values for a given channel
def pchip_interpolate_channel(channel_data, column_name):
    pchip_func = PchipInterpolator(channel_data['Wavelength'], channel_data[column_name])
    interpolated_values = pchip_func(wavelength_range)
    return interpolated_values

# Interpolate each channel
clear_interpolated = pchip_interpolate_channel(data, 'Clear')
red_interpolated = pchip_interpolate_channel(data, 'Red')
green_interpolated = pchip_interpolate_channel(data, 'Green')
blue_interpolated = pchip_interpolate_channel(data, 'Blue')

# Function to calculate FWHM (Full Width at Half Maximum) in nm
def calculate_fwhm_width(interpolated_values):
    # Find the half-maximum value
    half_max = np.max(interpolated_values) * 0.5

    # Find indices where the values cross the half-maximum (FWHM edges)
    above_half_max = np.where(interpolated_values >= half_max)[0]

    if len(above_half_max) > 0:
        left_edge = above_half_max[0]
        right_edge = above_half_max[-1]
    else:
        raise ValueError("Could not find FWHM edges")

    # Calculate the FWHM width in nanometers
    fwhm_width = wavelength_range[right_edge] - wavelength_range[left_edge]
    return fwhm_width

# Calculate FWHM widths for each channel
clear_width = calculate_fwhm_width(clear_interpolated)
red_width = calculate_fwhm_width(red_interpolated)
green_width = calculate_fwhm_width(green_interpolated)
blue_width = calculate_fwhm_width(blue_interpolated)

# Calculate factors relative to the Clear channel width
factor_red_clear = clear_width / red_width
factor_green_clear = clear_width / green_width
factor_blue_clear = clear_width / blue_width

# Print results
print(f"FWHM Widths (in nm):")
print(f"Clear Channel Width: {clear_width:.2f} nm")
print(f"Red Channel Width: {red_width:.2f} nm")
print(f"Green Channel Width: {green_width:.2f} nm")
print(f"Blue Channel Width: {blue_width:.2f} nm")

print(f"\nWidth Factors relative to Clear channel:")
print(f"Clear/Red: {factor_red_clear}")
print(f"Clear/Green: {factor_green_clear}")
print(f"Clear/Blue: {factor_blue_clear}")
