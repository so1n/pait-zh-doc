## 1.介绍
`Pait`除了参数类型转换与校验功能外，还支持自动生成路由函数的OpenAPI数据.你只需要编写路由函数的代码，`Pait`就可以生成路由函数的对应OpenAPI文档，如[文档首页](/)的示例代码:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_demo.py" hl_lines="21 23-24 31"

    --8<-- "docs_source_code/docs_source_code/introduction/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_demo.py" hl_lines="23 25-26 32"
    --8<-- "docs_source_code/docs_source_code/introduction/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_demo.py" hl_lines="22 24-25 32"
    --8<-- "docs_source_code/docs_source_code/introduction/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_demo.py" hl_lines="23 26-27 33"
    --8<-- "docs_source_code/docs_source_code/introduction/tornado_demo.py"
    ```
在运行代码并在浏览器访问: [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger) 就可以看到SwaggerUI的页面：
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1648292884021Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-Swagger%E9%A6%96%E9%A1%B5.png)

通过页面可以发现，Swagger页面展示的数据包括了响应对象的数据，通过`Pait`装饰器标注的数据，以及路由函数的参数据。

## 2.路由函数的OpenAPI属性
为路由函数绑定OpenAPI属性非常简单，只需要在`Pait`装饰器填写对应的属性即可，常见的路由函数属性绑定如下代码：
```python
from pait.app.any import pait
from pait.model.tag import Tag

demo_tag = Tag("demo tag", desc="demo tag desc")


@pait(
    desc="demo func desc",
    name="demo",
    summary="demo func summary",
    tag=(demo_tag,)
)
def demo() -> None:
    pass
```
该代码通过`Pait`的属性来指定路由函数的OpenAPI信息，它们的具体作用如下：

| 属性     | OpenAPI属性    | 描述                        |
|--------|--------------|---------------------------|
| desc   | description  | 接口的文档详细描述        |
| name   | operation_id | 接口的名称|
| summary | summary      | 接口的简介 |
| tag    | tag          | 接口的OpenAPI标签 |

!!! note
    - 1.在大多数情况下，`name`属性只是`operation_id`属性的一部分，`Pait`并不保证`name`与`operation_id`完全相等。
    - 2.Tag的声明应该保证全局唯一


不过`name`和`desc`属性分别可以通过路由函数名和路由函数的`__doc__`获取，比如下面代码中路由函数的`name`和`desc`属性与上面代码一致。
```python
from pait.app.any import pait
from pait.model.tag import Tag

demo_tag = Tag("demo tag", desc="demo tag desc")


@pait(
    summary="demo func summary",
    tag=(demo_tag,)
)
def demo() -> None:
    """demo func desc"""
    pass
```


除了上面几个属性外，OpenAPI还有一个名为`deprecated`的属性，该属性主要是用来标记接口是否已经被遗弃。
`Pait`没有直支持`deprecated`属性的标记，而是通过`PaitStatus`来判断路由函数的`deprecated`是否为`True`， `PaitStatus`的使用方法非常简单，如下代码：
```python
from pait.app.any import pait
from pait.model.status import PaitStatus


@pait(status=PaitStatus.test)
def demo() -> None:
    pass
```
该代码表示路由函数为测试中且`deprecated`为`False`，更多的状态以及是否为`deprecated`见下表:

| 状态值                 |阶段| deprecated | 描述           |
|---------------------|---|------------|--------------|
| undefined           |默认| `False`    | 未定义，默认的状态    |
| design              |开发中| `False`    | 设计中          |
| dev                 |开发中| `False`    | 开发测试中        |
| integration_testing |开发中| `False`    | 联合调试中        |
| complete            |开发完成| `False`    | 开发完成         |
| test                |开发完成| `False`    | 测试中          |
| pre_release         |上线| `False`    | 预发布          |
| release             |上线| `False`    | 发布           |
| abnormal            |下线| `True`     | 出现异常，临时下线    |
| maintenance         |下线| `False`    | 维护中          |
| archive             |下线| `True`     | 归档           |
| abandoned           |下线| `True`     | 被遗弃的，后续不会再使用 |
## 3.路由函数的响应对象

在前文的介绍中，通过`response_model_list`定义了路由函数的响应对象的列表，其中包含了一个或多个响应对象。

!!! note

    建议只填写一个响应对象，如果有多个响应对象，大多数非OpenAPI功能（如插件）会默认读取第一个响应对象。


`Pait`提供多种响应对象，如下列表：

|响应对象名称| 描述           |
|---|--------------|
|JsonResponseModel| 响应格式为Json的对象 |
|XmlResponseModel| 响应格式为Xml的对象  |
|TextResponseModel| 响应格式为文本的对象   |
|HtmlResponseModel| 响应格式为Html的对象 |
|FileResponseModel| 响应格式为File的对象 |

`Pait`只提供常见的响应类型的响应对象，如果没有适用的响应对象，可以通过`pait.model.response.BaseResponseModel`定义一个符合需求的响应对象。
`pait.model.response.BaseResponseModel`是一个包含OpenAPI响应对象不同属性的容器，如下表:


| 属性名            | 描述                                                                                                            |
|----------------|---------------------------------------------------------------------------------------------------------------|
| response_data  | 定义响应数据，如果是带有结构的响应数据，那么应该是一个描述结构体的`pydantic.BaseModel`                                                         |
| media_type     | 响应对象的`Media Type`                                                                                             |
| name           | 响应对象的名称                                                                                                       |
| description    | 响应对象的描述                                                                                                       |
| header         | 响应对象的Header，填入的值应该是`pydantic.BaseModel`而不是`Dict`                                                              |
| status_code    | 响应对象的Http状态码，默认为`(200, )`                                                                                     |
| openapi_schema | 响应对象的[openapi.schema](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#schema-object) |


通过这些属性可以定义大多数响应对象，示例代码如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/flask_demo.py" hl_lines="12-31 34"

    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/starlette_demo.py" hl_lines="14-33 36"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/sanic_demo.py" hl_lines="13-32 35"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/tornado_demo.py" hl_lines="13-32 36"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/tornado_demo.py"
    ```
该代码的第一段高亮代码是定义一个响应对象，它表示的Http状态码可能为200，201和404，
`Media Type`是`application/json`，
Header拥有`X-Token`和`Content-Type`两个属性，
而最重要的是定义了如下的返回数据结构:
```json
{
  "code": 0,
  "msg": "",
  "data": [
    {
      "name": "so1n",
      "sex": "man",
      "age": 18
    }
  ]
}
```
而第二段代码则是把响应对象与路由函数进行绑定，
现在运行代码，并在浏览器访问[127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc#tag/default/operation/demo_get)，可以看到当前页面完整的展示出路由函数的OpenAPI数据，如下图
![](https://fastly.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16867985131801686798512631.png)

!!! note
    由于`Redoc`展示的数据比`Swagger`简约了许多，本用例采用`Redoc`展示数据，实际上`Pait`支持多种OpenAPI的UI页面，详见[OpenAPI路由](/3_2_openapi_route/)。

## 4.Field
上一节的页面不仅包含了响应对象的数据，还包括请求参数的数据，如`uid`参数被声明为`required`，也就是该参数是必填的，同时也声明了它的类型是`integer`且取值范围是10-1000。
这些请求参数都是通过`Field`对象声明的，它们不仅可以校验参数，也可以为OpenAPI提供数据。除此之外，`Field`对象有部分属性是专门为`OpenAPI`服务的，它们包括：


| 属性 | 作用                                                                                              |
|----|-------------------------------------------------------------------------------------------------|
|links| OpenAPI link功能，用于指定参数与某个响应对象有关联                                                                 |
|media_type| 定义参数的`Media Type`，目前只有`Body`, `Json`, `File`, `Form`, `MultiForm`有使用，建议一个接口只采用同一种`Media Type`   |
|openapi_serialization| 定义参数的`serialization`，具体请参考[serialization](https://swagger.io/docs/specification/serialization/) |
|example| 定义参数的示例值；`Pait`支持工厂函数，但是转化为OpenAPI则会变成当下生成的固定值                                                  |
|openapi_include| 如果值为`False`，那么`Pait`在生成OpenAPI时不会考虑该参数                                                          |

### 4.1.Links
Links是OpenAPI的一个功能，用于指定A接口的请求参数与B接口的响应对象的某个数据有关联。比如下面的例子：
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/flask_link_demo.py" hl_lines="27 38"

    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/flask_link_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/starlette_link_demo.py" hl_lines="29 43-47"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/starlette_link_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/sanic_link_demo.py" hl_lines="28 40-44"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/sanic_link_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/how_to_use_openapi/tornado_link_demo.py" hl_lines="28 45-49"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/tornado_link_demo.py"
    ```

这个例子定义了一个登陆路由函数--`login_route`以及获取用户详情的路由函数--`get_user_route`，
其中获取用户详情的路由函数需要一个token参数来校验用户并获取用户的id，而这个token参数是通过登陆路由函数生成的，
所以用户详情路由函数的token参数与登陆路由函数的响应数据中的token是有关联的。

为了能让OpenAPI识别到token参数与响应对象中的token有关联，
首先创建一个名为`link_login_token_model`的实例，这个实例与`LoginRespModel`响应对象绑定，且通过表达式"$response.body#/data/token"`表明要绑定的参数。
接着把`link_login_token_model`赋值到`get_user_route`路由函数中`token`的`Field`的`links`属性，这样就完成了一次关联。

在运行代码并在浏览器访问[http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger)后会出现如下页面:
![](https://fastly.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/16868942366701686894235797.png)
可以看到登陆接口的`Response`那一栏的最右边展示了`Links`的数据。

!!! note
    目前许多OpenAPI工具只提供简单的Links支持，更多关于Links的使用与说明见[Swagger Links](https://swagger.io/docs/specification/links/)。

## 5.OpenAPI生成

在OpenAPI生态中，它的核心是一份符合OpenAPI格式的json或者yaml文本，这个文本可以在Swagger等OpenAPI页面中使用，也可以导入到Postman等工具中使用。
`Pait`会把收集到的数据委托给[AnyAPI](https://github.com/so1n/any-api)处理并生成一个OpenAPI对象，OpenAPI对象支持被转化为各种人类易读的文本或者页面。

!!! note

    [AnyAPI](https://github.com/so1n/any-api)是从`Pait`分离出来的，目前仅供`Pait`使用，在后续的版本中，[AnyAPI](https://github.com/so1n/any-api)会新增更多的功能。


下面是一个生成OpenAPI对象以及基于OpenAPI对象生成输出内容的示例:
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/how_to_use_openapi/flask_with_output_demo.py"

    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/flask_with_output_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/how_to_use_openapi/starlette_with_output_demo.py"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/starlette_with_output_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/how_to_use_openapi/sanic_with_output_demo.py"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/sanic_with_output_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/openapi/how_to_use_openapi/tornado_with_output_demo.py"
    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/tornado_with_output_demo.py"
    ```

该示例代码第一步是创建`openapi_model`，它在创建的过程中会获取到`app`对应的接口以及数据。
第二步是调用`openapi_model`的`content`方法，该方法的`serialization_callback`参数的默认值为`json.dump`。所以直接调用`openapi_model.content()`会生成如下JSON文本:

??? note "Json示例(示例文本较长，请按需打开)"

    ```json

    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/openapi.json"
    ```

此外，示例代码中还自定义了一个序列化为yaml的函数--`my_serialization`，并通过`openapi_model.content(serialization_callback=my_serialization)`生成如下yaml文本：

??? note "Yson示例(示例文本较长，请按需打开)"

    ```yaml

    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/openapi.yml"
    ```

Finally, Markdown documents in different languages are also generated via the `Markdown` method of [AnyAPI](https://github.com/so1n/any-api).

??? note "Chinese Markdown example (the example text is long, please open it as needed, only native data is displayed)"

    ```markdown

    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/openapi_zh_cn.md"
    ```


??? note "English Markdown example (the example text is long, please open it as needed, only native data is displayed)"



    ```markdown

    --8<-- "docs_source_code/docs_source_code/openapi/how_to_use_openapi/openapi_en.md"
    ```
