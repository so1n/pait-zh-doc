## 缓存插件
缓存插件能缓存除流式响应意外的响应对象，同时也能根据函数签名来自动生成缓存的Key, 所以缓存插件属于后置插件，这样才能读取到函数签名的参数。
缓存插件使用的示例代码如下：
```Python
import time

import aiofiles  # type: ignore
from redis.asyncio import Redis  # type: ignore
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from pait.app.starlette import pait
from pait.app.starlette.plugin.cache_resonse import CacheResponsePlugin
from pait.model.response import PaitTextResponseModel


@pait(
    response_model_list=[PaitTextResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10)],
)
async def demo() -> PlainTextResponse:
    return PlainTextResponse(str(time.time()))


def create_app() -> Starlette:
    app: Starlette = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
    # 延后绑定Redis实例，这样可以在不同的实例使用不同的Redis实例
    CacheResponsePlugin.set_redis_to_app(app, redis=Redis(decode_responses=True))
    return app


if __name__ == "__main__":
    import uvicorn  # type: ignore

    from pait.extra.config import apply_block_http_method_set
    from pait.g import config

    config.init_config(apply_func_list=[apply_block_http_method_set({"HEAD", "OPTIONS"})])
    uvicorn.run(create_app(), log_level="debug")
```
运行代码后然后运行`curl`命令，可以发现每次返回的数据都是一样的：
```bash
➜ curl http://127.0.0.1:8000/api/demo
1652714661.9645622
➜ curl http://127.0.0.1:8000/api/demo
1652714661.9645622
➜ curl http://127.0.0.1:8000/api/demo
1652714661.9645622
```


缓存插件的简单使用方法，目前还支持其它的参数来拓展使用，如下：

- redis: 指定插件可以使用的Redis实例，建议通过`CacheResponsePlugin.set_redis_to_app`方法指定Redis实例。
- name: 指定路由函数的缓存Key，如果为空，则以函数名为Key。
- enable_cache_name_merge_param: 如果为True，缓存的Key还会包括参数名，比如下面的一个路由函数:
    ```Python
    @pait(
        response_model_list=[PaitTextResponseModel],
        post_plugin_list=[CacheResponsePlugin.build(cache_time=10)],
    )
    async def demo(uid: str = Query.i(), name: str = Query.i()) -> PlainTextResponse:
        return PlainTextResponse(str(time.time()))
    ```
    当请求的url中携带`?uid=10086&name=so1n`时，缓存插件会认为当前的缓存Key为`demo:10086:so1n`
- include_exc: 接收一个异常的元祖，如果路由函数抛出的错误属于开发者填写的一种错误，则会缓存该异常。
- cache_time: 缓存的时间。
- timeout: 为了防止高并发场景下的缓存冲突，缓存插件里通过Reids锁来防止资源竞争。timeout代表该锁的最长持有时间。
- sleep: 当发现锁被另一个请求持有时，当前请求会休眠设置对应的时间，然后再尝试获取锁，直到获取到对应的锁或者超时。
- blocking_timeout: 指尝试获取锁的最长时间，如果为None，则会一直等待。
