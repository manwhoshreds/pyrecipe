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
    version='1.2.3',
    packages=packages,
    keywords='recipe culinary food',
    package_data={
        'pyrecipe': ['culinary_units.txt']
        },
    entry_points={
        'console_scripts': [
            'recipe_tool = pyrecipe.__main__:main'
        ]
    },
    data_files=data_files,
    license='GNU General Public License',
    long_description='A python tool for managing recipes',
    install_requires=deps,
)
