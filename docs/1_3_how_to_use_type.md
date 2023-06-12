`Type`用于指明该变量值的最终类型是什么，如下的示例代码:
```Python hl_lines="3-4"
@pait()
def demo(
    a: str = field.Body.i(),
    b: int = field.Body.i(),
) -> dict:
    return {"a": a, "b": b}
```
在程序运行的过程中，可以认为`Pait`会在内部将函数签名转换为如下的`Pydantic.BaseModel`:
```Python
from pydantic import BaseModel, Field

class Demo(BaseModel):
    a: str = Field()
    b: int = Field()
```

所以路由函数中的`Type`可以变得非常灵活，使用者可以像[Pydantic Field Types](https://pydantic-docs.helpmanual.io/usage/types/)一样使用以及直接使用[Pydantic Field Types](https://pydantic-docs.helpmanual.io/usage/types/)的拓展`Type`，此外，还可以通过编写符合`Pait`规范的`Type`来使用`Pait`的一些功能。
## 1.Type为Pydantic.BaseModel
在经历了一段时间的开发后，会发现有些接口的参数可能可以复用，这时可以采用`Type`为`Pydantic.BaseModel`的方案把两个接口重复的参数抽象为一个`pydantic.Basemodel`

示例代码如下， 首先是第一段高亮中的`DemoModel`，它继承于`Pydantic.BaseModel`且有三个属性分别为`uid`,`name`以及`age`，然后有两个不一样的接口，
其中接口`demo`会从Url中获取所有的值，并交给`DemoModel`进行校验，然后通过`.dict`方法生成dict并返回，而接口`demo1`与接口`demo`很像， 只不过获取数据的来源从Url变为Json Body。

=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/flask_with_model_demo.py" hl_lines="7-10"

    --8<-- "docs_source_code/introduction/how_to_use_type/flask_with_model_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/starlette_with_model_demo.py"  hl_lines="10-13"
    --8<-- "docs_source_code/introduction/how_to_use_type/starlette_with_model_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/sanic_with_model_demo.py"  hl_lines="8-11"
    --8<-- "docs_source_code/introduction/how_to_use_type/sanic_with_model_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/tornado_with_model_demo.py"   hl_lines="8-11"
    --8<-- "docs_source_code/introduction/how_to_use_type/tornado_with_model_demo.py"
    ```

!!! note
    如果`Field`对象的`raw_return`不为True，则`Pait`会以Key为`demo_model`从请求资源中获取值

接下来运行代码并使用`curl`对两个接口进行测试：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=u12345&name=so1n&age=10"
{"uid":"u12345","name":"so1n","age":10}
➜  ~ curl "http://127.0.0.1:8000/api/demo1" -X POST -d '{"uid": "u12345", "name": "so1n", "age": 10}' --header "Content-Type: application/json"
{"uid":"u12345","name":"so1n","age":10}
```
通过输出的结果可以发现两个接口都能正常的工作，但是在这种用法下，Field的作用是限定于整个BaseModel的，无法为每一个属性使用单独的`field`，这时可以采用另外一种方法。

## 2.Type为特殊的Pydantic.BaseModel
`Pait`的`Field`对象继承于`pydantic.FieldInfo`对象，同时也支持转为标准的`pydantic.FieldInfo`方法，所以可以把`Field`对象认为是一个携带资源来源标识的`pydantic.FieldInfo`对象，也是可以用于`pydantic.BaseModel`中，比如前文说到的`DemoModel`对象可以改写为如下代码:
```Python
from pait import field

from pydantic import BaseModel

class DemoModel(BaseModel):
    uid: str = field.Query.i(max_length=6, min_length=6, regex="^u")
    name: str = field.Query.i(min_length=4, max_length=10)
    age: int = field.Query.i(ge=0, le=100)
```
这样一来就可以让每个属性都使用不一样的`Field`对象，不过现在`DemoModel`中每个变量都使用了`Pait`的`Field`，所以在使用的时候需要做一点改变，填写的参数形式需要从`<name>:<type>=<default>`改为`<name>:<type>`，如下:
```Python
@pait()
def demo(demo_model: DemoModel) -> None:
    pass
```
此外，当前`DemoModel`中每个属性的`Field`对象都被固定为`Query`，而前文`demo1`接口用到的是`Body`对象，与`Query`对象不匹配，这时候就需要使用到`Pait`的`AnyField`功能了，首先把每个`Field`对象都替换为`pydantic.FieldInfo`:
```Python
from pydantic import BaseModel, Field

class DemoModel(BaseModel):
    uid: str = Field(max_length=6, min_length=6, regex="^u")
    name: str = Field(min_length=4, max_length=10)
    age: int = Field(ge=0, le=100)
```
然后通过`pait`装饰器中的`default_field_class`分别指定了`demo`路由的`AnyField`为`Query`，`demo1`路由的`AnyField`为`Body`:
```python
@pait(default_field_class=field.Query)
def demo(demo_model: DemoModel) -> None:
    pass

@pait(default_field_class=field.Body)
def demo1(demo_model: DemoModel) -> None:
    pass
```
这样就可以只编写一份`DemoModel`，但可以在不同功能的路由函数中使用了，完整的代码如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/flask_with_pait_model_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_type/flask_with_pait_model_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/starlette_with_pait_model_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/starlette_with_pait_model_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/sanic_with_pait_model_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/sanic_with_pait_model_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/tornado_with_pait_model_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/tornado_with_pait_model_demo.py"
    ```

这份代码为了验证属于`pait`的`Field`对象不被影响，还增加了一个`request_id`的属性，它使用了`Header`对象，这意味着会从Header获取数据。

现在运行代码，并使用`curl`进行调用发现响应的结果是正常的：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=u12345&name=so1n&age=10"
{"age":10,"name":"so1n","request_id":"6a5827f7-5767-46ef-91c6-f2ae99770865","uid":"u12345"}
➜  ~ curl "http://127.0.0.1:8000/api/demo1" -X POST -d '{"uid": "u12345", "name": "so1n", "age": 10}' --header "Content-Type: application/json"
{"age":10,"name":"so1n","request_id":"3279944c-6de7-4270-8536-33619641f25e","uid":"u12345"}
```

!!! note
    需要注意的是，在[如何使用Field对象](/1_2_how_to_user_field/)中`Pait`是按照变量顺序去处理/校验每一个变量的值，如果发现有不合法的值就直接抛错，不会对剩下的值进行处理，而`Type`为`pydantic.BaseModel`时，`Pait`会把参数委托给`pydantic.BaseModel`校验，而`pydantic.BaseModel`会对所有值都进行校验，然后再把错误抛出来。

## 3.其它
### 3.1.Request对象
在使用`Pait`时，`Request`对象使用的频率会大幅的降低，所以`Pait`会自动把`Request`对象省略，比如原本`Starlette`框架路由函数的写法是：
```Python
from starlette.requests import Request


async def demo(request: Request) -> None:
    pass
```
而在使用了`Pait`后会变为如下代码：
```Python
from pait.app.starlette import pait


@pait()
async def demo():
    pass
```

如果开发者需要`Request`对象，则任然可以使用框架原本的方法来获取`Request`对象，不过`Pait`会要求填写的`Type`必须是`Request`对象的`Type`，`pait`才能正确的把`Request`对象注入给对应的变量，代码如下：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/flask_with_request_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_type/flask_with_request_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/starlette_with_request_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/starlette_with_request_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/sanic_with_request_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/sanic_with_request_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/tornado_with_request_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/tornado_with_request_demo.py"
    ```
运行代码并执行如下`curl`命令即可看到类似的结果：
```bash
curl "http://127.0.0.1:8000/api/demo"
{"url": "http://127.0.0.1:8000/api/demo", "method": "GET"}
```

### 3.2.如何自定义符合Pydantic校验的Type
前文提到，在`Pait`中`Type`跟Pydantic的`Type`的作用是一样的，这也意味着可以通过`Type`来拓展校验规则从而弥补`Field`对象的不足，
比如在一个用户可能分布在不同国家的业务中，我们通常会选用时间戳来做时间传递，防止时区不同带来的数据错误，这时代码可以写为：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/flask_with_datetime_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_type/flask_with_datetime_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/starlette_with_datetime_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/starlette_with_datetime_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/sanic_with_datetime_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/sanic_with_datetime_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/tornado_with_datetime_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/tornado_with_datetime_demo.py"
    ```

不过在运行代码并使用如下`curl`调用可以发现，`Pydantic`自动把时间戳转为datetime类型了，且时区是UTC：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?timestamp=1600000000"
{"time":"2020-09-13T12:26:40+00:00"}
```
这种处理方式是没问题的，但假设这个业务的数据库的服务器是位于某个非UTC时区，而数据库与程序的时区都依赖于机器的时区，这样开发者在每次获取数据后还需要再转化一次参数的时区， 非常麻烦。 这时可以采用编写一个符合`Pydantic`校验规则的`Type`类来解决这个问题。

一个符合`Pydantic`校验方法的类必须满足带有`__get_validators__`类方法，且该方法是一个生成器，
于是可以这样实现一个时间戳的转换方法，使`Pydantic`在遇到时间戳时，能把时间转为`datetime`且该值的时区为服务器的时区：
```Python
import datetime
from typing import Callable, Generator, Union


class UnixDatetime(datetime.datetime):

    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[int, str]) -> datetime.datetime:
        if isinstance(v, str):
            v = int(v)
        return datetime.datetime.fromtimestamp(v)
```
然后把这个类应用到我们的代码中：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/flask_with_unix_datetime_demo.py"

    --8<-- "docs_source_code/introduction/how_to_use_type/flask_with_unix_datetime_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/starlette_with_unix_datetime_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/starlette_with_unix_datetime_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/sanic_with_unix_datetime_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/sanic_with_unix_datetime_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/how_to_use_type/tornado_with_unix_datetime_demo.py""
    --8<-- "docs_source_code/introduction/how_to_use_type/tornado_with_unix_datetime_demo.py"
    ```
重新运行这份代码后使用`curl`命令进行测试， 发现返回的时间值已经没有带时区了：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?timestamp=1600000000"
{"time":"2020-09-13T20:26:40"}
```
