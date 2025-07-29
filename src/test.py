import asyncio
from dataclasses import field
from pathlib import Path

### Basic Usage
from toomanyconfigs import TOMLConfig

class Test(TOMLConfig):
    foo: str = None #Each field that should prompt user input should be 'None'

if __name__ == "__main__":
    Test.create() #Without specifying a path, TOMLDataclass will automatically make a .toml in your cwd with the name of your inheriting class.

#Example STDOUT
# 2025-07-25 14:04:37.151 | WARNING  | toomanyconfigs.core:from_toml:37 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml, creating new one
# Test(foo=None): Enter value for 'foo' (or press Enter to paste from clipboard): bar
# 2025-07-25 14:04:45.721 | SUCCESS  | toomanyconfigs.core:_prompt_field:91 - Test(foo='bar'): Set foo
# 2025-07-25 14:04:45.721 | DEBUG    | toomanyconfigs.core:write:101 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml

#Example STDOUT with loaded config
# 2025-07-25 14:09:30.142 | DEBUG    | toomanyconfigs.core:read:110 - [TooManyConfigs] Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml
# 2025-07-25 14:09:30.143 | DEBUG    | toomanyconfigs.core:_load_from_data:59 - Test(foo='bar'): Loaded foo from config


### Advanced Usage
from toomanyconfigs import TOMLConfig
from loguru import logger as log

class Test2(TOMLConfig):
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

#Example STDOUT
# 2025-07-25 14:36:16.836 | DEBUG    | toomanyconfigs.core:read:111 - [TooManyConfigs] Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml
# 2025-07-25 14:36:16.837 | DEBUG    | toomanyconfigs.core:_load_from_data:59 - Test(foo='bar'): Loaded foo from config
# 2025-07-25 14:36:16.838 | WARNING  | toomanyconfigs.core:from_toml:37 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml, creating new one
# Test2(foo=None, bar=33): Enter value for 'foo' (or press Enter to paste from clipboard): val
# 2025-07-25 14:36:18.826 | SUCCESS  | toomanyconfigs.core:_prompt_field:92 - Test2(foo='val', bar=33): Set foo
# 2025-07-25 14:36:18.826 | DEBUG    | toomanyconfigs.core:write:102 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# 2025-07-25 14:36:18.827 | DEBUG    | __main__:<module>:34 - 33
# 2025-07-25 14:36:18.828 | DEBUG    | __main__:<module>:36 - 34
# 2025-07-25 14:36:18.828 | DEBUG    | toomanyconfigs.core:write:102 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# 2025-07-25 14:36:18.829 | DEBUG    | toomanyconfigs.core:read:111 - [TooManyConfigs] Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test2.toml
# 2025-07-25 14:36:18.831 | DEBUG    | __main__:<module>:39 - {'foo': 'val', 'bar': 34}

#Subconfigs:
#Usage
from toomanyconfigs import TOMLConfig, TOMLSubConfig

class Test3(TOMLSubConfig):
    foo: str = None

class Test4(TOMLConfig):
    key: str = "val"
    sub_config: Test3 = field(default_factory=Test3.create)

if __name__ == "__main__":
    t = Test4.create()
    log.debug(t)

#STDOUT
# 2025-07-28 20:12:23.275 | WARNING  | toomanyconfigs.core:create:80 - [TooManyConfigs]: Config file not found at C:\Users\cblac\PycharmProjects\TooManyConfigs\src\test4.toml, creating new one
# 2025-07-28 20:12:23.276 | INFO     | toomanyconfigs.core:create:21 - Test3(foo=None): Missing fields detected: ['foo']
# Test3(foo=None): Enter value for 'foo' (or press Enter to paste from clipboard): bar
# 2025-07-28 20:12:27.411 | SUCCESS  | toomanyconfigs.core:_prompt_field:35 - Test3(foo='bar'): Set foo
# 2025-07-28 20:12:27.411 | DEBUG    | toomanyconfigs.core:write:135 - [TooManyConfigs]: Writing config to C:\Users\cblac\PycharmProjects\TooManyConfigs\src\test4.toml
# 2025-07-28 20:12:27.412 | DEBUG    | __main__:<module>:67 - Test4(key='val', sub_config=Test3(foo='bar'))

#STDOUT after .toml
# 2025-07-28 20:16:11.741 | DEBUG    | toomanyconfigs.core:create:60 - [TooManyConfigs]: Building config from C:\Users\cblac\PycharmProjects\TooManyConfigs\src\test4.toml
# 2025-07-28 20:16:11.743 | DEBUG    | __main__:<module>:67 - Test4(key='val', sub_config=Test3(foo='bar'))

#API Configs
### Basic Usage
from toomanyconfigs import API

if __name__ == "__main__":
    api = API()
    log.debug(api.config)

# Example STDOUT
# 2025-07-28 20:23:58.113 | DEBUG    | toomanyconfigs.core:create:60 - [TooManyConfigs]: Building config from C:\Users\cblac\PycharmProjects\TooManyConfigs\src\apiconfig.toml
# 2025-07-28 20:23:58.115 | DEBUG    | __main__:<module>:87 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), routes=RoutesConfig(base='', routes={}), vars=VarsConfig())

# Example TOML
# [headers]
# authorization = "Bearer ${API_KEY}"
# accept = "application/json"
#
# [routes]
# base = ""
#
# [vars]
#
# [routes.routes]



#
# #API Configs
# ### Advanced Usage
from toomanyconfigs import API, APIConfig, HeadersConfig, RoutesConfig, VarsConfig
from loguru import logger as log

if __name__ == "__main__":
    src = (Path.cwd() / "json_api.toml")
    src.touch(exist_ok=True)

    base_url = 'https://jsonplaceholder.typicode.com/'
    quick_routes = {
        "c": "/comments?postId=1"
    }
    routes = RoutesConfig(
        base=base_url,
        routes=quick_routes
    )
    class JSONVars(VarsConfig):
        api_key: str = None

    json_vars = JSONVars.create(
        source=src,
        name="vars"
    )

    cfg = APIConfig.create(
        source=src,
        routes=routes,
        vars=json_vars
    )
    json_placeholder = API(cfg)
    response = asyncio.run(json_placeholder.api_get("c"))
    log.debug(response)

# Example STDOUT
# 2025-07-28 20:34:21.070 | DEBUG    | toomanyconfigs.core:create:60 - [TooManyConfigs]: Building config from C:\Users\cblac\PycharmProjects\TooManyConfigs\src\apiconfig.toml
# 2025-07-28 20:34:21.072 | DEBUG    | __main__:<module>:88 - APIConfig(headers=HeadersConfig(authorization='Bearer ${API_KEY}', accept='application/json'), routes=RoutesConfig(base='', routes={}), vars=VarsConfig())
# 2025-07-28 20:34:21.073 | INFO     | toomanyconfigs.core:create:21 - JSONVars(api_key=None): Missing fields detected: ['api_key']
# JSONVars(api_key=None): Enter value for 'api_key' (or press Enter to paste from clipboard): foobar
# 2025-07-28 20:34:25.602 | SUCCESS  | toomanyconfigs.core:_prompt_field:35 - JSONVars(api_key='foobar'): Set api_key
# 2025-07-28 20:34:25.603 | WARNING  | toomanyconfigs.core:create:80 - [TooManyConfigs]: Config file not found at C:\Users\cblac\PycharmProjects\TooManyConfigs\src\json_api.toml, creating new one
# 2025-07-28 20:34:25.610 | DEBUG    | toomanyconfigs.api:api_request:156 - <toomanyconfigs.api.Receptionist object at 0x000001893ADC11D0>: Attempting request to API:
#   - method=get
#   - headers={'authorization': 'Bearer foobar', 'accept': 'application/json'}
#   - path=https://jsonplaceholder.typicode.com//comments?postId=1
# 2025-07-28 20:34:26.400 | DEBUG    | __main__:<module>:134 - Response(status=200, method='get', headers={'date': 'Tue, 29 Jul 2025 01:34:26 GMT', 'content-type': 'application/json; charset=utf-8', 'transfer-encoding': 'chunked', 'connection': 'keep-alive', 'access-control-allow-credentials': 'true', 'cache-control': 'no-cache', 'content-encoding': 'gzip', 'etag': 'W/"5e6-4bSPS5tq8F8ZDeFJULWh6upjp7U"', 'expires': '-1', 'nel': '{"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}', 'pragma': 'no-cache', 'report-to': '{"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=d6pOrWB1iyEm8zs0cvyRwyT%2F9DRU9HWVfN6mVcLRaj8%3D\\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\\u0026ts=1753752866"}],"max_age":3600}', 'reporting-endpoints': 'heroku-nel="https://nel.heroku.com/reports?s=d6pOrWB1iyEm8zs0cvyRwyT%2F9DRU9HWVfN6mVcLRaj8%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1753752866"', 'server': 'cloudflare', 'vary': 'Origin, Accept-Encoding', 'via': '2.0 heroku-router', 'x-content-type-options': 'nosniff', 'x-powered-by': 'Express', 'x-ratelimit-limit': '1000', 'x-ratelimit-remaining': '998', 'x-ratelimit-reset': '1753752891', 'cf-cache-status': 'BYPASS', 'cf-ray': '9668dfb67aa26216-ORD', 'alt-svc': 'h3=":443"; ma=86400'}, body=[{'postId': 1, 'id': 1, 'name': 'id labore ex et quam laborum', 'email': 'Eliseo@gardner.biz', 'body': 'laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium'}, {'postId': 1, 'id': 2, 'name': 'quo vero reiciendis velit similique earum', 'email': 'Jayne_Kuhic@sydney.com', 'body': 'est natus enim nihil est dolore omnis voluptatem numquam\net omnis occaecati quod ullam at\nvoluptatem error expedita pariatur\nnihil sint nostrum voluptatem reiciendis et'}, {'postId': 1, 'id': 3, 'name': 'odio adipisci rerum aut animi', 'email': 'Nikita@garfield.biz', 'body': 'quia molestiae reprehenderit quasi aspernatur\naut expedita occaecati aliquam eveniet laudantium\nomnis quibusdam delectus saepe quia accusamus maiores nam est\ncum et ducimus et vero voluptates excepturi deleniti ratione'}, {'postId': 1, 'id': 4, 'name': 'alias odio sit', 'email': 'Lew@alysha.tv', 'body': 'non et atque\noccaecati deserunt quas accusantium unde odit nobis qui voluptatem\nquia voluptas consequuntur itaque dolor\net qui rerum deleniti ut occaecati'}, {'postId': 1, 'id': 5, 'name': 'vero eaque aliquid doloribus et culpa', 'email': 'Hayden@althea.biz', 'body': 'harum non quasi et ratione\ntempore iure ex voluptates in ratione\nharum architecto fugit inventore cupiditate\nvoluptates magni quo et'}])
#Example TOML
# [headers]
# authorization = "Bearer ${API_KEY}"
# accept = "application/json"
#
# [routes]
# base = "https://jsonplaceholder.typicode.com/"
#
# [vars]
# api_key = "foobar"
#
# [routes.routes]
# c = "/comments?postId=1"
#
