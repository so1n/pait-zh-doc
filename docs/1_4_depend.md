前文提到的`Field`对象都是与请求对象相关的，他们的作用都是把请求对象指定的资源注入到路由函数中。
而`Depend`则是一种特殊`Field`对象，他可以把符合`Pait`规则的函数注入到路由函数中，它可以实现如下功能:

- 共享相同的逻辑
- 实现安全校验的功能
- 与别的系统交互(如数据库)。


!!! note

    `Depend`只做请求对象相关的依赖注入，无法完成请求对象之外的依赖注入功能。如果你有这方面的需求，推荐通过DI工具来实现依赖注入功能，具体的DI工具见[Awesome Dependency Injection in Python](https://github.com/sfermigier/awesome-dependency-injection-in-python)。

## 1.Depend的使用
通常情况下，业务系统都会有用户Token校验的功能，这个功能是非常符合`Depend`的使用场景。
在这个场景中，用户每次访问系统时都需要带上Token，而服务端在收到用户的请求后会先判断Token是否合法，合法则会放行，不合法则会返回错误信息。


大多数类`Flask`微Web框架使用者都会选择使用`Python`装饰器来解决这个问题，如下:
```python
@check_token()
def demo_route() -> None:
    pass
```
有些时候还会增加一些功能，比如根据Token去获取到uid数据并传给路由函数:
```python
@check_token()
def demo_route(uid: str) -> None:
    pass
```
不过可以看出这种实现方法比较动态，它会导致代码检测工具很难检测这段代码是否存在问题。
只有在拥有良好的内部规范才有可能防止开发人员错误的使用`check_token`装饰器，但它也没办法完全防止`check_token`装饰器被错误的使用。

使用`Pait`的`Depend`可以解决这个问题，`Pait`的`Depend`使用示例代码如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_depend_demo.py"  hl_lines="14 17-20 24"

    --8<-- "docs_source_code/docs_source_code/introduction/depend/flask_with_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_depend_demo.py"   hl_lines="17 20-23 27"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/starlette_with_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_depend_demo.py"    hl_lines="14 17-20 24"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/sanic_with_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_depend_demo.py" hl_lines="19 22-25 30"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/tornado_with_depend_demo.py"
    ```

示例代码中第一段高亮代码是模仿数据库的调用方法，目前假设数据库只有用户`so1n`拥有token，且token值为"u12345"。
第二段高亮代码是一个名为`get_user_by_token`的函数，它负责从Header中获取Token并校验Token是否存在，如果存在则返回用户,不存在则抛错。
这个函数是一个特殊的函数，它的参数填写规则与被`Pait`装饰的路由函数一致， 所以之前提到的任何写法都可以在这个函数中使用，同时该函数可以被`Pait`的`Depend`使用。
第三段高亮代码则是路由函数填写的Token参数，这里比较特殊的是通过`field.Depend`来裹住`get_user_by_token`函数，
这样`Pait`就能够知道当前路由函数的Token参数必须通过`get_user_by_token`函数获取。

在运行代码并调用`curl`命令可以发现发现这段代码工作一切正常，当token存在时返回用户，不存在则返回抛错信息:
After running the code and calling the `curl` command, can find that this code works normally.
When the token exists, it returns to the user. If it does not exist, it returns an error message:
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
```

除此之外，`Pait`还能支持多层Depend嵌套的。
以上面的代码为例子，现在假设需要先校验Token合法后才会去数据库获取对应的用户，代码可以进行如下改写：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_nested_depend_demo.py"  hl_lines="17-20 23"

    --8<-- "docs_source_code/docs_source_code/introduction/depend/flask_with_nested_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_nested_depend_demo.py"   hl_lines="20-23 26"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/starlette_with_nested_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_nested_depend_demo.py"   hl_lines="17-20 23"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/sanic_with_nested_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_nested_depend_demo.py"    hl_lines="22-25 28"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/tornado_with_nested_depend_demo.py"
    ```

示例代码中的高亮代码为本次修改后的代码， 这部分代码主要是新增了一个`check_token`的函数用来获取和校验Token，
同时`get_user_by_token`获取Token的来源从`Header`变为`check_token`。

在运行代码并调用`curl`命令进行测试，通过输出结果可以发现不符合校验逻辑的会返回抛错信息：
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:fu12345"
{"data":"Illegal Token"}
```

## 2.基于ContextManager的Depend
上文所示的`Depends`用法虽然都能够正常的运行，但是它们没办法像`Python`装饰器一样知道函数的运行情况，包括函数是否正常运行，产生的异常是什么，何时运行结束等等等，
这时就需要基于`ContextManager`的`Depend`来解决这个问题。

基于`ContextManager`的`Depend`使用很简单，只要把函数加上对应的`ContextManager`装饰器，然后按照[ContextManager官方文档](https://docs.python.org/3/library/contextlib.html)中描述使用`try`,`except`,`finally`语法块即可，如下示例代码:
```Python
from contextlib import contextmanager
from typing import Any, Generator

@contextmanager
def demo() -> Generator[Any, Any, Any]:
    try:
        # 1
        yield None
    except Exception:
        # 2
        pass
    finally:
        # 3
        pass
```
该示例代码中序号1的位置用来编写正常的函数逻辑，并通过yield返回数据。
序号2的位置用来编写当函数运行异常时的代码逻辑。
最后的序号3则是用来编写统一的函数运行结束处理逻辑。

下面的代码是一个使用了`ContextManager`和`Depend`的例子：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_context_manager_depend_demo.py"  hl_lines="17-33 36-47 51"

    --8<-- "docs_source_code/docs_source_code/introduction/depend/flask_with_context_manager_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_context_manager_depend_demo.py"   hl_lines="20-36 39-50 55"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/starlette_with_context_manager_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_context_manager_depend_demo.py"  hl_lines="17-33 36-47 52"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/sanic_with_context_manager_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_context_manager_depend_demo.py"    hl_lines="13-29 32-43 58"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/tornado_with_context_manager_depend_demo.py"
    ```
该示例假设每次调用请求时都会基于对应的uid创建一个Session且Session会在请求结束时自动关闭.
其中第一段高亮代码是模拟一个基于uid的Session;
第二段高亮代码则是一个被`ContextManger`装饰的`Depends`函数，它会在`try`, `except`以及`finally`打印不同的内容;
而第三段高亮代码则是路由函数，它会依据参数`is_raise`是否为`True`来决定抛错还是正常返回。

现在运行代码并使用`curl`进行接口测试，发现第一个请求的响应结果是正常的，而第二个请求发生异常(返回空字符串)：
<!-- termynal -->
```bash
> curl "http://127.0.0.1:8000/api/demo?uid=999"
{"code":0,"msg":999}
> curl "http://127.0.0.1:8000/api/demo?uid=999&is_raise=True"
{"data":""}
```
这时切回到运行示例代码的终端，可以发现终端打印了类似如下数据:
```bash
context_depend init
context_depend exit
INFO:     127.0.0.1:44162 - "GET /api/demo?uid=999 HTTP/1.1" 200 OK
context_depend init
context_depend error
context_depend exit
INFO:     127.0.0.1:44164 - "GET /api/demo?uid=999&is_raise=True HTTP/1.1" 200 OK
```
通过终端输出的数据可以看出， 在第一次请求时, 终端只打印了`init`和`exit`，而在第二次请求时，终端会在`init`和`exit`中间多打印了一行`error`。
## 3.基于类的Depend
基于类的`Depend`与基于函数的`Depend`类似，它们之间的区别是`Pait`不但会解析类的`__call__`方法的函数签名之外，还会去解析类的属性，如下示例：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_class_depend_demo.py"  hl_lines="17-26 30"

    --8<-- "docs_source_code/docs_source_code/introduction/depend/flask_with_class_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_class_depend_demo.py"   hl_lines="20-29 33"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/starlette_with_class_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_class_depend_demo.py"  hl_lines="17-26 30"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/sanic_with_class_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_class_depend_demo.py"    hl_lines="22-31 36"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/tornado_with_class_depend_demo.py"
    ```
示例代码中的第一段高亮代码是基于类的`Depend`实现，这段代码主要分为两部分，
第一部分是类的属性，这里也采用`<name>: <type> = <default>`的格式编写的，每当请求命中路由时，`Pait`都会为该类注入对应的值。
第二部分代码是根据`Depend的使用`中的例子进行改写的，它会校验Token以及对应的用户名(正常的逻辑基本不会这样做，这里只做功能演示)，`__call__`方法的使用方法与基于函数的`Depend`类似。

??? tip "`__call__`方法使用限制说明"
    在`Python`中万物皆对象，所以一个拥有`__call__`方法的类与函数类似，如下示例代码：
    ```Python
    from typing import Any

    class DemoDepend(object):
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            pass
    ```
    代码中的`__call__`方法是一个直观的使用方式，但是由于`Python`的限制，`__call__`方法不支持函数签名重写，比如下面的例子:
    ```Python
    from typing import Any
    from pait import field

    class DemoDepend(object):
        def __init__(self) -> Any:
            def new_call(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any:
                pass
            setattr(self, "__call__", new_call)

        def __call__(self, uid: str = field.Query.i()) -> Any:
            pass
    ```
    该类实例化后，`inspect`解析出来的`__call__`方法的函数签名仍然是`__call__(self, uid: str = field.Query.i()) -> Any`，而不是`__call__(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any`。
    这会导致`Pait`无法提取正确的参数规则，为了解决这个问题，`Pait`会优先解析允许被重写的`pait_handler`方法，如下:
    ```Python
    from typing import Any
    from pait import field

    class DemoDepend(object):
        def __init__(self) -> Any:
            def new_call(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any:
                pass
            setattr(self, "pait_handler", new_call)

        def pait_handler(self, uid: str = field.Query.i()) -> Any:
            pass
    ```
    该类实例化后，`Pait`就能正常解析出`pait_handler`的函数签名是`pait_handler(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any`

而第二段高亮代码中则把`Depend`参数中的基于函数的`Depend`替换为基于类的`Depend`。

在运行代码并执行如下`curl`命令，可以看到如下输出:
<!-- termynal -->
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"data":"Can not found user_name value"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?user_name=so1n" --header "token:u12345"
{"user":"so1n"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?user_name=faker" --header "token:u12345"
{"data":"The specified user could not be found through the token"}
```

??? tip "基于类的`Depend`的初始化说明"
    由于每次请求都会创建一个新的实例，这意味着无法跟平常一样自定义初始化参数。
    这时可以采用`pait.util.partial_wrapper`绑定初始化参数，如下例子:
    ```python
    from pait import field
    from pait.util import partial_wrapper

    class GetUserDepend(object):
        user_name: str = field.Query.i()
        age: int = field.Query.i()

        def __init__(self, age_limit: int = 18) -> None:
            self.age_limit: int = age_limit

        def __call__(self, token: str = field.Header.i()) -> str:
            if token not in fake_db_dict:
                raise RuntimeError(f"Can not found by token:{token}")
            user_name = fake_db_dict[token]
            if user_name != self.user_name:
                raise RuntimeError("The specified user could not be found through the token")
            if self.age < self.age_limit:
                raise ValueError("Minors cannot access")
            return user_name


    @pait()
    def demo(user_name: str = field.Depends.i(partial_wrapper(GetUserDepend, age_limit=16))):
        pass

    @pait()
    def demo1(user_name: str = field.Depends.i(GetUserDepend)):
        pass
    ```

    这个例子中每个路由函数针对使用者的限制年龄有所不同，
    其中`demo`是限制年龄小于16的用户不可以访问，而`demo1`限制小于18岁的用户是不可以访问，
    所以他们的`GetUserDepend`的初始化参数是不同的。

    为此，`demo`函数采用了`pait.util.partial_wrapper`把初始化参数跟`GetUserDepend`绑定。
    `pait.util.partial_wrapper`的作用与官方的`functools.partial`类似，唯一不同的是它支持PEP612，可以获得代码提示以及使用检查工具进行代码检查。

## 4.Pre-Depend
在一些场景下路由函数只需要`Depends`函数执行校验逻辑，并不需要`Depends`函数的返回值，那么这时候可能会考虑用变量名`_`来进行替代，如下:
```python
@pait()
def demo(_: str = field.Depends.i(get_user_by_token)) -> None:
    pass
```
不过`Python`并不支持一个函数内出现多个相同名字的变量，这意味着有多个类似的参数时，无法把他们的变量名都改为`_`。

为此，`Pait`通过可选参数`pre_depend_list`来解决这个问题。它的使用方法很简单，只需要把`Depend`函数从参数迁移到`Pait`的`pre_depend_list`可选参数即可，
`Depend`代码的逻辑和功能均不会被受到影响，修改后代码会变为如下（高亮代码为修改部分）：

=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/depend/flask_with_pre_depend_demo.py"  hl_lines="23-24"

    --8<-- "docs_source_code/docs_source_code/introduction/depend/flask_with_pre_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/depend/starlette_with_pre_depend_demo.py"   hl_lines="26-27"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/starlette_with_pre_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/depend/sanic_with_pre_depend_demo.py"   hl_lines="23-24"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/sanic_with_pre_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/depend/tornado_with_pre_depend_demo.py"    hl_lines="29-30"
    --8<-- "docs_source_code/docs_source_code/introduction/depend/tornado_with_pre_depend_demo.py"
    ```

运行代码并执行`curl`命令后，通过如下输出结果可以看到`Pre-Depend`能够正常工作。：
<!-- termynal -->
```python
> curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"msg":"success"}
> curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
```

!!! note
    - 1.当使用`Pre-Depend`时，`Pait`会先按顺序执行`Pre-Depend`后再执行路由函数，如果`Pre-Depend`执行出错则会直接抛错。
    - 2.`Pre-Depend`绑定是`Pait`而不是路由函数，这意味着`Pre-Depend`可以跟随`Pait`一起复用，详见[Pait的复用](/2_how_to_use_pait/)。


## 5.:warning:不要共享有限的资源
`Depend`是共享相同逻辑的最佳实现，不过务必注意不要共享有限资源。因为共享的资源是给整个路由函数使用的，这意味着可能会影响到系统的并发数，甚至拖垮整个系统。

!!! note
    有限的资源的种类很多，常见的有限的资源有:线程池，`MySQL`连接池，`Redis`连接池等。

由于本节内容与`Pait`的使用方法无关，所以以`Redis`的连接举例说明共享有限资源的危害性。

!!! note
    - 1.最佳的示范用例是`MySQL`的连接池，不过为了节省代码量，这里采用`Redis`连接诶吃简要说明共享有限资源的危害。
    - 2.通常情况下是不会直接去获取`Redis`的连接，`Redis`也没有暴露出类似的接口，只是`execute_command`方法的执行逻辑与获取连接类似，所以使用该方法来举例说明。

一个`Redis`连接只能做一件事，但是`Redis`本身的设计非常出色，客户端在采用连接池的情况下仍然可以实现高并发。
但是如果路由函数的逻辑比较复杂，执行的时间比较久，那么整个服务的并发数就会受限于连接池的数量，如下代码:
```Python
import time
from typing import Callable
from flask import Flask, Response, jsonify
from redis import Redis
from pait.app.flask import pait
from pait import field

redis = Redis(max_connections=100)


def get_redis() -> Callable:
    return redis.execute_command


@pait()
def demo(my_redis_conn: Callable = field.Depends.i(get_redis)) -> Response:
    # mock redis cli
    my_redis_conn("info")
    # mock io
    time.sleep(5)
    return jsonify()


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.run(port=8000)
```
示例代码中每个路由函数都会先获取`Redis`连接再执行路由函数逻辑，最终再释放`Redis`连接。
所以`Redis`连接的使用时间是整个路由函数的运行时间，这意味着如果路由函数的逻辑比较复杂，那么会导致整个服务的并发数受限于`Redis`连接池的数量。
就像示例代码中的`demo`路由函数一样，`demo`路由函数会先调用`Redis`的`info`命令，然后模拟`IO`操作睡眠了5秒。
这意味着，在获取`Redis`连接后，`Redis`的大部分时间都浪费在了等待`IO`操作上，这是非常糟糕的。

要解决这个问题很简单，只要把共享资源变为共享获取资源的方法就可以了，如下代码:
```py linenums="1" hl_lines="12 18-20"
import time
from typing import Callable
from flask import Flask, Response, jsonify
from redis import Redis
from pait.app.flask import pait
from pait import field

redis = Redis(max_connections=100)


def get_redis() -> Callable:
    return lambda :redis.execute_command


@pait()
def demo(my_redis_conn: Callable = field.Depends.i(get_redis)) -> Response:
    # mock redis cli
    conn = my_redis_conn()
    conn("info")
    del conn
    # mock io
    time.sleep(5)
    return jsonify()


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.run(port=8000)
```
该代码有两部分变动，
第一部分是第一段高亮代码，该代码的`get_redis`函数从返回一个`Redis`连接变为返回一个获取`Redis`连接的方法，
第二部分是第二段高亮代码，从直接调用`Redis`连接变为先获取`Redis`连接再调用，最后再释放对`Redis`连接的占用。
这样一来只有使用到了`Redis`时才会去获取到`Redis`的连接，系统的并发也就不会很容易的受到`Redis`连接池影响了。
