from __future__ import print_function, division

import os, os.path
import pandas as pd
import numpy as np

class DataStore(object):
    def __init__(self, data=None, **kwargs):
        """Basic constructor.

        """
        self._maintable = 'data' 
        self._properties = []

        if data is None:
            return
        elif type(data)==type(''):
            self.load_hdf(data)
        else:
            assert type(data) in (pd.DataFrame, pd.Series)

            self.data = data

            for kw,val in kwargs.items():
                self._properties.append(kw)
                setattr(self, kw, val)
            
            #require proper other tables to be defined
            need_tables = []
            for t in self._othertables:
                if not hasattr(self, t):
                    need_tables.append(t)

            if need_tables != []:
                raise ValueError('You must provide table(s): {}'.format(need_tables))
            
    @property
    def _othertables(self):
        """list of names of other tables to save (besides "data")

        all tables must be pandas DataFrames or Series
        """
        return []

    def save_hdf(self, filename, path='', properties=None,
                 overwrite=False, append=False):
        """Saves to hdf5 file, under given path

        all attributes are attached to the 'data' table
        """

        if os.path.exists(filename):
            if overwrite:
                os.remove(filename)
            elif not append:
                raise IOError('{} exists. Set either overwrite or append option.'.format(filename))


        #write main datatable
        df = getattr(self, self._maintable)
        df.to_hdf(filename, '{}/{}'.format(path, self._maintable))

        #write other attributes
        store = pd.HDFStore(filename)
        attrs = store.get_storer('{}/{}'.format(path,self._maintable)).attrs

        if properties is None:
            properties = {}
        for p in self._properties:
            properties[p] = getattr(self, p)
        attrs.properties = properties
        #save type, so that object can only be restored to proper type
        attrs.type = type(self)
        store.close()

        for t in self._othertables:
            df = getattr(self, t)
            df.to_hdf(filename, '{}/{}'.format(path,t))

    
    def load_hdf(self, filename, path=''):
        """Loads from hdf5 file, restoring correct properties to object
        """

        store = pd.HDFStore(filename)
        attrs = store.get_storer('{}/{}'.format(path,self._maintable)).attrs

        #check for property type
        mytype = attrs.type
        if mytype != type(self):
            raise TypeError('Saved DataStore is {}.  Please instantiate proper class before loading.'.format(mytype))

        #restore attributes
        for kw, val in attrs.properties.items():
            setattr(self, kw, val)

        store.close()

        #load main data table
        data = pd.read_hdf(filename, '{}/{}'.format(path,self._maintable),
                           autoclose=True)
        setattr(self, self._maintable, data)

        #load other tables, if necessary
        for t in self._othertables:
            df = pd.read_hdf(filename, '{}/{}'.format(path,t),
                             autoclose=True)
            setattr(self, t, df)

        return self

        
        
