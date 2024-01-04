变量的类型--`Type`用于指明该变量值的最终类型是什么，通过定义`Type`可以拓展变量的校验规则，如下示例代码:
```Python
from pait.app.any import pait
from pait import field

@pait()
def demo(
    a: str = field.Body.i(),
    b: int = field.Body.i(),
) -> dict:
    return {"a": a, "b": b}
```
在代码运行时，`Pait`会在内部将函数签名转换为如下的`Pydantic.BaseModel`:
```Python
from pydantic import BaseModel, Field

class Demo(BaseModel):
    a: str = Field()
    b: int = Field()
```

所以路由函数中的`Type`可以变得非常灵活，使用者可以像[Pydantic Field Types](https://pydantic-docs.helpmanual.io/usage/types/)一样使用`Type`，此外，还可以通过编写符合`Pait`规范的`Type`来使用`Pait`的一些功能。
## 1.Type的值为Pydantic.BaseModel
在经历了一段时间的开发后，会发现有些路由函数的参数是可以复用的，这时可以采用`Type`的值为`Pydantic.BaseModel`的方案把路由函数的参数转化为`pydantic.Basemodel`。


此外，还有两个不一样的路由函数`demo`和`demo1`。
其中`demo`会从Url Path中获取所有的值并交给`DemoModel`进行校验再返回`.dict`方法生成的数据。
而`demo1`虽然与路由函数`demo`很像， 只不过获取数据的来源从Url Path变为Json Body。

=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_model_demo.py"

    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_model_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_model_demo.py"
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_model_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_model_demo.py"
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_model_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_model_demo.py"
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_model_demo.py"
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

通过输出的结果可以发现两个路由函数都能正常的工作，但是在这种用法下`BaseModel`的所有字段都只能使用同一种`Field`类型，这时可以采用另外一种方法。

## 2.Type的值为特殊的Pydantic.BaseModel
`Pait`的`Field`对象是一个携带资源来源标识的`pydantic.FieldInfo`对象，同时也支持转为标准的`pydantic.FieldInfo`方法，
所以可以用于`pydantic.BaseModel`中，比如前文说到的`DemoModel`对象可以改写为如下代码:
```Python
from pait import field

from pydantic import BaseModel

class DemoModel(BaseModel):
    uid: str = field.Query.i(max_length=6, min_length=6, regex="^u")
    name: str = field.Body.i(min_length=4, max_length=10)
    age: int = field.Header.i(ge=0, le=100)
```
可以看到`DemoModel`每个属性的`Field`对象都是不一样的，不过为了能让`Pait`正确的加载`DemoModel`填写的参数形式需要从`<name>:<type>=<default>`改为`<name>:<type>`，如下:
```Python
@pait()
def demo(demo_model: DemoModel) -> None:
    pass
```

### 2.1.DefaultField
除此之外，还可以使用`Pait`的`DefaultField`功能，该功能可以根据路由函数定义的`Field`来自动替换`pydantic.BaseModel`中每个属性的`Field`，如下还是一个普通的`DemoModel`:
```Python
from pydantic import BaseModel, Field

class DemoModel(BaseModel):
    uid: str = Field(max_length=6, min_length=6, regex="^u")
    name: str = Field(min_length=4, max_length=10)
    age: int = Field(ge=0, le=100)
```
然后通过`pait`装饰器中的`default_field_class`属性指定了`demo`路由的`DefaultField`为`Query`，`demo1`路由的`DefaultField`为`Body`:
```python
from pait import field
from pait.app.any import pait


@pait(default_field_class=field.Query)
def demo(demo_model: DemoModel) -> None:
    pass

@pait(default_field_class=field.Body)
def demo1(demo_model: DemoModel) -> None:
    pass
```
这样一来，就可以在使用不同请求资源的路由函数中使用同一个`DemoModel`，完整的代码如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_pait_model_demo.py"

    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_pait_model_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_pait_model_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_pait_model_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_pait_model_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_pait_model_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_pait_model_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_pait_model_demo.py"
    ```


代码中的`DemoModel`增加了一个名为`request_id`的属性，它使用的`Field`对象是`Header`对象。
由于`Default Field`功能只会替换`pydantic.FieldInfo`，这意味着在运行的过程中`request_id`属性不会被`Default Field`影响，它还是会从Header获取数据。
现在运行代码，并调用`curl`命令可以看到如下输出：

```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?uid=u12345&name=so1n&age=10"
{"age":10,"name":"so1n","request_id":"6a5827f7-5767-46ef-91c6-f2ae99770865","uid":"u12345"}
➜  ~ curl "http://127.0.0.1:8000/api/demo1" -X POST -d '{"uid": "u12345", "name": "so1n", "age": 10}' --header "Content-Type: application/json"
{"age":10,"name":"so1n","request_id":"3279944c-6de7-4270-8536-33619641f25e","uid":"u12345"}
```

!!! note
    需要注意的是在正常情况下，`Pait`是按照变量顺序去处理/校验每一个变量的值，如果发现有不合法的值就直接抛错，不会对剩下的值进行处理。
    但是当`Type`的值为`pydantic.BaseModel`时，`Pait`会把参数委托给`pydantic.BaseModel`校验， 而`pydantic.BaseModel`会对所有值都进行校验，然后再把错误抛出来。

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

!!! note
    注：`Sanic`框架要求路由函数最少必须拥有一个参数。

如果需要在路由函数中使用`Request`对象，则需要以`<var name>: <RequestType>`的形式来定义路由函数参数，`pait`才能正确的把`Request`对象注入给对应的变量，例如：
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_request_demo.py"

    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_request_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_request_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_request_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_request_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_request_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_request_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_request_demo.py"
    ```
运行代码并执行如下`curl`命令即可看到类似的结果：
```bash
curl "http://127.0.0.1:8000/api/demo"
{"url": "http://127.0.0.1:8000/api/demo", "method": "GET"}
```

### 3.2.如何自定义符合Pydantic要求且带有校验功能的Type

前文提到，在被`Pait`装饰的路由函数中使用的`Type`跟Pydantic的`Type`的作用是一样的，这也意味着可以通过`Type`来拓展校验规则从而弥补`Field`对象的不足，
比如在一个用户可能分布在不同国家的业务中，通常会使用时间戳来传递时间以防止时区不同带来的数据错误，如下：
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_datetime_demo.py"

    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_datetime_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_datetime_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_datetime_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_datetime_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_datetime_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_datetime_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_datetime_demo.py"
    ```

不过在运行代码并调用如下`curl`命令后可以发现，`Pydantic`自动把时间戳转为datetime类型且时区是UTC：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?timestamp=1600000000"
{"time":"2020-09-13T12:26:40+00:00"}
```
这种处理方式是没问题的，但假设这个业务的服务器是位于某个非UTC且数据库与程序的都依赖于机器的时区时，
就需要在每次获取数据后再进行一次时区转化。
为此，可以采用编写一个符合`Pydantic`校验规则的`Type`类来解决这个问题，实现代码如下:

=== "Pydantic V1"
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
=== "Pydantic V2"
    ```py
    from pydantic import BeforeValidator
    from typing import Union
    from typing_extensions import Annotated
    from datetime import datetime


    def validate(v: Union[int, str]) -> datetime:
        if isinstance(v, str):
            v = int(v)
        return datetime.fromtimestamp(v)

    UnixDatetime = Annotated[datetime, BeforeValidator(validate)]
    ```

通过示例代码可以看到由于`Pydantic`版本的不同，`Type`的实现也是不一样的，但是它们的逻辑是一样的，编写完成后就可以把`Type`应用到代码中：
=== "Flask"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_unix_datetime_demo.py"

    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/flask_with_unix_datetime_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_unix_datetime_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/starlette_with_unix_datetime_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_unix_datetime_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/sanic_with_unix_datetime_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_unix_datetime_demo.py""
    --8<-- "docs_source_code/docs_source_code/introduction/how_to_use_type/tornado_with_unix_datetime_demo.py"
    ```
重新运行修改后的代码并使用调用`curl`命令后可以发现返回的时间值已经没有带时区了：
```bash
➜  ~ curl "http://127.0.0.1:8000/api/demo?timestamp=1600000000"
{"time":"2020-09-13T20:26:40"}
```
