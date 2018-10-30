class DocumentFromDict(object):
    '''
    This decorator inspects the argspec of a decorated function, method, or class and
    adds a Numpy formatted paramter list to the docstring of that object.  This is
    intended to ease the process of creating and maintaining docstrings across a package
    where many positional arguments and keywords are frequently repeated.

    To be included in docstrings, the arguments and keywords must be registered with
    the decorator prior to use.  This is done through two methods: `.DictDoc.register_arguments`
    and `.DictDoc.register_keywords`.

    At present, this only produces Numpy-style docstrings, but can easily be extended to
    output other docstring formats.
    '''
    arguments = {}
    keywords = {}

    def __call__(self, obj):
        if hasattr(obj, '__doc__'):
            if isclass(obj):
                args, vargs, kwargs, defaults = getargspec(obj.__init__)
            else:
                args, vargs, kwargs, defaults = getargspec(obj)
            if defaults:
                defaults = list(defaults)
            else:
                defaults = []

            # Pop off the keywords, get their descriptions, and associate with defaults
            keywords = {}
            while defaults:
                kw = args.pop()
                keywords[kw] = self.keywords[kw]
                # Defer to the registered default
                if 'default' not in keywords[kw]['default']:
                    keywords[kw]['default'] = defaults.pop()
            # Pop off the arguments and get their descriptions
            arguments = {}
            while args:
                arg = args.pop()
                # May need to be more careful here...
                if arg == 'self':
                    continue
                arguments[arg] = self.arguments[arg]

            # Construct the docstring
            doc = obj.__doc__ if obj.__doc__ else ''
            doc = doc.strip()
            if arguments or keywords:
                doc += '\n\nParameters\n----------\n'
            if arguments:
                for argname, arginfo in arguments.items():
                    doc += self.create_numpy_format_argument(argname, arginfo)
            if keywords:
                for kwname, kwinfo in keywords.items():
                    doc += self.create_numpy_format_argument(kwname, kwinfo)
            doc += '    \n'
        else:
            raise AttributeError('Object has no docstring')
        obj.__doc__ = doc
        return obj

    def __register_param(self, name, typ, desc, default=None, force=False, keyword=False):
        if keyword:
            errstr = 'Keyword'
            store = self.keywords
        else:
            errstr = 'Positional argument'
            store = self.arguments

        if not force and argname in store:
            raise ValueError('{} {} already registered.'.format(errstr, argname))
        else:
            try:
                typ = argtype.__name__
            except AttributeError:
                typ = str(argtype)
            store[argname] = {'type': argtype,
                              'desc': argdesc}
            if default is not None:
                store[argname]['default'] = default

    def register_argument(self, name, typ, desc, force=False):
        '''
        Register an argument with a type and description
        '''
        self.__register_param(name, typ, desc, force=force, keyword=False)

    def register_keyword(self, argname, argtype, argdesc, argdefault=None, force=False):
        '''
        Register a keyword with a type and description
        '''
        self.__register_param(argname, argtype, argdesc, force=force, keyword=True)


    def create_numpy_format_argument(self, name, info):
        argstr = '{} : {}'.format(name, info['type'])
        desc = info['desc']
        if 'default' in info:
            argstr += ', optional'
            desc += ' (Default: {})'.format(info['default'])
        argstr = '{}\n    {}\n'.format(argstr, desc)
        return argstr
