from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import os, os.path
import pandas as pd
import numpy as np

class DataObject(object):
    """
    An abstract class that enables saving to HDF files, with attribute retention

    Subclasses must define _tables and _params, lists of table and parameter
    names to be saved/restored
    """

    #subclasses should name the tables to save...
    _tables = []

    #...and the other parameters to pickle
    _params = []

    #subclasses define parameter defaults here
    defaults = {}
    
    def __init__(self, **kwargs):
        """Basic constructor.

        """
        for k,v in kwargs.items():
            if k not in (self._tables + self._params):
                raise NotImplementedError('{} must be in _tables or _params!'.format(k)) 
            setattr(self, k, v)

        #check to see if all required arguments are set
        missing = []
        for p in (self._tables + self._params):
            if not hasattr(self, p):
                missing.append(p)
        if len(missing) > 0:
            raise RuntimeError('Required parameters {} not provided.'.format(missing))

    def get_arg(self, k, kwargs):
        if k in kwargs:
            return kwargs.pop(k)
        if k in self.defaults:
            return self.defaults[k]
        raise RuntimeError("Missing required argument {0}".format(k))
    
    def save_hdf(self, filename, path='', 
                 overwrite=False, append=False):
        """Saves to hdf5 file, under given path

        If overwrite is True, existing file will be deleted
        
        If append is True, only existing path will 
        be rewritten, if it exists.
        """

        if os.path.exists(filename):
            if overwrite:
                os.remove(filename)
            else:
                store = pd.HDFStore(filename)
                if path in store:
                    if append:
                        #delete any paths beginning with path
                        for k in store.keys():
                            if re.match('path',k):
                                del store[k]
                        store.close()
                    else:
                        store.close()
                        raise IOError('{} in {} exists. Set either overwrite or append option.'.format(path,filename))
        
        #write tables 
        for tab in self._tables:
            t = getattr(self, tab)
            t.to_hdf(filename, '{}/{}'.format(path, tab))

        #write other attributes, attached to a blank DataFrame
        store = pd.HDFStore(filename)
        store['{}/_params'.format(path)] = pd.DataFrame()
        attrs = store.get_storer('{}/_params'.format(path)).attrs
        
        params = {}
        for par in self._params:
            params[par] = getattr(self, par)

        attrs.params = params
        attrs.type = type(self)
        store.close()

    @classmethod
    def load_hdf(cls, filename, path=''):
        """Loads from hdf5 file, restoring correct properties to object
        """

        store = pd.HDFStore(filename)
        attrs = store.get_storer('{}/_params'.format(path)).attrs

        #check for property type
        mytype = attrs.type
        if mytype != cls:
            store.close()
            raise TypeError('Saved DataObject is {}.  Cannot load into {}.'.format(mytype,cls))

        #make a default object
        new = cls() #this shouldn't do any big calculation...

        #set attributes appropriately
        #fits tables
        for tab in cls._tables:
            setattr(new, tab, store['{}/{}'.format(path, tab)])

        #then other params
        for par in cls._params:
            setattr(new, par, attrs.params[par])

        return new
        
        
