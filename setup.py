from distribute_setup import use_setuptools
use_setuptools() 

import sys
from setuptools import setup, find_packages
from requirements_utils import parse_dependency_links, parse_requirements


if sys.version_info < (2, 6):
    print 'ERROR: beam_integrals requires at least Python 2.6 to run.'
    sys.exit(1)


setup(
    name='beam_integrals',
    version='0.1.0-pre-alpha',
    url='https://bitbucket.org/petar/beam_integrals/',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Console app and Python API for determining beam integrals of '\
                'all 6 supported beam types, as described in D.D. Milasinovic,'\
                ' "The Finite Strip Method in Computational Mechanics" (ISBN '\
                '8680297194)',
    long_description=open('README').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires = parse_requirements('requirements.txt'),
    dependency_links = parse_dependency_links('requirements.txt'),
    setup_requires = ['nose>=1.0'],
    tests_require = parse_requirements('requirements-test.txt'),
    test_suite = 'nose.collector',
)
