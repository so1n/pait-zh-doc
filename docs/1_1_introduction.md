# 介绍
`Pait`只是一个辅助框架，它并不会对Web框架的使用方式进行改变，所以在介绍`Pait`的使用之前，先看看不同Web框架的使用方式。
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_hello_world_demo.py"

    --8<-- "docs_source_code/introduction/flask_hello_world_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_hello_world_demo.py"
    --8<-- "docs_source_code/introduction/starlette_hello_world_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_hello_world_demo.py"
    --8<-- "docs_source_code/introduction/sanic_hello_world_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_hello_world_demo.py"
    --8<-- "docs_source_code/introduction/tornado_hello_world_demo.py"
    ```

示例代码展示的是将一个路由注册到Web框架的实例中，当Web框架在收到一个url为'/api'，method为`POST`请求后会把请求交由路由函数处理。
而路由函数的处理逻辑也很简单，它会先进行数据校验，当数据在符合要求的情况下才会返回，否则会直接抛出错误。

接下来，将展示在各个Web框架中如何使用`Pait`的参数类型转换和参数校验功能，代码如下(与文档首页的示例代码一样)：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_demo.py" hl_lines="20 22-23 30"

    --8<-- "docs_source_code/introduction/flask_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_demo.py" hl_lines="23 25-26 32"
    --8<-- "docs_source_code/introduction/starlette_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_demo.py" hl_lines="22 24-25 32"
    --8<-- "docs_source_code/introduction/sanic_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_demo.py" hl_lines="22 25-26 32"
    --8<-- "docs_source_code/introduction/tornado_demo.py"
    ```

代码中第一段高亮代码中的`@pait`是`Pait`所有功能的核心，在使用`@pait`装饰路由函数后，`Pait`会通过`inspect`获取到函数签名并生成依赖注入规则。
比如第二段高亮代码中路由函数的参数都以`<name>:<type>=<default>`格式的关键参数填写，`Pait`在初始化的时候自动通过如下的规则将关键参数转化为自己的依赖注入规则：

| key| 含义  | 作用                                                                |
|------|-----|-------------------------------------------------------------------|
| name | 参数名 | 在大多数情况下会作为Key到请求资源获取对应的值                                          |
| type | 参数类型 | 用于参数校验或者转化的类型                                                     |
|default| `Pait`的`Field`对象| 不同的`Field`代表从不同的请求类型获取值， 而`Field`对象的属性则告诉`Pait`该如何从请求中获取的值，并进行校验。 |

以上面的`uid`参数为例子，`Pait`会通过Body判断应该从请求中获取Json数据，接着以uid为Key从Json数据中获取对应的的值并转化并验证是否为`int`类型， 最后再判断该值是否处于10-1000之间，如果不是就直接报错， 如果是则赋值给`uid`变量。

通过`Hello World`代码与使用`Pait`后的代码做对比，可以看到使用`Pait`后的代码更加简单明了，同时也符合了现在`Python`流行的`Type Hint`，提高了代码的稳健性。



!!! note
    直接使用Body()时, `mypy`会检查到类型不匹配, 为此可以通过Body.i()忽略这个问题。
    如果需要`mypy`检查Body中`default`，`default_factory`以及`example`属性的值， 那么建议直接使用Body.t()。
