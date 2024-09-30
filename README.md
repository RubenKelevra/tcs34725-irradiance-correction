# Process of correction:

- Used engauge to get the color curves from the spectral resonsivity curve from the spec sheet (TCS34725_color_curve.jxl).
- This is saved in the TCS34725_color_curve.dig file for future modifications
- Results are exported into the TCS34725_spectral_responsivity.csv
- The "Optical Characteristics" page in the spec sheet notes several light specs and the responses of the clear channel to those lights in irradiance per units of the sensor (called counts).
- So we simulate those lights onto the responsivity curve, to convert the unitless graph's (TCS34725_color_curve.jxl) Y axis into counts per µW/cm², this is done in `calculate_conversion_factor_for_graph_data_to_µm_per_cm2_response_by_simulation.py`.
- This gives us the conversion factor of `20.90876186340115`, which we add to `calculate_counts_per_µw_per_cm2_from_spectral_responsivity.py`
- Now we need factors of the different channel width, meaning how often red, green, blue's channel width fit into the clear channel. This is done width `calculate_spectral_width_factors.py`, which we add to `calculate_counts_per_µw_per_cm2_from_spectral_responsivity.py`, too.
- Afterwards we can calculate the average responsivity of each color channel's FWHM, convert it to counts/µW/cm² and correct the result for the smaller channel width with the factors we just calculated - this is done with `calculate_counts_per_µw_per_cm2_from_spectral_responsivity.py`.
