import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator

data = pd.read_csv('TCS34725_spectral_responsivity.csv')

# Define the full wavelength range for interpolation
wavelength_range = np.arange(data['Wavelength'].min(), data['Wavelength'].max() + 1, 1)

# PCHIP interpolation function for the clear channel
def pchip_interpolate_clear(channel_data):
    # Create a PCHIP interpolation function for the clear channel
    pchip_func = PchipInterpolator(channel_data['Wavelength'], channel_data['Clear'])
    # Apply interpolation to the full wavelength range (1 nm steps)
    interpolated_values = pchip_func(wavelength_range)
    return interpolated_values

# Interpolate the Clear channel using PCHIP
clear_interpolated = pchip_interpolate_clear(data)

# Put interpolated data into a DataFrame for easier handling
interpolated_data = pd.DataFrame({
    'Wavelength': wavelength_range,
    'Clear': clear_interpolated
})

# Define a Gaussian function to model the LED's emission profile
def gaussian(wavelength, center, halfwidth):
    sigma = halfwidth / (2 * np.sqrt(2 * np.log(2)))  # Convert halfwidth to standard deviation
    return np.exp(-0.5 * ((wavelength - center) / sigma) ** 2)

# Define the dominant wavelengths and halfwidths for each LED, along with counts/µW/cm² from the datasheet
leds = {
    'Blue': {'center': 465, 'halfwidth': 22 / 2, 'counts_per_uW_cm2': 13.8},
    'Green': {'center': 525, 'halfwidth': 35 / 2, 'counts_per_uW_cm2': 16.6},
    'Red': {'center': 615, 'halfwidth': 15 / 2, 'counts_per_uW_cm2': 19.5}
}

# Function to calculate unitless average response based on the LED's emission curve
def calculate_unitless_avg_response(led, channel_data):
    # Generate the Gaussian-like emission curve for the LED
    emission_curve = gaussian(channel_data['Wavelength'], led['center'], led['halfwidth'])

    # Multiply the emission curve by the Clear channel response
    weighted_response = emission_curve * channel_data['Clear']

    # Calculate the unitless average response by integrating over the range
    avg_response_unitless = np.trapezoid(weighted_response, channel_data['Wavelength']) / np.trapezoid(emission_curve, channel_data['Wavelength'])

    return avg_response_unitless

# Function to calculate the conversion factor for each LED
def calculate_conversion_factor(led, channel_data):
    # Calculate the unitless average response for the LED
    unitless_avg_response = calculate_unitless_avg_response(led, channel_data)

    # Calculate the conversion factor using the known counts/µW/cm² from the datasheet
    conversion_factor = led['counts_per_uW_cm2'] / unitless_avg_response

    return conversion_factor

# Calculate the conversion factor for each LED
blue_conversion_factor = calculate_conversion_factor(leds['Blue'], interpolated_data)
green_conversion_factor = calculate_conversion_factor(leds['Green'], interpolated_data)
red_conversion_factor = calculate_conversion_factor(leds['Red'], interpolated_data)

# Median the conversion factors to get a general scaling factor
median_conversion_factor = np.median([blue_conversion_factor, green_conversion_factor, red_conversion_factor])

# Output the results
print(f"Blue LED Conversion Factor: {blue_conversion_factor}")
print(f"Green LED Conversion Factor: {green_conversion_factor}")
print(f"Red LED Conversion Factor: {red_conversion_factor}")
print(f"Median Conversion Factor: {median_conversion_factor}")
