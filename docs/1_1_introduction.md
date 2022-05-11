# 介绍
使用`Pait`来进行参数类型转换与参数校验非常简单，以示例的代码为例子：
``` py hl_lines="11 13 14"  linenums="1" 
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait.field import Body


# 使用pait装饰器装饰函数
@pait()
async def demo_post(
    uid: int = Body.i(description="user id", gt=10, lt=1000),
    user_name: str = Body.i(description="user name", min_length=2, max_length=4)
) -> JSONResponse:
    # 获取对应的值进行返回
    return JSONResponse({'result': {'uid': uid, 'user_name': user_name}})


app = Starlette(
    routes=[
        Route('/api', demo_post, methods=['POST']),
    ]
)

uvicorn.run(app)
```
代码中其中第11行是`Pait`的核心，`Pait`的所有运行功能都在这个装饰器中实现，在这个核心中，会通过`inspect`获取到函数对应的函数签名，并通过函数签名生成一个`pydantic.BaseModel`对象, 然后通过该对象校验和转换请求点值并根据函数签名返回给函数对应的参数。

而13,14行代码则是开发者自己填写的参数， 开发者在编写函数时， 只要把函数的参数都写成类似于`<name>:<type>=<default>`格式的关键参数即可，这种写法除了符合`Python`的关键参数标准外， `Pait`还会赋予其它的意义：

- `name`为参数名， 在大多数情况下会作为Key来中请求资源获取对应的值
- `type`为值对应的类型，`Pait`会用它来做参数校验和转化
- `default`则是`Pait`的`field`对象，不同的`field`代表从不同的请求类型获取值， 而对象的属性则告诉`Pait`该如何去预处理从请求中获取的值。

以上面的`uid`参数为例子，`Pait`会通过Body从请求中的获取Json数据，接着以Key为uid从Json数据中获取对应的的值并转化或验证是否为`int`类型， 最后再判断该值是否处于10-1000之间，如果不是就直接报错， 如果是则赋值给`uid`这个变量。

!!! note
    直接使用Body()时, mypy会检查到类型不匹配, 而Body.i()则可兼容这个问题， 一般情况下建议直接使用Body.i()。
