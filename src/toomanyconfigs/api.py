from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

import httpx
from loguru import logger as log

from . import TOMLSubConfig
from .core import TOMLConfig

class HeadersConfig(TOMLSubConfig):
    """Configuration for HTTP headers"""
    authorization: str = "Bearer ${API_KEY}"
    accept: str = "application/json"

    def to_headers(self):
        return self.as_dict()

class Shortcuts(TOMLSubConfig):
    pass

class RoutesConfig(TOMLSubConfig):
    """Configuration for URLs and shortcuts"""
    base: str = None
    shortcuts: Shortcuts

    def get(self, item):
        return str(self.base + self.shortcuts[item])

class VarsConfig(TOMLSubConfig):
    """Configuration for variable substitution"""

class APIConfig(TOMLConfig):
    """Main API configuration with sub-configs"""
    headers: HeadersConfig
    routes: RoutesConfig
    vars: VarsConfig

    def apply_variable_substitution(self):
        """Apply variable substitution recursively to all annotated attributes"""
        vars_dict = self.vars
        log.debug(f"{self.__class__.__name__}: Starting recursive variable substitution with vars: {vars_dict}")

        self._apply_substitution_recursive(self, vars_dict, "root")
        log.debug(f"{self.__class__.__name__}: Recursive variable substitution complete")

    def _apply_substitution_recursive(self, obj, vars_dict: dict, path: str = ""):
        """Recursively apply variable substitution to object attributes"""
        log.debug(f"{self.__class__.__name__}: Processing object at path '{path}' (type: {type(obj).__name__})")

        # Get annotations for this object's class
        annotations = getattr(obj.__class__, '__annotations__', {})
        log.debug(f"{self.__class__.__name__}: Found annotations: {list(annotations.keys())}")

        for attr_name in annotations:
            if not hasattr(obj, attr_name):
                log.debug(f"{self.__class__.__name__}: Skipping missing attribute '{attr_name}' at path '{path}'")
                continue

            attr_value = getattr(obj, attr_name)
            current_path = f"{path}.{attr_name}" if path != "root" else attr_name
            log.debug(f"{self.__class__.__name__}: Processing attribute '{current_path}' with value: {attr_value} (type: {type(attr_value).__name__})")

            if isinstance(attr_value, str):
                # Apply variable substitution to string
                original_value = attr_value
                new_value = attr_value

                for var_key, var_val in vars_dict.items():
                    if var_val:
                        old_value = new_value
                        new_value = new_value.replace(f"${{{var_key.upper()}}}", str(var_val))
                        new_value = new_value.replace(f"${var_key.upper()}", str(var_val))
                        if old_value != new_value:
                            log.debug(f"{self.__class__.__name__}: Replaced variable '{var_key}' in '{current_path}': {old_value} → {new_value}")
                    else:
                        log.debug(f"{self.__class__.__name__}: Skipping empty variable '{var_key}' for '{current_path}'")

                if original_value != new_value:
                    log.debug(f"{self.__class__.__name__}: Final substitution for '{current_path}': {original_value} → {new_value}")
                    setattr(obj, attr_name, new_value)
                else:
                    log.debug(f"{self.__class__.__name__}: No changes made to string '{current_path}'")

            elif hasattr(attr_value, '__annotations__'):
                # This is a subconfig - recurse into it
                log.debug(f"{self.__class__.__name__}: Recursing into subconfig '{current_path}'")
                self._apply_substitution_recursive(attr_value, vars_dict, current_path)

            else:
                log.debug(f"{self.__class__.__name__}: Skipping non-string/non-config attribute '{current_path}' (type: {type(attr_value).__name__})")

class Headers:
    """Container for HTTP headers used in outgoing API requests."""
    index: Dict[str, str]
    accept: Optional[str] = None

    def __post_init__(self):
        self.accept = self.accept or "application/json"
        self.index["Accept"] = self.accept
        for k, v in self.index.items():
            setattr(self, k.lower().replace("-", "_"), v)
        if not self._validate():
            log.error("[Headers] Validation failed")

    def _validate(self) -> bool:
        try:
            if not isinstance(self.index, dict):
                raise TypeError
            for k, v in self.index.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ValueError
        except Exception as e:
            log.error(f"[Headers] Invalid headers: {e}")
            return False
        return True

    @cached_property
    def as_dict(self):
        return self.index

class _API:
    def __init__(self, config: APIConfig | Path = None):
        if isinstance(config, APIConfig):
            self.config = config
        elif isinstance(config, Path) or config is None:
            self.config = APIConfig.create(config)
        else:
            raise TypeError("Config must be 'APIConfig', Path, or None")
        self.config.apply_variable_substitution()

@dataclass
class Response:
    status: int
    method: str
    headers: dict
    body: Any

class Receptionist(_API):
    cache: dict[str | SimpleNamespace] = {}

    def __init__(self, config: APIConfig | Path | None = None):
        _API.__init__(self, config)

    async def api_request(self,
                          method: str,
                          route: str = None,
                          append: str = "",
                          format: dict = None,
                          force_refresh: bool = False,
                          append_headers: dict = None,
                          override_headers: dict = None,
                          **kw
                          ) -> Response:
        if not route:
            path = self.config.routes.base
        else:
            try:
                path = self.config.routes.get(route)
            except KeyError:
                path = self.config.routes.base
                path = path + str(route)

        if format:
            path = path.format(**format)
        if append:
            path += append

        if override_headers:
            headers = override_headers
        else:
            headers = self.config.headers.to_headers()
            if append_headers:
                for k in append_headers:
                    headers[k] = append_headers[k]

        log.debug(f"{self}: Attempting request to API:\n  - method={method}\n  - headers={headers}\n  - path={path}")

        if not force_refresh:
            if path in self.cache:
                cache: Response = self.cache[path]
                log.debug(f"{self}: Found cache containing same route\n  - cache={cache}")
                if cache.method is method:
                    log.debug(
                        f"{self}: Cache hit for API Request:\n  - request_path={path}\n  - request_method={method}")
                    return self.cache[path]
                else:
                    log.warning(
                        f"{self}: No match! Cache was {cache.method}, while this request is {method}! Continuing...")

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.request(method.upper(), path, **kw)

            try:
                content_type = response.headers.get("Content-Type", "")
                if "json" in content_type:
                    content = response.json()
                else:
                    content = response.text
            except Exception as e:
                content = response.text  # always fallback
                log.warning(f"{self}: Bad response decode → {e} | Fallback body: {content}")

            out = Response(
                status=response.status_code,
                method=method,
                headers=dict(response.headers),
                body=content,
            )

            self.cache[path] = out
            return self.cache[path]

    async def api_get(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("get", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

    async def api_post(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("post", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

    async def api_put(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("put", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

    async def api_delete(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("delete", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

    def sync_api_request(self,
                         method: str,
                         route: str = None,
                         append: str = "",
                         format: dict = None,
                         force_refresh: bool = False,
                         append_headers: dict = None,
                         override_headers: dict = None,
                         **kw
                         ) -> Response:
        if not route:
            path = self.config.routes.base
        else:
            try:
                path = self.config.routes.get(route)
            except KeyError:
                path = self.config.routes.base
                path = path + str(route)

        if format:
            path = path.format(**format)
        if append:
            path += append

        if override_headers:
            headers = override_headers
        else:
            headers = self.config.headers.to_headers()
            if append_headers:
                for k in append_headers:
                    headers[k] = append_headers[k]

        log.debug(f"{self}: Attempting sync request to API:\n  - method={method}\n  - headers={headers}\n  - path={path}")

        if not force_refresh:
            if path in self.cache:
                cache: Response = self.cache[path]
                log.debug(f"{self}: Found cache containing same route\n  - cache={cache}")
                if cache.method is method:
                    log.debug(
                        f"{self}: Cache hit for API Request:\n  - request_path={path}\n  - request_method={method}")
                    return self.cache[path]
                else:
                    log.warning(
                        f"{self}: No match! Cache was {cache.method}, while this request is {method}! Continuing...")

        with httpx.Client(headers=headers) as client:
            response = client.request(method.upper(), path, **kw)

            try:
                content_type = response.headers.get("Content-Type", "")
                if "json" in content_type:
                    content = response.json()
                else:
                    content = response.text
            except Exception as e:
                content = response.text  # always fallback
                log.warning(f"{self}: Bad response decode → {e} | Fallback body: {content}")

            out = Response(
                status=response.status_code,
                method=method,
                headers=dict(response.headers),
                body=content,
            )

            self.cache[path] = out
            return self.cache[path]

    def sync_api_get(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return self.sync_api_request("get", route, append=append, format=format, force_refresh=force_refresh,
                                     append_headers=append_headers, **kw)

    def sync_api_post(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return self.sync_api_request("post", route, append=append, format=format, force_refresh=force_refresh,
                                     append_headers=append_headers, **kw)

    def sync_api_put(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return self.sync_api_request("put", route, append=append, format=format, force_refresh=force_refresh,
                                     append_headers=append_headers, **kw)

    def sync_api_delete(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return self.sync_api_request("delete", route, append=append, format=format, force_refresh=force_refresh,
                                     append_headers=append_headers, **kw)

API = Receptionist

