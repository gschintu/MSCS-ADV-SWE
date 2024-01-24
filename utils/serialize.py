""" JSON Serial Data Manager """

import json

from collections.abc import (
    Sequence,
    Mapping
)

class SerializeJSON:
    """ JSON Serializer """
    
    def __init__(self, jsonobject):
        if not isinstance(jsonobject, (Mapping, Sequence, str, float, int, bool, type(None))):
            raise ValueError("Object is not a valid JSON Object")
        self.object = dict(jsonobject)
        
    def __getattr__(self, data):
        if isinstance(self.object, Mapping):
            if data in self.object:
                return self.drill(self.object[data])
            raise AttributeError(f"'{type(self).__name__}' object has not attribute '{data}'")
        raise TypeError(f"'{type(self).__name__}' underlying object is not a dictionary")

    @classmethod
    def drill(cls, data):
        """ recurse through mapping """

        if isinstance(data, Mapping):
            return cls(data)
        elif isinstance(data, Sequence) and not isinstance(data, str):
            return [cls.drill(i) for i in data]
        else:
            return data
