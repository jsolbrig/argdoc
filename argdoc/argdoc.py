from __future__ import division, print_function, unicode_literals
from builtins import super

import sys
import pkg_resources
from inspect import getdoc
try:
    from inspect import signature, _empty
    from inspect import Parameter
except ImportError:
    from funcsigs import signature, _empty
    from funcsigs import Parameter

from IPython import embed as shell

POSITIONAL_ONLY = Parameter.POSITIONAL_ONLY
POSITIONAL_OR_KEYWORD = Parameter.POSITIONAL_OR_KEYWORD
VAR_POSITIONAL = Parameter.VAR_POSITIONAL
KEYWORD_ONLY = Parameter.KEYWORD_ONLY
VAR_KEYWORD = Parameter.VAR_KEYWORD

POSITIONALS = [POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, VAR_POSITIONAL]

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
    def __new__(cls, form='numpy', ignore_args=[], ignore_kws=[], **kwargs):
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
                # Get the original docstring and signature
                doc = getdoc(obj)
                if not doc:
                    doc = ''
                sig = signature(obj)

                # Add parameters
                has_args = False
                has_keywords = False
                has_vargs = False
                has_vkeywords = False
                for param in sig.parameters.values():
                    if param.kind in POSITIONALS and param.default is _empty:
                        if param.name in self.ignore_args:
                            continue
                        if has_keywords:
                            raise ValueError('Argument encountered after keyword')
                        if has_vargs:
                            raise ValueError('Argument encountered after vargs')
                        if not has_args:
                            has_args = True
                            doc += self.__get_argument_header()
                        if param.kind == VAR_POSITIONAL:
                            has_vargs = True
                            doc += self.__create_vargs_doc(param)
                        else:
                            doc += self.__create_argument_doc(param)
                    else:
                        if param.name in self.ignore_kws:
                            continue
                        if has_vargs:
                            raise ValueError('Keyword encountered after vargs')
                        if has_vkeywords:
                            raise ValueError('Keyword encountered after vkeywords')
                        if not has_keywords:
                            has_keywords = True
                            doc += self.__get_keyword_header()
                        if param.kind == VAR_KEYWORD:
                            has_vkeywords = True
                            doc += self.__create_vkeywords_doc(param)
                        else:
                            doc += self.__create_keyword_doc(param)

                # Add errors
                if self.raises:
                    doc += self.__get_error_header()
                    for ename, econd in self.raises.items():
                        doc += self.__create_error_doc(ename, econd)

                doc += '    \n'

            else:
                raise AttributeError('Object has no docstring')
            try:
                obj.__doc__ = doc
            except AttributeError:
                # Required for python 2.7
                obj.__func__.__doc__ = doc
            return obj

        def __get_argument_header(self):
            if self.form == 'numpy':
                return '\n\nArguments\n----------\n'
            elif self.form == 'google':
                return '\n\nArgs:\n'

        def __get_keyword_header(self):
            if self.form == 'numpy':
                return '\n\nKeyword Arguments\n-----------------\n'
            elif self.form == 'google':
                return '\n\nKeywords:\n'

        def __get_error_header(self):
            if self.form == 'numpy':
                return '\n\nRaises\n------\n'
            elif self.form == 'google':
                return '\n\nRaises:\n'

        def __create_argument_doc(self, param):
            info = self.arguments[param.name]
            if self.form == 'numpy':
                argstr = '{} : {}\n    {}\n'.format(param.name, info['type'], info['desc'])
            elif self.form == 'google':
                argstr = '    {} ({}): {}\n'.format(param.name, info['type'], info['desc'])
            return argstr

        def __create_keyword_doc(self, param):
            info = self.keywords[param.name]
            try:
                default = info['default']
            except KeyError:
                default = param.default
            if self.form == 'numpy':
                argstr = '{} : {}, optional\n    {} Default: {}\n'.format(
                    param.name, info['type'], info['desc'], default)
            elif self.form == 'google':
                argstr = '    {} ({}, optional): {}\n'.format(
                    param.name, info['type'], info['desc'], default)
            return argstr

        def __create_vargs_doc(self, param):
            if self.form == 'numpy':
                argstr = '*{}\n    Variable length argument list.'.format(param.name)
            elif self.form == 'google':
                argstr = '    *{}: Variable length argument list.'.format(param.name)
            return argstr

        def __create_vkeywords_doc(self, param):
            if self.form == 'numpy':
                argstr = '**{}\n    Arbitrary keyword arguments.'.format(param.name)
            elif self.form == 'google':
                argstr = '    **{}: Arbitrary keyword arguments.'.format(param.name)
            return argstr

        def __create_error_doc(self, name, condition):
            if self.form == 'numpy':
                argstr = '{}\n    {}\n'.format(name, condition)
            elif self.form == 'google':
                argstr = '    {}: {}\n'.format(name, condition)
            return argstr

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
__arg_doc(raises=raises)(ArgDoc.register_argument)
__arg_doc(raises=raises)(ArgDoc.register_keyword)
