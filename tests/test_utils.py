from nose.tools import eq_, raises
from nose_extra_tools import assert_equal, assert_is, issues_warnings #@UnresolvedImport
from beam_integrals.exceptions import CoercionError, PerformanceWarning
from beam_integrals.utils import AttrDict, FriendlyNameFromClassMixin, PluginMount


def test_friendly_name_from_class_mixin():
    class IsHTML5BetterThanFlash11OrIsItMe(FriendlyNameFromClassMixin):
        answer = 'yes'
    
    eq_(
        IsHTML5BetterThanFlash11OrIsItMe().name,
        'Is HTML5 Better Than Flash11 Or Is It Me'
    )


class TestPluginMount(object):
    def setup_http_method_plugins(self):
        class HTTPMethod(FriendlyNameFromClassMixin):
            """Mount point should not be registered as a plugin"""
            __metaclass__ = PluginMount
            class Meta:
                id_field = 'name'
                id_field_coerce = str
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
        
        self.HTTPMethod = HTTPMethod
        self.GET = GET
        self.POST = POST
        self.FakePOST = FakePOST
        
        self.actual_http_method_id = 'POST'
        self.desired_http_method_instance = HTTPMethod.plugins.id_to_instance[
            self.actual_http_method_id
        ]
        
        id_to_class = {
            'GET': GET, 'POST': POST, 'Fake POST': FakePOST, 'PUT': PUT,
            'DELETE': DELETE
        }
        self.desired_http_method_plugins = AttrDict(
            classes=set(id_to_class.values()),
            id_to_class=id_to_class,
            class_to_id=dict((v, k) for k, v in id_to_class.items()),
            classes_sorted_by_id=[v for _, v in sorted(id_to_class.items())],
            valid_ids=set(id_to_class.keys()),
        )
    
    def setup_http_response_plugins(self):
        class HttpResponse(object):
            """Mount point should not be registered as a plugin"""
            status_code = None
            __metaclass__ = PluginMount
            class Meta:
                id_field = 'status_code'
            @classmethod
            def _contribute_to_plugins(cls, _plugins):
                _plugins.contribute_to_plugins_works = True
        class OK(HttpResponse):
            status_code = 200
        class BaseRedirection(HttpResponse):
            """Both parent and its child should be registered as plugins"""
            pass
        class MovedPermanently(BaseRedirection):
            status_code = 301
        class NotModified(BaseRedirection):
            status_code = 304
        class BadRequest(HttpResponse):
            status_code = 400
        class NotFound(HttpResponse):
            status_code = 404
        
        self.HttpResponse = HttpResponse
        
        self.actual_http_response_class = MovedPermanently
        self.desired_http_response_instance = HttpResponse.plugins.id_to_instance[
            self.actual_http_response_class.status_code
        ]
        self.desired_http_response_class = type(self.desired_http_response_instance)
    
    def setup(self):
        self.setup_http_method_plugins()
        self.setup_http_response_plugins()
    
    def test_plugin_registration(self):
        # Not comparing as sets to be able to confirm there are no duplicates
        # in the plugin registry
        assert_equal(
            sorted(self.HTTPMethod._plugin_registry),
            sorted(self.desired_http_method_plugins.classes)
        )
    
    def test_plugin_info(self):
        actual_plugins = self.HTTPMethod.plugins.copy()
        
        # Special case for any instances related information
        assert_equal(
            set(type(obj) for obj in actual_plugins.pop('instances')),
            self.desired_http_method_plugins.classes
        )
        assert_equal(
            dict((k, type(v)) for k, v in actual_plugins.pop('id_to_instance').items()),
            self.desired_http_method_plugins.id_to_class
        )
        assert_equal(
            [type(obj) for obj in actual_plugins.pop('instances_sorted_by_id')],
            self.desired_http_method_plugins.pop('classes_sorted_by_id')
        )
        
        # Compare the remaining plugin information directly
        assert_equal(actual_plugins, self.desired_http_method_plugins)
    
    def test_contribute_to_plugins(self):
        assert_is(self.HttpResponse.plugins.contribute_to_plugins_works, True)
    
    def test_distant_relatives_use_same_plugin_info_cache(self):
        self.GET._plugins = None
        self.POST._plugins = None
        assert_is(self.GET.plugins, self.POST.plugins)
    
    def test_child_uses_same_plugin_info_cache_as_parent(self):
        self.FakePOST._plugins = None
        self.POST._plugins = None
        assert_is(self.FakePOST.plugins, self.POST.plugins)
    
    def test_child_uses_same_plugin_info_cache_as_base_class(self):
        self.FakePOST._plugins = None
        self.HTTPMethod._plugins = None
        assert_is(self.FakePOST.plugins, self.HTTPMethod.plugins)
    
    def test_parent_uses_same_plugin_info_cache_as_base_class(self):
        self.POST._plugins = None
        self.HTTPMethod._plugins = None
        assert_is(self.POST.plugins, self.HTTPMethod.plugins)
    
    def test_plugins_not_shared_between_mount_points(self):
        assert self.HTTPMethod.plugins.classes.isdisjoint(
            self.HttpResponse.plugins.classes
        )
    
    @issues_warnings(PerformanceWarning)
    def test_coerce_valid_http_response_instance(self):
        assert_is(
            type(self.HttpResponse.coerce(self.actual_http_response_class())),
            self.desired_http_response_class
        )
    
    @issues_warnings(PerformanceWarning)
    def test_coerce_valid_http_response_class(self):
        assert_is(
            type(self.HttpResponse.coerce(self.actual_http_response_class)),
            self.desired_http_response_class
        )
    
    def test_coerce_works_with_empty_plugin_info_cache(self):
        self.HttpResponse._plugins = None
        self.HTTPMethod.coerce(self.actual_http_method_id)
    
    def test_coerce_nonnumeric_id(self):
        assert_is(
            self.HTTPMethod.coerce(self.actual_http_method_id),
            self.desired_http_method_instance
        )
    
    def test_coerce_valid_http_response_id(self):
        assert_is(
            self.HttpResponse.coerce(self.actual_http_response_class.status_code),
            self.desired_http_response_instance
        )
    
    @raises(CoercionError)
    def test_coerce_invalid_http_response_id(self):
        self.HttpResponse.coerce(-1)
    
    @raises(CoercionError)
    def test_coerce_unknown_type(self):
        self.HttpResponse.coerce(object())
