import numpy as np

# XYZ values for the three LEDs
T = np.array([
    [0.2360, 0.0796, 1.4286],  # Blue LED
    [0.1481, 0.7430, 0.0882],  # Green LED
    [0.9225, 0.4424, 0.0003]   # Red LED
])

# Normalized RGB values for the three LEDs
S = np.array([
    [0.00788, 0.24832, 0.81474],  # Blue LED
    [0.06882, 0.69933, 0.24771],  # Green LED
    [0.89728, 0.06816, 0.09401]   # Red LED
])

# Calculate the inverse of the RGB matrix
S_inv = np.linalg.inv(S)

# Compute the transformation matrix
C = np.dot(T, S_inv)

# Display the transformation matrix
print("Transformation matrix (C):")
print(C)
