config能为`Pait`提供一些配置支持，在整个程序的运行期间，它只允许初始化一次，建议在添加完所有路由并且调用`load_app`后再进行初始化，如下代码：
```Python
from starlette.applications import Starlette
from pait.g import config
from pait.app import load_app

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
该代码中在`run app`代码块之前通过调用`config.init_config`进行初始化，目前`config.init_config`支持以下几个参数:

|参数|描述|
|---|---|
|author|全局的默认API作者, 如果`@pait`中没有填写author, 则路由函数对应的auth为`config.author`|
|status|全局的默认API状态, 如果`@pait`中没有填写status, 则路由函数对应的status为`config.status`|
|json_type_default_value_dict|配置json类型的默认值，用于Pait生成一些默认Json值。|
|python_type_default_valur_dict|配置Python类型的默认值，用于Pait生成一些Python默认值。|
|json_encoder|Pait全局调用的Json序列化的对象|
|apply_func_list|按照一定规则适配路由函数属性的函数列表|

## 1.apply func介绍
在使用`Pait`的过程中可能会依据路由函数对应的生命周期来应用不同的`Pait`属性，比如对于`status`为`design`的路由函数，往往会使用Mock插件，而对于`status`为`test`的路由函数，往往会使用响应结果检查的插件等等，每次都是手动去改会非常麻烦，这时候就可以使用apply func功能。

!!! note

    该功能可以认为是路由组功能，但是请不要把它认为是中间件，因为它无法处理无法命中路由的请求。

`Pait`提供了一系列的apply func，每个apply func只会应用一种`Pait`属性，每个apply func的格式如下：
```python
from typing import Any, Optional
from pait.model import APPLY_FN

def apply_func_demo(
    value: Any, match_rule: Optional["MatchRule"] = None
) -> "APPLY_FN":
    pass
```
它们都是接收2个参数，第一个参数某个`Pait`属性要被应用的值，第二个参数是匹配规则。

匹配规则是一个名为`MatchRule`的对象，这个对象初始化时会接受两个参数，一个名为`key`，另一个名为`target`，其中Key是指路由函数对应`Pait`属性的Key，默认值为`all`(代表所有路由函数都匹配)，而target则是对应的是属性对应的值，Key目前支持的值如下：
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
他们分为三类，一类为`all`，比如`MatchRule("all")`代表所有路由函数都会匹配，一类为`status`、`group`、`tag`、`method_list`、`path`，比如`MatchRule("group", "demo")`代表路由函数对应的`group`为`demo`时会被匹配，
另一类则是以`!`开头的，代表反向匹配，比如`MatchRule("!status", "test")`代表是匹配`status`的值不是`test`的路由函数。

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
    需要注意的是，apply func遵循的一个原则是对于数组类型的值，它提供的是追加，而不是覆盖。

### 1.1.apply_extra_openapi_model
在使用Web框架的时候，经常会通过中间件使用到一些非路由函数声明的请求参数，比如有一个中间件，它会通过Header获取APP版本号并根据APP版本号来进行限制，版本号小于1的都返回404，大于1才通过。
在这种情况`Pait`无法获取到这个中间件使用的请求值，导致生成OpanAPI的数据会缺少这些请求值，这时可以使用`apply_extra_openapi_model`来解决这个问题，它的使用方法如下：
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
与`apply_extra_openapi_model`一样，在使用中间件限制版本号小于1的时候，可能返回的是一个内部的响应，这时候可以使用apply_response_model来添加一个默认的响应，使用方法如下：
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
由于`Pait`只是一个装饰器，它只能捕获到路由函数本身的属性，像URL, HTTP方法之类的参数需要后续调用`load_app`来补全，但是很多Web框架会自动为路由函数补上`HEAD`，`OPTIONS`等Http方法，即使开发者在注册路由时并没有填写。
这样会导致路由函数对应的OpenAPI数据也包含了`HEAD`和`OPTIONS`等HTTP方法，这时可以使用`apply_block_http_method_set`来禁用一些HTTP方法方法不被`Pait`捕获，使用方法如下：
```Python
from pait.extra.config import apply_block_http_method_set
from pait.g import config


config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])
```

### 1.4.apply_multi_plugin
插件是`Pait`的重要组成部分，其中有些插件只适用于接口的某些生命周期，所以这类插件比较推荐通过`apply_multi_plugin`根据路由函数的生命周期来使用不同的插件，如下:
```Python
from pait.app.starlette.plugin.mock_response import MockPlugin
from pait.app.starlette.plugin.check_json_resp import CheckJsonRespPlugin
from pait.extra.config import apply_multi_plugin, MatchRule
from pait.g import config
from pait.model.status import PaitStatus


config.init_config(
    apply_func_list=[
        apply_multi_plugin(
            # 为了能复用插件，这里只允许lambda写法，也可以使用pait自带的create_factory方法
            [lambda: MockPlugin.build()],
            # 限定status为design的使用Mock插件
            match_rule=MatchRule(key="status", target=PaitStatus.design)
        ),
        apply_multi_plugin(
            [lambda: CheckJsonRespPlugin.build()],
            # 限定status为test的使用响应体检查插件
            match_rule=MatchRule(key="status", target=PaitStatus.test)
        ),
    ]
)
```
### 1.5.apply_pre_depend
大多数时候可能会为某一组路由函数使用一个Token检验函数，这种情况不适合使用中间件，但是一个一个路由函数去添加depend却是很麻烦的一件事，这时可以使用`apply_pre_depend`，使用方法如下：
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
