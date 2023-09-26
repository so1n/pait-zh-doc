在API接口开发流程中，后端开发者往往都会先定义接口文档，并通过接口文档与前端开发者讨论接口的实现并进行修改，在这个阶段的接口并没有具体的代码实现。
同时在对接完文档后，前后端开发者会同时进行开发，这时可能会出现前端在开发过程中需要接口进行联调，而后端由于尚未开发完成无法提供该功能。

为此可以使用`Mock`插件，通过`Mock`插件即使路由函数没有具体的代码也可以生成指定的响应数据，如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/flask_with_mock_plugin_demo.py" hl_lines="16 21 25"

    --8<-- "docs_source_code/plugin/mock_plugin/flask_with_mock_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/starlette_with_mock_plugin_demo.py" hl_lines="20 25 29"
    --8<-- "docs_source_code/plugin/mock_plugin/starlette_with_mock_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/sanic_with_mock_plugin_demo.py" hl_lines="18 23 27"
    --8<-- "docs_source_code/plugin/mock_plugin/sanic_with_mock_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/mock_plugin/tornado_with_mock_plugin_demo.py" hl_lines="19 25 29"
    --8<-- "docs_source_code/plugin/mock_plugin/tornado_with_mock_plugin_demo.py"
    ```

这份代码先是实现了一个名为`UserSuccessRespModel2`的响应对象，这个响应对象与之前的响应对象有一些不同的是它的部分字段拥有`example`属性。
接着实现了一个没有任何代码逻辑的`demo`路由函数，这个函数只拥有一些参数，同时通过`pait`使用了`Mock`插件以及`UserSuccessRespModel2`响应对象，
接着运行代码并执行如下命令：
```bash
➜  curl http://127.0.0.1:8000/api/demo
{"code":0,"data":{"age":99,"email":"example@so1n.me","multi_user_name":["mock_name"],"uid":666,"user_name":"mock_name"},"msg":"success"}
```
通过输出结果可以看到在使用了`Mock`插件后，API接口能够正常返回数据，且数据与`UserSuccessRespModel2`响应对象中`example`的值是一样的。

> NOTE:
> - 1.example也支持工厂函数它的作用与`default_factory`效果类似。可填写的值如`example=time.now`，` example=lambda :random.randint(100000, 900000)`等。
> - 2.Mock插件支持通过参数`example_column_name`定义默认值字段，默认为`example`，也可以是`mock`。
