#!coding: utf-8
import json
import logging
import os
import urllib.parse
from importlib import import_module
from tornado.httpclient import AsyncHTTPClient, HTTPClient
from tornado.ioloop import PeriodicCallback

import dotdict
from confhelper import ConfHelper

CONF_ENV = "CONFIG_FILE"
# a .py module
SETTINGS_EVN = "SETTING_MODULE"

# net config
SETTING_SERVICE = "SETTING_SERVICE"


_logger = logging.getLogger(__name__)


class ImproperlyConfigured(Exception):
    """Improperly configured"""
    pass


class ConfService(object):
    def __init__(self, protocol, host, namespace, arg):
        self.protocol = protocol
        self.host = host
        self.namespace = namespace
        self.arg = arg
        self._setup()

    def _setup(self):
        raise NotImplementedError()

    def get(self, key):
        raise NotImplementedError()

    def __getitem__(self, item):
        value = self.get(item)
        if value is None:
            raise KeyError("can not get value with key:%s" % item)
        return value


class HTTPConfService(ConfService):
    _wrapped = None
    poll_interval = 5 * 1000
    client = AsyncHTTPClient()

    STATUS_REMAIN = 204
    STATUS_UPDATE = 200

    _code = None
    # last err info
    _err_info = None

    @property
    def uri(self):
        return "{scheme}://{host}/conf/{namespace}".format(
            scheme=self.protocol, host=self.host, namespace=self.namespace
        )

    def _call_back(self, response):
        self._code = response.code
        err_info = None
        if response.error:
            err_info = "conf service is down with err:%s" % response.error
        elif response.code == self.STATUS_REMAIN:
            pass
        elif response.code == self.STATUS_UPDATE:
            raw_data = response.body
            try:
                data = json.loads(raw_data)
                if type(data) is not dict:
                    raise ValueError
                self._wrapped = type("_wrapped", (object,), data)
            except ValueError:
                err_info = "got invalid format response %s" % raw_data
        else:
            err_info = "unrecognized response code %s" % response.code
        self._err_info = err_info
        if err_info:
            _logger.error(err_info)
            # TODO: broadcast this err message

    def _poll(self):
        self.client.fetch(self.uri, self._call_back)

    def first_sync(self):
        response = HTTPClient().fetch(self.uri)
        self._call_back(response)
        if self._err_info:
            # no err would occur in initializing context
            raise ValueError(self._err_info)

    def _setup(self):
        # initialize
        self.first_sync()
        PeriodicCallback(self._poll, self.poll_interval)

    def get(self, key):
        return getattr(self._wrapped, key, None)


# map config
_PROTOCOL = {
    "http": HTTPConfService
}


def get_conf_service(route):
    """Dispatch a conf service  client with `route`
    :param route: {protocol}://{host}/{namespace}?{arg}

    * `route` is not the uri of conf service, don't request the route

    Usage Example
    -------------
    httpConfService = get_conf_service("http://localhost:1516/gateway")
    env_conf = httpConfService.get("ENV_CONF")

    # a socket service
    sockConfService = get_conf_service("sock://localhost:1516/gateway")
    env_conf = sockConfService.get("ENV_CONF")

    """
    re = urllib.parse.urlsplit(route)
    namespace = re.path.replace("/", "")
    host = re.netloc
    protocol = re.scheme
    arg = re.query
    if protocol not in _PROTOCOL:
        raise ValueError("unsupported protocol %s" % protocol)
    return _PROTOCOL[protocol](protocol, host, namespace, arg)


def check_database_conf(config):
    assert len(list(config.keys())) > 0, "invalid settings of database"

required_settings = {
}


class DummyWrapped(object):
    def __getattr__(self, item):
        return None


class LazySettings(object):
    """Lazy Object as a proxy of config object
    """
    def __init__(self):
        self._wrapped = None

    def _setup(self):
        """Setup settings from either config file or setting module
        """
        conf_file = os.environ.get(CONF_ENV)
        settings_mod = os.environ.get(SETTINGS_EVN)
        settings_service_route = os.environ.get(SETTING_SERVICE)
        if all([k is None for k in [conf_file, settings_mod, settings_service_route]]) and not ConfHelper.loaded():
            desc = "Before using conf, " \
                   "you must set environment variable %s, %s or %s" % (CONF_ENV, SETTINGS_EVN, SETTING_SERVICE)
            raise ImproperlyConfigured(desc)

        if ConfHelper.loaded():
            self._wrapped = ConfHelper

        elif conf_file:
            self._setup_from_config(conf_file)

        elif settings_mod:
            self._setup_from_settings(settings_mod)

        else:
            # Dummy wrapped
            self._wrapped = DummyWrapped()

        if settings_service_route:
            self._conf_service = get_conf_service(settings_service_route)
        else:
            # ensure attribute `_conf_service` be set
            self._conf_service = DummyWrapped()

        self._check_settings()

    def _setup_from_settings(self, settings_mod):
        try:
            mod = import_module(settings_mod)
        except ImportError:
            raise ImproperlyConfigured("Can not import settings module with %s" % settings_mod)
        else:
            self._wrapped = mod

    def _setup_from_config(self, conf_file):
        try:
            ConfHelper.load(conf_file=conf_file)
        except Exception:
            raise ImproperlyConfigured("Can not load config file %s" % conf_file)
        else:
            self._wrapped = ConfHelper

    def _check_settings(self):
        # To check required settings
        for key, validator in list(required_settings.items()):
            config = getattr(self._wrapped, key)
            assert config, "need settings of %s" % key
            validator(config)

    def __getattr__(self, name):
        if self._wrapped is None:
            self._setup()
        value = getattr(self._wrapped, name, None)
        #
        if value is None:
            return getattr(self._conf_service, name)
        if type(value) is dict:
            value = dotdict.DotDict(value)
            setattr(self._wrapped, name, value)
        return value


settings = LazySettings()


def setup_logging(logging_config):
    import logging.config
    logging.config.dictConfig(logging_config)
