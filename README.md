# TooManyConfigs

A simple Python library for TOML-based configuration with interactive setup and clipboard integration.

## Installation

```bash
pip install toomanyconfigs
```

## Basic Usage

```python
from dataclasses import dataclass
from toomanyconfigs import TOMLDataclass

@dataclass #You must inherit TOMLDataclass on another dataclass
class Test(TOMLDataclass):
    foo: str = None #Each field that should prompt user input should be 'None'

if __name__ == "__main__":
    Test.create() #Without specifying a path, TOMLDataclass will automatically make a .toml in your cwd with the name of your inheriting class.
```
```
2025-07-25 14:04:37.151 | WARNING  | toomanyconfigs.core:from_toml:37 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml, creating new one
Test(foo=None): Enter value for 'foo' (or press Enter to paste from clipboard): bar
2025-07-25 14:04:45.721 | SUCCESS  | toomanyconfigs.core:_prompt_field:91 - Test(foo='bar'): Set foo
2025-07-25 14:04:45.721 | DEBUG    | toomanyconfigs.core:write:101 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml
```
```
2025-07-25 14:09:30.142 | DEBUG    | toomanyconfigs.core:read:110 - [TooManyConfigs] Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml
2025-07-25 14:09:30.143 | DEBUG    | toomanyconfigs.core:_load_from_data:59 - Test(foo='bar'): Loaded foo from config
```

## Advanced Usage

```python
from loguru import logger as log

@dataclass
class Test2(TOMLDataclass):
    foo: str = None
    bar: int = 33 #We'll set bar at 33 to demonstrate the translation ease between dynamic python objects and .toml

if __name__ == "__main__":
    t = Test2.create() #initialize a dataclass from a .toml
    log.debug(t.bar) #view t.bar
    t.bar = 34 #override python memory
    log.debug(t.bar) #view updated t.bar
    t.write() #write to the specified .toml file
    data = t.read() #ensure overwriting
    log.debug(data)
```
```
2025-07-25 14:36:16.836 | DEBUG    | toomanyconfigs.core:read:111 - [TooManyConfigs] Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml
2025-07-25 14:36:16.837 | DEBUG    | toomanyconfigs.core:_load_from_data:59 - Test(foo='bar'): Loaded foo from config
2025-07-25 14:36:16.838 | WARNING  | toomanyconfigs.core:from_toml:37 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml, creating new one
Test2(foo=None, bar=33): Enter value for 'foo' (or press Enter to paste from clipboard): val
2025-07-25 14:36:18.826 | SUCCESS  | toomanyconfigs.core:_prompt_field:92 - Test2(foo='val', bar=33): Set foo
2025-07-25 14:36:18.826 | DEBUG    | toomanyconfigs.core:write:102 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
2025-07-25 14:36:18.827 | DEBUG    | __main__:<module>:34 - 33
2025-07-25 14:36:18.828 | DEBUG    | __main__:<module>:36 - 34
2025-07-25 14:36:18.828 | DEBUG    | toomanyconfigs.core:write:102 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
2025-07-25 14:36:18.829 | DEBUG    | toomanyconfigs.core:read:111 - [TooManyConfigs] Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
2025-07-25 14:36:18.831 | DEBUG    | __main__:<module>:39 - {'foo': 'val', 'bar': 34}
```

## API Configurations

### Basic API Usage

```python
from toomanyconfigs import API

if __name__ == "__main__":
    api = API()
```
```
2025-07-28 16:37:56.222 | WARNING  | src.toomanyconfigs.core:create:47 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml, creating new one
2025-07-28 16:37:56.223 | INFO     | src.toomanyconfigs.core:_prompt_all_fields:130 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), url=RoutesConfig(base='', routes={}), vars=VarsConfig(api_key=None)): Configuring sub-section 'headers'
2025-07-28 16:37:56.223 | INFO     | src.toomanyconfigs.core:_prompt_all_fields:130 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), url=RoutesConfig(base='', routes={}), vars=VarsConfig(api_key=None)): Configuring sub-section 'url'
2025-07-28 16:37:56.223 | INFO     | src.toomanyconfigs.core:_prompt_all_fields:130 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), url=RoutesConfig(base='', routes={}), vars=VarsConfig(api_key=None)): Configuring sub-section 'vars'
VarsConfig(api_key=None): Enter value for 'api_key' (or press Enter to paste from clipboard): foobar
2025-07-28 16:38:01.264 | SUCCESS  | src.toomanyconfigs.core:_prompt_field:161 - VarsConfig(api_key='foobar'): Set api_key
2025-07-28 16:38:01.264 | DEBUG    | src.toomanyconfigs.core:write:170 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml
```

Generated TOML:
```toml
[headers]
authorization = "Bearer: ${API_KEY}"
accept = "application/json"

[url]
base = ""

[vars]
api_key = "foobar"

[url.routes]
```

### Advanced API Usage

```python
import asyncio
from toomanyconfigs import API, APIConfig, HeadersConfig, RoutesConfig, VarsConfig
from loguru import logger as log

if __name__ == "__main__":
    base_url = 'https://jsonplaceholder.typicode.com/'
    quick_routes = {
        "c": "/comments?postId=1"
    }
    routes = RoutesConfig(
        base=base_url,
        routes=quick_routes
    )
    cfg = APIConfig.create(
        routes=routes,
    )
    json_placeholder = API(cfg)
    response = asyncio.run(json_placeholder.api_get("c"))
    log.debug(response)
```
```
2025-07-28 16:52:57.364 | WARNING  | toomanyconfigs.core:create:47 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml, creating new one
2025-07-28 16:52:57.364 | INFO     | toomanyconfigs.core:_prompt_all_fields:130 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), routes=RoutesConfig(base='https://jsonplaceholder.typicode.com/', routes={'c': '/comments?postId=1'}), vars=VarsConfig(api_key=None)): Configuring sub-section 'headers'
2025-07-28 16:52:57.364 | INFO     | toomanyconfigs.core:_prompt_all_fields:130 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), routes=RoutesConfig(base='https://jsonplaceholder.typicode.com/', routes={'c': '/comments?postId=1'}), vars=VarsConfig(api_key=None)): Configuring sub-section 'routes'
2025-07-28 16:52:57.365 | INFO     | toomanyconfigs.core:_prompt_all_fields:130 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), routes=RoutesConfig(base='https://jsonplaceholder.typicode.com/', routes={'c': '/comments?postId=1'}), vars=VarsConfig(api_key=None)): Configuring sub-section 'vars'
VarsConfig(api_key=None): Enter value for 'api_key' (or press Enter to paste from clipboard): foobar
2025-07-28 16:53:09.950 | SUCCESS  | src.toomanyconfigs.core:_prompt_field:161 - VarsConfig(api_key='foobar'): Set api_key
2025-07-28 16:53:09.952 | DEBUG    | src.toomanyconfigs.core:write:170 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml
2025-07-28 16:53:09.959 | DEBUG    | toomanyconfigs.api:api_request:176 - <toomanyconfigs.api.Receptionist object at 0x000001F8D230F380>: Attempting request to API:
  - method=get
  - headers={'Authorization': 'Bearer foobar', 'Accept': 'application/json'}
  - path=https://jsonplaceholder.typicode.com//comments?postId=1
2025-07-28 16:53:10.716 | DEBUG    | __main__:<module>:105 - Response(status=200, method='get', headers={'date': 'Mon, 28 Jul 2025 21:53:10 GMT', 'content-type': 'application/json; charset=utf-8', 'content-length': '657', 'connection': 'keep-alive', 'access-control-allow-credentials': 'true', 'cache-control': 'no-cache', 'content-encoding': 'gzip', 'etag': 'W/"5e6-4bSPS5tq8F8ZDeFJULWh6upjp7U"', 'expires': '-1', 'nel': '{"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}', 'pragma': 'no-cache', 'report-to': '{"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=dDOiIoCyXvurmNJkKE2aaOtJIHNjkpULnmhy79xG8BQ%3D\\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\\u0026ts=1753739590"}],"max_age":3600}', 'reporting-endpoints': 'heroku-nel="https://nel.heroku.com/reports?s=dDOiIoCyXvurmNJkKE2aaOtJIHNjkpULnmhy79xG8BQ%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1753739590"', 'server': 'cloudflare', 'vary': 'Origin, Accept-Encoding', 'via': '2.0 heroku-router', 'x-content-type-options': 'nosniff', 'x-powered-by': 'Express', 'x-ratelimit-limit': '1000', 'x-ratelimit-remaining': '999', 'x-ratelimit-reset': '1753739631', 'cf-cache-status': 'BYPASS', 'cf-ray': '96679b97d9ecfa09-MCI', 'alt-svc': 'h3=":443"; ma=86400'}, body=[{'postId': 1, 'id': 1, 'name': 'id labore ex et quam laborum', 'email': 'Eliseo@gardner.biz', 'body': 'laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium'}, {'postId': 1, 'id': 2, 'name': 'quo vero reiciendis velit similique earum', 'email': 'Jayne_Kuhic@sydney.com', 'body': 'est natus enim nihil est dolore omnis voluptatem numquam\net omnis occaecati quod ullam at\nvoluptatem error expedita pariatur\nnihil sint nostrum voluptatem reiciendis et'}, {'postId': 1, 'id': 3, 'name': 'odio adipisci rerum aut animi', 'email': 'Nikita@garfield.biz', 'body': 'quia molestiae reprehenderit quasi aspernatur\naut expedita occaecati aliquam eveniet laudantium\nomnis quibusdam delectus saepe quia accusamus maiores nam est\ncum et ducimus et vero voluptates excepturi deleniti ratione'}, {'postId': 1, 'id': 4, 'name': 'alias odio sit', 'email': 'Lew@alysha.tv', 'body': 'non et atque\noccaecati deserunt quas accusantium unde odit nobis qui voluptatem\nquia voluptas consequuntur itaque dolor\net qui rerum deleniti ut occaecati'}, {'postId': 1, 'id': 5, 'name': 'vero eaque aliquid doloribus et culpa', 'email': 'Hayden@althea.biz', 'body': 'harum non quasi et ratione\ntempore iure ex voluptates in ratione\nharum architecto fugit inventore cupiditate\nvoluptates magni quo et'}])
```

Generated TOML:
```toml
[headers]
authorization = "Bearer ${API_KEY}"
accept = "application/json"

[routes]
base = "https://jsonplaceholder.typicode.com/"

[vars]
api_key = "foobar"

[routes.routes]
c = "/comments?postId=1"
```