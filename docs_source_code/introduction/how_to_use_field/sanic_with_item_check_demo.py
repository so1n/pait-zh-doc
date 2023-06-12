from typing import List

import uvicorn
from pait import field
from pait.app.sanic import pait
from pait.exceptions import TipException
from pydantic import ValidationError
from sanic import HTTPResponse, Request, Sanic, json


async def api_exception(request: Request, exc: Exception) -> HTTPResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return json({"data": exc.errors()})
    return json({"data": str(exc)})


@pait()
async def demo(demo_value: List[int] = field.MultiQuery.i(min_items=1, max_items=2)) -> HTTPResponse:
    return json({"data": demo_value})


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods={"GET"})
app.exception(Exception)(api_exception)
uvicorn.run(app)
