import abc
from typing_extensions import Self

class ISerializable(metaclass=abc.ABCMeta):
    
    @abc.abstractstaticmethod
    def fromJson(json:dict) -> Self:
        pass
    
    @abc.abstractmethod
    def toJson(self:Self) -> dict:
        pass
    
    