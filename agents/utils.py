import colorama

def print_colored(text, color="blue"):
    """
    Print text in a specified color using colorama.
    
    Args:
        text (str): The text to print.
        color (str): The color to use ('red', 'green', 'yellow', 'blue', 'magenta', 'cyan').
    """
    colors = {
        'red': colorama.Fore.RED,
        'green': colorama.Fore.GREEN,
        'yellow': colorama.Fore.YELLOW,
        'blue': colorama.Fore.BLUE,
        'magenta': colorama.Fore.MAGENTA,
        'cyan': colorama.Fore.CYAN,
        'reset': colorama.Style.RESET_ALL
    }
    
    if color in colors:
        print(colors[color] + text + colors['reset'])
    else:
        print(text)  # Default to no color if the specified color is not found