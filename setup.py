# setup.py

from setuptools import setup
from distutils.util import convert_path
from sphinx.setup_command import BuildDoc

name = 'ArgDoc'

main_ns = {}
ver_path = convert_path('argdoc/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

cmdclass = {'build_sphinx': BuildDoc}

with open('README.md', 'r') as rm:
    long_description = rm.read()

setup(name=name,
      version=main_ns['__version__'],
      author='Jeremy Solbrig',
      author_email='jeremy.solbrig@colostate.edu',
      description='A package for reducing copy/paste of argument descriptions in docstrings',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=['argdoc'],
      cmdclass=cmdclass,
      command_options={
          'build_sphinx': {
              'project': ('setup.py', name),
              'version': ('setup.py', main_ns['__version__']),
              'source_dir': ('setup.py', 'doc')}},
      install_requires=['future', 'sphinx', 'sphinxcontrib-programoutput'],
      url='https://github.com/jsolbrig/argdoc',
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.7',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent']
     )

