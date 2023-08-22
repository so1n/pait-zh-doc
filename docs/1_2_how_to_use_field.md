`Field`对象在`Pait`中起到了至关重要的作用， `Pait`除了通过`Field`对象获取数据来源外， 还可以实现其它的功能， 不过本章中只着重说明参数校验。

## 1.Field的种类

除了[介绍](/1_1_introduction/)提到的`Body`外， 还有其他不同含义的`Field`对象， 它们的名称和作用如下:

- Body: 获取当前请求的json数据
- Cookie: 获取当前请求的cookie数据(注意， 目前Cookie数据会被转化为Python的dict对象， 这意味着Cookie的Key不能重复。建议当Field为Cookie时，参数的类型为str)
- File：获取当前请求的file对象，该对象与原Web框架的file对象一致
- Form：获取当前请求的form数据，如果有多个重复Key，只会返回第一个值
- Header: 获取当前请求的header数据
- Json: 获取当前请求的json数据(与Body一样)
- Path: 获取当前请求的path数据，如`/api/{version}/test`，则会获取到version的数据
- Query: 获取当前请求的Url参数对应的数据，如果有多个重复Key，只会返回第一个值
- MultiForm：获取当前请求的form数据， 返回Key对应的数据列表
- MultiQuery：获取当前请求的Url参数对应的数据， 返回Key对应的数据列表

各个种类的具体使用方法很简单，只要填入`<name>:<type>=<default>`中的`default`位置即可，以这段代码为例子:

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_demo.py"
    ```

!!! note
    为了确保演示的代码能够在不同的机器上顺利运行，这里没有演示`File`字段的用法，具体用法请参考不同Web框架示例代码中的`field_route.py`文件中`/api/pait-base-field`对应的路由函数。

示例代码演示了通过不同种类`Field`从请求对象获取请求者的参数，并组装成一定的格式返回。
接下来运行示例代码，然后使用`curl`命令在终端进行一次请求测试，命令如下:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/demo/18?multi_user_name=aaa&multi_user_name=bbb&uid=999&user_name=so1n&sex=man' \
  -H 'accept: */*' \
  -H 'Cookie: cookie=aaa,aaa' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'a=aaa&b=bbb&c=ccc1&c=ccc2'
```
正常情况下，会在终端看到如下输出:
```json
{
    "code": 0,
    "data": {
        "age": 18,
        "cookie": {
            "cookie": "aaa,aaa"
        },
        "email": "example@xxx.com",
        "form_a": "aaa",
        "form_b": "bbb",
        "form_c": [
            "ccc1",
            "ccc2"
        ],
        "multi_user_name": [
            "aaa",
            "bbb"
        ],
        "sex": "man",
        "uid": 999,
        "user_name": "so1n"
    },
    "msg": ""
}
```
通过输出结果可以发现，`Pait`都能通过`Field`的种类准确的从请求对象获取对应的值。

## 2.Field的功能
从上面的例子可以看出，`curl`命令的`url`并没有携带`email`参数， 但是接口返回的响应值中的`email`却不为空，且值是`example@xxx.com`，
这是因为`email`字段的`Field`的`default`属性被设置为`example@xx.com`， 这样`Pait`会在无法通过请求体获取到`email`值的的情况下，也能把默认值赋给变量。

除了默认值之外， `Field`也有很多的功能，这些功能大部分来源于`Field`所继承的`pydantic.Field`。


### 2.1.default
`Pait`通过读取`Field`的`default`属性来获取该参数的默认值，当`Field`的`default`属性不为空且请求体没有对应的值时，`Pait`就会把`default`的值注入到对应的变量中。

下面是简单的示例代码，示例代码中的两个接口都直接返回获取到的值`demo_value`，其中`demo`接口带有默认值， 默认值为字符串123，而`demo1`接口没有默认值:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_default_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_default_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_default_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_default_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_default_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_default_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_default_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_default_demo.py"
    ```

在运行代码，并使用`curl`调用后可以发现，当没有传demo_value参数时，`/api/demo`接口默认返回123, 而`/api/demo1`接口会抛出找不到`demo_value`值的错误:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo"
123
➜  curl "http://127.0.0.1:8000/api/demo1"
Can not found demo_value value
```

当传的demo_value参数为456时，`/api/demo`接口和`/api/demo1`接口都会返回456:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=456"
456
➜  ~ curl "http://127.0.0.1:8000/api/demo1?demo_value=456"
456
```

!!! note
    错误处理使用了`TipException`，可以通过[异常提示](/1_5_introduction/)了解`TipException`的作用。

### 2.2.default_factory
`default_factory`的作用与`default`类似，只不过`default_factory`接收的值是函数，只有当请求命中路由函数且`Pait`无法从请求对象中找到变量需要的值时才会被执行并将返回值注入到变量中。

示例代码如下，第一个接口的默认值是当前时间， 第二个接口的默认值是uuid，他们每次的返回值都是收到请求时生成的:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_default_factory_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_default_factory_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_default_factory_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_default_factory_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_default_factory_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_default_factory_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_default_factory_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_default_factory_demo.py"
    ```
在运行代码并使用`curl`调用可以发现接口每次返回的结果都是不一样的:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:29.127519
➜  ~ curl "http://127.0.0.1:8000/api/demo"
2022-02-07T14:54:33.789994
➜  ~ curl "http://127.0.0.1:8000/api/demo1"
7e4659e18103471da9db91ed4843d962
➜  ~ curl "http://127.0.0.1:8000/api/demo1"
ef84f04fa9fc4ea9a8b44449c76146b8
```
### 2.3.alias
通常情况下`Pait`会以参数名为key从请求体中获取数据，但是一些参数名如`Content-Type`是Python不支持的变量命名方式， 此时可以使用`alias`来为变量设置别名，如下示例代码:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_alias_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_alias_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_alias_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_alias_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_alias_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_alias_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_alias_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_alias_demo.py"
    ```

运行代码并使用`curl`调用可以发现，`Pait`正常的从请求体的Header中提取`Content-Type`的值并赋给了`content_type`变量，所以路由函数能正常返回值`123`:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" -H "Content-Type:123"
123
```

### 2.4.数值类型校验之gt，ge，lt，le，multiple_of
`gt`，`ge`，`lt`，`le`，`multiple_of`都属于`pydantic`的数值类型校验， 仅用于数值的类型，他们的作用各不相同：

- gt：仅用于数值的类型，会校验数值是否大于该值，同时也会在OpenAPI添加`exclusiveMinimum`属性。
- ge：仅用于数值的类型，会校验数值是否大于等于该值，同时也会在OpenAPI添加`exclusiveMinimum`属性。
- lt：仅用于数值的类型，会校验数值是否小于该值，同时也会在OpenAPI添加`exclusiveMaximum`属性。
- le：仅用于数值的类型，会校验数值是否小于等于该值，同时也会在OpenAPI添加`exclusiveMaximum`属性。
- multiple_of：仅用于数字， 会校验该数字是否是指定值得倍数。

使用方法如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_num_check_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_num_check_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_num_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_num_check_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_num_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_num_check_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_num_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_num_check_demo.py"
    ```

这份示例代码只有一个接口，但是接受了三个参数`demo_value1`, `demo_value2`, `demo_value3`，他们分别只接收符合大于1小于10，等于1以及3的倍数的三个参数。

在运行代码并使用`curl`调用可以发现第一个请求符合要求并得到了想要的响应结果，
第二，三，四个请求分别是`demo_value1`，`demo_value2`，`demo_value3`的值不在要求的范围内，所以`Pait`会生成`Pydantic.ValidationError`的错误信息，从错误信息可以简单的看出来三个参数都不符合接口设置的限定条件：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=1&demo_value3=3"
{"data":[2,1,3]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=11&demo_value2=1&demo_value3=3"
{
    "data": [
        {
            "ctx": {"limit_value": 10},
            "loc": ["query", "demo_value1"],
            "msg": "ensure this value is less than 10",
            "type": "value_error.number.not_lt"
        }
    ]
}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=2&demo_value3=3"
{
    "data": [
        {
            "ctx": {"limit_value": 1},
            "loc": ["query", "demo_value2"],
            "msg": "ensure this value is less than or equal to 1",
            "type": "value_error.number.not_le"
        }
    ]
}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=2&demo_value2=1&demo_value3=4"
{
    "data": [
        {
            "ctx": {"multiple_of": 3},
            "loc": ["query", "demo_value3"],
            "msg": "ensure this value is a multiple of 3",
            "type": "value_error.number.not_multiple"
        }
    ]
}
```
### 2.5.数组校验之min_items，max_items
`min_items`，`max_items`都属于`pydantic`的`Sequence`类型校验，仅用于`Sequence`的类型，他们的作用各不相同：

- min_items：仅用于`Sequence`类型，会校验`Sequence`是否满足大于等于指定的值。
- max_items： 仅用于`Sequence`类型，会校验`Sequence`是否满足小于等于指定的值。

> 注：如果使用的Pydantic版本大于2.0.0，请使用`min_length`和`max_length`代替`min_items`和`max_items`。

示例代码如下，该接口通过`field.MultiQuery`从请求Url中获取参数`demo_value`的数组，并返回给调用端，其中数组的长度限定在大于等于1且小于等于2之间：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_item_check_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_item_check_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_item_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_item_check_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_item_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_item_check_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_item_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_item_check_demo.py"
    ```

与2.4一样，通过`curl`调用可以发现合法的参数会放行，不合法的参数则会抛错：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[1]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2"
{"data":[1,2]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1&demo_value=2&demo_value=3"
{
    "data": [
        {
            "loc": [
                "demo_value"
            ],
            "msg": "ensure this value has at most 2 items",
            "type": "value_error.list.max_items",
            "ctx": {
                "limit_value": 2
            }
        }
    ]
}
```
### 2.6.字符串校验之min_length，max_length，regex
`min_length`，`max_length`，`regex`都属于`pydantic`的字符串类型校验，仅用于字符串的类型，他们的作用各不相同：

- min_length：仅用于字符串类型，会校验字符串的长度是否满足大于等于指定的值。
- max_length：仅用于字符串类型，会校验字符串的长度是否满足小于等于指定的值。
- regex：仅用于字符串类型，会校验字符串是否符合该正则表达式。

> 注：如果使用的Pydantic版本大于2.0.0，请使用`min_length`和`max_length`还可以校验序列类型。而`regex`字段会被`pattern`代替。

示例代码如下， 该接口需要从Url中获取一个值， 这个值得长度大小为6，且必须为英文字母u开头：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_string_check_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_string_check_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_string_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_string_check_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_string_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_string_check_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_string_check_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_string_check_demo.py"
    ```
运行代码并使用`curl`进行三次请求，通过结果可以看出，第一次为正常数据，第二次为不符合正则表达式，第三次为长度不符合：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=u66666"
{"data":"u66666"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=666666"
{"data":[{"loc":["demo_value"],"msg":"string does not match regex \"^u\"","type":"value_error.str.regex","ctx":{"pattern":"^u"}}]}
➜  ~ curl "http://127.0.0.1:8000/api/demo?demo_value=1"
{"data":[{"loc":["demo_value"],"msg":"ensure this value has at least 6 characters","type":"value_error.any_str.min_length","ctx":{"limit_value":6}}]}
```
### 2.7.raw_return
该参数的默认值为`False`，如果为`True`，则`Pait`不会根据参数名或者`alias`为key从请求数据获取值， 而是把整个请求值返回给对应的变量。

示例代码如下， 该接口为一个POST接口， 它需要两个值，第一个值为整个客户端传过来的Json参数， 而第二个值为客户端传过来的Json参数中Key为a的值：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_raw_return_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_raw_return_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_raw_return_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_raw_return_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_raw_return_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_raw_return_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_raw_return_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_raw_return_demo.py"
    ```

运行代码并使用`curl`调用， 可以发现结果符合预期：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" -X POST -d '{"a": "1", "b": "2"}' --header "Content-Type: application/json"
{"demo_value":{"a":"1","b":"2"},"a":"1"}
```

### 2.8.自定义查询不到值的异常
在正常情况下，如果请求对象中没有`Pait`需要的数据，那么`Pait`会抛出`NotFoundValueException`异常。
不过`Pait`可以支持开发者通过`not_value_exception`定义自定义异常，如下代码中路由函数有两个变量，第一个变量`demo_value1`没有设置任何`Field`的属性，而第二个变量`demo_value2`设置了`not_value_exception`属性为`RuntimeError("not found data")`：

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/flask_with_not_found_exc_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_field/flask_with_not_found_exc_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/starlette_with_not_found_exc_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/starlette_with_not_found_exc_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/sanic_with_not_found_exc_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/sanic_with_not_found_exc_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_field/tornado_with_not_found_exc_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_field/tornado_with_not_found_exc_demo.py"
    ```
运行代码，并在终端执行如下`curl`命令，可以看到`demo_value1`变量缺值和`demo_value2`缺值的响应是不同的：
```bash
➜ ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=1&demo_value2=2"
{"data": {"demo_value1": "1", "demo_value2": "2"}}
➜ ~ curl "http://127.0.0.1:8000/api/demo?demo_value2=2"
{"data": "Can not found demo_value1 value"}
➜ ~ curl "http://127.0.0.1:8000/api/demo?demo_value1=1"
{"data": "not found data"}
```

### 2.8.其它功能
除了上述功能外，`Pait`还有其它功能，可以到对应模块文档了解：

| 属性                   | 文档                           | 描述                                                                                                               |
|----------------------|------------------------------|------------------------------------------------------------------------------------------------------------------|
| links                | [OpenAPI](/3_1_openapi/)     | 用于支持OpenAPI的link功能                                                                                               |
| media_type           | [OpenAPI](/3_1_openapi/)     | Field对应的media_type，用于OpenAPI的Scheme的参数media type分类。                                                              |
| openapi_serialization | [OpenAPI](/3_1_openapi/)     | 用于该值在OpenAPI的Schema的序列化方式。                                                                                       |
| example              | [OpenAPI](/3_1_openapi/)     | 用于文档的示例值，以及Mock请求与响应等Mock功能，同时支持变量和可调用函数如`datetime.datetim.now`，推荐与[faker](https://github.com/joke2k/faker)一起使用。 |
| description          | [OpenAPI](/3_1_openapi/)     | 用于OpenAPI的参数描述                                                                                                   |
| openapi_include      | [OpenAPI](/3_1_openapi/)     | 定义该字段不被OpenAPI读取                                                                                                 |                                                                                                 |
| extra_param_list     | [Plugin](/5_1_introduction/) | 定义插件的行为                                                                                                          |
