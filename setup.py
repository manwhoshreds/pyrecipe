from distutils.core import setup

setup(
    name='pyrecipe',
    version='0.8.0',
    packages=['pyrecipe', 'console_gui', 'gui'],
    license='GNU General Public License',
    long_description='A python tool for managing recipes',
    install_requires=['pint', 'urwid', 'bs4']
    )
