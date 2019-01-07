import os
import socket
from collections import abc
from typing import Any, Dict, Optional

import yaml

from wallet.validation import ValidationError, Validator


class ImproperlyConfigured(Exception):
    pass


class Config(abc.MutableMapping):
    def __init__(self, schema: Dict[str, str], initial: Optional[Dict[str, str]] = None) -> None:
        self._fields = {
            "app_hostname": socket.gethostname(),
            "access_log": '%a %s %Tf %b "%r" "%{Referrer}i" "%{User-Agent}i"',
            "db_name": "postgres",
            "db_user": "postgres",
            "db_password": "postgres",
            "db_host": "localhost",
            "db_port": 5432,
            "consul_host": "localhost",
            "consul_port": 8500,
            "logging": {
                "version": 1,
                "formatters": {
                    "simple": {
                        "format": "%(asctime)s | %(levelname)s | %(message)s",
                        "datefmt": "%Y-%m-%d %H:%M:%S",
                    }
                },
                "handlers": {
                    "console": {
                        "level": "INFO",
                        "class": "logging.StreamHandler",
                        "formatter": "simple",
                        "stream": "ext://sys.stdout",
                    }
                },
                "loggers": {
                    "aiohttp": {"level": "INFO", "handlers": ["console"], "propagate": False},
                    "app": {"level": "INFO", "handlers": ["console"], "propagate": False},
                },
            },
        }
        self._schema = schema

        if initial and isinstance(initial, dict):
            for key, value in iter(initial.items()):
                self[key] = value

    def __setitem__(self, key: str, value: str) -> None:
        self._fields[key] = value

    def __getitem__(self, key: str) -> Any:
        return self._fields[key]

    def __delitem__(self, key: str) -> None:
        del self._fields[key]

    def __iter__(self):
        return iter(self._fields)

    def __len__(self) -> int:
        return len(self._fields)

    def __str__(self) -> str:
        return str(self._fields)

    def validate(self) -> None:
        config_validator = Validator(schema=self._schema)

        try:
            config_validator.validate_payload(self._fields)
        except ValidationError:
            raise ImproperlyConfigured(config_validator.errors)

        self.__dict__.update(**config_validator.document)

    def update_from_env_var(self, variable_name: str) -> None:
        value = os.environ.get(variable_name.upper())
        if value:
            self[variable_name] = value

    def update_from_yaml(self, filename: str, silent: bool = False) -> None:
        if not filename.endswith("yml"):
            raise RuntimeError("Config should be in yaml format")

        try:
            with open(filename, "r") as fp:
                data = fp.read()
                conf = yaml.load(data)
        except IOError as exc:
            if not silent:
                exc.strerror = "Unable to load configuration file `{}`".format(exc.strerror)
                raise
        else:
            for key, value in iter(conf.items()):
                self[key] = value
