#!/bin/env python

from setuptools import setup
from sphinx.setup_command import BuildDoc

cmdclass = {'build_sphinx': BuildDoc}

name = 'argdoc'
version = '0.1'
release = '0.1.0'

with open('README.md', 'r') as rm:
    long_description = rm.read()

setup(name=name,
      version=release,
      author='Jeremy Solbrig',
      author_email='jeremy.solbrig@colostate.edu',
      description='A package for reducing copy/paste of argument descriptions in docstrings',
      long_description=long_description,
      long_description_content_type="text/markdown",
      py_modules=['argdoc'],
      cmdclass=cmdclass,
      command_options={
          'build_sphinx': {
              'project': ('setup.py', name),
              'version': ('setup.py', version),
              'release': ('setup.py', release),
              'source_dir': ('setup.py', 'doc')}},
      install_requires=['sphinx', 'sphinxcontrib-programoutput'],
      url='https://github.com/jsolbrig/argdoc',
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.7',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent']
     )

