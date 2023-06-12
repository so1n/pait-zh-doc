from typing import List

import uvicorn  # type: ignore
from pait import exceptions, field
from pait.app.sanic import pait
from pait.param_handle import AsyncParamHandler
from pydantic import ValidationError
from sanic import HTTPResponse, Request, Sanic, json


class NotTipAsyncParamHandler(AsyncParamHandler):
    tip_exception_class = None


async def api_exception(request: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, exceptions.PaitBaseParamException):
        return json({"code": -1, "msg": f"error param:{exc.param}, {exc.msg}"})
    elif isinstance(exc, ValidationError):
        error_param_list: List = []
        for i in exc.errors():
            error_param_list.extend(i["loc"])
        return json({"code": -1, "msg": f"check error param: {error_param_list}"})
    elif isinstance(exc, exceptions.PaitBaseException):
        return json({"code": -1, "msg": str(exc)})

    return json({"code": -1, "msg": str(exc)})


@pait(param_handler_plugin=NotTipAsyncParamHandler)
async def demo(demo_value: int = field.Query.i()) -> HTTPResponse:
    return json({"code": 0, "msg": "", "data": demo_value})


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods={"GET"})
app.exception(Exception)(api_exception)

uvicorn.run(app)