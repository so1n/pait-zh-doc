目前，`Pait`通过`TestHelper`对单元测试提供一个了简单的支持，`TestHelper`在执行时会通过路由函数自动补充URL，HTTP方法等参数运行测试，并在获得结果时会从`response_modle_list`中获取与测试结果最匹配的响应模型进行简单的校验，从而减少开发者编写测试用例的代码量。

!!! note

    自动测试，混沌测试等其他测试功能正在开发中，敬请期待。

## 1.TestHelper使用方法
本次使用的示例代码是以首页的示例代码进行拓展，主要变动是在路由函数添加了一个名为`return_error_resp`的参数，当`return_error_resp`为`True`时会返回不符合响应模型的响应，代码如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py" hl_lines="23 25-26"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py::31"
    app.run(port=8000)
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py" hl_lines="25 27-28"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py::32"

    import uvicorn
    uvicorn.run(app)
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py" hl_lines="24 26-27"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py::32"

    import uvicorn
    uvicorn.run(app)
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py" hl_lines="25 27-28"
    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py::33"
    app.listen(8000)

    from tornado.ioloop import IOLoop
    IOLoop.instance().start()
    ```

接着就可以通过`TestHelper`来编写测试用例了，首先需要导入`TestHelper`以及对应Web框架的测试客户端，同时还要进行测试框架的初始化:
=== "Flask"

    !!! note

        由于`Flask`在注册路由选定`POST`时会自动注册一个`OPTIONS`方法，会干扰`TestHelper`的HTTP方法自动发现，所以需要通过`apply_block_http_method_set`屏蔽`OPTIONS`方法。

    ```py linenums="33" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:33:62"
    ```

=== "Starlette"

    !!! note

        在使用`with TestClient(app) as client`时，`Starlette`会自动调用app的`startup`和`shutdown`方法，虽然本次测试用例并没有用到，但是使用`with TestClient(app) as client`是一个好习惯。

    ```py linenums="38" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:38:47"
    ```

=== "Sanic"

    ```py linenums="39" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:39:47"
    ```

=== "Tornado"

    !!! note

        目前我并不知道如何通过`Pytest`执行`Tornado`的测试用例，所以使用了`Tornado`的`AsyncHTTPTestCase`进行初始化。如果你知道如何通过`Pytest`执行`Tornado`的测试用例，欢迎通过[issue](https://github.com/so1n/pait/issues)反馈。

    ```py linenums="38" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:38:48"
    ```

在编写完测试用例的初始化代码后，就可以编写测试用例代码了，首先将演示如何通过`TestHelper`来编写一个测试用例，代码如下：
=== "Flask"

    ```py linenums="65" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:65:71"
    ```

=== "Starlette"

    ```py linenums="50" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:50:56"
    ```

=== "Sanic"

    ```py linenums="50" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:50:56"
    ```

=== "Tornado"

    ```py linenums="50" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:50:56"
    ```

在这个测试用例中， 会对`TestHelper`进行初始化，`TestHelper`的初始化需要Web框架对应的测试客户端、路由函数，以及路由函数的一些请求参数， 在初始化完成后就可以通过`TestHelper`获得请求响应了。

在执行测试的时候，`TestHelper`会通过路由函数自动发现了路由函数的`URL`和HTTP方法，所以调用`json`方法的时候`TestHelper`会自动发起了`post`请求，并通过`post`请求获得响应结果，
然后把响应Body序列化为`Python`的`dict`对象并返回， 但是当该路由函数绑定了多个请求方法时，`TestHelper`则无法自动执行，需要在调用`json`方法时指定对应的HTTP方法，
使用方法如下:
=== "Flask"

    ```py linenums="74" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py" hl_lines="7"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:74:80"
    ```

=== "Starlette"

    ```py linenums="59" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py" hl_lines="7"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:59:65"
    ```

=== "Sanic"

    ```py linenums="59" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py" hl_lines="7"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:59:65"
    ```

=== "Tornado"

    ```py linenums="58" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py" hl_lines="10"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:58:64"
    ```

此外，在编写测试用例时，可能需要获得到一个响应对象，而不是响应数据，以便对状态码，`Header`之类的数据进行校验。
这时可以通过`TestHelper`的HTTP方法进行调用并获得Web框架对应测试客户端的响应对象`Response`，如下代码就会通过`post`方法对路由函数发起请求，并返回Web框架测试客户端的响应对象，再通过响应对象进行断言:
=== "Flask"

    ```py linenums="83" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py" hl_lines="7-9"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:83:91"
    ```

=== "Starlette"

    ```py linenums="68" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py" hl_lines="7-9"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:68:76"
    ```

=== "Sanic"

    ```py linenums="68" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py" hl_lines="7-9"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:68:76"
    ```

=== "Tornado"

    ```py linenums="66" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py" hl_lines="10-12"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:66:74"
    ```
虽然这种情况下`TestHelper`与使用Web框架对应的测试客户端的使用方式没有太大的差别，但是`TestHelper`在获取到路由函数的响应后，
会根据路由响应从路由函数的`response_model_list`挑选一个最匹配的响应模型进行校验，如果检查到响应对象的HTTP状态码，Header与响应数据三者中有一个不符合响应模型的条件就会抛出错误并中断测试用例，如下例子：
=== "Flask"

    ```py linenums="92" title="docs_source_code/unit_test_helper/flask_test_helper_demo.py"

    --8<-- "docs_source_code/unit_test_helper/flask_test_helper_demo.py:92:100"
    ```

=== "Starlette"

    ```py linenums="77" title="docs_source_code/unit_test_helper/starlette_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/starlette_test_helper_demo.py:77:85"
    ```

=== "Sanic"

    ```py linenums="77" title="docs_source_code/unit_test_helper/sanic_test_helper_demo.py"
    --8<-- "docs_source_code/unit_test_helper/sanic_test_helper_demo.py:77:85"
    ```

=== "Tornado"

    ```py linenums="76" title="docs_source_code/unit_test_helper/tornado_test_helper_demo.py"
    class TestTornado(AsyncHTTPTestCase):
        ...

    --8<-- "docs_source_code/unit_test_helper/tornado_test_helper_demo.py:76:82"
    ```

在执行完测试用例后，`TestHelper`会发现路由函数的响应结果与路由函数定义的响应模型不匹配，此时会抛出异常，中断测试用例，并输出结果如下:
```bash
>               raise exc
E               pait.app.base.test_helper.CheckResponseException: maybe error result:
E               >>>>>>>>>>
E               check json content error, exec: 2 validation errors for ResponseModel
E               uid
E                 field required (type=value_error.missing)
E               user_name
E                 field required (type=value_error.missing)
E
E               >>>>>>>>>>
E               by response model:<class 'docs_source_code.unit_test_helper.flask_test_helper_demo.DemoResponseModel'>
```
通过输出结果可以发现，此时抛出的异常为`CheckResponseException`，并根据异常信息可以了解到，本次参与校验的响应模型是`DemoResponseModel`，它发现响应数据缺少了`uid`字段和`user_name`字段。


## 2.参数介绍
`TestHelper`的参数分为初始化必填参数，请求相关的参数，响应相关的结果参数共3种。其中，初始化参数的描述如下：

| 参数     | 描述          |
|--------|-------------|
| client | Web框架的测试客户端 |
| func   | 要进行测试的路由函数  |

而请求参数有多个，对于大部分Web框架来说只是封装了一层调用，但对于使用`Tornado`之类的没对测试客户端做过多封装的框架的则能提供了一些便利，这些参数有:

- body_dict: 发起请求时的Json数据。
- cookie_dict: 发起请求时的cookie数据。
- file_dict: 发起请求时的file数据。
- form_dict: 发起请求时的form数据。
- header_dict: 发起请求时的header数据。
- path_dict: 发起请求时的path数据。
- query_dict: 发起请求时的query数据。

除此之外，`TestHelper`还有几个与响应结果校验相关的参数，比如`strict_inspection_check_json_content`参数。
默认情况下，`strict_inspection_check_json_content`参数的值为True，这会让`TestHelper`对响应结果的数据结构进行严格校验，比如下面的例子:
```Python
a = {
    "a": 1,
    "b": {
        "c": 3
    }
}
b = {
    "a": 2,
    "b": {
        "c": 3,
        "d": 4
    }
}
```
在这个例子中，`a`与`b`的数据结构是不一样的，其中a变量代指响应模型的数据结构，b变量则是响应体的数据结构，当`TestHelper`进行校验时， 会因为检测到b变量多出来一个结构`b['b']['d']`而直接抛出错误，
不过也可以直接设置参数`strict_inspection_check_json_content`的值为`False`，这样`TestHelper`只会校验出现在响应模型中出现的字段，而不会检查响应模型之外的字段。

除了参数`strict_inspection_check_json_content`外，`TestHelper`还有另外几个参数，如下:

|参数|描述|
|---|---|
|target_pait_response_class|如果值不为空，那么`TestHelper`会通过`target_pait_response_class`从`response_model_list`中筛选出一批符合条件的`response_model`来进行校验。该值通常是响应模型的父类，默认值为`None`代表不匹配。|
|enable_assert_response|表示`TestHelper`是否会对响应结果进行断言，默认值为True。|
