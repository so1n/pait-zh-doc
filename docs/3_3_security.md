OpenAPI通过`security`提供了对HTTP基本身份验证的描述，但是不同的Web框架对HTTP基本身份验证的实现方式不同，
因此`Pait`通过`Depends`对OpenAPI的security提供了简单支持(`api key`, `http`, `oauth2`)，从而简化Security在不同的Web框架使用。

!!! note

    JWT等高级身份验证方法将会在未来通过拓展包提供支持。

## 1.APIKey
`API Key`是Security中最简单的方法，也正因为简单，它的使用场景也是最多的。`Pait`提供`APIKey`类来支持`API Key`的使用，使用方法如下：


=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_apikey_demo.py" hl_lines="7-24 27-39"

    --8<-- "docs_source_code/openapi/security/flask_with_apikey_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_apikey_demo.py" hl_lines="10-27 30-42"
    --8<-- "docs_source_code/openapi/security/starlette_with_apikey_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_apikey_demo.py" hl_lines="8-25 28-40"
    --8<-- "docs_source_code/openapi/security/sanic_with_apikey_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_apikey_demo.py" hl_lines="8-25 28-43"
    --8<-- "docs_source_code/openapi/security/tornado_with_apikey_demo.py"
    ```

代码中第一段高亮代码是针对不同的`APIKey`字段进行初始化，它们使用的参数略有不同，具体的参数说明如下：

| 参数    | 描述                                                                                                               |
|-------|------------------------------------------------------------------------------------------------------------------|
| name  | `APIKey`字段的名字                                                                                                    |
| field | `APIKey`字段对应`Pait`中的Field类，`API Key`只支持Query，Header和Cookie的参数，所以只允许使用`field.Query`，`field.Header`，`field.Cookie` |
| verify_api_key_callable | 接受一个校验`APIKey`的函数，`Pait`从请求体中提取`APIKey`值后会传递给函数，交由函数处理，如果函数返回`True`则代表校验通过，反之则校验不通过。                             |
| security_name | 指定Security的名称，不同作用的`APIKey`的名称必须是不同的，默认值为APIKey的类名。                                                              |

!!! note

    为了能在OpenAPI工具中正常使用APIKey，传递的`Field`在初始化时必须指定`openapi_include`为False。

第二段高亮的代码则是通过`Depend`连接了APIKey和路由函数，其中`Depend`的参数为`APIKey`的实例。

当路由函数收到请求时`Pait`会自动从请求体中提取`APIKey`的值，然后交由`APIKey`的`verify_api_key_callable`函数进行校验，如果校验通过则把值通过`Depend`传递给路由函数执行，反之则返回`401`。

在运行代码后，运行如下命令，可以看到`APIKey`的执行效果：
```bash
# Success Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-cookie-key' \
  -H 'accept: */*' \
  -H 'Cookie: token=token'
{"code":0,"msg":"","data":"token"}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-header-key' \
  -H 'accept: */*' \
  -H 'token: token'
{"code":0,"msg":"","data":"token"}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-query-key?token=token' \
  -H 'accept: */*'
{"code":0,"msg":"","data":"token"}

# Fail Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-cookie-key' \
  -H 'accept: */*' \
  -H 'Cookie: token='
Not authenticated

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-header-key' \
  -H 'accept: */*' \
  -H 'token: '
Not authenticated

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/api-query-key?token=' \
  -H 'accept: */*'
Not authenticated
```

### 1.1.APIKey与Links的结合
大部分使用APIKey的接口所需要的参数(如Token)都是通过其他接口获取的，此时可以通过使用`Field`中的`Links`来描述该接口与其他接口之间的关系，比如下面的这个场景，它的Token是通过登陆接口中获取的：

=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_apikey_and_link_demo.py" hl_lines="14-32 37"

    --8<-- "docs_source_code/openapi/security/flask_with_apikey_and_link_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_apikey_and_link_demo.py" hl_lines="17-39 44"
    --8<-- "docs_source_code/openapi/security/starlette_with_apikey_and_link_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_apikey_and_link_demo.py" hl_lines="15-35 40"
    --8<-- "docs_source_code/openapi/security/sanic_with_apikey_and_link_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_apikey_and_link_demo.py" hl_lines="15-38 43"
    --8<-- "docs_source_code/openapi/security/tornado_with_apikey_and_link_demo.py"
    ```

第一段高亮代码来自于[Field-Links](/3_1_openapi/#41links)，而第二段高亮代码中的`Query`设置了`links`属性为`link_login_token_model`，这样一来`Pait`生成OpenAPI时会把`login_route`与`api_key_query_route`通过Link绑定在一起。

!!! note

    - Links的使用方法详见[Field-Links](/3_1_openapi/#41links)
    - 使用`openapi_include=False`会导致`Swggaer`无法展示Link的数据


## 2.HTTP
HTTP基本身份校验分为两种，一种是`HTTPBasic`，另一种是`HTTPBearer`或`HTTPDIgest`，
两者的区别在于`HTTPBasic`需要在请求头中传递`username`和`password`进行校验，如果校验成功则代表验证成功，
如果校验错误会返回`401`响应，浏览器在收到`401`响应后会弹出一个窗口让用户输入`username`和`password`，
而`HTTPBearer`或`HTTPDIgest`则只需要在请求头中按要求传递`token`。

`Pait`为HTTP基本校验的三个方式分别封装了`HTTPBasic`，`HTTPBearer`和`HTTPDigest`三个类，
同样的，它们也需要通过`Depend`与路由函数绑定，使用方法如下：


=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_http_demo.py"

    --8<-- "docs_source_code/openapi/security/flask_with_http_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_http_demo.py"
    --8<-- "docs_source_code/openapi/security/starlette_with_http_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_http_demo.py"
    --8<-- "docs_source_code/openapi/security/sanic_with_http_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_http_demo.py"
    --8<-- "docs_source_code/openapi/security/tornado_with_http_demo.py"
    ```

代码分成三部分，它们都是先初始化对应的基本身份验证类，然后通过`Depend`与路由函数绑定，最后在路由函数中使用`Depend`获取身份验证类的实例。

不过`HTTPBasic`的使用方法与其他两个略有不同，首先`HTTPBasic`的初始化参数就略有不同，如下:

|参数|描述|
|---|---|
|security_model|关于HTTPBasic的OpenAPI描述Model，默认情况下已经提供了一个通用的HTTPBasicModel，如有定制需求请访问OpenAPI的[securitySchemeObject](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#securitySchemeObject)了解|
|security_name|指定Security的名称，不同作用的基本身份校验实例的名称必须是不同的，默认值为A类名。|
|header_field|`Pait`的Header Field实例|
|realm|HTTP基本身份校验的realm参数|

其次，它不会直接用于路由函数中，而是存在于`get_user_name`函数中，`get_user_name`函数负责进行身份校验，如果身份校验成功则返回用户名到路由函数中，否则返回`401`响应。

而`HTTPBearer`和`HTTPDigest`使用方法与`APIKey`类似，需要按要求初始化，并通过`Depend`与路由函数绑定即可，它们的参数说明如下:

|参数| 描述                                                                                                                                                                                             |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|security_model| 关于基本身份校验的OpenAPI描述Model，默认情况下已经提供了一个通用的HTTPBasicModel，如有定制需求请访问OpenAPI的[securitySchemeObject](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#securitySchemeObject)了解 |
|security_name| 指定Security的名称，不同作用的基本身份校验实例的名称必须是不同的，默认值为A类名。                                                                                                                                                  |
|header_field| `Pait`的Header Field实例                                                                                                                                                                          |
|is_raise| 当设置为`True`时，`Pait`在解析失败后抛出标准的错误，为`False`时在解析失败后悔返回`None`， 默认值为`True`                                                                                                                             |
| verify_callable | 接受一个校验函数，`Pait`从请求体中提取值后会传递给函数，交由函数处理，如果函数返回`True`则代表校验通过，反之则校验不通过。                             |

在运行代码后，运行如下命令，可以看到它们的执行效果如下：
```bash
# Success Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-basic-credentials' \
  -H 'accept: */*' \
  -H 'Authorization: Basic c28xbjpzbzFu'

{"code":0,"data":"so1n","msg":""}

➜   curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-bearer' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer http'

{"code":0,"data":"http","msg":""}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-digest' \
  -H 'accept: */*' \
  -H 'Authorization: Digest http'

{"code":0,"data":"http","msg":""}

# Fail Result
➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-digest' \
  -H 'accept: */*' \
  -H 'Authorization: Digest '

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>403 Forbidden</title>
<h1>Forbidden</h1>
<p>Not authenticated</p>

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/user-name-by-http-bearer' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer '

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>403 Forbidden</title>
<h1>Forbidden</h1>
<p>Not authenticated</p>
```

!!! note

    `HTTPDigest`类只提供简单的`HTTODigest`身份校验支持，在使用时需要根据自己的业务逻辑进行修改。

## 3.Oauth2
OAuth 2.0是一种授权协议，为 API 客户端提供对 Web 服务器上的用户数据的有限访问权限，它除了提供身份校验的功能外，还支持权限校验。
`Pait`的`Oauth2`使用方法如下：
=== "Flask"

    ```py linenums="1" title="docs_source_code/openapi/security/flask_with_oauth2_demo.py"

    --8<-- "docs_source_code/openapi/security/flask_with_oauth2_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/openapi/security/starlette_with_oauth2_demo.py"
    --8<-- "docs_source_code/openapi/security/starlette_with_oauth2_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/openapi/security/sanic_with_oauth2_demo.py"
    --8<-- "docs_source_code/openapi/security/sanic_with_oauth2_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/openapi/security/tornado_with_oauth2_demo.py"
    --8<-- "docs_source_code/openapi/security/tornado_with_oauth2_demo.py"
    ```

代码中第一部分是创建一个关于用户数据的Model--`User`，和一个`key`为token，`value`为`User`的`temp_token_dict`用于模拟数据库存储。

第二部分是编写一个标准的登陆接口，该接口接受的参数类型是`OAuth2PasswordRequestFrom`，这是`Pait`针对`Oauth2`的登陆参数封装的，它的源码如下，
```Python
from pydantic import BaseModel
from pait.field import Form

class BaseOAuth2PasswordRequestFrom(BaseModel):
    username: str = Form()
    password: str = Form()
    scope: ScopeType = Form("")
    client_id: Optional[str] = Form(None)
    client_secret: Optional[str] = Form(None)


class OAuth2PasswordRequestFrom(BaseOAuth2PasswordRequestFrom):
    grant_type: Optional[str] = Form(None, regex="password")
```
可以看到`OAuth2PasswordRequestFrom`继承了`BaseModel`，并且所有参数的`Field`都使用`Form`，这意味着它的参数是从请求体中的表单获取数据。

登陆接口在接收`form_data`参数后会进行校验，这里只是简单的校验了用户名和密码是否正确，如果错误则返回400响应，正确则生成一个`token`，并将`token`和`User`存储到`temp_token_dict`中，最后通过`oauth2.OAuth2PasswordBearerJsonRespModel`返回Oauth2标准的响应格式。

第三部分先是通过`oauth2.OAuth2PasswordBearer`创建`oauth2_pb`实例，其中`route`参数为登陆路由函数，`oauth2_pb`会在路由函数注册到Web框架时把路由函数的URL写入到`tokenUrl`属性中，而`scopes`则是对权限的描述，这里创建了`oauth2_pb`和`user-name`两个`scope`。

然后是编写获取用户的函数--`get_current_user`， `get_current_user`函数会通过Token获取到当前使用接口的用户，然后再通过`is_allow`方法判断当前用户是否有权限访问该接口，如果没有则返回403响应，如果有则返回`User` Model。
此外，该函数接受的值为`oauth2.OAuth2PasswordBearer`的代理类，这个代理类已经明确了只允许了哪些权限，同时
该类有两个功能，一个是通过`Depend`把请求的参数传递给函数，另外一个是提供`is_allow`方法用于判断用户是否有权限访问该接口。


第四部分则是路由函数，它们使用了第三部分创建的`get_current_user`，其中传递的参数`oauth2_pb.get_depend(["user-name"])`的作用是通过`oauth2.OAuth2PasswordBearer`创建了一个代理实例，其中`user-name`表示当前的路由函数只拥有`user-name`一个权限。


在运行代码后，运行如下命令，可以看到它们的执行效果如下：
```bash
➜  curl 'http://127.0.0.1:8000/api/oauth2-login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'grant_type=password&scope=user-info&username=so1n&password=so1n' \

{"access_token":"pomeG4jCDh","token_type":"bearer"}

➜  curl 'http://127.0.0.1:8000/api/oauth2-login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'grant_type=password&scope=user-name&username=so1n1&password=so1n1' \

{"access_token":"G8ckqKGkDO","token_type":"bearer"}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-info' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer pomeG4jCDh'

{"code":0,"data":{"age":23,"name":"so1n","scopes":["user-info"],"sex":"M","uid":"123"},"msg":""}

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-info' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer G8ckqKGkDO'

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Not authenticated</p>

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-name' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer pomeG4jCDh'

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<title>401 Unauthorized</title>
<h1>Unauthorized</h1>
<p>Not authenticated</p>

➜  curl -X 'GET' \
  'http://127.0.0.1:8000/api/oauth2-user-name' \
  -H 'accept: */*' \
  -H 'Authorization: Bearer G8ckqKGkDO'
{"code":0,"data":"so1n1","msg":""}

```
通过响应结果可以看到权限为`user-info`的用户只能访问`/api/oauth2-user-info`接口，而权限为`user-name`的用户只能访问`/api/oauth2-user-name`接口。

!!! note

    当前版本尚未支持`refreshUrl`
