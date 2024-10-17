import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Read the CIE1931 colour-matching functions
cie_data = pd.read_csv('CIE_xyz_1931_2deg.csv', header=None, names=['Wavelength', 'x_bar', 'y_bar', 'z_bar'])

# Define the wavelength range for the calculation
wavelength_range = np.arange(360, 831, 1)  # 1 nm steps from 360 to 830 nm

# Interpolate the CIE data to match the wavelength range
interp_funcs = {}
for color in ['x_bar', 'y_bar', 'z_bar']:
    interp_funcs[color] = interp1d(cie_data['Wavelength'], cie_data[color], kind='linear', bounds_error=False, fill_value=0)

cie_x = interp_funcs['x_bar'](wavelength_range)
cie_y = interp_funcs['y_bar'](wavelength_range)
cie_z = interp_funcs['z_bar'](wavelength_range)

# Define a Gaussian function to model the LED's emission profile
def gaussian(wavelength, center, halfwidth):
    sigma = halfwidth / (2 * np.sqrt(2 * np.log(2)))  # Convert halfwidth to standard deviation
    amplitude = 1 / (sigma * np.sqrt(2 * np.pi))  # Normalize the area under the curve to 1
    return amplitude * np.exp(-0.5 * ((wavelength - center) / sigma) ** 2)

# Define the LEDs with their dominant wavelengths and halfwidths
leds = {
    'Blue': {'center': 465, 'halfwidth': 22},
    'Green': {'center': 525, 'halfwidth': 35},
    'Red': {'center': 615, 'halfwidth': 15}
}

# Calculate the XYZ tristimulus values for each LED
for led_name, led in leds.items():
    sigma = led['halfwidth'] / (2 * np.sqrt(2 * np.log(2)))
    emission_curve = gaussian(wavelength_range, led['center'], led['halfwidth'])

    # Multiply the emission curve by the CIE colour-matching functions
    x_weighted = emission_curve * cie_x
    y_weighted = emission_curve * cie_y
    z_weighted = emission_curve * cie_z

    # Integrate over the wavelength range to get the XYZ values
    X = np.trapezoid(x_weighted, wavelength_range)
    Y = np.trapezoid(y_weighted, wavelength_range)
    Z = np.trapezoid(z_weighted, wavelength_range)

    print(f"{led_name} LED XYZ tristimulus values:")
    print(f"  X = {X:.4f}")
    print(f"  Y = {Y:.4f}")
    print(f"  Z = {Z:.4f}")
    print()
