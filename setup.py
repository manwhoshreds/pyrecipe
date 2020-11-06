from distutils.core import setup
from setuptools import find_packages

DEPS = [
    'pint',
    'urwid',
    'bs4',
    'lxml',
    'termcolor',
    'inflect',
    'requests'
]

DATA_FILES = [
    ('share/bash-completion/completions', ['misc/completion/recipe_tool']),
    ('/etc/pyrecipe', ['misc/pyrecipe.cfg'])
]


with open("README.asc", "r") as fh:
    long_description = fh.read()

setup(
    name="pyrecipe",
    version="0.7.2",
    author="Michael K. Miller",
    author_email="m.k.miller@gmx.com",
    description='A python tool for managing recipes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    data_files=DATA_FILES,
    package_data={
        'pyrecipe': [
            'db/tables.sql', 
            'culinary_units.txt'
        ],
    },
    url="https://github.com/manwhoshreds/pyrecipe",
    entry_points={
        'console_scripts': [
            'recipe_tool = pyrecipe.__main__:main'
        ]
    },
    packages=find_packages(),
    install_requires=DEPS,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
