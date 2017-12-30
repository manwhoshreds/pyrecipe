#!/usr/bin/env python 
# PYTHON_ARGCOMPLET_OK
import argparse
import argcomplete

def stuf(**kw):
    return ['onee', 'thow', 'why']

parser = argparse.ArgumentParser(description='test parser')

parser.add_argument('stuff').completer = stuf

argcomplete.autocomplete(parser)

args = parser.parse_args()
print(args)
