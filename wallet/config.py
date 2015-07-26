from collections import abc
import os
import errno
import yaml


class Config(abc.MutableMapping):

    def __init__(self, root_path, defaults=None):
        self.root_path = root_path
        self.__dict__.update(self._keys_to_upper(defaults or {}))

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def _keys_to_upper(self, obj):
        return {key.upper(): value for key, value in iter(obj.items())}

    def from_envvar(self, variable_name, silent=False):
        rv = os.environ.get(variable_name)
        if not rv:
            if silent:
                return False
            else:
                raise RuntimeError('The environment variable %r is not set. '
                                   'Set this variable.' % variable_name)
        self[variable_name] = rv

    def from_yaml(self, filename, silent=False):
        if self.root_path:
            filename = os.path.join(self.root_path, filename)

        try:
            with open(filename, 'rb') as fp:
                data = fp.read()
                config = yaml.load(data)
        except IOError as exc:
            if silent and exc.errno in (errno.ENOENT, errno.EISDIR):
                return False
            exc.strerror = 'Unable to load configuration file (%s)' % exc.strerror
            raise
        self.__dict__.update(**self._keys_to_upper(config))
        return True

    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)
