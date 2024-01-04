在使用`Pait`的过程中，可能会发现有多个路由函数使用到参数配置是相同的，如下代码：
```Python
from pait.app.any import pait
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


示例代码中共有3个路由函数，由于他们还处于测试阶段，所以它们`status`的值都是`PaitStatus.test`。
在经过一段时间的测试后，代码已经变得完善了并且可以准备发布，此时路由函数的状态需要变更为`Relese`，
于是就得手动的把每个路由函数的状态都切换为`PaitStatus.release`，
在路由函数比较多的时候，手动的切换状态是非常麻烦的。
为此，可以先定义一个公共的`Pait`并在所有路由函数使用，使这些路由函数可以共享同一个`Pait`，从而共享同一份配置功能。

!!! note
    - 1.本章节提供的示例都是基于`Starlette`框架，其他框架在使用的时候只有导入`Pait`类的`import`语句稍有不同外。
    - 2.本章节着重介绍的是`Pait`类的用法，不同属性的作用会在其对应的文档介绍。
    - 3.`Pait`可以认为是一个托管数据的容器，只要他们的属性一致，那么他们的功能是一致的，即使他们之间没有任何关系。

## 1.自定义Pait
在前文关于`Pait`的介绍，都是通过如下语法导入`Pait`:
```Python
from pait.app.flask import pait
from pait.app.sanic import pait
from pait.app.starlette import pait
from pait.app.tornado import pait
```


通过该语法导入的`pait`是每个Web框架对应`Pait`类的单例，在自定义`Pait`时，建议通过Web框架对应的`Pait`类入手，比如下面的示例代码：
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
示例代码的第一段高亮代码是基于`Pait`类创建一个名为`global_pait`的`Pait`实例，它与框架对应`pait`实例类似，唯一的区别是它的`status`属性被指定为`PaitStatus.test`。
其他高亮代码则是把`global_pait`都应用到所有的路由函数中，路由函数的`status`与下面这段代码的`status`是一致的：
```Python
@pait(status=PaitStatus.test)
async def demo() -> Response:
    pass
```

## 2.创建子Pait
`Pait`可以通过`create_sub_pait`方法创建自己的子`Pait`，每个子`Pait`的属性都是从父`Pait`克隆的，比如下面这段代码：
```Python
from pait.app.starlette import Pait
from pait.model.status import PaitStatus

global_pait: Pait = Pait(status=PaitStatus.test)
other_pait: Pait = global_pait.create_sub_pait()
```
代码中`other_pait`是通过`global_pait`创建的，所以它的`status`属性也跟`global_pait`的`status`属性一样都是`PaitStatus.test`。

如果不想克隆父`Pait`的属性，那么可以在创建子`Pait`时指定子`Pait`的属性，从而达到覆盖父`Pait`属性的效果，如下代码:
```Python
from pait.app.starlette import Pait

global_pait: Pait = Pait(author=("so1n",), group="global")
user_pait: Pait = global_pait.create_sub_pait(group="user")
```
`global_pait`与`user_pait`的`author`属性都为`("so1n", )`，
但是由于在创建`user_pait`时指定了`group`的值为`user`，所以`global_pait`与`user_pait`的`group`属性是不同的，它们分别为`global`和`user`。

## 3.使用Pait
子`Pait`的用法与标准`pait`装饰器的用法是完全一致的，唯一不同的是它本身已经携带了部分配置数据，在装饰路由之后，会使路由函数拥有了对应的配置功能。如下代码：
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
路由函数`user_login`和`user_logout`都被`user_pait`装饰， 所以他们的`group`的值都为`user`；
而路由函数`get_server_timestamp`被`global_pait`装饰，所以它的`group`的值为`global`。


此外，在子`pait`装饰路由函数时，可以通过定义属性的值实现覆写子`pait`原先的属性值。
如下面的代码，高亮代码中的路由函数的`user_logout`的`group`属性变为`user-logout`而不再是`user`:
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
高亮部分代码中使用到了`Pait`的`append_xxx`系列的参数来追加值，从而使`user_logout`的`author`值变为`("so1n", "Other Author")`

!!! note
    追加的值只会添加到序列中的末尾，而部分功能如`Pre-Depend`需要考虑值的放置顺序，使用时请留意追加的顺序是否合适。
