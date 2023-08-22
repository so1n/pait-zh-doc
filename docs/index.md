# 介绍
`Pait`是一个轻量级的Python API开发工具，拥有参数类型检查, 类型转换，提供文档输出等功能，适合用于后端的接口开发。
此外，它还被设计成可以用于多个Python的Web应用开发框架(目前适配了`Flask`, `Starlette`, `Sanic`, `Tornado`)，基于`Pait`可以无需考虑Web框架的差异性，快速编写功能，比如[grpc-gateway](https://github.com/python-pai/grpc-gateway)。

> `Pait`设计灵感见文章[《给python接口加上一层类型检》](https://so1n.me/2019/04/15/%E7%BB%99python%E6%8E%A5%E5%8F%A3%E5%8A%A0%E4%B8%8A%E4%B8%80%E5%B1%82%E7%B1%BB%E5%9E%8B%E6%A3%80/) 。

## 功能
 - [x] 融入Type Hints生态，使用者可以快速方便的编写安全的代码
 - [x] 参数的自动校验和转化(参数校验依赖于`Pydantic`，目前支持`Pydantic`V1和V2版本)
 - [x] 参数关系依赖校验
 - [x] 自动生成openapi文件
 - [x] 支持swagger,redoc路由
 - [x] 支持mock响应
 - [x] TestClient支持, 支持测试用例的响应结果校验
 - [x] 支持插件拓展
 - [x] 支持gRPC GateWay路由
 - [ ] 自动API测试
 - [ ] WebSocket支持

## 安装
!!! note
    仅支持Python3.7+版本

```bash
pip install pait --pre
```

## 使用
### 参数校验与文档生成
`Pait`的主要功能是提供参数校验和文档生成，使用方法非常简单，如下：
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

其中第一段高亮代码中的`@pait`会装饰路由函数， 在运行时`@pait`会自动从路由函数提取接口的请求参数数据，但是它没办法了解到路由函数的响应内容是什么，
所以需要通过`response_model_list`参数声明了路由函数的响应对象是`DemoResponseModel`，
而`DemoResponseModel`对象的`description`和`response_data`分别用于描述路由函数的响应对象文档和响应对象的结构类型。

第二段高亮代码中路由函数的参数是一种符合`Pait`规范的参数，
在初始化时`@pait`会主动去解析路由函数并根据路由函数的函数签名生成依赖注入规则，
当请求命中路由函数时，`Pait`会根据依赖注入规则从`Request`对象获取到对应的值并将其注入到路由函数中。

最后的高亮代码主要的工作是向`app`实例注册`OpenAPI`路由，为Web框架提供接口API文档功能。

在一切准备就绪后开始运行代码，并在浏览器访问: [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger) 就可以看到SwaggerUI的页面，目前这个页面显示了两组接口：
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1648292884021Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-Swagger%E9%A6%96%E9%A1%B5.png)

其中一组是`Pait doc`自带的`OpenAPI`接口，另外一组是`default`，里面有刚创建的`/api`接口，点开`/api`接口后会弹出该接口的详情：
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1648292937018Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-api%E6%8E%A5%E5%8F%A3.png)

详情里的数据是由`Pait`通过读取路由的函数签名以及传入的`DemoResponseModel`对象生成的， 接着可以点击`try it out`按钮，然后输入参数并点击`Excute`，就可以看到`curl`命令生成结果以及服务器响应结果:
![](https://cdn.jsdelivr.net/gh/so1n/so1n_blog_photo@master/blog_photo/1648292980016Pait%20doc-%E9%A6%96%E9%A1%B5%E7%A4%BA%E4%BE%8B%E6%8E%A5%E5%8F%A3-Swagger%E8%AF%B7%E6%B1%82.png)


!!! note
    想要了解更多？ 马上进入[类型转换与参数校验](/1_1_introduction/)章节


### 插件
`Pait`除了参数校验和`OpenAPI`功能外，还可以通过插件系统拓展功能，比如Mock响应功能，它能根据ResponseModel来自动返回数据，即使这个路由没有数据返回，比如下面的代码：
=== "Flask"

    ```py linenums="1" title="docs_source_code/introduction/flask_demo_with_mock_plugin.py" hl_lines="14 21"

    --8<-- "docs_source_code/introduction/flask_demo_with_mock_plugin.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/introduction/starlette_demo_with_mock_plugin.py" hl_lines="17 24"
    --8<-- "docs_source_code/introduction/starlette_demo_with_mock_plugin.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/introduction/sanic_demo_with_mock_plugin.py" hl_lines="16 23"
    --8<-- "docs_source_code/introduction/sanic_demo_with_mock_plugin.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/introduction/tornado_demo_with_mock_plugin.py" hl_lines="15 23"
    --8<-- "docs_source_code/introduction/tornado_demo_with_mock_plugin.py"
    ```

该代码是根据`参数校验与文档生成`的代码进行更改，它移除了路由函数的返回响应功能，同时引入了高亮部分的代码， 其中`DemoResponseModel`中的`uid: int = Field(example=999)`指定了响应结构中uid的example值为999， 而`@pait`添加了一个名为`MockPlugin`的插件，他可以根据`response_model_list`生成一个mock响应。

在一切准备就绪后开始运行代码，并重新点击`Swagger`页面的`Excute`按钮或者在终端运行`Swagger`页面生成的`curl`命令:
```bash
➜  ~ curl -X 'POST' \
  'http://127.0.0.1:8000/api' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "uid": 666,
  "user_name": "so1n"
}'
```
无论在`Swagger`页面或者终端中都可以看到如下输出：
```bash
{"uid":999,"username":""}
```
通过返回结果可以看到，路由函数虽然没有执行任何操作，但是该接口仍然可以返回响应。这个响应结果是Mock插件自动生成的，响应结果中`uid`的值是999，与响应模型中`uid: int = Field(example=999)`设定的值一致，而`username`由于没有设定`example`值，所以响应结果中它的值是默认的空字符串。


!!! note
    除了`MockPlugin`插件外，`Pait`还有其它的插件和功能，将在后续的[文档](/5_1_introduction/)中详细的进行介绍。

## 性能
`Pait`的主要目的是提供一个开发者可以快速开发API接口的工具，首要目标是提升开发速度，次要目标才是性能提升，
它的运行原理决定了它与其他带有参数校验框架一样都需要对参数进行校验，所以会带来一定的性能损耗，不过`Python`采用`Python`的标准库`inspect`实现函数签名提取，
并基于`Pydantic`实现参数校验和类型转换，同时还运用了很多预加载设计，所以`Pait`的运行时性能并不会受到太多影响。
不过`Pait`还在成长中， 还有许多需要优化的地方，欢迎通过[issues](https://github.com/so1n/pait/issues)反馈`Pait`相关问题并一起优化。

## 使用示例
每个`Pait`支持的Web框架都有完善的代码示例， 可以通过访问示例代码了解最佳实践:

- [flask example](https://github.com/so1n/pait/blob/master/example/param_verify/flask_example.py)

- [sanic example](https://github.com/so1n/pait/blob/master/example/param_verify/sanic_example.py)

- [starlette example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py)

- [tornado example](https://github.com/so1n/pait/blob/master/example/param_verify/starlette_example.py)
