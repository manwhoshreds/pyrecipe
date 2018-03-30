from distutils.core import setup

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
    'pyrecipe/color',
    'pyrecipe/db'
]

setup(
    name='pyrecipe',
    version='0.6.2',
    packages=packages,
    package_data={
        'pyrecipe': ['culinary_units.txt']
        },
    license='GNU General Public License',
    long_description='A python tool for managing recipes',
    install_requires=deps,
    scripts=['bin/recipe_tool']
    )
