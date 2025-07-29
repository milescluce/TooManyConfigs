from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

import httpx
from loguru import logger as log

from . import TOMLSubConfig, DEBUG
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
        """Apply variable substitution recursively to all dict values"""
        vars_dict = self.vars
        if DEBUG:
            log.debug(f"[{self.__class__.__name__}]: Starting variable substitution with vars: {vars_dict}")

        self._substitute_dict_values(self, vars_dict)
        if DEBUG:
            log.debug(f"[{self.__class__.__name__}]: Variable substitution complete")

    def _substitute_dict_values(self, obj, vars_dict: dict):
        """Recursively substitute variables in all string values within dict-like objects"""
        if DEBUG:
            log.debug(f"[{self.__class__.__name__}]: Processing dict-like object: {type(obj).__name__}")

        # Handle both regular dicts and dict-like config objects
        if hasattr(obj, 'items'):
            items = obj.items()
        elif hasattr(obj, '__dict__'):
            items = obj.__dict__.items()
        else:
            if DEBUG:
                log.debug(f"[{self.__class__.__name__}]: Object {type(obj).__name__} is not dict-like, skipping")
            return

        for key, value in items:
            if key.startswith('_'):
                continue  # Skip private attributes

            if DEBUG:
                log.debug(f"[{self.__class__.__name__}]: Processing key '{key}' with value: {value} (type: {type(value).__name__})")

            if isinstance(value, str):
                # Apply variable substitution to string
                original_value = value
                new_value = value

                for var_key, var_val in vars_dict.items():
                    if var_val:
                        old_value = new_value
                        new_value = new_value.replace(f"${{{var_key.upper()}}}", str(var_val))
                        new_value = new_value.replace(f"${var_key.upper()}", str(var_val))
                        if old_value != new_value and DEBUG:
                            log.debug(f"[{self.__class__.__name__}]: Replaced '{var_key}' in '{key}': {old_value} → {new_value}")

                if original_value != new_value:
                    log.success(f"[{self.__class__.__name__}]: Final substitution for '{key}': {original_value} → {new_value}")
                    try:
                        if hasattr(obj, 'items'):
                            obj[key] = new_value  # Regular dict
                        else:
                            setattr(obj, key, new_value)  # Config object
                    except (AttributeError, TypeError) as e:
                        if DEBUG:
                            log.debug(f"[{self.__class__.__name__}]: Cannot set '{key}': {e}")
                elif DEBUG:
                    log.debug(f"[{self.__class__.__name__}]: No changes for '{key}'")

            elif isinstance(value, (dict, object)) and not isinstance(value, (int, float, bool, list, tuple, str)):
                # Recurse into dict-like objects
                if DEBUG:
                    log.debug(f"[{self.__class__.__name__}]: Recursing into '{key}'")
                self._substitute_dict_values(value, vars_dict)

            elif DEBUG:
                log.debug(f"[{self.__class__.__name__}]: Skipping '{key}' (type: {type(value).__name__})")

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

    def __repr__(self):
        return f"[{self.__class__.__name__}]"

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

        log.info(f"{self}: Attempting request to API:\n  - method={method}\n  - headers={headers}\n  - path={path}")

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

        log.info(f"{self}: Attempting sync request to API:\n  - method={method}\n  - headers={headers}\n  - path={path}")

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

