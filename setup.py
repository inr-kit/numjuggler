# from distutils.core import setup
from setuptools import setup

# Get the version from numjuggler/__init__.py
fd = {}
with open('./numjuggler/__version__.py', 'r') as f:
    exec(f.read(), fd)
    version = fd['__version__']


setup(name='numjuggler',
      version=version,  # __version__,  # '2.41a.27',
      description='MCNP input file renumbering tool',
      author='A. Travleev',
      author_email='anton.travleev@gmail.com',
      packages=['numjuggler', ],
      # scripts = ['numjuggler/numjuggler'],
      entry_points={'console_scripts': ['numjuggler = numjuggler.main:main']},
      )
