# Irradiation:

- Used engauge to get the color curves from the spectral resonsivity curve from the spec sheet (TCS34725_color_curve.jxl).
- This is saved in the TCS34725_color_curve.dig file for future modifications
- Results are exported into the TCS34725_spectral_responsivity.csv
- The "Optical Characteristics" page in the spec sheet notes several light specs and the responses of the clear channel to those lights in irradiance per units of the sensor (called counts).
- So we simulate those lights onto the responsivity curve, to convert the unitless graph's (TCS34725_color_curve.jxl) Y axis into counts per µW/cm², this is done in `calculate_conversion_factor_for_graph_data_to_µm_per_cm2_response_by_simulation.py`.
- This gives us the conversion factor of `20.797879440786556`, which we add to `calculate_counts_per_µw_per_cm2_from_spectral_responsivity.py`
- Afterwards we can calculate the average responsivity of each color channel, convert it to counts/µW/cm² - this is done with `calculate_counts_per_µw_per_cm2_from_spectral_responsivity.py`.

# Lux:

CIE Dataset: https://cie.co.at/datatable/cie-spectral-luminous-efficiency-photopic-vision


