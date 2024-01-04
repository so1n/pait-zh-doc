config能为`Pait`提供一些配置支持，在整个程序的运行期间，它只允许初始化一次，建议在添加完所有路由并且调用`load_app`后再进行初始化，
如下代码， `config.init_config`在`run app`代码块之前被调用 ：
```Python
from starlette.applications import Starlette
from pait.g import config
from pait.app.any import load_app

# ------
# 通过from ... import 导入路由模块
# ------

app: Starlette = Starlette()
# --------
# app.add_route
# --------
load_app(app)
config.init_config(author=("so1n", ))
# --------
# run app
# --------
```

`config.init_config`支持以下几个参数:

|参数| 描述                                                               |
|---|------------------------------------------------------------------|
|author| 全局的默认路由函数作者, 如果`@pait`中的author为空, 则路由函数对应的auth为`config.author`   |
|status| 全局的默认路由函数状态, 如果`@pait`中的status为空, 则路由函数对应的status为`config.status` |
|json_type_default_value_dict| 配置json类型的默认值，在自动生成响应时会发挥作用。                                      |
|python_type_default_valur_dict| 配置Python类型的默认值，在自动生成响应时会发挥作用。                              |
|json_encoder| Pait的Json序列化的对象                                              |
|apply_func_list| 按照一定规则适配路由函数属性的函数列表                                              |

## 1.apply func介绍
在使用`Pait`时，可能会根据路由函数生命周期来使用不同的`Pait`属性。
比如对于`status`为`design`的路由函数，往往会使用Mock插件，
而对于`status`为`test`的路由函数，往往会使用响应结果检查的插件等等。
如果每次都是手动的去更改配置，那么会非常麻烦，这时候就可以使用apply func功能。

!!! note
    该功能可以认为是路由组，但是请不要把它认为是中间件，因为它无法处理不被`Pait`装饰的路由。

`Pait`提供了一系列的apply func，每个apply func只会处理一种`Pait`属性，它的格式如下：
```python
from typing import Any, Optional
from pait.model.config import APPLY_FN
from pait.extra.config import MatchRule

def apply_func_demo(
    value: Any, match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    pass
```
它要求有2个参数，第一个参数是要被应用的值，第二个参数是匹配哪些路由函数需要被应用。

匹配规则是一个名为`MatchRule`的对象，这个对象初始化时会接受两个参数，一个名为`key`，另一个名为`target`，
其中`key`是指路由函数对应`Pait`属性的Key，默认值为`all`(代表所有路由函数都匹配)，而target则是对应的是属性对应的值，Key目前支持的值如下：
```Python
MatchKeyLiteral = Literal[
    "all",              # 所有路由函数都会匹配
    "status",           # 路由函数的status为对应值得都会匹配
    "group",            # 路由函数的group为对应值得都会匹配
    "tag",              # 路由函数的tag包含对应值得都会匹配
    "method_list",      # 路由函数的http请求方法包含对应值得都会匹配
    "path",             # 路由函数的url与输入的正则匹配到的都会匹配
    "!status",
    "!group",
    "!tag",
    "!method_list",
    "!path",
]
```
他们分为三类，
一类为`all`，比如`MatchRule("all")`代表所有路由函数都会匹配，
一类为`status`、`group`、`tag`、`method_list`、`path`，比如`MatchRule("group", "demo")`代表`group`为`demo`的路由函数会被匹配，
另一类则是以`!`开头的，代表反向匹配，比如`MatchRule("!status", "test")`代表是匹配`status`的值不是`test`的路由函数会被匹配。

除此之外，匹配规则还支持`&`和`|`的多规则匹配，如下：
```Python
from pait.extra.config import MatchRule
from pait.model.status import PaitStatus

# 匹配status为test或者是dev的路由函数
MatchRule("status", PaitStatus.test) | MatchRule("status", PaitStatus.dev)
# 匹配path为/api/user且 method_list为GET或者group为gRPC的路由函数
MatchRule("path", "/api/user") & (MatchRule("method_list", "GET") | MatchRule("group", "gRPC"))
```

!!! note Note
    需要注意的是，`apply func`对于数组类型的值，它只追加值，而不是覆盖值。

### 1.1.apply_extra_openapi_model
在使用Web框架的时候，经常会通过中间件使用到一些非路由函数声明的请求参数，
比如有一个中间件，它会通过Header获取APP版本号并根据APP版本号来进行处理，对于版本号小于1的都返回404响应，只有大于1才允许访问。
在这种情况会导致`Pait`无法获取到中间件使用的请求值，导致生成的OpanAPI数据会缺少这些请求值。
这时可以使用`apply_extra_openapi_model`来解决这个问题，它的使用方法如下：
```Python
from pydantic import BaseModel
from pait.field import Header
from pait.extra.config import apply_extra_openapi_model
from pait.g import config

class DemoModel(BaseModel):
    """中间件一般都是通过Header读取对应的版本号值"""
    version_code: int = Header.i(description="版本号")
    version_name: str = Header.i(description="版本名称")


# 通过apply_extra_openapi_model应用当前这个Model，由于中间件都是应用到所有的路由函数，所以直接使用MatchRule的默认值。
config.init_config(apply_func_list=[apply_extra_openapi_model(DemoModel)])
```
### 1.2.apply_response_model
与`apply_extra_openapi_model`一样，在使用中间件限制版本号小于1的时候，可能返回的是一个异常的响应，
这时候可以使用apply_response_model来添加一个默认的响应，使用方法如下：
```Python
from pait.extra.config import apply_response_model
from pait.g import config
from pait.model.response import HtmlResponseModel



class DefaultResponseModel(HtmlResponseModel):
    response_data: str = "<h1> Default Html</h1>"


# 由于中间件都是应用到所有的路由函数，所以直接使用MatchRule的默认值。
config.init_config(apply_func_list=[apply_response_model([DefaultResponseModel])])
```
### 1.3.apply_block_http_method_set
`Pait`是一个装饰器，所以它只能捕获到路由函数的属性，像URL, HTTP方法的参数需要通过`load_app`来补全。
但是很多Web框架在注册路由函数时，会自动为路由函数补充`HEAD`，`OPTIONS`等HTTP方法，
这样会导致路由函数的OpenAPI数据包含了`HEAD`和`OPTIONS`等HTTP方法，
这时可以使用`apply_block_http_method_set`来禁用一些HTTP方法方法不被`Pait`捕获，使用方法如下：
```Python
from pait.extra.config import apply_block_http_method_set
from pait.g import config


config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])
```

### 1.4.apply_multi_plugin
插件是`Pait`的重要组成部分，然而有的插件只适用于某些状态的路由函数。推荐通过`apply_multi_plugin`根据路由函数的`status`使用不同的插件，如下:
```Python
from pait.app.starlette.plugin.mock_response import MockPlugin
from pait.app.starlette.plugin.check_json_resp import CheckJsonRespPlugin
from pait.extra.config import apply_multi_plugin, MatchRule
from pait.g import config
from pait.model.status import PaitStatus


config.init_config(
    apply_func_list=[
        apply_multi_plugin(
            # 为了能复用插件，这里使用了lambda写法，也可以使用pait自带的create_factory方法
            [lambda: MockPlugin.build()],
            # 为status为design的路由函数使用Mock插件
            match_rule=MatchRule(key="status", target=PaitStatus.design)
        ),
        apply_multi_plugin(
            [lambda: CheckJsonRespPlugin.build()],
            # 为status为test的路由函数使用响应结果检查插件
            match_rule=MatchRule(key="status", target=PaitStatus.test)
        ),
    ]
)
```
### 1.5.apply_pre_depend
大多数时候可能会为某一组路由函数使用一个Token检验函数，这种情况不适合使用中间件，但是一个一个路由函数去添加`depend`却是很麻烦的一件事，这时可以使用`apply_pre_depend`，使用方法如下：
```Python
from pait.extra.config import apply_pre_depend, MatchRule
from pait.field import Header
from pait.g import config


def check_token(token: str = Header.i("")) -> bool:
    return bool(token)


config.init_config(
    apply_func_list=[
        # 匹配url以/api/v1/user开头的
        apply_pre_depend(check_token, match_rule=MatchRule(key="path", target="^/api/v1/user")),
        # 匹配路由函数的group属性为user的
        apply_pre_depend(check_token, match_rule=MatchRule(key="group", target="user"))
    ],
)
```
