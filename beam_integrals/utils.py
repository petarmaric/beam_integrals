import re


# Based on `django.db.models.options.get_verbose_name`
class FriendlyNameFromClassMixin(object):
    _name_re = re.compile('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z0-9]|$)))')
    
    @property
    def name(self):
        if not hasattr(self, '_name'):
            class_name = self.__class__.__name__
            self._name = self._name_re.sub(r' \1', class_name).strip()
        
        return self._name


# Based on http://djangosnippets.org/snippets/542/
class PluginMount(type):
    def __init__(cls, name, bases, attrs): #@UnusedVariable
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # Don't register 'Base*' classes as plugin implementations
            if not name.startswith('Base'):
                # This must be a plugin implementation, which should be registered.
                # Simply appending it to the list is all that's needed to keep
                # track of it later.
                cls.plugins.append(cls)
