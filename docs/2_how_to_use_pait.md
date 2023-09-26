在前面的章节中介绍了通过使用`Pait`装饰器以及改写路由函数的函数签名来使用`Pait`的参数转换与类型校验功能，也有简单的介绍通过`pre_depend_list`参数来使用`Pait`的Pre-Depend功能。
这功能都是简单的使用`Pait`装饰器来装饰函数，并通过配置不同属性的值来启用不同的功能，此时的`Pait`装饰器更像是一个针对路由函数的配置功能，不过很多路由函数本身都有一些共性导致它们在使用`Pait`时填写的参数的一样的，
比如在编写几个同个功能的路由函数时，可能会这样编写代码：
```Python
from pait.app import pait
from pait.model.status import PaitStatus

@pait(status=PaitStatus.test)
def demo1() -> None:
    pass


@pait(status=PaitStatus.test)
def demo2() -> None:
    pass

@pait(status=PaitStatus.test)
def demo3() -> None:
    pass
```
这份示例代码共有3个路由函数，它们都使用相同的`Pait`的`status`参数--`PaitStatus.test`，代表现在的路由函数的状态都处于测试中。
在经过一段时间的测试后，路由函数通过测试了，此时他们的状态需要变为`Relese`，于是就得手动的把每个接口的状态都切换为`PaitStatus.release`。
在路由函数比较多的时候，手动的切换状态是非常麻烦的，这时候可以先定义一个公共的`Pait`并在所有路由函数使用，使这些路由函数可以共享同一个`Pait`，从而共享同一份配置功能。

!!! note
    - 1.本章节只提供的示例都是基于`Starlette`框架，其他框架在使用的时候除了引入`Pait`类的`import`语句稍有不同外，其他的使用方法都是一致的。
    - 2.本章节着重描写的是`Pait`类的用法，至于不同属性的作用会在其对应的功能文档中描写。
    - 3.`Pait`可以认为是一个托管数据的容器，只要他们的属性一致，那么他们表达的功能是一致的，即使他们之间没有任何关系。

## 1.自定义Pait
在前文关于`Pait`的介绍，都是通过如下语法去引入并使用的:
```Python
from pait.app.flask import pait
from pait.app.sanic import pait
from pait.app.starlette import pait
from pait.app.tornado import pait
```


这是最方便的引用`Pait`的方法，不过它本身是针对每个Web框架定制`Pait`类的单例（在本章暂且称为标准`pait`装饰器），在自定义`Pait`时，建议通过Web框架对应的`Pait`类入手，
并基于`Pait`类重新实例化一个自定义的`Pait`实例，然后把路由函数的`Pait`装饰器替换为自定义的`Pait`实例，比如下面的示例代码：
```py hl_lines="6 8 13 18"
from pait.app.starlette import Pait
from pait.model.status import PaitStatus
from starlette.responses import Response


global_pait: Pait = Pait(status=PaitStatus.test)

@global_pait()
async def demo() -> Response:
    pass


@global_pait()
async def demo1() -> Response:
    pass


@global_pait()
async def demo2() -> Response:
    pass
```
其中的第一段高亮代码是基于`Pait`类来创建一个变量名为`global_pait`的`Pait`实例，它与之前使用的标准`pait`装饰器基本类似，唯一的区别是它的`status`属性被指定为`PaitStatus.test`。
而其他高亮代码把`global_pait`都应用到所有的路由函数中，此时路由函数应用`global_pait`的效果与如下代码的效果是一致的：
```Python
@pait(status=PaitStatus.test)
async def demo() -> Response:
    pass
```
所有路由函数的`status`属性都为`PaitStatus.test`，
如果在后续的代码迭代导致这几个路由函数的`status`属性需要变动时，只需要直接修`global_pait`的属性则可以让所有接口的`Pait`属性都得到更改。

## 2.创建子Pait
`Pait`可以通过`create_sub_pait`方法创建自己的子`Pait`，每个子`Pait`的属性都是从父`Pait`克隆的，比如下面这段代码：
```Python
from pait.app.starlette import Pait
from pait.model.status import PaitStatus

global_pait: Pait = Pait(status=PaitStatus.test)
other_pait: Pait = global_pait.create_sub_pait()
```
代码中`other_pait`是通过`global_pait`创建的，所以它的`status`属性也跟`global_pait`的`status`属性一样都是`PaitStatus.test`。

如果子`Pait`的部分属性不想克隆于父`Pait`，那么可以通过在创建的时候通过指定属性的值，使子`Pait`的属性被指定的值覆盖，如下代码:
```Python
from pait.app.starlette import Pait

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")
```
代码中`global_pait`与`user_pait`的`author`属性都是`("so1n", )`，但是由于在创建`user_pait`时指定了`group`的值为`user`，所以`global_pait`的`group`属性为`global`，而`user_pait`的`group`属性为`user`。

## 3.使用Pait
子`Pait`创建之后的用法与标准`pait`装饰器的用法是完全一致的，唯一不同的是它本身已经携带了部分属性的配置信息，在装饰路由之后，会使路由函数拥有了对应的配置功能。如下代码：
```Python
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()  # group="user"
async def user_login() -> JSONResponse:
    pass

@user_pait()  # group="user"
async def user_logout() -> JSONResponse:
    pass

@global_pait()  # group="global"
async def get_server_timestamp() -> JSONResponse:
    pass
```
代码中的用户登录路由函数`user_login`以及用户注销路由函数`user_logout`都使用`user_pait`，
所以他们的`group`的值都为`user`；而获取服务器时间戳的路由函数`get_server_timestamp`则单独使用的是`global_pait`，它的`group`的值是`global`。


如果想更改`user_logout`路由函数的`Pait`属性， 还可以在`user_logout`的`user_pait`装饰器填写对应的参数来达到更改的目的，
如下面的代码，其中高亮部分会把路由函数`user_logout`的`group`属性变为`user-logout`而不是`user`:
```py hl_lines="12"
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()
async def user_login() -> JSONResponse:
    pass

@user_pait(group="user-logout")
async def user_logout() -> JSONResponse:
    pass

@global_pait()
async def get_server_timestamp() -> JSONResponse:
    pass
```

除了覆盖原有的值外，部分属性还支持追加值，如下代码：
```py hl_lines="13"
from pait.app.starlette import Pait
from starlette.responses import JSONResponse

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")


@user_pait()  # group="user"
async def user_login() -> JSONResponse:
    pass


@user_pait(append_author=("Other Author",))  # group="user"; author=("so1n", "Other Author",)
async def user_logout() -> JSONResponse:
    pass


@global_pait()  # group="global"
async def get_server_timestamp() -> JSONResponse:
    pass
```
其中高亮部分使用到了`Pait`的`append_xxx`系列的参数来追加值，从而使`user_logout`的`author`值变为`("so1n", "Other Author")`

!!! note
    追加的值只会添加都最后一个元素，而部分功能如`Pre-Depend`需要考虑元素放置的顺序，使用时请留意追加的顺序是否合适。
