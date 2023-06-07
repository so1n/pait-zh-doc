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
def demo(
    demo_value: str = field.Query.i(),
    demo_value1: str = field.Query.i(not_value_exception=RuntimeError("not found data")),
) -> HTTPResponse:
    return json({"data": {"demo_value": demo_value, "demo_value1": demo_value1}})


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods={"GET"})
app.exception(Exception)(api_exception)
uvicorn.run(app)
