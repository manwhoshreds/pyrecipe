from termcolor import colored



def color(text, color=''):
    if color:
        return colored(text, color)
    else:
        return text

# Section divider e.g. "~~~~~~~~~~~~~"
S_DIV = color("~" * 60, 'white')
