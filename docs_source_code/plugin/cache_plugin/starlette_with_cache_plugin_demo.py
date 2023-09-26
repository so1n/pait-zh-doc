import time

import uvicorn
from pait.app.starlette import pait
from pait.app.starlette.plugin.cache_response import CacheRespExtraParam, CacheResponsePlugin
from pait.field import Query
from pait.model.response import HtmlResponseModel
from redis.asyncio import Redis
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse


@pait(
    response_model_list=[HtmlResponseModel],
    post_plugin_list=[CacheResponsePlugin.build(cache_time=10, enable_cache_name_merge_param=True)],
)
async def demo(
    key1: str = Query.i(extra_param_list=[CacheRespExtraParam()]), key2: str = Query.i()
) -> PlainTextResponse:
    return PlainTextResponse(str(time.time()), 200)


app = Starlette()
CacheResponsePlugin.set_redis_to_app(app, Redis(decode_responses=True))
app.add_route("/api/demo", demo, methods=["GET"])


if __name__ == "__main__":
    uvicorn.run(app)
