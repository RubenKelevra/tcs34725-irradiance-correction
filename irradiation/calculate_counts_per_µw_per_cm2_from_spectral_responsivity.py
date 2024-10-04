import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

# Read the CSV file
data = pd.read_csv('TCS34725_spectral_responsivity.csv')

# Define the wavelength range for interpolation
wavelength_range = np.arange(int(data['Wavelength'].min()), int(data['Wavelength'].max()) + 1, 1)

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

# Function to determine FWHM of a given channel
def calculate_fwhm(wavelength, response):
    half_max = max(response) / 2
    indices = np.where(response >= half_max)[0]
    if len(indices) > 0:
        fwhm_range = wavelength[indices[0]:indices[-1] + 1]
        return fwhm_range
    else:
        return np.array([])

# Calculate FWHM ranges for each channel
fwhm_range_clear = calculate_fwhm(wavelength_range, clear_interpolated)
fwhm_range_red = calculate_fwhm(wavelength_range, red_interpolated)
fwhm_range_green = calculate_fwhm(wavelength_range, green_interpolated)
fwhm_range_blue = calculate_fwhm(wavelength_range, blue_interpolated)

# Function to calculate total response by integrating over a specified range
def calculate_total_response_in_range(interpolated_values, specific_wavelength_range):
    mask = (wavelength_range >= specific_wavelength_range.min()) & (wavelength_range <= specific_wavelength_range.max())
    total_response = np.trapezoid(interpolated_values[mask], wavelength_range[mask])
    return total_response

# Calculate total responses using FWHM ranges for each channel
clear_total_response = calculate_total_response_in_range(clear_interpolated, fwhm_range_clear)
red_total_response = calculate_total_response_in_range(red_interpolated, fwhm_range_red)
green_total_response = calculate_total_response_in_range(green_interpolated, fwhm_range_green)
blue_total_response = calculate_total_response_in_range(blue_interpolated, fwhm_range_blue)

# Calculate ratios relative to the Clear channel
red_ratio = red_total_response / clear_total_response
green_ratio = green_total_response / clear_total_response
blue_ratio = blue_total_response / clear_total_response

# Conversion factor from the Clear channel (as previously calculated)
conversion_factor = 20.797879440786556

# Adjust conversion factors for each color channel
red_conversion_factor_16x_24ms = conversion_factor * red_ratio
green_conversion_factor_16x_24ms = conversion_factor * green_ratio
blue_conversion_factor_16x_24ms = conversion_factor * blue_ratio

# Adjust conversion factors for 1x gain
gain_factor = 16  # Since the original data is at 16x gain

red_conversion_factor_1x_24ms = red_conversion_factor_16x_24ms / gain_factor
green_conversion_factor_1x_24ms = green_conversion_factor_16x_24ms / gain_factor
blue_conversion_factor_1x_24ms = blue_conversion_factor_16x_24ms / gain_factor

integration_time_factor = 2.4 / 24.0
# Adjust conversion factors for 1x gain and 2.4 ms integration time
red_conversion_factor_1x_2_4ms = red_conversion_factor_1x_24ms * integration_time_factor
green_conversion_factor_1x_2_4ms = green_conversion_factor_1x_24ms * integration_time_factor
blue_conversion_factor_1x_2_4ms = blue_conversion_factor_1x_24ms * integration_time_factor

print("Conversion Factors at 1x Gain and 2.4 ms Integration Time:")
print(f"Red Channel: {red_conversion_factor_1x_2_4ms} counts/µW/cm²")
print(f"Green Channel: {green_conversion_factor_1x_2_4ms} counts/µW/cm²")
print(f"Blue Channel: {blue_conversion_factor_1x_2_4ms} counts/µW/cm²")
