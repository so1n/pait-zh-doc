## 1.隐式引入与显式引入
`pait`支持多个Web框架, 如果项目对应的依赖环境中只安装了其中的一个框架, 那么可以直接使用隐式引入:
```Python3
from pait.app.any import pait, load_app, add_simple_route
```
但是如果同时安装了多个框架, 那么隐式import将会引发异常, 建议使用显示引入，如下:
```Python3
from pait.app.flask import pait, load_app, add_simple_route
from pait.app.sanic import pait, load_app, add_simple_route
from pait.app.starlette import pait, load_app, add_simple_route
from pait.app.tornado import pait, load_app, add_simple_route
```
## 2.内部方法
`Pait`内部封装了一些通用的方法，通过这些方法，开发者可以在不考虑兼容不同的Web框架的情况下快速的开发出拓展包，或者对`Pait`进行拓展，
[OpenAPI路由](/3_2_openapi_route/)和[grpc-gateway](https://github.com/python-pai/grpc-gateway)就是基于这些方法开发的。
### 2.1.data
`data`是每个`CoreModel`的载体，`Pait`装饰路由函数时会生成一个`CoreModel`并存放在`pait.g.data`中，以便为配置，文档生成等功能提供支持。

### 2.2.load_app

`CoreModel`会存储很多路由函数的信息, 但是路由函数缺少关键的OpenAPI信息数据如`url`, `method`等，
所以在使用OpenAPI之前还需要使用`load_app`补全数据，它的使用方法很简单，不过需要要在注册所有路由后再调用，如下:

!!! note
    [OpenAPI 路由](/3_2_openapi_route/)在初始化之前会自动调用`load_app`

=== "Flask"

    ```Python3
    from flask import Flask

    from pait.app.flask import load_app

    app: Flask = Flask()

    load_app(app) # 错误的使用方法
    # --------
    # app.add_url_rule
    # --------

    load_app(app) # 正确的使用方法
    app.run()
    ```

=== "Starlette"

    ```Python3
    import uvicorn
    from starlette.applications import Starlette

    from pait.app.starlette import load_app

    app: Starlette = Starlette()
    # 错误的使用方法
    load_app(app)
    # --------
    # app.add_route
    # --------

    # 正确的使用方法
    load_app(app)
    uvicorn.run(app)
    ```

=== "Sanic"

    ```Python3
    from sanic import Sanic

    from pait.app.sanic import load_app

    app: Sanic = Sanic()

    load_app(app) # 错误的使用方法

    # --------
    # app.add_route
    # --------

    load_app(app) # 正确的使用方法
    app.run()
    ```

=== "Tornado"

    ```Python3
    from tornado.web import Application
    from tornado.ioloop import IOLoop

    from pait.app.tornado import load_app

    app: Application = Application()

    load_app(app) # 错误的使用方法
    # --------
    # app.add_handlers
    # --------
    load_app(app) # 正确的使用方法
    app.listen(8000)
    IOLoop.instance().start()
    ```

### 2.3.HTTP异常
`Pait`为每个Web框架提供了一个HTTP异常生成函数，它通过HTTP状态码，错误内容，Headers等参数生成Web框架的HTTP标准异常，它们的使用方法如下:

=== "Flask"

    ```python
    from pait.app.flask import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

=== "Sanic"
    ```python
    from pait.app.sanic import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

=== "Starlette"
    ```python
    from pait.app.starlette import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

=== "Tornado"
    ```python
    from pait.app.tornado import http_exception

    http_exception(status_code=401, message="Unauthorized", headers={"WWW-Authenticate": "Basic"})
    ```

此外，`Pait`还提供了一套常见的HTTP异常响应的Model，如下:
```python
from pait.app.any import pait
from pait.model import response

# response.Http400RespModel
# response.Http401RespModel
# response.Http403RespModel
# response.Http404RespModel
# response.Http405RespModel
# response.Http406RespModel
# response.Http407RespModel
# response.Http408RespModel
# response.Http429RespModel

@pait(response_model_list=[response.Http400RespModel])
def demo() -> None:
    pass
```
同时HTTP异常响应的Model也支持自定义创建，如下使用示例:
```python
from pait.model import response

# 创建一个状态码为500,content-type为html的响应Model
response.HttpStatusCodeBaseModel.clone(resp_model=response.HtmlResponseModel, status_code=500)
# 创建一个状态码为500,content-type为text的响应Model
response.HttpStatusCodeBaseModel.clone(resp_model=response.TextResponseModel, status_code=500)
```

### 2.4.SimpleRoute
`Pait`通过SimpleRoute统一了不同Web框架的路由注册以及生成响应的方法。
开发者通过SimpleRoute可以在不考虑兼容的情况下很方便的完成路由创建和注册。

!!! note
    统一的路由响应生成功能由`UnifiedResponsePluginProtocol`插件提供，
    路由函数被注册时会为路由函数添加`UnifiedResponsePluginProtocol`插件


SimpleRoute的使用方法如下:

=== "Flask"

    ```py linenums="1" title="docs_source_code/other/flask_with_simple_route_demo.py" hl_lines="8-20 24-32"

    --8<-- "docs_source_code/docs_source_code/other/flask_with_simple_route_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/other/starlette_with_simple_route_demo.py" hl_lines="8-20 24-32"
    --8<-- "docs_source_code/docs_source_code/other/starlette_with_simple_route_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/other/sanic_with_simple_route_demo.py" hl_lines="9-21 25-33"
    --8<-- "docs_source_code/docs_source_code/other/sanic_with_simple_route_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/other/tornado_with_simple_route_demo.py" hl_lines="9-21 25-33"
    --8<-- "docs_source_code/docs_source_code/other/tornado_with_simple_route_demo.py"
    ```
第一段高亮代码是按照`SimpleRoute`标准创建了三个路由函数，SimpleRoute的标准如下:

- 1.路由函数需要被`pait`装饰，同时`response_model_list`属性不能为空（代码中路由函数的响应模型分别为`JsonResponseModel`，`TextResponseModel`，`HtmlResponseModel`，这些都是SimpleRoute要求的，如果没有响应模型，那么SimpleRoute无法把路由函数注册到Web框架中。）
- 2.路由函数的返回值从响应对象变为是`Python`的基础类型，返回的`Python`基础类型需要跟响应模型的`response_data`保持一致。


第二段高亮是通过`add_simple_route`和`add_multi_simple_route`方法注册路由，其中`add_simple_route`只能注册一个路由，而`add_multi_simple_route`可以注册多个路由，它们的都接收app和SimpleRoute实例，而SimpleRoute只支持三个属性，如下:

| 参数     | 描述                   |
|--------|----------------------|
| route  | 符合SimpleRoute标准的路由函数 |
| url    | 当前路由的Url             |
| method | 当前路由对应的HTTP Method   |

此外，`add_multi_simple_route`还支持两个可选参数，如下:

| 参数     | 描述                                                                                    |
|--------|---------------------------------------------------------------------------------------|
| prefix | 路由前缀，比如prefix为"/api"，SimpleRoute的url为"/user"时，注册的路由URL为"/api/user"                    |
| title  | 当前路由组的标题，对于某些框架，它们采用的路由组或者蓝图都需要有唯一的命名，所以不同`add_multi_simple_route`的`title`都应该不同 |

在运行代码后，通过`curl`命令测试路由可以正常工作:
<!-- termynal -->
```bash
>  curl http://127.0.0.1:8000/json
{}
>  curl http://127.0.0.1:8000/api/json
{}
>  curl http://127.0.0.1:8000/api/text
demo
>  curl http://127.0.0.1:8000/api/html
<h1>demo</h1>
```

### 2.5.设置与获取Web框架属性
`Pait`为Web框架的设置与获取Web框架属性值的方法提供了一个统一的方法，它们分别是`set_app_attribute`和`get_app_attribute`，
通过`set_app_attribute`和`get_app_attribute`可以在任一时刻设置与获取Web框架属性，使用方法如下：


=== "Flask"

    ```py linenums="1" title="docs_source_code/other/flask_with_attribute_demo.py" hl_lines="8 14"

    --8<-- "docs_source_code/docs_source_code/other/flask_with_attribute_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/other/starlette_with_attribute_demo.py" hl_lines="10 16"
    --8<-- "docs_source_code/docs_source_code/other/starlette_with_attribute_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/other/sanic_with_attribute_demo.py" hl_lines="8 14"
    --8<-- "docs_source_code/docs_source_code/other/sanic_with_attribute_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/other/tornado_with_attribute_demo.py" hl_lines="10 16"
    --8<-- "docs_source_code/docs_source_code/other/tornado_with_attribute_demo.py"
    ```

在运行代码后，可以通过以下命令进行测试:
```bash
➜  curl http://127.0.0.1:8000/api/demo
{"status_code": 200}
```
通过结果可以看到，路由函数能够获取到`client`并通过`client`获取到url的`status_code`。

!!! note

    通过为Web框架设置属性值，可以使组件与框架解耦，同时也可以使组件更加灵活，但是更加推荐通过DI工具来实现解耦，具体的DI工具见[Awesome Dependency Injection in Python](https://github.com/sfermigier/awesome-dependency-injection-in-python)。

## 3.如何在其它Web框架使用Pait
目前`Pait`还在快速迭代中，所以还是以功能开发为主，如果要在其他尚未支持的框架中使用`Pait`, 或者要对功能进行拓展, 可以参照两个框架进行简单的适配即可.

同步类型的web框架请参照 [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask)

异步类型的web框架请参照 [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette)

## 4.示例代码
更多完整示例请参考[example](https://github.com/so1n/pait/tree/master/example)
## 5.发行说明
详细的发版说明见[CHANGELOG](https://github.com/so1n/pait/blob/master/CHANGELOG.md)
