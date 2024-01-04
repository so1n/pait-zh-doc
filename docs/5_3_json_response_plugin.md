目前路由函数中用得最多的序列化方式是JSON，所以`Pait`也自带了一些与JSON响应相关的插件，如校验JSON响应结果，自动补充JSON响应结果数据等，它们都用到了`response_model_list`中的响应模型拓展对应的功能。


!!! note
    - 1.由于插件需要获取到返回的结果，所以插件有可能侵入到原有框架，导致使用方法与原先的用法有些不同。
    - 2.插件都需要根据不同的Web框架进行适配，请以`from pait.app.{web framework name}.plugin.{plugin name} import xxx`的形式来引入对应的插件。

## 校验JSON响应结果插件
校验JSON响应结果插件的主要功能是对路由函数的响应结果进行校验，如果校验成功，才会返回响应，否则就会抛出错误，如下例子:
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/flask_with_check_json_plugin_demo.py"

    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/flask_with_check_json_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/starlette_with_check_json_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/starlette_with_check_json_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/sanic_with_check_json_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/sanic_with_check_json_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/tornado_with_check_json_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/tornado_with_check_json_plugin_demo.py"
    ```
首先是定义了一个名为`UserSuccessRespModel3`的JSON响应结果Model，
然后是定义一个错误处理函数用于捕获插件校验结果失败后抛出的异常，
接着是定义一个`demo`路由函数，路由函数使用了`CheckJsonRespPlugin`插件。
另外，当`display_age`不等于1时，`demo`路由函数返回的结果会与`UserSuccessRespModel3`不匹配。

在运行代码并执行如下命令，通过执行结果可以发现，当响应结果与定义的响应Model不匹配时，会直接抛出错误：
```bash
➜  curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18\&display_age\=1
{"code": 0, "msg": "", "data": {"uid": 123, "user_name": "so1n", "email": "example@xxx.com", "age": 18}}
➜  curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n\&age\=18
1 validation error for ResponseModel
data -> age
  field required (type=value_error.missing)
```

## 自动补全JSON响应结果插件
路由函数返回的结果应该与API文档定义的结构体一致，因为只返回部分字段就有可能导致客户端发生崩溃。
如果由于某些原因只能返回结构体的部分字段，那么可以采用自动补全JSON响应结果插件为缺少值的字段补上字段对应的默认值，如下例子:
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/flask_with_auto_complete_json_plugin_demo.py"

    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/flask_with_auto_complete_json_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/starlette_with_auto_complete_json_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/starlette_with_auto_complete_json_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/sanic_with_auto_complete_json_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/sanic_with_auto_complete_json_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/plugin/json_plugin/tornado_with_auto_complete_json_plugin_demo.py"
    --8<-- "docs_source_code/docs_source_code/plugin/json_plugin/tornado_with_auto_complete_json_plugin_demo.py"
    ```

这段代码先定义了一个`AutoCompleteRespModel`响应Model，其中`UID`的默认值为100。接着再实现一个`demo`函数，这个`demo`函数的返回结构有部分字段是缺失的但是它使用了`AutoCompleteJsonRespPlugin`插件，接着运行代码并执行如下命令：
```bash
➜  ~ curl http://127.0.0.1:8000/api/demo
{
  "code":0,
  "data":{
      "image_list":[{},{}],
      "music_list":[{"name":"music1","singer":"singer1","url":"http://music1.com"},{"name":"","singer":"","url":"http://music1.com"}],
      "uid":100
    },
  "msg":""
}
```
通过输出的结果可以发现，`data->uid`，`data->music_list->[0]->name`以及`data->music_list->[0]->singer`都被补上了默认值，
其中`data->uid`的默认值为`AutoCompleteRespModel`的Field定义的，而其他字段的默认值为类型对应的零值。


!!! note
    1.通过`Field`的`default`或者是`default_factory`可以定义响应的默认值。
    2.AutoCompletePlugin会侵入路由函数，导致路由函数只能返回`Python`类型而不是响应对象。
