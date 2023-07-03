## 1.隐式引入与显式引入
`pait`支持多个Web框架, 如果项目对应的依赖环境中只安装了其中的一个框架, 那么可以直接使用隐式引入:
```Python3
from pait.app import pait, load_app, add_simple_route

```
但是如果同时安装了多个框架, 那么上面的导包方式将会引发异常, 建议使用显示引入，如下:
```Python3
from pait.app.flask import pait, load_app, add_simple_route
from pait.app.sanic import pait, load_app, add_simple_route
from pait.app.starlette import pait, load_app, add_simple_route
from pait.app.tornado import pait, load_app, add_simple_route
```
## 2.内部方法
`Pait`内部封装了一些通用的方法，通过这些方法，开发者可以在不考虑兼容不同的Web框架的情况下快速的开发出拓展包，或者对`Pait`进行拓展，
OpenAPI路由和gRPCGateway就是基于这些方法开发的。
### 2.1.data
`data`是`Pait`的数据载体，`Pait`在装饰路由函数时生成的数据会按照一定的规则存放在`pait.g.data`中，以便为后续的配置，文档生成等功能提供支持。

### 2.2.load_app
data会存储很多路由函数的信息, 但是会缺少关键的OpenAPI信息数据如`url`, `method`等，
所以在使用OpenAPI之前还需要使用`load_app`把相关参数与`pait`装饰器装饰的路由函数数据在data中绑定，使用方法很简单，不过它一定要在注册所有路由后再调用，如下:

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

!!! note

    OpenAPI模块在初始化之前也会通过`load_app`方法加载数据

### 2.3.HTTP错误异常
`Pait`为每个Web框架封装了一个HTTP异常生成函数，它们通过HTTP状态码，错误内容，Headers等参数生成Web框架的HTTP标准异常，常用于身份校验等模块，它们的使用方法如下:

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
from pait.app import pait
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
`Pait`除了统一了不同Web框架的请求处理外，还通过SimpleRoute统一了不同Web框架的路由注册方法以及路由生成响应的方法。
开发者通过SimpleRoute可以在不考虑兼容的情况下很方便的完成路由编写和注册功能，
比如`gRPC Gateway`和OpenAPI路由功能完全使用SimpleRoute的方式编写路由，并由SimpleRoute注册到对应的Web框架中，节省了很多工作量。

!!! note

    统一的路由生成响应功能由`UnifiedResponsePluginProtocol`插件提供，SimpleRoute在注册路由函数时会为路由函数使用`UnifiedResponsePluginProtocol`插件

SimpleRoute的使用方法如下:

=== "Flask"

    ```py linenums="1" title="docs_source_code/other/flask_with_simple_route_demo.py" hl_lines="7-19 23-31"

    --8<-- "docs_source_code/other/flask_with_simple_route_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/other/starlette_with_simple_route_demo.py" hl_lines="8-20 24-32"
    --8<-- "docs_source_code/other/starlette_with_simple_route_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/other/sanic_with_simple_route_demo.py" hl_lines="9-21 25-33"
    --8<-- "docs_source_code/other/sanic_with_simple_route_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/other/tornado_with_simple_route_demo.py" hl_lines="8-20 24-32"
    --8<-- "docs_source_code/other/tornado_with_simple_route_demo.py"
    ```

代码中第一段高亮代码是编写了三个路由函数，它们都符合SimpleRoute的路由函数标准，SimpleRoute路由函数的标准如下:

- 1.路由函数需要被`pait`装饰，同时response_model_list属性不能为空（代码中路由函数的响应模型分别为`JsonResponseModel`，`TextResponseModel`，`HtmlResponseModel`，这些都是SimpleRoute路由强制要求的，如果没有响应模型，那么无法通过SimpleRoute把路由函数注册到Web框架中。）
- 2.路由函数的返回值不再是各种响应对象，而是`Python`的基础类型，但是需要跟响应模型保持一致。


第二段高亮是通过`add_simple_route`和`add_multi_simple_route`方法注册路由，其中`add_simple_route`只能注册一个路由，而`add_multi_simple_route`可以注册多个路由，它们的都接收app和SimpleRoute实例，而SimpleRoute只支持三个属性，如下:

| 参数     | 描述                   |
|--------|----------------------|
| route  | 符合SimpleRoute标准的路由函数 |
| url    | 当前路由的Url             |
| method | 当前路由对应的HTTP Method   |

此外，`add_multi_simple_route`还支持两个可选参数，如下:

| 参数     | 描述                                                                                      |
|--------|-----------------------------------------------------------------------------------------|
| prefix | 路由前缀，比如prefix为"/api"，某个SimpleRoute的url为"/user"时，注册的路由URL为"/api/user"                    |
| title  | 当前路由组的标题是什么，对于某些框架，它们采用的路由组或者蓝图都需要有唯一的命名，所以不同批次`add_multi_simple_route`的`title`参数都应该不同  |

`add_simple_route`和`add_multi_simple_route`在添加路由函数时，会先检查路由函数是否符合SimpleRoute标准，如果不符合，则抛出异常，
如果符合，会使用`UnifiedResponsePluginProtocol`插件使路由函数的返回转换为符合Web框架的响应类型，最后再把路由函数注册到Web框架中。

在运行代码后，可以通过以下命令进行测试:
```bash
➜  curl http://127.0.0.1:8000/json
{}
➜  curl http://127.0.0.1:8000/api/json
{}
➜  curl http://127.0.0.1:8000/api/text
demo
➜   curl http://127.0.0.1:8000/api/html
<h1>demo</h1>
```

### 2.5.设置与获取Web框架属性
`Pait`为Web框架的设置与获取Web框架属性值的方法提供了一个统一的方法，它们分别是`set_app_attribute`和`get_app_attribute`，
通过`set_app_attribute`和`get_app_attribute`可以在任一时刻设置与获取Web框架属性，使用方法如下：

=== "Flask"

    ```py linenums="1" title="docs_source_code/other/flask_with_attribute_demo.py" hl_lines="7 13"

    --8<-- "docs_source_code/other/flask_with_attribute_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/other/starlette_with_attribute_demo.py" hl_lines="10 16"
    --8<-- "docs_source_code/other/starlette_with_attribute_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/other/sanic_with_attribute_demo.py" hl_lines="8 14"
    --8<-- "docs_source_code/other/sanic_with_attribute_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/other/tornado_with_attribute_demo.py" hl_lines="9 15"
    --8<-- "docs_source_code/other/tornado_with_attribute_demo.py"
    ```
在运行代码后，可以通过以下命令进行测试:
```bash
➜  curl http://127.0.0.1:8000/api/demo
{"status_code": 200}
```

!!! note

    通过为Web框架设置属性值，可以使组件与框架解耦，同时也可以使组件更加灵活，但是更加推荐通过DI工具来实现解耦，具体的DI工具见[Awesome Dependency Injection in Python](https://github.com/sfermigier/awesome-dependency-injection-in-python)。

## 3.如何在其它Web框架使用Pait
目前`Pait`还在快速迭代中，所以还是以功能开发为主，如果要在其他尚未支持的框架中使用`Pait`, 或者要对功能进行拓展, 可以参照两个框架进行简单的适配即可.

同步类型的web框架请参照 [pait.app.flask](https://github.com/so1n/pait/blob/master/pait/app/flask.py)

异步类型的web框架请参照 [pait.app.starlette](https://github.com/so1n/pait/blob/master/pait/app/starlette.py)

## 4.IDE支持
pait的类型校验和转换以及类型拓展得益于`Pydantic`,同时也从`pydantic`获得到IDE的支持，目前支持`Pycharm`和`Mypy`

- [PyCharm plugin](https://pydantic-docs.helpmanual.io/pycharm_plugin/)

- [Mypy plugin](https://pydantic-docs.helpmanual.io/mypy_plugin/)

## 5.示例代码
更多完整示例请参考[example](https://github.com/so1n/pait/tree/master/example)
## 6.发行说明
详细的发版说明见[CHANGELOG](https://github.com/so1n/pait/blob/master/CHANGELOG.md)
