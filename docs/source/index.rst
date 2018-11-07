.. ArgDoc documentation master file, created by
   sphinx-quickstart on Tue Oct 30 15:18:02 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ArgDoc - Reduce copy/paste in docstrings
==========================================

This package provides a single class: :py:class:`.ArgDoc`.  :py:class:`.ArgDoc` is a decorator
that will inspect the argspec of any decorated function, method, or class
to determine which arguments and keywords are used.  It will then modify
the docstring of the decorated object to add a parameters list in the
Numpy format.

Installation
============

Via PIP
-------

.. code-block:: bash

    pip install argdoc

From Source
-----------

Clone the repo and install using setup.py:

.. code-block:: bash

    git clone https://github.com/jsolbrig/argdoc.git
    cd argdoc
    python setup.py install

Usage
=====

To use :py:class:`.ArgDoc` as a decorator, it must first be imported within your source
code and and an instance must be instantiated:

>>> from argdoc import ArgDoc
>>> arg_doc = ArgDoc()

Next, in order for the decorator to have any effect, positional arguments and
keywords must be registered with the :py:class:`.ArgDoc` instance.  If a positional
argument or keyword that has not been registered with the :py:class:`.ArgDoc` instance
is encountered in a decorated object's argspec a :py:class:`KeyError` will be raised.

Registering a Positional Argument
---------------------------------

Positional arguments can be registered by calling :py:meth:`.ArgDoc.register_argument`
on an instantiated :py:class:`.ArgDoc` instance.  For example, the code below shows how
to register an argument called `arg1` with type `str` and a description
stating that it is `"The first argument"`:

>>> arg_doc.register_argument('arg1', str, 'The first argument')
>>> print(arg_doc.arguments['arg1'])
{'type': 'str', 'desc': 'The first argument'}

Note that the `typ` argument to :py:meth:`.ArgDoc.register_argument` can be anything.
If a :py:class:`type` object is passed, `typ.__name__` will be used in the documentation
while, if anything else is passed, its `__str__` representation will be used.
To register `arg2` whose type is a `"list of str"`:

>>> arg_doc.register_argument('arg2', 'list of str', 'The second argument')
>>> print(arg_doc.arguments['arg2'])
{'type': 'list of str', 'desc': 'The second argument'}

.. note:: Maybe this is not the appropriate behavior here.  Think about it...

At this point, there are two registered positional arguments:

.. testcode::

    print(arg_doc.arguments)

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    {'arg1': {'type': 'str', 'desc': 'The first argument'},
     'arg2': {'type': 'list of str', 'desc': 'The second argument'}}

Registering a Keyword Argument
------------------------------

Registering a keyword argument is similar to registering a positional argument.  To
register a keyword argument, call :py:meth:`.ArgDoc.register_keyword`
Keyword arguments can be registered by calling :py:meth:`.ArgDoc.register_keyword`
on an instantiated :py:class:`.ArgDoc` instance.  To register a keyword with named
`def_kw` with type `int`, the description `"Keyword with default"`, and a default
of `1`:

>>> arg_doc.register_keyword('def_kw', int, 'Keyword with default defined during registration', default=1)
>>> print(arg_doc.keywords['def_kw'])
{'type': 'int', 'desc': 'Keyword with default defined during registration', 'default': 1}

Providing a default value during registration is optional.  If a default value is
provided, that default value will be used in the docstring for all decorated objects
that include the named keyword in their argspec.  If, on the other hand, no default
value is provided for a keyword that is found in a decorated object's argspec, the
default value to use in the documentation will be extracted from the object's argspec
for each decorated object:

>>> arg_doc.register_keyword('no_def_kw', int, 'Keyword that gathers default from argspec')
>>> print(arg_doc.keywords['no_def_kw'])
{'type': 'int', 'desc': 'Keyword that gathers default from argspec'}

.. note:: Setting the default value of a keyword argument during registration does not impact
          the code, only the documentation.  This functionality is provided to allow documentation
          of keywords whose defaults are not set in the argspec and are, instead, set inside the
          decorated callable.

At this point, we have two registered keywords:

.. testcode::

    print(arg_doc.keywords)

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    {'def_kw': {'type': 'int', 'desc': 'Keyword with default defined during registration', 'default': 1},
     'no_def_kw': {'type': 'int', 'desc': 'Keyword that gathers default from argspec'}}

Decorating a function
---------------------

To decorate a function, create an instance of :py:class:`.ArgDoc` and register positional
arguments and keywords with the instance as shown above.  Then, simply decorate an object
with the :py:class:`.ArgDoc` instance:

.. testcode::

    @arg_doc()
    def test_func(arg1, arg2, def_kw=None, no_def_kw=None):
        '''
        This is a test function that does nothing
        '''
        pass
    print(test_func.__doc__)

Note that in the resulting docstring, the default for `def_kw` was defined during registration
of the keyword argument while the default for `no_def_kw` is gathered from the argspec of
the decorated function:

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    This is a test function that does nothing

    Arguments
    ----------
    arg1 : str
        The first argument
    arg2 : list of str
        The second argument


    Keyword Arguments
    -----------------
    def_kw : int, optional
        Keyword with default defined during registration Default: 1
    no_def_kw : int, optional
        Keyword that gathers default from argspec Default: None

It is not necessary for a decorated function's argspec to contain all of the registered
positional or keyword arguments.  Decorating a function with a subset of the registered
arguments produces an appropriate docstring:

.. testcode::

    @arg_doc()
    def single_argument(arg1):
        '''
        This function's argspec only contains `arg1`
        '''
        pass

    @arg_doc()
    def single_keyword(no_def_kw=100):
        '''
        This function's argspec only contains `no_def_kw`
        '''
        pass

    print(single_argument.__doc__)
    print(single_keyword.__doc__)

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    This function's argspec only contains `arg1`

    Arguments
    ----------
    arg1 : str
        The first argument
        

    This function's argspec only contains `no_def_kw`

    Keyword Arguments
    -----------------
    no_def_kw : int, optional
        Keyword that gathers default from argspec Default: None

Unregistered Arguments
----------------------

By default, if a positional or keyword argument is encountered in the decorated function's
argspec that has not been registered with the :py:class:`.ArgDoc` instance a KeyError will
be raised:

.. testcode::

    @arg_doc()
    def bad_argument(badarg):
        '''
        This function has an unregistered argument and will raise a KeyError when decorated
        '''
        pass

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    Traceback (most recent call last):
    ...
    KeyError: 'Unregistered positional argument `badarg` encountered in argspec of
    `<function bad_argument at ...>`'

.. testcode::
    :hide:

    @arg_doc()
    def bad_keyword(badkw=None):
        '''
        This function has an unregistered keyword and will raise a KeyError when decorated
        '''
        pass

.. testoutput::
    :hide:
    :options: +NORMALIZE_WHITESPACE

    Traceback (most recent call last):
    ...
    KeyError: 'Unregistered keyword argument `badkw` encountered in argspec of
    `<function bad_keyword at ...>`'

Ignoring Arguments
------------------

In the case where it is undesirable to document a specific positional or keyword argument 
it can be ignored during the initialization of the :py:class:`.ArgDoc` instance.  To
ignore the positional argument `ignored_arg` and the keyword argument `ignored_kw`:

>>> arg_doc = ArgDoc(ignore_args=['ignored_arg'], ignore_kws=['ignored_kw'])
>>> arg_doc.register_argument('arg1', str, 'The first argument')
>>> arg_doc.register_argument('arg2', 'list of str', 'The second argument')
>>> arg_doc.register_keyword('def_kw', int, 'Keyword with default defined during registration', default=1)
>>> arg_doc.register_keyword('no_def_kw', int, 'Keyword that gathers default from argspec')
>>> print(arg_doc.ignore_args)
['ignored_arg']
>>> print(arg_doc.ignore_kws)
['ignored_kw']

Decorating a function whose argspec contains ignored arguments results in those arguments
being silently omitted from the resulting docstring:

.. testcode::

    @arg_doc()
    def test_func(ignored_arg, arg1, arg2, ignored_kw=None, def_kw=None, no_def_kw=None):
        '''
        In this function's docstring, `ignored_arg` and `ignored_kw` will be omitted
        '''
        pass
    print(test_func.__doc__)

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    In this function's docstring, `ignored_arg` and `ignored_kw` will be omitted

    Arguments
    ----------
    arg1 : str
        The first argument
    arg2 : list of str
        The second argument


    Keyword Arguments
    -----------------
    def_kw : int, optional
        Keyword with default defined during registration Default: 1
    no_def_kw : int, optional
        Keyword that gathers default from argspec Default: None

Documenting Raised Errors
-------------------------

The errors that a function can raise cannot be determined via introspection.  To add
documentation for the errors that a function can raise, pass them to the decorator
via the `raises` argument:

.. testcode::

    raised_errors = {'KeyError': 'Raises a KeyError under all circumstances.'}

    @arg_doc(raises=raised_errors)
    def raise_key_error(arg1):
        '''
        Raises a KeyError
        '''
        raise KeyError()
    print(raise_key_error.__doc__)

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    Raises a KeyError

    Arguments
    ----------
    arg1 : str
        The first argument


    Raises
    ------
    KeyError
        Raises a KeyError under all circumstances.

API
===

.. autoclass:: argdoc.ArgDoc
    :members:
    :member-order: bysource

    .. automethod:: __call__

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
