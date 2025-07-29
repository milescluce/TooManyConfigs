import asyncio
from dataclasses import field
from pathlib import Path

from src.toomanyconfigs.api import Shortcuts
### Basic Usage
from toomanyconfigs import TOMLConfig

class Test(TOMLConfig):
    foo: str = None #Each field that should prompt user input should be 'None'

if __name__ == "__main__":
    Test.create()  #Without specifying a path, TOMLDataclass will automatically make a .toml in your cwd with the name of your inheriting class.

#Example STDOUT
# 2025-07-29 01:06:55.623 | WARNING  | toomanyconfigs.core:create:164 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml, creating new one
# 2025-07-29 01:06:55.624 | INFO     | toomanyconfigs.core:create:182 - [Test]: Missing fields detected: ['foo']
# [Test]: Enter value for 'foo' (or press Enter to paste from clipboard): bar
# 2025-07-29 01:06:59.532 | SUCCESS  | toomanyconfigs.core:_prompt_field:226 - [Test]: Set foo

### Advanced Usage
from toomanyconfigs import TOMLConfig
from loguru import logger as log

class Test2(TOMLConfig):
    foo: str = None
    bar: int = 33 #We'll set bar at 33 to demonstrate the translation ease between dynamic python objects and .toml

if __name__ == "__main__":
    t = Test2.create()  #initialize a dataclass from a .toml
    log.debug(t.bar) #view t.bar
    t.bar = 34 #override python memory
    log.debug(t.bar) #view updated t.bar
    t.write() #write to the specified .toml file
    data = t.read() #ensure overwriting
    log.debug(data)

#Example STDOUT
# 2025-07-29 01:06:59.539 | WARNING  | toomanyconfigs.core:create:164 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml, creating new one
# 2025-07-29 01:06:59.541 | INFO     | toomanyconfigs.core:create:182 - [Test2]: Missing fields detected: ['foo']
# [Test2]: Enter value for 'foo' (or press Enter to paste from clipboard): bar
# 2025-07-29 01:07:31.410 | SUCCESS  | toomanyconfigs.core:_prompt_field:226 - [Test2]: Set foo
# 2025-07-29 01:07:31.413 | DEBUG    | __main__:<module>:35 - 33
# 2025-07-29 01:07:31.413 | DEBUG    | __main__:<module>:37 - 34
# 2025-07-29 01:07:31.414 | DEBUG    | toomanyconfigs.core:write:241 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# 2025-07-29 01:07:31.416 | DEBUG    | toomanyconfigs.core:read:248 - [TooManyConfigs]: Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# 2025-07-29 01:07:31.421 | DEBUG    | toomanyconfigs.core:read:263 - [Test2]: Overrode 'foo' from file!
# 2025-07-29 01:07:31.421 | DEBUG    | toomanyconfigs.core:read:263 - [Test2]: Overrode 'bar' from file!
# 2025-07-29 01:07:31.421 | DEBUG    | __main__:<module>:40 - {'foo': 'bar', 'bar': 34}

#Subconfigs:
#Usage
from toomanyconfigs import TOMLConfig, TOMLSubConfig

class Test4(TOMLSubConfig):
    foo: str = None

class Test3(TOMLConfig):
    key: str = "val"
    sub_config: Test4

if __name__ == "__main__":
    t = Test3.create()
    log.debug(t.__dict__)

#STDOUT
# 2025-07-29 01:09:12.537 | WARNING  | toomanyconfigs.core:create:164 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test3.toml, creating new one
# 2025-07-29 01:09:12.537 | INFO     | toomanyconfigs.core:create:182 - [Test3]: Missing fields detected: ['sub_config']
# 2025-07-29 01:09:12.537 | DEBUG    | toomanyconfigs.core:create:39 - [TooManyConfigs]: Building subconfig named 'test4' from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test3.toml
# 2025-07-29 01:09:12.538 | INFO     | toomanyconfigs.core:create:57 - [Test4]: Missing fields detected: ['foo']
# [Test4]: Enter value for 'foo' (or press Enter to paste from clipboard): bar
# 2025-07-29 01:09:16.321 | SUCCESS  | toomanyconfigs.core:_prompt_field:73 - [Test4]: Set foo
# 2025-07-29 01:09:16.322 | SUCCESS  | toomanyconfigs.core:create:190 - [Test3]: Created Test4 for sub_config
# 2025-07-29 01:09:16.323 | DEBUG    | __main__:<module>:63 - {'_private': {'_cwd': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src'), '_path': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src/test3.toml')}, 'key': 'val', '_cwd': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src'), '_path': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src/test3.toml'), 'sub_config': [Test4]}

#API Configs
### Basic Usage
from toomanyconfigs import API

if __name__ == "__main__":
    obj = API()
    response = asyncio.run(obj.api_request("get"))
    log.debug(response)

# Example STDOUT
# 2025-07-29 01:42:28.125 | WARNING  | toomanyconfigs.core:create:179 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml, creating new one
# 2025-07-29 01:42:28.126 | INFO     | toomanyconfigs.core:create:197 - APIConfig: Missing fields detected: ['headers', 'routes', 'vars']
# 2025-07-29 01:42:28.126 | DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'headersconfig' from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml
# 2025-07-29 01:42:28.126 | SUCCESS  | toomanyconfigs.core:create:205 - APIConfig: Created HeadersConfig for headers
# 2025-07-29 01:42:28.126 | DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'routesconfig' from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml
# 2025-07-29 01:42:28.126 | INFO     | toomanyconfigs.core:create:59 - RoutesConfig: Missing fields detected: ['base', 'shortcuts']
# [RoutesConfig]: Enter value for 'base' (or press Enter to paste from clipboard): http://example.com
# 2025-07-29 01:42:38.796 | SUCCESS  | toomanyconfigs.core:_prompt_field:84 - [RoutesConfig]: Set base
# 2025-07-29 01:42:38.796 | SUCCESS  | toomanyconfigs.core:create:68 - RoutesConfig: Created Shortcuts for shortcuts
# 2025-07-29 01:42:38.796 | SUCCESS  | toomanyconfigs.core:create:205 - APIConfig: Created RoutesConfig for routes
# 2025-07-29 01:42:38.796 | DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'varsconfig' from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\apiconfig.toml
# 2025-07-29 01:42:38.797 | SUCCESS  | toomanyconfigs.core:create:205 - APIConfig: Created VarsConfig for vars
# 2025-07-29 01:42:38.800 | DEBUG    | toomanyconfigs.api:api_request:146 - <toomanyconfigs.api.Receptionist object at 0x000001DBEB8EB0E0>: Attempting request to API:
#   - method=get
#   - headers={'authorization': 'Bearer ${API_KEY}', 'accept': 'application/json'}
#   - path=http://example.com
# 2025-07-29 01:42:39.490 | DEBUG    | __main__:<module>:82 - Response(status=200, method='get', headers={'accept-ranges': 'bytes', 'content-type': 'text/html', 'etag': '"84238dfc8092e5d9c0dac8ef93371a07:1736799080.121134"', 'last-modified': 'Mon, 13 Jan 2025 20:11:20 GMT', 'vary': 'Accept-Encoding', 'content-encoding': 'gzip', 'content-length': '648', 'cache-control': 'max-age=1954', 'date': 'Tue, 29 Jul 2025 06:42:39 GMT', 'connection': 'keep-alive'}, body='<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n    <meta charset="utf-8" />\n    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1" />\n    <style type="text/css">\n    body {\n        background-color: #f0f0f2;\n        margin: 0;\n        padding: 0;\n        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;\n        \n    }\n    div {\n        width: 600px;\n        margin: 5em auto;\n        padding: 2em;\n        background-color: #fdfdff;\n        border-radius: 0.5em;\n        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);\n    }\n    a:link, a:visited {\n        color: #38488f;\n        text-decoration: none;\n    }\n    @media (max-width: 700px) {\n        div {\n            margin: 0 auto;\n            width: auto;\n        }\n    }\n    </style>    \n</head>\n\n<body>\n<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.</p>\n    <p><a href="https://www.iana.org/domains/example">More information...</a></p>\n</div>\n</body>\n</html>\n')

# Example TOML
# [headers]
# authorization = "Bearer ${API_KEY}"
# accept = "application/json"
#
# [routes]
# base = "http://example.com"
#
# [vars]
#
# [routes.shortcuts]

### Advanced Usage
from toomanyconfigs import API, APIConfig, HeadersConfig, RoutesConfig, VarsConfig, Shortcuts
from loguru import logger as log

if __name__ == "__main__":
    src = (Path.cwd() / "json_api.toml")
    src.touch(exist_ok=True)

    base_url = 'https://jsonplaceholder.typicode.com/'
    quick_routes = {
        "c": "/comments?postId=${ID_KEY}"
    }
    routes = RoutesConfig(
        base=base_url,
        shortcuts=Shortcuts.create(_source=src, **quick_routes)
    )
    class JSONVars(VarsConfig):
        api_key: str = None
        id_key: str = 1

    json_vars = JSONVars.create(_source=src, _name="vars")

    cfg = APIConfig.create(_source=src, routes=routes, vars=json_vars)
    json_placeholder = API(cfg)
    json_placeholder.config.apply_variable_substitution()
    log.debug(json_placeholder.config.__dict__)
    response = asyncio.run(json_placeholder.api_get("c"))
    log.debug(response)
    sync_response = json_placeholder.sync_api_get("c")
    log.debug(sync_response)

# Example STDOUT
# 2025-07-29 01:54:10.820 | DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'shortcuts' from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\json_api.toml
# 2025-07-29 01:54:10.820 | DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'vars' from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\json_api.toml
# 2025-07-29 01:54:10.820 | INFO     | toomanyconfigs.core:create:59 - JSONVars: Missing fields detected: ['api_key']
# [JSONVars]: Enter value for 'api_key' (or press Enter to paste from clipboard): foobar
# 2025-07-29 01:54:15.000 | SUCCESS  | toomanyconfigs.core:_prompt_field:84 - [JSONVars]: Set api_key
# 2025-07-29 01:54:15.000 | DEBUG    | toomanyconfigs.core:create:153 - [TooManyConfigs]: Building config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\json_api.toml
# 2025-07-29 01:54:15.001 | INFO     | toomanyconfigs.core:create:197 - APIConfig: Missing fields detected: ['headers']
# 2025-07-29 01:54:15.002 | DEBUG    | toomanyconfigs.core:create:41 - [TooManyConfigs]: Building subconfig named 'headersconfig' from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\json_api.toml
# 2025-07-29 01:54:15.003 | SUCCESS  | toomanyconfigs.core:create:205 - APIConfig: Created HeadersConfig for headers
# 2025-07-29 01:54:15.005 | DEBUG    | __main__:<module>:149 - {'_private': {'_cwd': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src'), '_path': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src/json_api.toml')}, 'routes': {'base': 'https://jsonplaceholder.typicode.com/', 'shortcuts': {'c': '/comments?postId=1'}}, 'vars': {'api_key': 'foobar'}, '_cwd': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src'), '_path': WindowsPath('C:/Users/foobar/PycharmProjects/TooManyConfigs/src/json_api.toml'), 'headers': {'authorization': 'Bearer foobar', 'accept': 'application/json'}}
# 2025-07-29 01:54:15.006 | DEBUG    | toomanyconfigs.api:api_request:146 - <toomanyconfigs.api.Receptionist object at 0x000002A509CB0F50>: Attempting request to API:
#   - method=get
#   - headers={'authorization': 'Bearer foobar', 'accept': 'application/json'}
#   - path=https://jsonplaceholder.typicode.com//comments?postId=1
# 2025-07-29 01:54:15.679 | DEBUG    | __main__:<module>:151 - Response(status=200, method='get', headers={'date': 'Tue, 29 Jul 2025 06:54:15 GMT', 'content-type': 'application/json; charset=utf-8', 'transfer-encoding': 'chunked', 'connection': 'keep-alive', 'access-control-allow-credentials': 'true', 'cache-control': 'no-cache', 'content-encoding': 'gzip', 'etag': 'W/"5e6-4bSPS5tq8F8ZDeFJULWh6upjp7U"', 'expires': '-1', 'nel': '{"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}', 'pragma': 'no-cache', 'report-to': '{"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=2OLL4bBRfxjSzJxRsf42R5kKzab2sksJK6eRLWXKtas%3D\\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\\u0026ts=1753772055"}],"max_age":3600}', 'reporting-endpoints': 'heroku-nel="https://nel.heroku.com/reports?s=2OLL4bBRfxjSzJxRsf42R5kKzab2sksJK6eRLWXKtas%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1753772055"', 'server': 'cloudflare', 'vary': 'Origin, Accept-Encoding', 'via': '2.0 heroku-router', 'x-content-type-options': 'nosniff', 'x-powered-by': 'Express', 'x-ratelimit-limit': '1000', 'x-ratelimit-remaining': '999', 'x-ratelimit-reset': '1753772091', 'cf-cache-status': 'BYPASS', 'cf-ray': '966ab432fced299f-MCI', 'alt-svc': 'h3=":443"; ma=86400'}, body=[{'postId': 1, 'id': 1, 'name': 'id labore ex et quam laborum', 'email': 'Eliseo@gardner.biz', 'body': 'laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium'}, {'postId': 1, 'id': 2, 'name': 'quo vero reiciendis velit similique earum', 'email': 'Jayne_Kuhic@sydney.com', 'body': 'est natus enim nihil est dolore omnis voluptatem numquam\net omnis occaecati quod ullam at\nvoluptatem error expedita pariatur\nnihil sint nostrum voluptatem reiciendis et'}, {'postId': 1, 'id': 3, 'name': 'odio adipisci rerum aut animi', 'email': 'Nikita@garfield.biz', 'body': 'quia molestiae reprehenderit quasi aspernatur\naut expedita occaecati aliquam eveniet laudantium\nomnis quibusdam delectus saepe quia accusamus maiores nam est\ncum et ducimus et vero voluptates excepturi deleniti ratione'}, {'postId': 1, 'id': 4, 'name': 'alias odio sit', 'email': 'Lew@alysha.tv', 'body': 'non et atque\noccaecati deserunt quas accusantium unde odit nobis qui voluptatem\nquia voluptas consequuntur itaque dolor\net qui rerum deleniti ut occaecati'}, {'postId': 1, 'id': 5, 'name': 'vero eaque aliquid doloribus et culpa', 'email': 'Hayden@althea.biz', 'body': 'harum non quasi et ratione\ntempore iure ex voluptates in ratione\nharum architecto fugit inventore cupiditate\nvoluptates magni quo et'}])

# Example TOML
# [routes]
# base = "https://jsonplaceholder.typicode.com/"
# 
# [vars]
# api_key = "foobar"
# 
# [headers]
# authorization = "Bearer ${API_KEY}"
# accept = "application/json"
# 
# [routes.shortcuts]
# c = "/comments?postId=1"

#API Receptionist



#CWD
#Basic Usage
from toomanyconfigs import CWD

class Test5(CWD):
    def __init__(self):
        super().__init__({"foobar.py": "print('Hello, World!')"})

if __name__ == "__main__":
    t = Test5()
    log.debug(t.cwd)

# Example usage with recursive nested structure


c = CWD(
    "test.txt",                          # Simple file
    {"src": {                           # Nested folder structure
        "main.py": None,                # File in src/
        "utils": {                      # Nested folder src/utils/
            "helpers.py": None,
            "config": {                 # Deeply nested src/utils/config/
                "settings.toml": None,
                "database.toml": None
            }
        },
        "tests": ["test_main.py", "test_utils.py"]  # List of files in src/tests/
    }},
    {"docs": ["readme.md", "changelog.md"]},  # Multiple files in docs/
    Path("logs/app.log")                # Path object
)

log.debug(f"CWD: {c}")
log.debug(f"File structure count: {len(c.file_structure)}")
c.list_structure()