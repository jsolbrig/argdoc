#!/bin/env python

from __future__ import absolute_import, division, print_function, unicode_literals
from argdoc import ArgDoc

# Instantiate the :class:`.ArgDoc` object and ignore 'self', 'cls', and 'ignored'
arg_doc = ArgDoc(ignore=['self', 'cls', 'ignored'])

##################################
# Registering positional arguments
##################################

# `typ` can be a type
arg_doc.register_positional('arg1', str, 'The first test argument')

# `typ` can also be a str
arg_doc.register_positional('arg2', 'list of str', 'The second test argument')

###############################
# Registering keyword arguments
###############################

# If `default` is not `None` its value will be used as the default value for
# the keyword argument in documentation
arg_doc.register_keyword('kw1', str, 'The first keyword argument', default='Hello')

# If `default` is not provided or is `None`, the default value will be gathered
# the decorated object's argspec
arg_doc.register_keyword('kw2', str, 'The second keyword argument')

# Registering an already registered argument will cause a KeyError to be raised
try:
    print('Attempting to register `arg1` a second time')
    arg_doc.register_positional('arg1', str, 'The first test argument...again')
except KeyError:
    print('Cannot re-register `arg1`')

# Setting `force` to `True` will allow replacement of an already registered argument
# Note that the description for `arg1` below comes from this line
print('Forcing re-registration of `arg1`')
arg_doc.register_positional('arg1', str, 'The first test argument...forced', force=True)

# Registering a positional argument and a keyword argument under the same
# name works and is appropriate at times.
#
# This allows the same argument name to be used as a positional argument
# in some functions and as a keyword argument in other functions.
# Which to use is determined through introspection of the argspec.
arg_doc.register_positional('foo', str, 'Foo foo foo')
arg_doc.register_keyword('foo', str, 'Foo foo foo', default='foo')

# Decorating a function is done by using the :class:`.ArgDoc` instance
# as a decorator
#
# Note: Decorating a class is done by decorating its "special methods" such as
#       __new__, __init__, __call__, etc.
#
# Note: Decorating a function with an extra, unregistered argument will
#       cause a KeyError to be raised
@arg_doc
def test_function(arg1, arg2, kw1='Test1', kw2='Test2'):
    '''
    This function does nothing.
    '''
    pass

print('Docstring for `test_function`')
print(test_function.__doc__)

# Since it was defined as both a positional and keyword argument, `foo`
# can be used as either
@arg_doc
def positional_foo(foo):
    '''
    This function does nothing.
    Foo is positional.
    '''
    pass

@arg_doc
def keyword_foo(foo=None):
    '''
    This function does nothing.
    Foo is a keyword.
    '''
    pass

print('Docstring for `positional_foo`')
print(positional_foo.__doc__)

print('Docstring for `keyword_foo`')
print(keyword_foo.__doc__)

# Decorating a function that includes an ignored argument will document
# the function as though that argument is not there
@arg_doc
def function_with_ignored_argument(arg1, ignored):
    '''
    This function does nothing.
    The argument `ignored` is ignored in the docstring but remains
    in the argspec.
    '''
    pass

print('Docstring for `function_with_ignored_argument`')
print(function_with_ignored_argument.__doc__)
