import time

from pait.app.sanic import pait
from pait.app.sanic.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.field import Query
from pait.model.response import HtmlResponseModel
from redis.asyncio import Redis
from sanic import Sanic, response


@pait(
    response_model_list=[HtmlResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10, enable_cache_name_merge_param=True)],
)
async def demo(
    key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()
) -> response.HTTPResponse:
    return response.HTTPResponse(str(time.time()), 200)


app = Sanic("demo")
CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
app.add_route(demo, "/api/demo", methods=["GET"])


if __name__ == "__main__":
    app.run(port=8000)
