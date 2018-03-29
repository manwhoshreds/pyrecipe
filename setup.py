from distutils.core import setup

deps = [
        'pint',
        'urwid',
        'bs4',
        'argcomplete',
        'ruamel.yaml',
        'inflect',
        'lxml',
        'SpeechRecognition',
        'gtts'
        ]

setup(
    name='pyrecipe',
    version='0.5.12',
    packages=['pyrecipe', 'pyrecipe/console_gui', 'pyrecipe/gui'],
    package_data={
        'pyrecipe': ['culinary_units.txt']
        },
    license='GNU General Public License',
    long_description='A python tool for managing recipes',
    install_requires=deps,
    scripts=['bin/recipe_tool']
    )
