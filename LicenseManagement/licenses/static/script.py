import re

def extract_colors(css_text):
    """Extract all colors from CSS text."""
    color_regex = r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+(?:\s*,\s*\d+)?\s*\)'
    colors = re.findall(color_regex, css_text)
    return set(colors)

def generate_dark_mode_css(css_text, colors):
    """Generate dark mode CSS with inverted colors."""
    dark_mode_css = 'body.dark-mode {\n'
    for color in colors:
        # Simple inversion logic (you may want to customize this)
        if color.startswith('#'):
            if len(color) == 7:
                inverted_color = '#' + ''.join([format(255 - int(color[i:i+2], 16), '02x') for i in (1, 3, 5)]).upper()
            elif len(color) == 4:
                inverted_color = '#' + ''.join([format(255 - int(color[i:i+1] * 2, 16), '02x') for i in (1, 2, 3)]).upper()
            dark_mode_css += f'    --color-{color.lstrip("#")}: {inverted_color};\n'
    dark_mode_css += '}\n'

    return dark_mode_css
