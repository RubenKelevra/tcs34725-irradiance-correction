import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

data = pd.read_csv('TCS34725_spectral_responsivity.csv')

# Define the wavelength range for interpolation
wavelength_range = np.arange(data['Wavelength'].min(), data['Wavelength'].max() + 1, 1)

# Interpolation function for each color channel
def pchip_interpolate_channel(channel_data, column_name):
    pchip_func = PchipInterpolator(channel_data['Wavelength'], channel_data[column_name])
    interpolated_values = pchip_func(wavelength_range)
    return interpolated_values

# Interpolating Red, Green, and Blue channels
red_interpolated = pchip_interpolate_channel(data, 'Red')
green_interpolated = pchip_interpolate_channel(data, 'Green')
blue_interpolated = pchip_interpolate_channel(data, 'Blue')

# Function to calculate FWHM and average response within the FWHM range
def calculate_fwhm_and_avg_response(channel_name, interpolated_values):
    # Find the peak value
    peak_value = np.max(interpolated_values)

    # Find the half-maximum value (50% of peak)
    half_max = peak_value * 0.5

    # Find indices where the values cross the half-maximum (FWHM edges)
    above_half_max = np.where(interpolated_values >= half_max)[0]

    if len(above_half_max) > 0:
        left_edge = above_half_max[0]
        right_edge = above_half_max[-1]
    else:
        raise ValueError(f"Could not find FWHM for {channel_name}")

    # Extract the wavelength range corresponding to FWHM
    fwhm_range = wavelength_range[left_edge:right_edge + 1]
    fwhm_responses = interpolated_values[left_edge:right_edge + 1]

    # Calculate the average response within the FWHM range
    avg_response = np.mean(fwhm_responses)

    # Return the FWHM range as the min and max wavelengths
    return fwhm_range.min(), fwhm_range.max(), avg_response, peak_value

# Calculate FWHM and average response for each color channel
red_min_fwhm, red_max_fwhm, red_avg_response, red_peak = calculate_fwhm_and_avg_response("Red", red_interpolated)
green_min_fwhm, green_max_fwhm, green_avg_response, green_peak = calculate_fwhm_and_avg_response("Green", green_interpolated)
blue_min_fwhm, blue_max_fwhm, blue_avg_response, blue_peak = calculate_fwhm_and_avg_response("Blue", blue_interpolated)

# Conversion factor
conversion_factor = 20.90876186340115
spectral_width_conversion_factor_red=3.9464285714285716
spectral_width_conversion_factor_green=2.7974683544303796
spectral_width_conversion_factor_blue=2.1666666666666665

# Apply the conversion factor
red_avg_response_converted = red_avg_response * conversion_factor
green_avg_response_converted = green_avg_response * conversion_factor
blue_avg_response_converted = blue_avg_response * conversion_factor

# Output the results (printing min and max FWHM range)
print(f"Red Channel FWHM Range: {red_min_fwhm} nm to {red_max_fwhm} nm")
print(f"Red Channel Average Response: {red_avg_response}, Converted to counts/µW/cm² for 1x gain: {red_avg_response_converted/spectral_width_conversion_factor_red}")

print(f"Green Channel FWHM Range: {green_min_fwhm} nm to {green_max_fwhm} nm")
print(f"Green Channel Average Response: {green_avg_response}, Converted to counts/µW/cm² for 1x gain: {green_avg_response_converted/spectral_width_conversion_factor_green}")

print(f"Blue Channel FWHM Range: {blue_min_fwhm} nm to {blue_max_fwhm} nm")
print(f"Blue Channel Average Response: {blue_avg_response}, Converted to counts/µW/cm² for 1x gain: {blue_avg_response_converted/spectral_width_conversion_factor_blue}")
