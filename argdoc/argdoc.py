from __future__ import division, print_function, unicode_literals
import pkg_resources
from inspect import getargspec, isclass
try:
    from inspect import signature
except ImportError:
    from funcsig import signature

from IPython import embed as shell

__metaclass__ = type


class ArgDoc:
    '''
    This decorator inspects the argspec of a decorated function, method, or class and
    adds a Numpy formatted paramter list to the docstring of that object.  This is
    intended to ease the process of creating and maintaining docstrings across a package
    where many positional arguments and keyword arguments are frequently repeated.

    To be included in docstrings, the positional and keyword arguments must be registered with
    the decorator prior to use.  This is done through two methods: `.ArgDoc.register_argument`
    and `.ArgDoc.register_keyword`.

    At present, this only produces Numpy and Google style docstrings, but can easily be
    extended to output other docstring formats.
    '''
    def __new__(cls, form='numpy', ignore_args=[], ignore_kws=[]):
        obj = super().__new__(cls)
        obj.form = form
        obj.ignore_args = ignore_args
        obj.ignore_kws= ignore_kws
        obj.arguments = {}
        obj.keywords = {}
        return obj

    def __call__(self, raises=None):
        '''
        Return an instance of the actual decorator.
        '''
        return self.__ArgDocumenter(self.form, self.arguments, self.keywords, raises,
                                    self.ignore_args, self.ignore_kws)

    class __ArgDocumenter:
        def __init__(self, form, arguments, keywords, raises, ignore_args, ignore_kws):
            '''
            This is the actual decorator, which is contstructed by :py:class:`.ArgDoc.__call__`.
            :py:class:`.__ArgDocumenter` should never be instantiated directly.
            '''
            self.form = form
            self.arguments = arguments
            self.keywords = keywords
            self.ignore_args = ignore_args
            self.ignore_kws = ignore_kws
            self.raises = raises
    
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
                    if kw in self.ignore_kws:
                        continue
                    # Add to keywords to document
                    try:
                        keywords[kw] = self.keywords[kw]
                    except KeyError:
                        raise KeyError(
                            'Unregistered keyword argument `{}` encountered in argspec of `{}`'.format(kw, obj))
                    # Defer to the registered default
                    if 'default' not in keywords[kw]:
                        keywords[kw]['default'] = default
    
                # Pop off the positonal arguments and get their descriptions
                arguments = {}
                while args:
                    arg = args.pop()
    
                    # If ignored, then skip
                    if arg in self.ignore_args:
                        continue
                    try:
                        arguments[arg] = self.arguments[arg]
                    except KeyError:
                        raise KeyError(
                            'Unregistered positional argument `{}` encountered in argspec of `{}`'.format(arg, obj))
    
                # Construct the docstring
                doc = obj.__doc__ if obj.__doc__ else ''
                doc = doc.strip()
                if arguments:
                    doc += '\n\nArguments\n----------\n'
                    for argname in sorted(arguments.keys()):
                        arginfo = arguments[argname]
                        doc += self.__create_numpy_format_argument(argname, arginfo)
                if keywords:
                    doc += '\n\nKeyword Arguments\n-----------------\n'
                    for kwname in sorted(keywords.keys()):
                        kwinfo = keywords[kwname]
                        doc += self.__create_numpy_format_argument(kwname, kwinfo)
                if self.raises:
                    doc += '\n\nRaises\n------\n'
                    for errname in sorted(self.raises.keys()):
                        errcond = self.raises[errname]
                        doc += self.__create_numpy_format_error(errname, errcond)
                doc += '    \n'
    
            else:
                raise AttributeError('Object has no docstring')
            obj.__doc__ = doc
            return obj
    
        def __create_numpy_format_argument(self, name, info):
            if 'default' in info:
                argstr = '{} : {}, optional\n    {} Default: {}\n'.format(
                    name, info['type'], info['desc'], info['default'])
            else:
                argstr = '{} : {}\n    {}\n'.format(name, info['type'], info['desc'])
            return argstr
    
        def __create_numpy_format_error(self, name, condition):
            return '{}\n    {}\n'.format(name, condition)
    
        def __create_google_format_argument(self, name, info):
            if 'default' in info:
                argstr = '{} ({}, optional): {}\n'.format(name, info['type'], info['default'])
            else:
                argstr = '{} ({}): {}\n'.format(name, info['type'], info['default'])
            return argstr
    
        def __create_google_format_error(self, name, condition):
            return '{}: {}\n'.format(name, condition)

    def __register_param(self, name, typ, desc, default=None, force=False, keyword=False):
        if keyword:
            errstr = 'Keyword argument'
            store = self.keywords
        else:
            errstr = 'Positional argument'
            store = self.arguments

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

    def register_argument(self, name, typ, desc, force=False):
        '''
        Register a new positional argument with with the :py:class:`.ArgDoc` instance including
        its type and a description of the argument.  If an argument with the same name has already
        been registered with the instance, a :py:class:`KeyError` will be raised.
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
        '''
        self.__register_param(name, typ, desc, default=default, force=force, keyword=True)


# Use ArgDoc to document itself!
__arg_doc = ArgDoc(ignore_args=['self', 'cls'])

obj_desc = 'A callable object whose docstring should be updated.'
name_desc = 'The name of a positional argument that should be handled by the :py:class::`.ArgDoc` instance.'
typ_desc = ('The type of the positional argument.  If a `typ` is of type `type`, typ.__name__ will be used '
            ' in the documentation, otherwise typ.__str__ will be used.')
desc_desc = 'A description of the positional argument.'
default_desc = ('The default value to be used in docstrings.  If `None`, the default value will be '
                'gathered from the argspec of each decorated object.  If not `None`, this value '
                'will be used in place of the value gathered from the argspec.  This will have '
                '**no effect on the code** and is for documentation purposes only.')
force_desc = ('If set to `True`, allow arguments to be replaced if an attempt is made to register '
              'a previously registered argument.')
form_desc = 'Docstring specification to be followed: one of "numpy" or "google"'
ignore_args_desc = 'Names of positional arguments to be ignored.'
ignore_kws_desc = 'Names of keyword arguments to be ignored.'
raises_desc = ('A dictionary whose keys are possible error types that may be raised by the decorated '
               'object and whose values describe the contditions under which the error will be raised.')

__arg_doc.register_argument('obj', 'callable', obj_desc)
__arg_doc.register_argument('name', str, name_desc)
__arg_doc.register_argument('typ', 'type or str', typ_desc)
__arg_doc.register_argument('desc', str, desc_desc)
__arg_doc.register_keyword('default', bool, default_desc)
__arg_doc.register_keyword('force', bool, force_desc)
__arg_doc.register_keyword('form', str, form_desc)
__arg_doc.register_keyword('ignore_args', 'list of str', ignore_args_desc)
__arg_doc.register_keyword('ignore_kws', 'list of str', ignore_kws_desc)
__arg_doc.register_keyword('raises', 'dict', raises_desc)

raises = {'KeyError': 'If an argument has already been registered under the same name and `force` is `False`'}

__arg_doc()(ArgDoc.__new__)
__arg_doc()(ArgDoc.__call__)
# __arg_doc(raises=raises)(ArgDoc.register_argument)
# __arg_doc(raises=raises)(ArgDoc.register_keyword)
