from __future__ import division, print_function, unicode_literals
from inspect import getargspec, isclass

__metaclass__ == type


class ArgDoc():
    '''
    This decorator inspects the argspec of a decorated function, method, or class and
    adds a Numpy formatted paramter list to the docstring of that object.  This is
    intended to ease the process of creating and maintaining docstrings across a package
    where many positional arguments and keyword arguments are frequently repeated.

    To be included in docstrings, the positional and keyword arguments must be registered with
    the decorator prior to use.  This is done through two methods: `.ArgDoc.register_positional`
    and `.ArgDoc.register_keyword`.

    At present, this only produces Numpy and Google style docstrings, but can easily be
    extended to output other docstring formats.

    Keyword Arguments
    -----------------
    form : {'numpy', 'google'}
        The format to be used for argument formatting in docstrings.
        If set to `'numpy'`, Numpy format docstrings will be produced.
        If set to `'google'`, Google format docstrings will be produced.
        **Default**: `'numpy'`
    ignore : list of str, optional
        A list of positional and/or keyword arguments to ignore.
        **Default**: `['self', 'cls']`
    '''
    def __init__(self, form='numpy', ignore=['self', 'cls']):
        self.ignore = ignore
        self.positional= {}
        self.keywords = {}

    def __call__(self, obj):
        '''
        Inspect the input object and add a "parameters" section to its docstring
        based on its argspec.
        '''
        if hasattr(obj, '__doc__'):
            if isclass(obj):
                args, vargs, kwargs, defaults = getargspec(obj.__init__)
            else:
                args, vargs, kwargs, defaults = getargspec(obj)
            if defaults:
                defaults = list(defaults)
            else:
                defaults = []

            # Pop off the keyword arguments, get their descriptions, and associate with defaults
            keywords = {}
            while defaults:
                kw = args.pop()
                default = defaults.pop()

                # If ignored, then skip
                if kw in self.ignore:
                    continue
                # Add to keywords to document
                keywords[kw] = self.keywords[kw]
                # Defer to the registered default
                if 'default' not in keywords[kw]:
                    keywords[kw]['default'] = default

            # Pop off the positonal arguments and get their descriptions
            positional = {}
            while args:
                arg = args.pop()

                # If ignored, then skip
                if arg in self.ignore:
                    continue
                positional[arg] = self.positional[arg]

            # Construct the docstring
            doc = obj.__doc__ if obj.__doc__ else ''
            doc = doc.strip()
            if positional:
                doc += '\n\nArguments\n----------\n'
                for argname, arginfo in positional.items():
                    doc += self.__create_numpy_format_argument(argname, arginfo)
            if keywords:
                doc += '\n\nKeyword Arguments\n-----------------\n'
                for kwname, kwinfo in keywords.items():
                    doc += self.__create_numpy_format_argument(kwname, kwinfo)
            doc += '    \n'
        else:
            raise AttributeError('Object has no docstring')
        obj.__doc__ = doc
        return obj

    def __register_param(self, name, typ, desc, default=None, force=False, keyword=False):
        if keyword:
            errstr = 'Keyword argument'
            store = self.keywords
        else:
            errstr = 'Positional argument'
            store = self.positional

        if not force and name in store:
            raise KeyError('{} {} already registered.'.format(errstr, name))
        else:
            try:
                typ = typ.__name__
            except AttributeError:
                typ = str(typ)
            store[name] = {'type': typ,
                              'desc': desc}
            if default is not None:
                store[name]['default'] = default

    def register_positional(self, name, typ, desc, force=False):
        '''
        Register a new positional argument with with the :py:class:`.ArgDoc` instance including
        its type and a description of the argument.  If an argument with the same name has already
        been registered with the instance, a :py:class:`KeyError` will be raised.

        Arguments
        ----------
        name : str
            The name of a positional argument that should be handled by the
            :py:class:`.ArgDoc` instance
        typ : type or str
            The type of the positional argument as either a Python type or a string
        desc : str
            A description of the positional argument

        Keyword Arguments
        -----------------
        force : bool
            If set to True, positional arguments will be replaced if already
            registered with the :py:class:`.ArgDoc` instance.  **Default**: `False`

        Raises
        ------
        KeyError
            If a positional argument has already been registered under the same name
            and `force` is `False`.
        '''
        self.__register_param(name, typ, desc, force=force, keyword=False)

    def register_keyword(self, name, typ, desc, default=None, force=False):
        '''
        Register a keyword argument with with the :py:class:`.ArgDoc` instance including
        its type, a description of the argument, and, optionally, its default value.
        If no default value is provided, the default value will be collected from the
        argspec of each decorated object.  If a default value is provided it will take
        precidence over the default value from the argspec for documentation purposes
        but will have **no impact on the code**.  If a keyword argument with the same
        name has already been registered with the instance, a :py:class:`KeyError`
        will be raised.

        Arguments
        ----------
        name : str
            The name of a keyword argument that should be handled by the ArgDoc class
        typ : type or str
            The type of the keyword argument as either a Python type or a string
        desc : str
            A description of the keyword argument

        Keyword Arguments
        -----------------
        default : anything, optional
            The default value to be used in docstrings for the keyword argument.
            If `None` the default value will be gathered from each decorated object's
            argspec.  If not `None`, this value will override the value from the
            decorated object's argspec **for documentation purposes only** but will have
            no effect on the code.
            **Default**: `None`
        force : bool
            If set to True, keyword arguments will be replaced if already registered
            with the :py:class:`.ArgDoc` instance.  **Default**: `False`

        Raises
        ------
        KeyError
            If a keyword argument has already been registered under the same name and
            `force` is `False`
        '''
        self.__register_param(name, typ, desc, force=force, keyword=True)

    def __create_numpy_format_argument(self, name, info):
        if 'default' in info:
            argstr = '{} : {}, optional\n    {} Default: {}\n'.format(
                name, info['type'], info['desc'], info['default'])
        else:
            argstr = '{} : {}\n    {}\n'.format(name, info['type'], info['desc'])
        return argstr

    def __create_google_format_argument(self, name, info):
        if 'default' in info:
            argstr = '{} ({}, optional): {}\n'.format(name, info['type'], info['default'])
        else:
            argstr = '{} ({}): {}\n'.format(name, info['type'], info['default'])
        return argstr
