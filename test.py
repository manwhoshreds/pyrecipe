#!/usr/bin/env python 

from zipfile import ZipFile


with ZipFile('test.recipe', 'w') as myzip:
    myzip.write('hello')

