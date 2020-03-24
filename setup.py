import sys
from setuptools import setup, find_packages
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


packages = find_packages(
    include=("numjuggler", "numjuggler.*",),
)


with open('README.md', 'r') as f:
    long_description = f.read()
    long_description_type = 'text/markdown'


setup(
    name='numjuggler',
    description='MCNP input file renumbering tool',
    long_description=long_description,
    long_description_content_type=long_description_type,
    author='A.Travleev',
    author_email='anton.travleev@gmail.com',
    packages=packages,
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    tests_require=['pytest', 'pytest-cov>=2.3.1'],
    install_requires=[
        'six',
        'pathlib2',
    ],
    cmdclass={'test': PyTest},
    entry_points={'console_scripts': ['numjuggler = numjuggler.main:main']},
    # url='https://github.com/travleev/numjuggler',
    url='https://numjuggler.readthedocs.io',
    keywords='MCNP ITER PARSER RENUMBER'.split(),
    classifiers=[
        'Development Status :: 4 - Beta',  # changed, when tests for all modes
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
)
