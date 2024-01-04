在开发流程中，后端开发者往往都会先定义API文档并通过API文档与前端开发者讨论API的实现并进行修改，在这个阶段中API并没有具体的实现。
在这个阶段中，前后端开发者会同时进行开发，那么就有可能会出现前端开发者在开发过程中需要对API进行调试，但由于后端开发者尚未开发完成前端开发者导致无法调试的情况。

为此,可以通过`Mock`插件为没有实现逻辑的路由函数返回指定的响应数据，如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/mock_plugin/flask_with_mock_plugin_demo.py"

    --8<-- "docs_source_code/docs_source_code/plugin/mock_plugin/flask_with_mock_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/mock_plugin/starlette_with_mock_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/mock_plugin/starlette_with_mock_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/mock_plugin/sanic_with_mock_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/mock_plugin/sanic_with_mock_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/mock_plugin/tornado_with_mock_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/mock_plugin/tornado_with_mock_plugin_demo.py"
    ```
这份代码先是实现了一个名为`UserSuccessRespModel2`的响应对象，这个响应对象与之前的响应对象有一些不同的是它的部分字段拥有`example`属性。
接着创建一个没有任何代码逻辑的`demo`路由函数，这个函数只拥有一些参数，同时通过`pait`使用了`Mock`插件以及`UserSuccessRespModel2`响应对象。

运行代码并执行如下命令，通过输出结果可以看到在使用了`Mock`插件后，路由函数能够正常返回数据且数据与`UserSuccessRespModel2`响应对象中`example`的值是一样的：
```bash
➜  curl http://127.0.0.1:8000/api/demo
{"code":0,"data":{"age":99,"email":"example@so1n.me","multi_user_name":["mock_name"],"uid":666,"user_name":"mock_name"},"msg":"success"}
```


!!! note
    - 1.example也支持工厂函数，此时它与`default_factory`效果类似。可填写的值如`example=time.now`，` example=lambda :random.randint(100000, 900000)`等。
    - 2.Mock插件支持通过参数`example_column_name`定义默认值字段，默认为`example`，也可以是`mock`。
