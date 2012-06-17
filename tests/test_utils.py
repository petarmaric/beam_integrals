from nose.tools import eq_
from beam_integrals.utils import FriendlyNameFromClassMixin, PluginMount


def test_friendly_name_from_class_mixin():
    class IsHTML5BetterThanFlash11OrIsItMe(FriendlyNameFromClassMixin):
        answer = 'yes'
    
    eq_(
        IsHTML5BetterThanFlash11OrIsItMe().name,
        'Is HTML5 Better Than Flash11 Or Is It Me'
    )


class TestPluginMount(object):
    def setup_crud_operation_plugins(self):
        class CRUDOperation(object):
            """Mount point should not be registered as a plugin"""
            __metaclass__ = PluginMount
        class Create(CRUDOperation):
            pass
        class Read(CRUDOperation):
            pass
        class Update(CRUDOperation):
            pass
        class Delete(CRUDOperation):
            pass
        
        self.desired_crud_operation_plugins = set((Create, Read, Update, Delete))
        self.actual_crud_operation_plugins = set(CRUDOperation.plugins)
        
    def setup_http_method_plugins(self):
        class HTTPMethod(object):
            """Mount point should not be registered as a plugin"""
            __metaclass__ = PluginMount
        class BaseIdempotentHTTPMethod(HTTPMethod):
            """'Base*' classes should not be registered as plugins"""
            pass
        class GET(BaseIdempotentHTTPMethod):
            pass
        class POST(HTTPMethod):
            pass
        class FakePOST(HTTPMethod):
            """Both parent and its child should be registered as plugins"""
            pass
        class PUT(BaseIdempotentHTTPMethod):
            pass
        class DELETE(BaseIdempotentHTTPMethod):
            pass
        
        self.desired_http_method_plugins = set((GET, POST, FakePOST, PUT, DELETE))
        self.actual_http_method_plugins = set(HTTPMethod.plugins)
    
    def setup(self):
        self.setup_crud_operation_plugins()
        self.setup_http_method_plugins()
    
    def test_crud_operation_plugins(self):
        eq_(
            self.actual_crud_operation_plugins,
            self.desired_crud_operation_plugins
        )
    
    def test_http_method_plugins(self):
        eq_(self.actual_http_method_plugins, self.desired_http_method_plugins)
    
    def test_plugins_not_shared_between_mount_points(self):
        assert self.actual_crud_operation_plugins.isdisjoint(
            self.actual_http_method_plugins
        )
