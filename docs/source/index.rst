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

Clone the repo and install using setup.py:

.. code-block:: bash

    git clone https://github.com/jsolbrig/argdoc.git
    cd argdoc
    python setup.py install

Usage
=====

To use :py:class:`.ArgDoc` as a decorator, it must first be imported within your source
code and and an instance must be instantiated:

.. code-block:: python

    from argdoc import ArgDoc
    arg_doc = ArgDoc()

Next, in order for the decorator to have any effect, positional arguments and
keywords must be registered with the :py:class:`.ArgDoc` instance.  If a positional
argument or keyword that has not been registered with the :py:class:`.ArgDoc` instance
is encountered in a decorated object's argspec a :py:class:`KeyError` will be raised.

Registering a Positional Argument
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Positional arguments can be registered by calling :py:meth:`.ArgDoc.register_argument`
on an instantiated :py:class:`.ArgDoc` instance.  For example, the code below shows how
to register an argument called `testarg` with type `str` and a description
stating that it is `"A test argument"`.

.. code-block:: python

    # Import and instantiate
    from argdoc import ArgDoc
    arg_doc = ArgDoc()

    # An argument consists of a name, a type, and a description
    arg_doc.register_argument('testarg', str, 'A test argument')

Note that the `typ` argument to :py:meth:`.ArgDoc.register_argument` can be anything.
If a `type` object is passed, `typ.__name__` will be used in the documentation
while, if anything else is passed, its `__str__` representation will be used.

.. note:: Maybe this is not the appropriate behavior here.  Think about it...

Registering a Keyword Argument
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Keyword arguments can be registered by calling :py:meth:`.ArgDoc.register_keyword`
on an instantiated :py:class:`.ArgDoc` instance.  This is the same process as for
positional arguments, except that a default value can be provided.  When no
default value is provided the default value is derived from the argspec.
When a default value is provided, the default set in the argspec will be
overridden with the input default value.

.. code-block:: python

    # Use the argspec's default value
    arg_doc.register_keyword('testkw', bool, 'A test keyword that acts as a boolean flag')

    # Set a new default value
    arg_doc.register_keyword('overridden', str, 'A test string', default='Testing')

Decorating an object
====================

To decorate an object, create an instance of :py:class:`.ArgDoc` and register positional
arguments and keywords with the instance.  Then, simply decorate an object with the
:py:class:`.ArgDoc` instance like this:

.. code-block:: python

    @dict_doc
    def somefunction(arg1, arg2, kw1='Test', kw2=False):
        pass

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