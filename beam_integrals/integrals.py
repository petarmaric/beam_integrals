import re
from .utils import FriendlyNameFromClassMixin, PluginMount


class BaseIntegral(FriendlyNameFromClassMixin):
    _id_re = re.compile('I(\d+)')
    
    __metaclass__ = PluginMount
    
    def __str__(self):
        return self.name
    
    @property
    def id(self):
        if not hasattr(self, '_id'):
            self._id = int(self._id_re.match(self.name).group(1))
        
        return self._id


class I1(BaseIntegral):
    pass


class I2(BaseIntegral):
    pass


class I3(BaseIntegral):
    pass


class I4(BaseIntegral):
    pass


class I5(BaseIntegral):
    pass


class I6(BaseIntegral):
    pass


class I7(BaseIntegral):
    pass


class I8(BaseIntegral):
    pass


class I21(BaseIntegral):
    pass


class I22(BaseIntegral):
    pass


class I23(BaseIntegral):
    pass


class I24(BaseIntegral):
    pass


class I25(BaseIntegral):
    pass
