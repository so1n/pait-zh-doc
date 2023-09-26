缓存插件能根据不同的请求参数来缓存除流式响应以外的任意响应对象。它的使用方法如下:
=== "Flask"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/flask_with_cache_plugin_demo.py" hl_lines="16 21 25"

    --8<-- "docs_source_code/plugin/cache_plugin/flask_with_cache_plugin_demo.py"
    ```

=== "Starlette"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/starlette_with_cache_plugin_demo.py" hl_lines="20 25 29"
    --8<-- "docs_source_code/plugin/cache_plugin/starlette_with_cache_plugin_demo.py"
    ```

=== "Sanic"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/sanic_with_cache_plugin_demo.py" hl_lines="18 23 27"
    --8<-- "docs_source_code/plugin/cache_plugin/sanic_with_cache_plugin_demo.py"
    ```

=== "Tornado"

    ```py linenums="1" title="docs_source_code/plugin/cache_plugin/tornado_with_cache_plugin_demo.py" hl_lines="19 25 29"
    --8<-- "docs_source_code/plugin/cache_plugin/tornado_with_cache_plugin_demo.py"
    ```
代码中的路由函数使用了`CachePlugin`，声明了缓存时间为10秒，且缓存名采纳了请求参数的功能。
同时，路由函数中只有`key1`参数使用了`CacheRespExtraParam`拓展参数，这样一来`CachePlugin`只会采纳使用了`CacheRespExtraParam`的参数，而不是所有参数。

在运行代码后，运行`curl`命令，可以发现`key1`参数一样时，返回的内容是一致的：
```bash
➜ curl http://127.0.0.1:8000/api/demo\?key1\=1\&key2\=1
1695627610.021101
➜ curl http://127.0.0.1:8000/api/demo\?key1\=1\&key2\=1
1695627610.021101
➜ curl http://127.0.0.1:8000/api/demo\?key1\=2\&key2\=1
1695627613.0265439
```


通过示例代码可以看到，缓存插件的简单使用方法，目前还支持其它的参数来拓展它的功能，如下：

- redis: 指定缓存插件可以使用的Redis实例，建议通过`CacheResponsePlugin.set_redis_to_app`方法指定Redis实例。
- name: 指定路由函数的缓存Key，如果该值为空，则缓存Key的默认值为路由函数名。
- enable_cache_name_merge_param: 如果为True，缓存的Key还会包括所有参数值，比如下面的一个路由函数:
    ```Python
    @pait(post_plugin_list=[CacheResponsePlugin.build(cache_time=10)])
    async def demo(uid: str = Query.i(), name: str = Query.i()) -> None:
        pass
    ```
    当请求的url中携带`?uid=10086&name=so1n`时，缓存插件会认为当前的缓存Key为`demo:10086:so1n`。
    但是如果有一个参数使用了`CacheRespExtraParam`拓展参数，那么缓存的Key只会包括使用了`CacheRespExtraParam`拓展参数的参数值，比如下面的路由函数:
    ```Python
    @pait(post_plugin_list=[CacheResponsePlugin.build(cache_time=10)])
    async def demo(uid: str = Query.i(extra_param_list=[CacheRespExtraParam()]), name: str = Query.i()) -> None:
        pass
    ```
    当请求的url中携带`?uid=10086&name=so1n`时，缓存插件会认为当前的缓存Key为`demo:10086`。
- include_exc: 接收一个可以缓存异常的元祖，如果路由函数抛出的错误属于元祖中的一种错误，则会缓存该异常，否则会抛出异常。
- cache_time: 缓存的时间，单位秒。
- timeout: 为了防止高并发场景下的缓存冲突，缓存插件里通过`Reids`锁来防止资源竞争。timeout代表该锁的最长持有时间。
- sleep: 当发现锁被另一个请求持有时，当前请求会休眠设置对应的时间，然后再尝试获取锁，直到获取到对应的锁或者超时。
- blocking_timeout: 指尝试获取锁的最长时间，如果为None，则会一直等待。
