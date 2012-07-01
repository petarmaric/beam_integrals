from distribute_setup import use_setuptools
use_setuptools() 

import re
import sys
from setuptools import setup, find_packages


if sys.version_info < (2, 6):
    print 'ERROR: beam_integrals requires at least Python 2.6 to run.'
    sys.exit(1)


# Thanks to http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy
def parse_requirements(file_name):
    requirements = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'(\s*#)|(\s*$)', line):
            continue
        if re.match(r'\s*-e\s+', line):
            requirements.append(re.sub(r'\s*-e\s+.*#egg=(.*)$', r'\1', line))
        elif re.match(r'\s*-f\s+', line):
            pass
        else:
            requirements.append(line)
    
    return requirements

# Thanks to http://cburgmer.posterous.com/pip-requirementstxt-and-setuppy
def parse_dependency_links(file_name):
    dependency_links = []
    for line in open(file_name, 'r').read().split('\n'):
        if re.match(r'\s*-[ef]\s+', line):
            dependency_links.append(re.sub(r'\s*-[ef]\s+', '', line))
    
    return dependency_links

def get_test_requirements():
    """
    Python 2.7 introduced new assert* methods in `unittest.TestCase`, fallback
    to backported library if Python < 2.7 
    """
    requirements = parse_requirements('requirements-test.txt')
    
    if sys.version_info < (2, 7):
        requirements.append('unittest2')
    
    return requirements

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
    tests_require = get_test_requirements(),
    test_suite = 'nose.collector',
)
