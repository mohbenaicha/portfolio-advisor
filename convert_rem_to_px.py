import re

def convert_rem_to_px(input_file, output_file, base_font_size=16):
    """
    Converts rem units to px in a CSS file.

    Args:
        input_file (str): Path to the input CSS file.
        output_file (str): Path to the output CSS file.
        base_font_size (int): Base font size in pixels (default is 16px).
    """
    try:
        with open(input_file, 'r') as file:
            css_content = file.read()

        # Regular expression to find rem values
        rem_pattern = re.compile(r'([\d.]+)rem')

        # Function to replace rem with px
        def rem_to_px(match):
            rem_value = float(match.group(1))
            px_value = int(rem_value * base_font_size)
            return f"{px_value}px"

        # Replace rem values with px values
        converted_css = rem_pattern.sub(rem_to_px, css_content)

        # Write the converted CSS to the output file
        with open(output_file, 'w') as file:
            file.write(converted_css)

        print(f"Conversion complete. Converted CSS saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_css_path = 'frontend/css/styles.css'
output_css_path = 'frontend/css/styles_converted.css'
convert_rem_to_px(input_css_path, output_css_path)