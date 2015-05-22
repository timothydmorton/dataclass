dataclass
---------

A generic python object enabling straightforward persistence of data tables and attributes.
    
simple example demonstrated `here <http://nbviewer.ipython.org/github/timothydmorton/dataclass/blob/master/examples/test_datastore.ipynb>`_.

If the main table attribute of a subclass is not named 'data', then the ``_maintable`` property must be overwritten to return the proper name.   
