前文介绍的`Field`对象都是与请求对象相关的，他们的作用都是把请求对象指定的资源注入到路由函数中。
而`Depend`则是一种特殊`Field`对象，他的作用是把符合`Pait`规则的函数注入到路由函数中，通过`Pait`的`Depend`可以实现如下功能:

- 共享相同的逻辑
- 实现安全校验的功能
- 与别的系统交互(如数据库)。


!!! note

    `Depend`只做请求对象相关的依赖注入，无法完成请求对象之外的依赖注入功能，推荐通过DI工具来实现依赖注入功能，具体的DI工具见[Awesome Dependency Injection in Python](https://github.com/sfermigier/awesome-dependency-injection-in-python)。

## 1.Depend的使用
一般的后端系统中都带有用户Token校验业务，这个业务是非常符合`Depend`的使用场景。
在这个场景中，用户每次访问接口时都需要带上Token，服务端在收到用户的请求后会先判断Token是否合法，如果不合法则会返回错误，合法则会执行接口的逻辑。

如果在使用类`Flask`的微Web框架，大多数使用者都会选择使用`Python`装饰器的方法来共享用户Token校验，如下:
```python
@check_token()
def demo_route() -> None:
    pass
```
有些时候还会根据Token去获取到uid数据并传给路由函数的功能，如下:
```python
@check_token()
def demo_route(uid: str) -> None:
    pass
```
但是这种实现方法比较动态，代码检测工具很难检测出来，只能订好内部规范，才有可能防止开发人员错误的使用`check_token`装饰器，但没办法完全防止错误的使用，而使用`Pait`的`Depend`可以解决这个问题。

`Pait`的`Depend`使用示例代码如下，其中第一段高亮代码是模仿数据库的调用方法，目前假设数据库只有用户`so1n`拥有token，且token值为"u12345"；
第二段高亮代码是一个名为`get_user_by_token`的函数，它的作用是从Header中获取Token，并校验Token是否存在，如果存在则返回用户，不存在则抛错。这个函数是一个特殊的函数，它的参数填写规则与被`Pait`装饰的路由函数一致， 之前提到的任何写法都可以在这个函数中使用，同时该函数可以被`Pait`的`Depend`使用。
第三段高亮则是路由函数填写的Token参数，比较特殊的是这里通过`field.Depend`来裹住`get_user_by_token`函数：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_depend_demo.py"  hl_lines="13 16-19 23"

    --8<-- "docs_source_code/introduction/depend/flask_with_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_depend_demo.py"   hl_lines="17 20-23 27"
    --8<-- "docs_source_code/introduction/depend/starlette_with_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_depend_demo.py"    hl_lines="14 17-20 24"
    --8<-- "docs_source_code/introduction/depend/sanic_with_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_depend_demo.py" hl_lines="18 21-24 29"
    --8<-- "docs_source_code/introduction/depend/tornado_with_depend_demo.py"
    ```
接着使用`curl`命令进行测试，发现这段代码工作一切正常，当token存在时返回用户，不存在则返回抛错信息:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
```

除此之外，`Pait`还能支持多层Depend嵌套的，以上面的代码为例子，假设Token要经过一层特别的校验，且该校验逻辑会被复用，则代码可以改写成如下代码：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_nested_depend_demo.py"  hl_lines="16-19 22"

    --8<-- "docs_source_code/introduction/depend/flask_with_nested_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_nested_depend_demo.py"   hl_lines="20-23 26"
    --8<-- "docs_source_code/introduction/depend/starlette_with_nested_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_nested_depend_demo.py"   hl_lines="17-20 23"
    --8<-- "docs_source_code/introduction/depend/sanic_with_nested_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_nested_depend_demo.py"    hl_lines="21-24 27"
    --8<-- "docs_source_code/introduction/depend/tornado_with_nested_depend_demo.py"
    ```

其中高亮部分为新修改的地方， 主要是新增了一个`check_token`的函数用来获取和校验Token，而`get_user_by_token`则依赖于`check_token`获取Token并判断用户是否存在。
使用`curl`进行接口测试，发现响应结果正常，不符合校验逻辑的会返回抛错信息：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"user":"so1n"}
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:fu12345"
{"data":"Illegal Token"}
```

## 2.基于ContextManager的Depend
上文所示的`Depends`用法虽然能正常的使用，但是它不能像`Python`装饰器一样知道函数的运行情况，包括函数是否正常运行，产生的异常是什么，何时运行结束等等等，
所以`Pait`的`Depend`通过支持`ContentManager`来解决这个问题。

这种方式的使用方法很简单，只要把函数加上对应的`ContextManager`装饰器，然后按照[官方文档](https://docs.python.org/3/library/contextlib.html)使用`try`,`except`,`finally`语法块即可，如下示例代码:
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
该例子中序号1的位置用来编写正常的函数逻辑，并通过yield返回数据，序号2的位置用来写当函数运行异常时的代码逻辑，最后的序号3则是一个统一的函数运行结束处理逻辑。

!!! note

    `ContextManager`的`Depend`函数除了参数外，其余的编写方法和官方的一致，具体可见[contextlib — Utilities for with-statement contexts](https://docs.python.org/3/library/contextlib.html)

下面的代码是一个使用了`ContextManager`和`Depend`例子：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_context_manager_depend_demo.py"  hl_lines="16-32 35-46 50"

    --8<-- "docs_source_code/introduction/depend/flask_with_context_manager_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_context_manager_depend_demo.py"   hl_lines="20-36 39-50 55"
    --8<-- "docs_source_code/introduction/depend/starlette_with_context_manager_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_context_manager_depend_demo.py"  hl_lines="17-33 36-47 52"
    --8<-- "docs_source_code/introduction/depend/sanic_with_context_manager_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_context_manager_depend_demo.py"    hl_lines="12-28 31-42 57"
    --8<-- "docs_source_code/introduction/depend/tornado_with_context_manager_depend_demo.py"
    ```
该例子假设每次调用请求时都会基于对应的uid创建一个Session，并在请求结束时自动关闭，
其中第一段高亮代码是模拟一个基于Uid的Session，第二段高亮代码则是带有`ContextManger`的Depends函数，并分别在`try`, `except`以及`finally`打印不同的内容，
而第三段高亮代码则是路由函数，它会依据参数`is_raise`是否为`True`来决定抛错还是正常返回。

现在运行代码并使用`curl`进行接口测试，发现第一个请求是通过的，但是第二个请求发生异常(返回空字符串)：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=999"
{"code":0,"msg":999}
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=999&is_raise=True"
{"data":""}
```
这时切回到运行Python进程的终端，可以发现终端打印了类似如下数据:
```bash
context_depend init
context_depend exit
INFO:     127.0.0.1:44162 - "GET /api/demo?uid=999 HTTP/1.1" 200 OK
context_depend init
context_depend error
context_depend exit
INFO:     127.0.0.1:44164 - "GET /api/demo?uid=999&is_raise=True HTTP/1.1" 200 OK
```
从输出的数据可以看出， 第一个请求访问服务端时，服务端进程只打印了`init`和`exit`，而对于第二个请求，服务端的逻辑会执行到异常处，所以会在`init`和`exit`中间多打印了一行`error`。
## 3.基于类的Depend
前文所述的都是基于函数的`Depend`，而`Pait`还提供基于类的的实现。
基于类的`Depend`用法与基于函数的`Depend`类似，不过`Pait`除了解析基于类的`Depend`的`__call__`方法的函数签名外，还会去解析它的属性，如下代码:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_class_depend_demo.py"  hl_lines="19-28 32"

    --8<-- "docs_source_code/introduction/depend/flask_with_class_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_class_depend_demo.py"   hl_lines="20-29 33"
    --8<-- "docs_source_code/introduction/depend/starlette_with_class_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_class_depend_demo.py"  hl_lines="17-26 30"
    --8<-- "docs_source_code/introduction/depend/sanic_with_class_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_class_depend_demo.py"    hl_lines="21-30 35"
    --8<-- "docs_source_code/introduction/depend/tornado_with_class_depend_demo.py"
    ```

其中的第一段高亮代码是基于类的`Depend`实现，这段代码主要分为两部分，
第一部分是类的属性，这里也采用`<name>: <type> = <default>`的格式编写的，这样一来每当请求命中路由时，`Pait`都会为该类注入对应的值。
第二部分是根据`Depend的使用`中的例子进行改写的，它除了校验Token外，还会校验Token对应的用户名是否正确(正常的逻辑基本不会这样做，这里只做功能演示)。
这里的`__call__`方法是真正被`pait`调用方法，所以它的使用方法与基于函数的`Depend`类似。

??? tip "`__call__`方法使用限制说明"
    ```Python
    from typing import Any
    class DemoDepend(object):
        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            pass
    ```
    是一个直观的使用方式，但是由于`Python`的限制，它不支持函数签名重写，比如下面的重写方法函数的例子:
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
    这时候解析出来的`__call__`方法仍然是`__call__(self, uid: str = field.Query.i()) -> Any`，而不是`__call__(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any`。此时推荐使用`pait_handler`方法，使用方法如下:
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
    这样`Pait`就能正常解析出`pait_handler`的函数签名是`pait_handler(uid: str = field.Query.i(), user_name: str = field.Query.i()) -> Any`
而第二段高亮代码中则把`Depend`参数中的基于函数的`Depend`替换为基于类的`Depend`。

运行代码并执行如下`curl`命令，可以看到如下输出:
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"data":"Can not found user_name value"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?user_name=so1n" --header "token:u12345"
{"user":"so1n"}
➜  ~ curl "http://127.0.0.1:8000/api/demo?user_name=faker" --header "token:u12345"
{"data":"The specified user could not be found through the token"}
```

??? tip "基于类的`Depend`的初始化说明"
    由于只支持传递基于类的`Depend`，而不是对应的实例，这意味着无法跟平常一样自定义初始化参数，这时可以采用`pait.util.partial_wrapper`，如下例子:
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
    这个例子中每个接口针对使用者的年龄有所不同，大部分情况下小于18岁是不可以访问的，而`demo1`接口的限制的是小于16岁的是不可以访问的，所以他们的初始化参数是不同的。
    而`pait.util.partial_wrapper`的作用与官方的`functools.partial`类似，它可以把参数跟`GetUserDepend`绑定，然后在初始化的时候会把参数传递进去，唯一不同的是它支持PEP612，所以可以在编写代码的时候获得`Type Hint`的功能，时刻保证自己的代码是健全的。

## 4.Pre-Depend
在一些场景下只需要`Depends`函数执行校验逻辑，如果校验失败就抛出错误，正常就返回空数据，路由函数实际上并不需要`Depends`函数的返回值，那么这时候可能会考虑用变量名`_`来进行替代，如下:
```python
@pait()
def demo(_: str = field.Depends.i(get_user_by_token)) -> None:
    pass
```
但是Python是不支持一个函数内出现相同名字的变量， 这意味着有多个类似的参数时，不能把他们的变量名都改为`_`。

为此，`Pait`通过可选参数`pre_depend_list`来提供了`Pre-Depends`功能，使用方法很简单，只需要把`Depend`函数从参数迁移到`Pait`的`pre_depend_list`可选参数即可，
`Depend`代码的逻辑和功能均不会被受到影响，这样修改后代码会变为如下（高亮代码为修改部分）：

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/depend/flask_with_pre_depend_demo.py"  hl_lines="22-23"

    --8<-- "docs_source_code/introduction/depend/flask_with_pre_depend_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/depend/starlette_with_pre_depend_demo.py"   hl_lines="26-27"
    --8<-- "docs_source_code/introduction/depend/starlette_with_pre_depend_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/depend/sanic_with_pre_depend_demo.py"   hl_lines="23-24"
    --8<-- "docs_source_code/introduction/depend/sanic_with_pre_depend_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/depend/tornado_with_pre_depend_demo.py"    hl_lines="28-29"
    --8<-- "docs_source_code/introduction/depend/tornado_with_pre_depend_demo.py"
    ```

运行代码并执行`curl`代码示例，输出结果如下：
```python
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u12345"
{"msg":"success"}
➜  ~ curl "http://127.0.0.1:8000/api/demo" --header "token:u123456"
{"data":"Can not found by token:u123456"}
```
可以看到能够正常执行校验逻辑。

!!! note
    - 1.当使用`Pre-Depend`时，`Pait`会先按顺序执行`Pre-Depend`再执行路由函数，如果`Pre-Depend`执行出错则会直接抛错。
    - 2.`Pre-Depend`绑定是`Pait`而不是路由函数，这意味着`Pre-Depend`可以跟随`Pait`一起复用，详见[Pait的复用](/2_how_to_use_pait/)。


## 5.:warning:不要共享有限的资源
`Depend`是共享相同逻辑的最佳实现，在其他的类似功能中可能会介绍如何共享有限的资源。
但是这种行为是不推荐的，因为此时共享的资源是给整个路由函数使用的，这意味着可能会影响到系统的并发数，或者拖垮整个系统。

!!! note
    有限的资源的种类很多，常见的有限的资源有:线程池，`MySQL`连接池，`Redis`连接池等。

由于本节内容与`pait`的使用方法无关，所以只是以`Flask`框架为例子，举例说明共享有限资源的危害性，这个例子的有限资源是`Redis`的连接。

!!! note
    - 1.最佳的示范用例是`Mysql`的连接池，但是代码量会比较多，所以这里采用`Redis`进行演示，简要说明共享有限资源的危害。
    - 2.通常情况下是不会直接去获取`Redis`的单一连接的，`Redis`也没有暴露出类似的接口，只是`execute_command`方法是先获取连接，再执行命令，最后释放连接的逻辑满足了获取连接的逻辑，所以以该方法来举例说明。


`Redis`的一个连接只能做一件事，但是得益于本身出色的设计，客户端采用连接池的情况下仍然可以实现高并发，但是如果路由函数的逻辑比较复杂，执行的时间比较久，那么整个服务的并发数就会受限于连接池的数量，如下代码:
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
示例代码中每个路由函数都会执行部分逻辑导致执行时长需要5秒钟，这意味着它会占用一个`Redis`连接5秒，但同时有超过100个请求访问的时候，部分请求会获取不到`Redis`连接而阻塞在`get_redis`逻辑中，这也意味着当前系统的瓶颈是`Redis`连接池的上限，但是真正使用到`Redis`的逻辑只有`my_redis_conn("info")`，这是非坏的。


要解决这个问题很简单，只要把共享资源变为共享获取资源的方法就可以了，比如这个例子一开始共享的是`Redis`连接这一个资源，现在有优化成共享获取`Redis`连接的逻辑，也就是从获取真正的`Redis`连接变为获取`Redis`连接的方法，然后在真正使用时才去获取连接，代码如下：

```py linenums="1" hl_lines="12 18"
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
    my_redis_conn()("info")
    # mock io
    time.sleep(5)
    return jsonify()


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.run(port=8000)
```
该代码主要变动有两个，第一个是第一段高亮代码，该代码的`get_redis`函数从返回一个`Redis`连接变为返回一个获取`Redis`连接的方法，
第二个变动是第二段高亮代码，这里从直接调用`Redis`连接变为先获取`Redis`连接再进行调用。
这样一来只有使用到了`Redis`才会去获取到`Redis`的连接，不会被其他逻辑影响，系统的并发瓶颈也就不会受到`Redis`连接池影响了。
