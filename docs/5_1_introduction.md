`Pait`的核心是一个装饰器，这个装饰器只负责插件的组装和编排，而真正负责功能实现的都是这些被装饰器初始化的插件，其中`Pait`的类型转换与参数校验功能是`Pait`的一个核心插件。

## 简单介绍
除了核心插件外，插件可以分为两大类，一类是继承于`PrePluginProtocol`的前置插件，另一类是继承于`PostPluginProtocol`的后置插件。

开发者可以通过`Pait`传入需要被启用的插件，在程序启动之后，`Pait`会以拦截器的形式把插件按照顺序进行初始化，如果该插件是前置插件，
那么它会被放置在核心插件之前，否则就会放在核心插件之后(后置插件)。

前置插件与后置插件除了继承的父类不同外，它们的最主要的区别是被调用时得到的参数是不同的。
其中，前置插件得到的是Web框架传递过来的请求参数(可以把它当成一个简单版的中间件)，
而后置形插件得到的是`Pait`核心插件转换后的请求数据，以下面的函数为例子：
```Python
import uvicorn  # type: ignore
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from pait.app.starlette import pait
from pait import field


@pait()
async def demo(
    uid: str = field.Query.i(),
    user_name: str = field.Query.i(),
) -> JSONResponse:
    return JSONResponse({"uid": uid, "user_name": user_name})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])

uvicorn.run(app)
```
假设代码中的`app`已经装载了一个中间件和对应的`Pait`插件，在收到一个请求时，它的处理逻辑会变为如下(采用不同的方式描述处理逻辑，核心逻辑是一致的):

=== "graph"

    ``` mermaid
    graph LR
      A[client] --> |send request| B[Middleware];
      B --> |recv response| A;
      B -->  C{Find match route?};
      C --> |Yes| D[Pre Plugin];
      C --> |No| B;
      D --> B;
      D --> E[Core Plugin];
      E --> D;
      E --> F[Post Plugin];
      F --> E;
      F --> G[Route Function];
      G --> F;
    ```

=== "sequence diagram"

    ``` mermaid
    sequenceDiagram
      client->>Middleware: send request
      Middleware->>Route Match: Find match route?
      Route Match->>Middleware: Success or Fail
      Middleware->>client: Route Match Fail, Return Not Found 404
      Middleware->>Pre Plugin: Route Match Success, send Request obj
      Pre Plugin->>Core Plugin:  send Request obj
      Core Plugin->>Post Plugin: send Param:{"uid": "", "user_name":""}
      Post Plugin->>Route Function: send Param:{"uid": "", "user_name":""}
      Route Function->>Post Plugin: recv Response obj
      Post Plugin->>Core Plugin: recv Response obj
      Core Plugin->>Pre Plugin: recv Response obj
      Pre Plugin->>Middleware: recv Response obj
      Middleware->>client: recv Response obj
    ```

=== "jpg"

    ![pait-plugin](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1647762511992pait-plugin.jpg)

在这个处理逻辑中， 请求会先由Web框架的中间件处理，接着由Web框架执行查找路由的功能，当找不到路由时就会返回`Not Found`的响应给客户端，如果找到了对应的路由，就会把请求传入到到`Pait`的处理逻辑。

在`Pait`的处理逻辑中请求被分为几步处理：

- 1.请求会先被前置插件处理，这时候前置插件只能得到框架对应的`request`参数(如果是`flask`框架，则没有)以及`Path`参数。
- 2.当前置插件处理完毕后就会把请求传入到核心插件进行参数提取和校验转换。
- 3.经核心插件处理完后会把提取的参数传递给后置插件，交由后置插件进行处理。
- 4.最后才经由后置插件把参数交给真正的路由函数处理生成响应并一一返回。

## 如何使用
目前`Pait`通过`plugin_list`和`post_plugin_list`参数分别接收前置插件和后置插件，如下：
```Python
from pait.plugin.required import RequiredPlugin

@pait(post_plugin_list=[RequiredPlugin.build(required_dict={"email": ["username"]})])
```
这段代码使用到的是一个名为`RequiredPlugin`的插件，这个插件属于后置插件，所以需要通过`post_plugin_list`参数使用插件。
同时，由于插件需要被`Pait`进行编排后才可以直接使用，所以插件不支持直接初始化插件，而是需要使用`build`方法来初始化插件(插件的`__init__`方法也不会提供准确的函数签名)。

如果考虑到插件的复用，推荐使用`create_factory`函数，该函数使用了[PEP-612](https://peps.python.org/pep-0612/)，支持IDE提醒和类型检查，`create_factory`使用方法如下：
```Python
from pait.util import create_factory

# 首先传入插件的build方法，并把build需要的参数传进去
# 然后得到的是一个可调用的方法
required_plugin = create_factory(RequiredPlugin.build)(required_dict={"email": ["username"]})

# 直接调用create_factory的返回，这时候插件会注入到路由函数中并进行一些初始化，同时也不影响其它路由函数的使用
@pait(post_plugin_list=[required_plugin()])
def demo_1():
    pass

@pait(post_plugin_list=[required_plugin()])
def demo_2():
    pass
```

## 关闭预检查
`Pait`是一个装饰器，用来装饰路由函数，所以在程序启动的时候会直接运行，装填各种参数并进行初始化。
不过`Pait`在把插件装填到路由函数时会调用到插件的`pre_check_hook`方法，对用户使用插件是否正确进行校验，比如下面的代码:
```Python
@pait()
def demo(
    uid: str = Body.i(default=None)
) -> None:
    pass
```
在启动的时候核心插件会校验到用户填写的`default`值并不属于`str`类型，所以会抛出错误。
不过这类检查可能会影响到程序的启动时间，所以建议在测试环境下才通过`pre_check`进行检查，在生产环境则关闭该功能。
关闭的方法很简单，通过设置环境变量`PAIT_IGNORE_PRE_CHECK`为True即可关闭。
