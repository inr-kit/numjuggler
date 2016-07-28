from distutils.core import setup

setup(name='numjuggler',
      # version: X.Y.Z, where:
      #    X -- major version. Different major versions are not back-compatible.
      #         New major version number, when code is rewritten
      #
      #    Y -- minor version. New minor version, when new function(s) added.
      #
      #    Z -- update, new update number when a bug is fixed.
      version='2.23a.17',
      description='MCNP input file renumbering tool',
      author='A.Travleev',
      author_email='anton.travleev@kit.edu',
      packages=['numjuggler', ],
      # scripts = ['numjuggler/numjuggler'],
      entry_points = {'console_scripts': ['numjuggler = numjuggler.main:main']},
      )
