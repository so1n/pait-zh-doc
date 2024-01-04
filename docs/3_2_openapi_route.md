`Pait`除了支持OpenAPI数据的生成外，还支持OpenAPI路由生成，默认情况下会提供`openapi.json`接口以及`swagger-ui`页面等，比如[文档首页](/index)的示例代码:
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/flask_demo.py"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/starlette_demo.py"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/sanic_demo.py"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/tornado_demo.py"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py"
    ```

通过示例代码可以看到，只需要简单的调用`AddDocRoute`即可为`app`绑定OpenAPI路由，具体的路由url和对应的功能如下表所示：

| 路由url         | 描述                                                             | 特点                  |
|---------------|----------------------------------------------------------------|---------------------|
| /openapi.json | 获取OpenAPI的json响应                                               |                     |
| /elements     | 使用[elements](https://github.com/stoplightio/elements)展示接口文档数据  | UI漂亮简单，支持请求调用       |
| /redoc        | 使用[Redoc](https://github.com/Redocly/redoc)展示接口文档数据            | UI漂亮简单，但是不支持请求调用    |
| /swagger      | 使用[Swagger](https://github.com/swagger-api/swagger-ui)展示接口文档数据 | 通用的OpenAPI展示UI，功能齐全 |
| /rapidoc      | 使用[RapiDoc](https://github.com/rapi-doc/RapiDoc)展示接口文档数据       | 功能齐全；UI现代化；支持自定义的UI |
| /rapipdf      | 提供一个可以下载[RapiDoc](https://github.com/rapi-doc/RapiDoc)pdf文档的页面 | 对非英文的支持比较差          |

## 1.OpenAPI路由的使用
`AddDocRoute`可以方便的为`app`实例绑定OpenAPI路由，同时`AddDocRoute`提供了一些参数方便开发者自定义路由扩展以及解决生产环境的复杂化。
目前`AddDocRoute`提供的参数有:

| 参数                         | 描述                                                                         |
|----------------------------|----------------------------------------------------------------------------|
| scheme                     | HTTP Schema，如http或者https                                                   |
| openapi_json_url_only_path | 生成的openapi.json url是拥有path部分(该参数生效时，scheme会失效)                             |
| prefix                     | 路由URL前缀                                                                    |
| pin_code                   | 一种简单的安全校验机制                                                                |
| title                      | 定义OpenAPI路由的Title，需要注意的是，调用多次`AddDocRoute`绑定不同的OpenAPI路由时，它们的Title应该保持不同   |
| doc_fn_dict                | OpenAPI路由中UI页面的实现                                                          |
| openapi                    | `Pait`的OpenAPI对象                                                           |
| pait                       | `Pait`实例，OpenAPI会基于传递的`pait`去创建子`pait`并使用。详见[如何使用Pait](/2_how_to_use_pait) |
| add_multi_simple_route     | 为app实例绑定路由的方法，详见[SimpleRoute](/8_other/#24simpleroute)章节                                            |
| not_found_exc              | pin_code错误的异常                                                              |

### 1.1.scheme
通过scheme参数可以显式的指定OpenAPI路由的HTTP Schema，比如HTTP和HTTPS。

需要注意的是，HTTP Schema并不是指代当前服务使用的HTTP Schema，而是访问者使用的HTTP Schema。
比如当前服务指定的是HTTP，不过为了增强服务安全，在服务前加上一层代理以支持HTTPS，如使用Nginx。
这时用户只能通过`https://127.0.0.1/openapi.json` 访问服务， 为了使OpenAPI路由能够正常做出响应，在绑定OpenAPI路由时应该填写`scheme="https"`。

使用方法:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, scheme="http")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, scheme="http")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, scheme="http")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, scheme="http")
    app.listen(8000)
    IOLoop.instance().start()
    ```

### 1.2.openapi_json_url_only_path
openapi_json_url_only_path默认为`False`，此时生成的OpenAPI Json url为完整的(`http://example.com/openapi.json`)，
当openapi_json_url_only_path为`True`的时候，生成的OpenAPI Json url为`/openapi.json`。

!!! note

    - 1.目前的OpenAPI UI都支持`/openapi.json`的URL，但不保证后续的OpenAPI UI都能支持。
    - 2.使用`openapi_json_url_only_path`时，`schema`参数会失效

使用方法:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, openapi_json_url_only_path=True)
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, openapi_json_url_only_path=True)
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, openapi_json_url_only_path=True)
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, openapi_json_url_only_path=True)
    app.listen(8000)
    IOLoop.instance().start()
    ```
### 1.3.prefix
默认情况下`AddDocRoute`会按如下URL将路由绑定到app实例中:

- /openapi.json
- /redoc
- /swagger
- /rapidoc
- /rapipdf
- /elements

不过采用默认的`/`前缀是一种不太好的行为，建议在使用的时候通过`prefix`指定一个符合自己习惯的URL前缀。
比如`/api-doc`，那么`AddDocRoute`会以如下URL绑定到路由：

- /api-doc/openapi.json
- /api-doc/redoc
- /api-doc/swagger
- /api-doc/rapidoc
- /api-doc/rapipdf
- /api-doc/elements

使用方法:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, prefix="/api-doc")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, prefix="/api-doc")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, prefix="/api-doc")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, prefix="/api-doc")
    app.listen(8000)
    IOLoop.instance().start()
    ```
### 1.4.pin_code
`pin_code`提供了一种简单的安全机制，防止外部人员访问OpenAPI路由，它的用法如下:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, pin_code="6666")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, pin_code="6666")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, pin_code="6666")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, pin_code="6666")
    app.listen(8000)
    IOLoop.instance().start()
    ```

当你运行代码后，如果在浏览器访问`http://127.0.0.1:8000/swagger` 会发现找不到对应的页面，但是改用`http://127.0.0.1:8000/swagger/pin_code=6666` 访问则发现页面正常展示。

!!! note

    - 1.通常情况下OpenAPI路由不应该暴露给外部人员使用，需要通过Nginx等工具来增强安全性(如IP白名单限制)，这种机制的安全性是远远高于`pin_code`的。
    - 2.可以通过Pre-depend为OpenAPI添加自定义的安全校验。
    - 3.如果访问时携带的pin code校验不通过，那么默认情况下会返回404异常，该异常可以通过not_found_exc定制。


### 1.5.Title
Title有两个作用，一个是用于定义OpenAPI对象的Title属性，另外一个是指定当前绑定的OpenAPI路由的组名，所以如果对于同一个app实例调用多次`AddDocRoute`时，需要确保Title参数是不一样的。

使用方法如下:
=== "Flask"

    ```py linenums="1" hl_lines="30"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py::29"
    AddDocRoute(app, title="Api Doc")
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py::31"
    AddDocRoute(app, title="Api Doc")
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py::31"
    AddDocRoute(app, title="Api Doc")
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="32"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py::31"
    AddDocRoute(app, title="Api Doc")
    app.listen(8000)
    IOLoop.instance().start()
    ```

### 1.6.doc_fn_dict
`doc_fn_dict`是一个以OpenAPI UI 名为Key,生成OpenAPI Html内容函数为Value的字典。如果没有传递该参数，那么默认情况下`AddDocRoute`会采纳如下的字典:
```Python
from any_api.openapi.web_ui.elements import get_elements_html
from any_api.openapi.web_ui.rapidoc import get_rapidoc_html, get_rapipdf_html
from any_api.openapi.web_ui.redoc import get_redoc_html
from any_api.openapi.web_ui.swagger import get_swagger_ui_html

default_doc_fn_dict = {
    "elements": get_elements_html,
    "rapidoc": get_rapidoc_html,
    "rapipdf": get_rapipdf_html,
    "redoc": get_redoc_html,
    "swagger": get_swagger_ui_html,
}
```

其中，`doc_fn_dict`规定的Key为字符串，Value为如下的函数:
```Python
def demo(url: str, title: str = "") -> str:
    pass
```
该函数的第一个参数接受的值是URL，而第二个参数接受的值是Title，之后在生成路由的时候会通过`doc_fn_dict`以Key为url，value为路由函数绑定到app实例中。


以下是新增一个自定义OpenAPI UI的示例：
=== "Flask"

    ```py linenums="1" hl_lines="31-39"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py::29"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="33-41"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py::31"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="33-41"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py::31"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="33-41"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py::31"

    def demo(url: str, title: str = "") -> str:
        pass

    from pait.openapi.doc_route import default_doc_fn_dict
    from copy import deepcopy
    default_doc_fn_dict = deepcopy(default_doc_fn_dict)
    default_doc_fn_dict["demo"] = demo

    AddDocRoute(app, doc_fn_dict=default_doc_fn_dict)
    app.listen(8000)
    IOLoop.instance().start()
    ```
该示例会先创建一个符合规范的`demo`函数，然后新增到默认的`default_doc_fn_dict`中，最后再通过`AddDocRoute`与app实例绑定。

现在，可以通过`http://127.0.0.1:8000/demo` 访问到自定义的OpenAPI UI页面。

### 1.7.OpenAPI
默认情况下，`AddDocRoute`会先创建一个OpenAPI对象，并根据OpenAPI对象生成json内容。

!!! note

    `openapi.json`路由中创建的OpenAPI对象的Title会被`AddDocRoute`指定的`title`参数覆盖，并在`Server List`追加当前APP实例的地址。


不过`AddDocRoute`也支持通过`openapi`参数来传递定义好的OpenAPI对象，使用方法如下：
=== "Flask"

    ```py linenums="1" hl_lines="31-35"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py::29"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" hl_lines="33-37"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py::31"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" hl_lines="33-37"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py::31"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" hl_lines="33-37"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py::31"

    from pait.util import partial_wrapper
    from pait.openapi.openapi import OpenAPI, InfoModel

    openapi = partial_wrapper(OpenAPI, openapi_info_model=InfoModel(version="1.0.0", description="Demo Doc"))
    AddDocRoute(flask_app, openapi=openapi)  # type: ignore
    app.listen(8000)
    IOLoop.instance().start()
    ```

运行示例代码并访问[http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger)就可以看到页面左上角的文档描述和版本号都发生了更改。

## 2.OpenAPI路由的模板变量
大部分接口都有鉴权机制，比如需要带上正确的Token参数才正常获取数据。
如果在OpenAPI页面请求数据时，每次都需要粘贴Token参数，非常不方便。
这时就可以使用模板变量，让OpenAPI 页面可以自动填写变量的值，代码如下：
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/openapi_route/flask_demo.py"

    --8<-- "docs_source_code/docs_source_code/openapi/openapi_route/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/openapi_route/starlette_demo.py"
    --8<-- "docs_source_code/docs_source_code/openapi/openapi_route/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/openapi_route/sanic_demo.py"
    --8<-- "docs_source_code/docs_source_code/openapi/openapi_route/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/openapi_route/tornado_demo.py"
    --8<-- "docs_source_code/docs_source_code/openapi/openapi_route/tornado_demo.py"
    ```

首先引入了`TemplateVar`类，然后在`uid`的Field的example属性中使用了`TemplateVar("uid")`，这样一来`Pait`就知道参数`uid`的模板变量为`uid`。

现在运行上面的代码，并在浏览器输入`http://127.0.0.1:8000/swagger?template-uid=123` ，打开后可以看到如下图:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16506183174491650618317309.png)

通过图可以发现`uid`的值已经被自动填充为`123`，而不是默认的0了。
`Pait`之所以能把用户的值设置到对应的参数中是因为这个url多了一段字符串`template-uid=123`，
这样一来OpenAPI路由在收到对应的请求时会发现请求携带了一个以`template-`开头的变量，知道这是用户为模板变量`uid`指定了对应的值，
于是在生成OpenAPI数据时，会自动帮模板变量为uid的参数附上用户指定的值。
