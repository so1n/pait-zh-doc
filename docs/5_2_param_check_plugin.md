`Pait`基于`Pydantic`实现了很多参数校验和转换的功能，但是在开发API的过程中，往往还需要一些参数依赖相关的校验功能，
在`Pait`中通过后置插件`Required`和`AtMostOneOf`提供两种参数依赖校验功能。

## 1.Required插件
在编写API接口时，经常会遇到一些参数依赖情况，比如某个接口存在请求参数A，B，C， 其中，B和C都是选填。
但是这个接口的参数C依赖于参数B，要求参数B存在时，C也需要存在，B参数不存在时，C就不能存在。
这时可以使用`Required`插件来进行参数限制，如下代码：
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_required_plugin_demo.py" hl_lines="16"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_required_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_required_plugin_demo.py" hl_lines="20"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_required_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_required_plugin_demo.py" hl_lines="18"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_required_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_required_plugin_demo.py" hl_lines="19"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_required_plugin_demo.py"
    ```

这个路由函数要求参数`uid`为必填参数，而参数`user_name`和`email`是选填参数，但是通过使用`ReuiredPlugin`插件后就会新增一个校验逻辑。
这个校验逻辑是由`required_dict`定义的，它表示的是参数`email`必须依赖于一个参数集合才可以存在，这里定义的集合只有一个参数--`user_name`，也就是参数`user_name`存在的时候，参数`email`才可以存在。

使用`curl`发送请求后可以通过响应结果发现，如果请求的参数只有`uid`时能正常返回，但请求的参数`user_name`为空时，参数`email`必须为空，不然会报错。
```bash
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123
{"uid":"123","user_name":null,"email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa
{"data":"email requires param user_name, which if not none"}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa\&user_name\=so1n
{"uid":"123","user_name":"so1n","email":"aaa"}%
```

`Required`插件除了通过`build`方法传递依赖规则外，也可以通过`ExtraParam`拓展参数来定义规则，`Required`插件支持`RequiredExtraParam`和`RequiredGroupExtraParam`两种拓展参数，
如下是`RequiredExtraParam`的使用:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_extra_param_demo.py" hl_lines="16 20"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_extra_param_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_extra_param_demo.py" hl_lines="20 24"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_extra_param_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_extra_param_demo.py" hl_lines="18 22"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_extra_param_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_extra_param_demo.py" hl_lines="19 24"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_extra_param_demo.py"
    ```

示例代码中通过向`user_name`参数的`Field`添加`extra_param_list=[RequiredExtraParam(main_column="email")`配置标记`user_name`依赖于`email`字段，

`Required`插件的另一个拓展参数`RequiredGroupExtraParam`则是通过`group`为参数做分类，同时通过`is_main`标记这组参数中的某个参数为主参数，这样一来该分组的其他参数都会依赖到主参数，示例代码如下：

=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_group_extra_param_demo.py" hl_lines="16 21 25"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_required_plugin_and_group_extra_param_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_group_extra_param_demo.py" hl_lines="20 25 29"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_required_plugin_and_group_extra_param_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_group_extra_param_demo.py" hl_lines="18 23 27"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_required_plugin_and_group_extra_param_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_group_extra_param_demo.py" hl_lines="19 25 29"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_required_plugin_and_group_extra_param_demo.py"
    ```
这段代码把`user_name`和`email`参数归为`my-group`组，同时定义`email`参数为`my-group`组的主参数，最终表现出来的依赖规则就是`user_name`参数依赖于`email`参数。

## 2.AtMostOneOf插件
`AtMostOneOf`插件的主要功能是检查参数的互斥，比如某个接口有三个参数分别为A、B和C，它们被要求B参数与C参数互斥，也就是B存在时，C就不能存在，C存在时，B就不能存在。
这时可以使用`AtMostOneOf`插件配置规则来实现功能，代码如下：
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_demo.py" hl_lines="16"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_demo.py" hl_lines="20"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_demo.py" hl_lines="18"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_demo.py" hl_lines="19"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_demo.py"
    ```



代码中的路由函数要求`uid`为必填参数，而`user_name`和`email`是选填参数，在使用`AtMostOneOfPlugin`插件后就会新增一个校验逻辑，
这个校验逻辑是由参数`at_most_one_of_list`定义的，它表示的是某一组参数不能同时存在，示例代码中定义的是参数`email`和`user_name`不能同时存在。

在使用`curl`发送请求后可以通过响应结果发现，参数`email`和`user_name`共存时候会返回错误，其它情况都能正常返回响应。
```bash
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123
{"uid":"123","user_name":null,"email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa
{"uid":"123","user_name":null,"email":"aaa"}%
➜  ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&user_name\=so1n
{"uid":"123","user_name":"so1n","email":null}%
➜ ~ curl http://127.0.0.1:8000/api/demo\?uid\=123\&email\=aaa\&user_name\=so1n
{"data":"requires at most one of param email or user_name"}%
```

`AtMostOneOf`插件支持通过`ExtraParam`对参数进行归类，并限制同一类的参数互斥不能同时出现，使用方法如下：

=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="16 21 25"

    --8<-- "docs_source_code/plugin/param_plugin/flask_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="20 25 29"
    --8<-- "docs_source_code/plugin/param_plugin/starlette_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="18 23 27"
    --8<-- "docs_source_code/plugin/param_plugin/sanic_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_and_extra_param_demo.py" hl_lines="19 25 29"
    --8<-- "docs_source_code/plugin/param_plugin/tornado_with_at_most_one_of_plugin_and_extra_param_demo.py"
    ```
在这段代码中，使用`AtMostOneOfExtraParam`把`user_name`和`email`参数归为`my-group`组，后续在运行时，`AtMostOneOf`插件会检查同组的`user_name`和`email`参数是否同时出现，如果同时出现则会直接抛出错误。
