# Data for each LED (counts per µW/cm²)
led_data = {
    "blue": {
        "clear": 16.6,
        "red": 0.13077824868528654,
        "green": 4.117461207346864,
        "blue": 13.524622639228118
    },
    "green": {
        "clear": 20.0,
        "red": 1.3764989327915196,
        "green": 13.986639904427568,
        "blue": 4.9541234880159815
    },
    "red": {
        "clear": 23.4,
        "red": 20.996322843190026,
        "green": 1.594786260065259,
        "blue": 2.1993912841509156
    }
}

# Function to normalize the RGB values based on the Clear channel
def normalize_rgb(led_data):
    normalized_values = {}
    for led_color, values in led_data.items():
        clear = values["clear"]
        normalized_values[led_color] = {
            "red": values["red"] / clear,
            "green": values["green"] / clear,
            "blue": values["blue"] / clear
        }
    return normalized_values

# Perform the normalization
normalized_rgb = normalize_rgb(led_data)

# Display the normalized values
for led_color, values in normalized_rgb.items():
    print(f"{led_color.capitalize()} LED:")
    print(f"  Normalized Red: {values['red']:.5f}")
    print(f"  Normalized Green: {values['green']:.5f}")
    print(f"  Normalized Blue: {values['blue']:.5f}")
    print()
