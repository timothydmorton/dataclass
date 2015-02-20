__version__ = '0.0'

try:
    __DATAOBJECT_SETUP__
except NameError:
    __DATAOBJECT_SETUP__ = False

if not __DATAOBJECT_SETUP__:
    pass

from .dataobject import DataObject


