
## 如何自定义插件
无论是`PrePluginProtocol`插件还是`PostPluginProtocol`插件，他们都继承于`PluginProtocol`，所以它们都实现了如下方法：
```Python
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

    def __call__(self, context: "PluginContext") -> Any
        ...
```
如果想自定义插件，则需要根据插件类型选择继承于`PrePluginProtocol`还是`PostPluginProtocol`，并实现上述的方法。
`PluginProtocol`中的五个方法对应着插件的五个声明周期，分别为插件的构建--`build`、插件的预检查--`pre_check_hook`、插件的预加载--`pre_load_hook`、插件的初始化--`__post_init__`以及插件的运行`__call__`。

### 插件的构建
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

### 插件的预检查
由于每个插件的职责是不同的，它们会依赖到`CoreModel`的不同属性，而`pre_check_hook`则是在插件初始化之前检查当前`CoreModel`是否可以使用该插件，尽早的帮助使用者发现问题。如下代码:
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
### 插件的预加载
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
在`pre_load_hook`阶段中，通过响应对象的`get_example_value`获取到它的示例数据并存入到`kwargs`中，后续`DemoPlugin`在初始化时就可以把示例数据存储到自身的`example_value`属性。

### `__post_init__`
通过上面的几个方法可以知道，`kwargs`这个存储插件初始化参数的容器会经历了`build`，`pre_check_hook`以及`pre_load_hook`方法的处理， 然后再通过插件的`__init__`方法写入到插件的实例中。
不过这一个过程是由`Pait`根据插件的属性自动处理的，它的规则比较简单死板，可能无法兼容一些场景，
所以插件在初始化的最后一步会调用`__post_init__`方法，开发者可以通过`__post_init__`方法中的`kwargs`变量完成自定义的插件初始化逻辑。


### `__call__`
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
当请求命中插件该插件后，不会调用后续的所有插件以及路由函数，而是直接抛出一个异常。



`Pait`自带少量的插件实现，开发者可以根据自己的需求自定义插件，下面以异常捕获插件为例子阐述如何自定义插件。
下面所示代码是一个简单的API接口：
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
这个接口由`Pait`提供参数校验功能，如果调用方发起的参数有错，则会直接抛出异常并最终被`starlette`捕获再分发到`api_exception`函数处理，比如下面的请求，
`Pait`在校验发现缺少参数uid时会抛出错误，最后被`api_exception`捕获并把异常返回给调用方：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{"data":"Can not found uid value"}
```
现在该接口多了一个需求，需要对该路由函数的异常的处理定制化，生成不一样的返回格式，但是`api_exception`是统一处理所有接口函数的异常，
它不可能为每个函数定义一个单独的函数处理，这时候可以定制一个捕获异常的插件来解决这个问题，如下是一个单独针对这个接口定制的插件：
```py linenums="1"
from typing import Any, Dict
from pait.plugin.base import BasePlugin
from pait.model.core import PaitCoreModel
from pydantic import ValidationError
from pait.exceptions import PaitBaseException


class DemoExceptionPlugin(BasePlugin):
    is_pre_core: bool = True

    @classmethod
    def pre_check(cls, pait_core_model: "PaitCoreModel", kwargs: Dict) -> Dict:
        if pait_core_model.func.__name__ != "demo":
            raise RuntimeError(f"The {cls.__name__} is only used for demo func")
        return super().cls_hook_by_core_model(pait_core_model, kwargs)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return await self.call_next(args, kwargs)
        except (ValidationError, PaitBaseException) as e:
            return JSONResponse({"plugin exc info": str(e)})
```
在这个示例插件中，需要注意的有几个地方：

- 0.由于该路由函数是`async`的，所以`__call__`方法需要加上async。
- 1.第9行的`is_pre_core = True`是设置该插件为前置插件，这样就能拦截`Pait`和路由函数的异常了。
- 2.第12行的`pre_check`方法会进行一些初始化的检查，该检查只会在初始化的时候运行，这个检查的逻辑是如果判定该插件并不是挂在`demo`函数上就会抛错，
其中`pait_core_model`是`Pait`为路由函数生成的一些属性。
- 3.第17行的`__call__`方法是该插件的主要处理逻辑，当有请求进来时，`Pait`会通过`__call__`方法调用插件，插件可以通过`call_next`来调用下一个插件，
该插件通过`try...except`来捕获后续所有调用段异常，如果是符合条件的异常就会被捕获，并生成不一样的响应结果。

编写完毕插件后，就可以直接使用了，对上面代码进行如下的小更改:
```python
@pait(plugin_list=[DemoExceptionPlugin.build])
async def demo(...): pass
```
然后重启程序并运行同样的请求，可以发现响应结果已经变为插件自己抛出的结果：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{"plugin exc info":"File \"/home/so1n/demo.py\", line 48, in demo.\nerror:Can not found uid value"}
```
