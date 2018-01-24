#!/usr/bin/env python 
# PYTHON_ARGCOMPLET_OK
import argparse
import argcomplete

from urllib.request import urlopen
import bs4


request = urlopen('https://tasty.co/recipe/honey-soy-glazed-salmon')

soup = bs4.BeautifulSoup(request, 'html.parser')

test = soup.find_all('script', attr={'type': 'application/ld+json'})
print(test)


