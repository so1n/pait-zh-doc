
# 如何自定义插件
无论是前置插件还是后置插件，他们都继承于`PluginProtocol`，所以它们都实现了如下方法：
```Python
from typing import Any, Dict

class PluginProtocol(object):

    def __post_init__(self, **kwargs: Any) -> None:
        pass

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        ...

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        ...

    @classmethod
    def build(cls, **kwargs: Any) -> "PluginManager[_PluginT]":
        ...

    def __call__(self, context: "PluginContext") -> Any:
        ...
```
如果想自定义插件，则需要根据插件类型选择继承于`PrePluginProtocol`还是`PostPluginProtocol`，并实现上述的方法。
`PluginProtocol`中的方法对应着插件的不同的生命周期，分别为插件的构建--`build`、插件的预检查--`pre_check_hook`、插件的预加载--`pre_load_hook`、插件的初始化--`__post_init__`以及插件的运行`__call__`。

## 1.生命周期
### 1.1.插件的构建
插件的`build`方法实际上是用于存储插件以及它对应需要的初始化参数，并交由`Pait`进行编排。
假如有一个前置插件，它需要用到`a`, `b`两个变量，那么插件的实现代码如下:
```python
from pait.plugin.base import PrePluginProtocol

class DemoPlugin(PrePluginProtocol):
    a: int
    b: str

    @classmethod
    def build(
        cls,
        a: int,
        b: str,
    ) -> "PluginManager[_PluginT]":
        cls.build(a=a, b=b)
```
代码中首先定义了`DemoPlugin`拥有`a`和`b`两个属性且它们都没有被赋值，这意味着`DemoPlugin`插件要求`a`和`b`参数为必须的，如果没有通过`build`方法传入`a`和`b`参数，那么插件在初始化时会失败。

### 1.2.插件的预检查
不同的插件会依赖到`CoreModel`的不同属性 ，而`pre_check_hook`则是在插件初始化之前检查当前`CoreModel`是否满足插件的要求，尽早地发现问题。如下代码:
```Python
from typing import Dict
from pait.plugin.base import PrePluginProtocol
from pait.model.status import PaitStatus

class DemoPlugin(PrePluginProtocol):
    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> None:
        if pait_core_model.status is not PaitStatus.test:
            raise ValueError("Only functions that are in test can be used")
        if not isinstance(kwargs.get("a", None), int):
            raise TypeError("param `a` type must int")
        super().pre_load_hook(pait_core_model, kwargs)
```
该代码通过`pre_check_hook`进行了两次检查，第一个检查是判断当前函数的状态是否被设置为`TEST`，第二个检查啥判断参数`a`的类型是否为int，在检查不通过时都会抛出异常进而中断`pait`的编排。
### 1.3.插件的预加载
每个路由函数中会通过`CoreModel`存储一些初始值，在插件的运行过程中会提取`CoreModel`的值并进行处理，不过每次请求都重新提取一次数据会比较耗时。
这时可以通过`pre_load_hook`提取数据并保存起来，后续处理每次请求时就不用进行数据提取的操作了。如下代码:
```Python
from typing import Dict
from pait.plugin.base import PrePluginProtocol
from pait.model.response import JsonResponseModel

class DemoPlugin(PrePluginProtocol):
    example_value: dict

    @classmethod
    def pre_load_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if not pait_core_model.response_model_list:
            raise ValueError("Not found response model")
        response_model = pait_core_model.response_model_list
        if not issubclass(response_model, JsonResponseModel):
            raise TypeError("Only support json response model")
        kwargs["example_value"] = response_model.get_example_value()
        return super().pre_load_hook(pait_core_model, kwargs)
```
该代码首先是定义了`DemoPlugin`需要一个名为`example_value`的参数。不过这个参数不是通过`build`方法传递的，而是通过`pre_load_hook`方法中解析响应模型对象的示例值获得的。
其中，通过响应对象的`get_example_value`获取到它的示例数据并存入到`kwargs`的`example_value`中，
之后，`DemoPlugin`在初始化时就可以把`kwargs`的`example_value`存储到自身的`example_value`属性。

### 1.4.`__post_init__`
通过上面的几个方法可以知道，`kwargs`这个存储插件初始化参数的容器会经历了`build`，`pre_check_hook`以及`pre_load_hook`方法的处理， 然后再通过插件的`__init__`方法写入到插件的实例中。
不过这一个过程是由`Pait`根据插件的属性自动处理的，它的规则比较简单死板，可能无法兼容一些场景，
所以插件在初始化的最后一步会调用`__post_init__`方法，开发者可以通过`__post_init__`方法中的`kwargs`变量完成自定义的插件初始化逻辑。


### 1.5.`__call__`
`Pait`会把插件按照顺序编排在一起，并把下一个插件设置到当前插件的`next_plugin`变量中。
当有请求命中时，`Pait`会把请求数据传递给第一个插件的`__call__`方法，并等待插件的处理和返回，而每个插件在`__call__`方法中会调用`self.next_plugin`方法继续调用下一个插件，如下:
```Python
from typing import Any
from pait.plugin.base import PrePluginProtocol


class DemoPlugin(PrePluginProtocol):
    def __call__(self, context: "PluginContext") -> Any:
        next_plugin_result = None
        try:
            next_plugin_result = self.next_plugin(context)
        except Exception as e:
            pass
        return next_plugin_result
```
在这个示例代码中，可以在`next_plugin`之前之后实现插件功能或者在`except`语法块中捕获后续插件的执行异常。
每个插件都是由上一个插件驱动的，每个插件之间的功能不会互相影响，但是它们可以通过`context`共享数据。
此外，也可以不再调用`next_plugin`方法直接返回一个值或者是抛出一个异常，如下:
```Python
from typing import Any
from pait.plugin.base import PrePluginProtocol


class RaiseExcDemoPlugin(PrePluginProtocol):
    def __call__(self, context: "PluginContext") -> Any:
        raise RuntimeError("Not working")
```
当插件被执行后，`Pait`不会调用后续的所有插件以及路由函数，而是直接抛出一个异常。



## 2.一个真实的例子
下面是一个基于`starlette`框架实现的简单例子：
```py
from typing import Optional
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from pait.exceptions import TipException

from pait.app.starlette import pait
from pait import field


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    """提取异常信息， 并以响应返回"""
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    uid: str = field.Query.i(),
    user_name: Optional[str] = field.Query.i(default=None),
    email: Optional[str] = field.Query.i(default=None)
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name, "email": email})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
```
路由函数由`Pait`提供参数校验功能，当调用方的参数不符合验证规则时，`Pait`会抛出异常并被`starlette`捕获再分发到`api_exception`函数处理。
比如一个没有携带请求参数的请求:
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{"data":"Can not found uid value"}
```
由于`Pait`在验证请求参数时发现缺少参数uid，所以会抛出错误并被`api_exception`捕获以及生成异常响应再返回给调用方。

假设路由函数的异常不想被`api_exception`处理，那么可以实现一个插件来处理路由函数的异常，如下是该插件的实现：
```py linenums="1"
from typing import Any, Dict
from pait.plugin.base import PrePluginProtocol
from pydantic import ValidationError
from pait.exceptions import PaitBaseException
from starlette.responses import JSONResponse


class DemoExceptionPlugin(PrePluginProtocol):

    @classmethod
    def pre_check_hook(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if pait_core_model.func.__name__ != "demo":
            raise RuntimeError(f"The {cls.__name__} is only used for demo func")

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return await self.next_plugin(args, kwargs)
        except (ValidationError, PaitBaseException) as e:
            return JSONResponse({"plugin exc info": str(e)})
```
可以看到这个插件有几个特点:

- 1.插件继承`PrePluginProtocol`，这是因为需要捕获`Pait`抛出的异常。
- 2.插件通过`pre_check_hook`方法判断当前插件是否是`demo`函数，如果不是则抛出异常。
- 3.由于路由函数是`async def`，所以插件的`__call__`方法也被`async`传染，需要以`async def`定义。

创建完插件后，就可以直接在路由函数使用了，例如:
```python
@pait(plugin_list=[DemoExceptionPlugin.build])
async def demo(...): pass
```
接下来重启程序并运行同样的请求，可以发现响应结果已经发生了改变：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{"plugin exc info":"File \"/home/so1n/demo.py\", line 48, in demo.\nerror:Can not found uid value"}
```
