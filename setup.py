from distutils.core import setup
import os

deps = [
    'pint',
    'urwid',
    'bs4',
    'argcomplete',
    'ruamel.yaml',
    'lxml',
    'SpeechRecognition',
    'gtts',
    'termcolor'
]

packages = [
    'pyrecipe', 
    'pyrecipe/console_gui', 
    'pyrecipe/db'
]

data_files = [
    ('/etc/pyrecipe/', ['config/pyrecipe.cfg'])
]
setup(
    name='pyrecipe',
    version='1.1.2',
    packages=packages,
    keywords='recipe culinary food',
    package_data={
        'pyrecipe': ['culinary_units.txt']
        },
    data_files=data_files,
    license='GNU General Public License',
    long_description='A python tool for managing recipes',
    install_requires=deps,
    scripts=['bin/recipe_tool']
    )
