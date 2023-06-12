`Pait`内部有很多参数校验逻辑，出现错误的情况也有很多种，为了方便的捕获和了解异常，`Pait`拥有一个简单的异常机制。

首先，`Pait`的异常都是继承于`PaitBaseException`，在发生异常时可以通过:
```python
isinstance(exc, PaitBaseException)
```
来判断异常是否属于`Pait`的异常。

此外， 由于`Pait`是使用`Pydantic`进行校验， 所以在运行时会因为校验不通过而抛出`Pydantic`相关异常， 可以通过[Error Handling](https://pydantic-docs.helpmanual.io/usage/models/#error-handling)了解如何使用`Pydantic`异常
## 1.Pait的不同异常介绍
### 1.1.TipException异常
在程序运行的时候，`Pait`会检查参数是否存在，参数是否合法，以及参数是否通过`Pydantic`的校验，
上述条件中如果有一个校验不通过都会抛出异常，但是该异常的堆栈只会在`Pait`里流转，从而让使用`Pait`的开发者无法了解异常是哪个路由函数抛出的，这样排查问题是十分困难的。
所以`Pait`会通过`TipException`对异常进行一个包装，在抛错信息里告诉用户说哪个路由函数抛错，抛错的位置在哪里，
如果用户使用`Pycharm`等IDE工具，还可以通过点击路径跳转到对应的地方，一个异常示例如下：
```bash
Traceback (most recent call last):
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/exceptions.py", line 71, in __call__
    await self.app(scope, receive, sender)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 583, in __call__
    await route.handle(scope, receive, send)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 243, in handle
    await self.app(scope, receive, send)
  File "/home/so1n/github/pait/.venv/lib/python3.7/site-packages/starlette/routing.py", line 54, in app
    response = await func(request)
  File "/home/so1n/github/pait/pait/core.py", line 232, in dispatch
    return await first_plugin(*args, **kwargs)
  File "/home/so1n/github/pait/pait/param_handle.py", line 448, in __call__
    async with self:
  File "/home/so1n/github/pait/pait/param_handle.py", line 456, in __aenter__
    raise e from gen_tip_exc(self.call_next, e)
  File "/home/so1n/github/pait/pait/param_handle.py", line 453, in __aenter__
    await self._gen_param()
  File "/home/so1n/github/pait/pait/param_handle.py", line 439, in _gen_param
    self.args, self.kwargs = await self.param_handle(func_sig, func_sig.param_list)
  File "/home/so1n/github/pait/pait/param_handle.py", line 396, in param_handle
    await asyncio.gather(*[_param_handle(parameter) for parameter in param_list])
  File "/home/so1n/github/pait/pait/param_handle.py", line 393, in _param_handle
    raise gen_tip_exc(_object, closer_e, parameter)
pait.exceptions.TipException: Can not found content__type value for <function raise_tip_route at 0x7f512ccdebf8>   Customer Traceback:
    File "/home/so1n/github/pait/example/param_verify/starlette_example.py", line 88, in raise_tip_route.
```
可以看到异常是通过`gen_tip_exc`抛出来的，而抛出来的异常信息则包含路由函数所在位置，和异常信息，此外，可以通过`TipException.exc`获取到原本的异常。

### 1.2.参数异常
目前`Pait`有3种参数异常，如下:

|异常|出现位置| 说明                                                               |
|---|---|------------------------------------------------------------------|
|NotFoundFieldException  | 预检查阶段| 该异常表示匹配不到对应的`Field`，正常使用时，不会遇到该异常。                               |
|NotFoundValueException | 路由函数命中阶段| 该异常表示无法从请求数据中找到对应的值，这是一个常见的异常                                    |
|FieldValueTypeException  |预检查阶段| 该异常表示`Pait`发现`Field`里的`default`，`example`等填写的值不合法，使用者需要根据提示进行改正。 |

这三种异常都是继承于`PaitBaseParamException`，它的源码如下：
```Python
class PaitBaseParamException(PaitBaseException):
    def __init__(self, param: str, msg: str):
        super().__init__(msg)
        self.param: str = param
        self.msg: str = msg
```
从代码可以看出`PaitBaseParamException`在抛异常时只会抛出错误信息，但是在需要根据异常返回一些指定响应时，可以通过`param`知道是哪个参数出错。

## 2.如何使用异常
### 2.1.异常的使用
在CRUD业务中，路由函数发生的异常都要被捕获，然后返回一个协定好的错误信息供前端使用，下面是一个异常捕获的示例代码：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/exception/flask_with_exception_demo.py"  hl_lines="10 13 15 20"

    --8<-- "docs_source_code/introduction/exception/flask_with_exception_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/exception/starlette_with_exception_demo.py"   hl_lines="14 17 19 24 35"
    --8<-- "docs_source_code/introduction/exception/starlette_with_exception_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/exception/sanic_with_exception_demo.py"    hl_lines="11 14 16 18 21"
    --8<-- "docs_source_code/introduction/exception/sanic_with_exception_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/exception/tornado_with_exception_demo.py" hl_lines="13 16 18 23"
    --8<-- "docs_source_code/introduction/exception/tornado_with_exception_demo.py"
    ```

代码中`api_exception`函数的异常处理是按照严格的顺序排列的，一般情况下建议以这种顺序处理异常。
`api_exception`函数的第一段高亮是提取`TipException`的原本异常，后面的所有异常处理都是针对于原本的异常，所以优先级最高。
而第二段高亮是处理所有`Pait`的参数异常，这里会提取参数信息和错误信息，告知用户哪个参数发生错误，接着第三段高亮代码处理的是`Pydantic`的校验异常，这里会解析异常，并返回校验失败的参数信息，第四段代码处理的是`Pait`的所有异常，通常很少出现，直接返回异常信息，最后是处理其他情况的异常，这里可能是业务系统定义的异常。

在代码中的最后一段高亮是通过Web框架的异常机制，把自定义的`api_exception`函数挂载到框架的异常处理回调中，
而`api_exception`函数里面包含了使用`Pait`时遇到的几种异常的处理，然后按照协议返回数据给调用端。

!!! note ""
    `Tornado`是在`RequestHandler`中实现的。

在运行代码并通过`curl`调用可以发现：

- 缺少参数时，会返回找不到参数的错误信息
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo"
    {"code":-1,"msg":"error param:demo_value, Can not found demo_value value"}
    ```
- 参数校验出错时，会返回校验出错的参数名
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=a"
    {"code":-1,"msg":"check error param: ['demo_value']"}
    ```
- 参数正常时返回正常的数据
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=3"
    {"code":0,"msg":"","data":3}
    ```


!!! note "交互协议说明"
    该代码的响应使用了常见的后端返回Json数据协议:
    ```json
    {
      "code": 0,
      "msg": "",
      "data": {}
    }
    ```
    其中`code`为0时代表响应正常，不为0则为异常且`msg`包括了一个错误信息供前端展示，而`data`是正常响应时的结构体。


### 2.2.自定义Tip异常
自定义Tip异常是默认启用的，如果在使用的过程中觉得错误提示在解析会消耗性能或者觉得错误提示没啥作用，想取消错误提示。那么只需要把`ParamHandler`的`tip_exception_class`属性定义为`None`即可，代码如下：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/exception/flask_with_not_tip_exception_demo.py"  hl_lines="10 11 14 28"

    --8<-- "docs_source_code/introduction/exception/flask_with_not_tip_exception_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/exception/starlette_with_not_tip_exception_demo.py"   hl_lines="14 15 18 32"
    --8<-- "docs_source_code/introduction/exception/starlette_with_not_tip_exception_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/exception/sanic_with_not_tip_exception_demo.py"    hl_lines="11 12 15 29"
    --8<-- "docs_source_code/introduction/exception/sanic_with_not_tip_exception_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/exception/tornado_with_not_tip_exception_demo.py" hl_lines="12 13 17 32"
    --8<-- "docs_source_code/introduction/exception/tornado_with_not_tip_exception_demo.py"
    ```

其中第一段高亮中是继承于`ParamHandler`（或者`AsyncParamHandler`），这个类主要负责`Pait`执行参数校验与注入的功能，它有一个`tip_exception_class`方法可以用来定义`TipException`的行为，当`tip_exception_class`为空且遇到错误时不会产生异常提示，而是抛出默认的异常。
第二段高亮则是移除从`TipException`提取原本移除的逻辑，因为现在不需要了，第三段高亮则是传入自定义的`ParamHandler`，这样`Pait`就能知道当前的路由函数不需要生成`TipException`。


在运行代码并通过`curl`调用可以发现程序正常运行，如下：

- 缺少参数时，会返回找不到参数的错误信息
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo"
    {"code":-1,"msg":"error param:demo_value, Can not found demo_value value"}
    ```
- 参数校验出错时，会返回校验出错的参数名
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=a"
    {"code":-1,"msg":"check error param: ['demo_value']"}
    ```
- 参数正常时返回正常的数据
    ```bash
    ➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=3"
    {"code":0,"msg":"","data":3}
    ```

!!! note

    也可以通过继承`TipException`去修改`TipException`的行为来自定义Tip异常提示。
