# -*- coding: utf-8 -*-
"""
    pyrecipe.user_interface.view
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The pyrecipe presentation layer
    
    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import textwrap


def wrap(str_list, width=79):
    """Textwrap for recipes."""
    if not isinstance(str_list, list):
        raise TypeError('First argument must be a list.')
    wrapped = []
    wrapper = textwrap.TextWrapper(width)
    wrapper.subsequent_indent = '   '
    if len(str_list) > 9:
        wrapper.initial_indent = ' '
        wrapper.subsequent_indent = '    '

    for index, step in enumerate(str_list, start=1):
        if index >= 10:
            wrapper.initial_indent = ''
        wrapp = wrapper.fill(step)
        wrapped_str = str(index) + ". ", wrapp
        wrapped.append(wrapped_str)
    return wrapped

