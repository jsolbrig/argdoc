#!/bin/env python

from setuptools import setup
from sphinx.setup_command import BuildDoc

cmdclass = {'build_sphinx': BuildDoc}

name = 'argdoc'
version = '0.1'
release = '0.1.0'

setup(name=name,
      version=release,
      description='Decorator to add parameters to docstrings',
      author='Jeremy Solbrig',
      author_email='jeremy.solbrig@colostate.edu',
      py_modules=['argdoc'],
      cmdclass=cmdclass,
      command_options={
          'build_sphinx': {
              'project': ('setup.py', name),
              'version': ('setup.py', version),
              'release': ('setup.py', release),
              'source_dir': ('setup.py', 'source')}}
     )

