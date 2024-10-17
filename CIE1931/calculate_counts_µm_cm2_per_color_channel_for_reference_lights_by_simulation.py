import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator

# Read the data
data = pd.read_csv('TCS34725_spectral_responsivity.csv')

# Define the full wavelength range for interpolation
wavelength_range = np.arange(data['Wavelength'].min(), data['Wavelength'].max() + 1, 1)

# PCHIP interpolation function for all channels
def pchip_interpolate_channels(channel_data):
    pchip_funcs = {}
    channels = ['Clear', 'Red', 'Green', 'Blue']
    for ch in channels:
        pchip_func = PchipInterpolator(channel_data['Wavelength'], channel_data[ch])
        pchip_funcs[ch] = pchip_func(wavelength_range)
    return pchip_funcs

# Interpolate all channels using PCHIP
interpolated_channels = pchip_interpolate_channels(data)

# Put interpolated data into a DataFrame for easier handling
interpolated_data = pd.DataFrame({'Wavelength': wavelength_range})
for ch in ['Clear', 'Red', 'Green', 'Blue']:
    interpolated_data[ch] = interpolated_channels[ch]

# Define a Gaussian function to model the LED's emission profile
def gaussian(wavelength, center, halfwidth):
    sigma = halfwidth / (2 * np.sqrt(2 * np.log(2)))  # Convert halfwidth to standard deviation
    return np.exp(-0.5 * ((wavelength - center) / sigma) ** 2)

# Define the dominant wavelengths and halfwidths for each LED, along with counts/µW/cm² from the datasheet
leds = {
    'Blue': {'center': 465, 'halfwidth': 22, 'counts_per_uW_cm2': 16.6},
    'Green': {'center': 525, 'halfwidth': 35, 'counts_per_uW_cm2': 20.0},
    'Red': {'center': 615, 'halfwidth': 15, 'counts_per_uW_cm2': 23.4}
}

# Function to calculate unitless average response based on the LED's emission curve
def calculate_unitless_avg_response(led, channel_response):
    # Generate the Gaussian-like emission curve for the LED
    emission_curve = gaussian(interpolated_data['Wavelength'], led['center'], led['halfwidth'])
    # Multiply the emission curve by the channel response
    weighted_response = emission_curve * channel_response
    # Calculate the unitless average response by integrating over the range
    avg_response_unitless = np.trapezoid(weighted_response, interpolated_data['Wavelength']) / np.trapezoid(emission_curve, interpolated_data['Wavelength'])
    return avg_response_unitless

# For each LED, calculate unitless average response for all channels
for led_name, led in leds.items():
    led['unitless_avg_responses'] = {}
    for ch in ['Clear', 'Red', 'Green', 'Blue']:
        led['unitless_avg_responses'][ch] = calculate_unitless_avg_response(led, interpolated_data[ch])

# For each LED, calculate the conversion factor using the Clear channel
for led_name, led in leds.items():
    led['conversion_factor'] = led['counts_per_uW_cm2'] / led['unitless_avg_responses']['Clear']

# For each LED, calculate counts_per_uW_cm2 for each channel
for led_name, led in leds.items():
    led['counts_per_uW_cm2_channels'] = {}
    for ch in ['Red', 'Green', 'Blue']:
        led['counts_per_uW_cm2_channels'][ch] = led['unitless_avg_responses'][ch] * led['conversion_factor']

# Output the results
for led_name, led in leds.items():
    print(f"{led_name} LED:")
    print(f"  Conversion Factor: {led['conversion_factor']}")
    print(f"  Counts per µW/cm² for Clear channel: {led['counts_per_uW_cm2']}")
    print(f"  Counts per µW/cm² for Red channel: {led['counts_per_uW_cm2_channels']['Red']}")
    print(f"  Counts per µW/cm² for Green channel: {led['counts_per_uW_cm2_channels']['Green']}")
    print(f"  Counts per µW/cm² for Blue channel: {led['counts_per_uW_cm2_channels']['Blue']}")
    print()
