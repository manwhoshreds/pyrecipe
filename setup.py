import setuptools
#from distutils.core import setup
#import os

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

#packages = setuptools.find_packages()
data_files = [
    ('/etc/pyrecipe/', ['config/pyrecipe.cfg'])
]


with open("README.asc", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrecipe",
    version="1.2.5",
    author="Michael K. Miller",
    author_email="m.k.miller@gmx.com",
    description='A python tool for managing recipes',
    long_description=long_description,
    long_description_content_type="text/markdown",
    data_files=data_files,
    url="https://github.com/manwhoshreds/pyrecipe",
    entry_points={
        'console_scripts': [
            'recipe_tool = pyrecipe.__main__:main'
        ]
    },
    packages=setuptools.find_packages(),
    install_require=deps,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
