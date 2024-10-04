import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt

# Counts to irradiance conversion factors (counts per μW/cm²)
C_red = 0.030895152730118627
C_green = 0.032402966993759885
C_blue = 0.03695911040578352

# Read the sensor spectral responsivity data
sensor_data = pd.read_csv('TCS34725_spectral_responsivity.csv')

# Extract wavelengths and relative channel responses
wavelengths_sensor = sensor_data['Wavelength'].values
red_response_rel = sensor_data['Red'].values
green_response_rel = sensor_data['Green'].values
blue_response_rel = sensor_data['Blue'].values

# Scale the spectral responses using the counts-to-irradiance factors
# Since the factors are in counts per μW/cm², we'll use the inverse to get relative scaling
red_response_scaled = red_response_rel / C_red
green_response_scaled = green_response_rel / C_green
blue_response_scaled = blue_response_rel / C_blue

# Combine all scaled responses to find the global maximum for normalization
all_scaled_responses = np.concatenate([np.abs(red_response_scaled),
                                       np.abs(green_response_scaled),
                                       np.abs(blue_response_scaled)])
global_max = np.max(all_scaled_responses)

# Normalize the scaled spectral responses using the global maximum
red_response_norm = red_response_scaled / global_max
green_response_norm = green_response_scaled / global_max
blue_response_norm = blue_response_scaled / global_max

# Read the CIE photopic luminous efficiency function
cie_data = pd.read_csv('CIE_sle_photopic.csv', header=None, names=['Wavelength', 'V_lambda'])
wavelengths_cie = cie_data['Wavelength'].values
V_lambda = cie_data['V_lambda'].values

# Define the interpolation wavelengths (common wavelength range)
wavelength_min = max(wavelengths_sensor.min(), wavelengths_cie.min())
wavelength_max = min(wavelengths_sensor.max(), wavelengths_cie.max())
wavelengths_interp = np.arange(wavelength_min, wavelength_max + 1, 1)  # 1 nm steps

# Interpolate sensor responses using PCHIP interpolation
def interpolate_response(wavelengths, response, wavelengths_interp):
    pchip = PchipInterpolator(wavelengths, response, extrapolate=False)
    response_interp = pchip(wavelengths_interp)
    response_interp = np.nan_to_num(response_interp)
    return response_interp

# Interpolate the normalized spectral responses
red_interp = interpolate_response(wavelengths_sensor, red_response_norm, wavelengths_interp)
green_interp = interpolate_response(wavelengths_sensor, green_response_norm, wavelengths_interp)
blue_interp = interpolate_response(wavelengths_sensor, blue_response_norm, wavelengths_interp)

# Interpolate the CIE photopic luminous efficiency function
V_lambda_interp = interpolate_response(wavelengths_cie, V_lambda, wavelengths_interp)

# Plot the normalized spectral responses and V(λ)
plt.figure(figsize=(10, 6))
plt.plot(wavelengths_interp, red_interp, label='Normalized Red Response')
plt.plot(wavelengths_interp, green_interp, label='Normalized Green Response')
plt.plot(wavelengths_interp, blue_interp, label='Normalized Blue Response')
plt.plot(wavelengths_interp, V_lambda_interp / np.max(V_lambda_interp), label='Normalized V(λ)')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Normalized Response')
plt.title('Normalized Spectral Responses and CIE Photopic Curve')
plt.legend()
plt.grid(True)
plt.show()

# Determine the FWHM for each channel
def calculate_fwhm(wavelengths, response):
    half_max = np.max(response) / 2.0
    indices = np.where(response >= half_max)[0]
    if len(indices) >= 2:
        fwhm_range = wavelengths[indices[0]], wavelengths[indices[-1]]
    else:
        fwhm_range = None
    return fwhm_range

red_fwhm = calculate_fwhm(wavelengths_interp, red_interp)
green_fwhm = calculate_fwhm(wavelengths_interp, green_interp)
blue_fwhm = calculate_fwhm(wavelengths_interp, blue_interp)

print("FWHM ranges:")
print(f"Red channel:   {red_fwhm}")
print(f"Green channel: {green_fwhm}")
print(f"Blue channel:  {blue_fwhm}")

# Function to integrate over the FWHM range
def integrate_over_fwhm(wavelengths, response, V_lambda):
    fwhm_range = calculate_fwhm(wavelengths, response)
    if fwhm_range is not None:
        idx_start = np.searchsorted(wavelengths, fwhm_range[0])
        idx_end = np.searchsorted(wavelengths, fwhm_range[1]) + 1
        wavelengths_fwhm = wavelengths[idx_start:idx_end]
        response_fwhm = response[idx_start:idx_end]
        V_lambda_fwhm = V_lambda[idx_start:idx_end]
        weighted_response = response_fwhm * V_lambda_fwhm
        integral = np.sum(weighted_response)
        return integral
    else:
        return 0.0

# Integrate the weighted responses over the FWHM range
red_factor = integrate_over_fwhm(wavelengths_interp, red_interp, V_lambda_interp)
green_factor = integrate_over_fwhm(wavelengths_interp, green_interp, V_lambda_interp)
blue_factor = integrate_over_fwhm(wavelengths_interp, blue_interp, V_lambda_interp)

print("Channel factors (unitless):")
print(f"Red factor:   {red_factor}")
print(f"Green factor: {green_factor}")
print(f"Blue factor:  {blue_factor}")

# Normalize the channel factors
total_factor = red_factor + green_factor + blue_factor
red_factor_norm = red_factor / total_factor
green_factor_norm = green_factor / total_factor
blue_factor_norm = blue_factor / total_factor

print("Normalized channel factors (unitless):")
print(f"Red factor:   {red_factor_norm}")
print(f"Green factor: {green_factor_norm}")
print(f"Blue factor:  {blue_factor_norm}")

# Apply a known irradiance to illuminance conversion factor for white light
# For standard illuminant D65 (average daylight), the conversion is approximately 0.0079 W/m² per lux
# Convert to μW/cm² per lux: 0.0079 W/m² = 790 μW/cm² per lux
irradiance_per_lux = 0.0079  # W/m² per lux

# Convert W/m² to μW/cm²
irradiance_per_lux_uW_cm2 = irradiance_per_lux * 100  # μW/cm² per lux

# Compute the total conversion factor from irradiance (μW/cm²) to illuminance (lux)
K_total = 1 / irradiance_per_lux_uW_cm2  # Total conversion factor in lux per μW/cm²

# Distribute the total conversion factor according to the normalized channel factors
K_red = K_total * red_factor_norm
K_green = K_total * green_factor_norm
K_blue = K_total * blue_factor_norm

print("Conversion factors (K_channel) in lux per μW/cm²:")
print(f"Red channel:   K_red = {K_red:.15f} lux per μW/cm²")
print(f"Green channel: K_green = {K_green:.15f} lux per μW/cm²")
print(f"Blue channel:  K_blue = {K_blue:.15f} lux per μW/cm²")
