import sys
from setuptools import setup
from setuptools.command.test import test as test_command


# noinspection PyAttributeOutsideInit
class PyTest(test_command):
    """
    See recomendations at https://docs.pytest.org/en/latest/goodpractices.html
    """
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        test_command.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def load_version():
    fd = {}
    with open('./numjuggler/__version__.py', 'r') as f:
        exec(f.read(), fd)
        return fd['__version__']


setup(
    name='numjuggler',
    version=load_version(),
    description='MCNP input file renumbering tool',
    author='A.Travleev',
    author_email='anton.travleev@kit.edu',
    packages=['numjuggler', ],
    tests_require=['pytest', 'pytest-cov>=2.3.1'],
    cmdclass={'test': PyTest},
    entry_points={'console_scripts': ['numjuggler = numjuggler.main:main']},
)
