from dataclasses import dataclass
from toomanyconfigs import TOMLDataclass

### Basic Usage

@dataclass #You must inherit TOMLDataclass on another dataclass
class Test(TOMLDataclass):
    foo: str = None #Each field that should prompt user input should be 'None'

if __name__ == "__main__":
    Test.from_toml() #Without specifying a path, TOMLDataclass will automatically make a .toml in your cwd with the name of your inheriting class.

#Example STDOUT
# 2025-07-25 14:04:37.151 | WARNING  | toomanyconfigs.core:from_toml:37 - [TooManyConfigs]: Config file not found at C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml, creating new one
# Test(foo=None): Enter value for 'foo' (or press Enter to paste from clipboard): bar
# 2025-07-25 14:04:45.721 | SUCCESS  | toomanyconfigs.core:_prompt_field:91 - Test(foo='bar'): Set foo
# 2025-07-25 14:04:45.721 | DEBUG    | toomanyconfigs.core:write:101 - [TooManyConfigs]: Writing config to C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml

#Example STDOUT with loaded config
# 2025-07-25 14:09:30.142 | DEBUG    | toomanyconfigs.core:read:110 - [TooManyConfigs] Reading config from C:\Users\foobar\PycharmProjects\TooManyConfigs\src\test.toml
# 2025-07-25 14:09:30.143 | DEBUG    | toomanyconfigs.core:_load_from_data:59 - Test(foo='bar'): Loaded foo from config


### Advanced Usage
from loguru import logger as log

@dataclass
class Test2(TOMLDataclass):
    foo: str = None
    bar: int = 33 #We'll set bar at 33 to demonstrate the translation ease between dynamic python objects and .toml

if __name__ == "__main__":
    t = Test2.from_toml() #initialize a dataclass from a .toml
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