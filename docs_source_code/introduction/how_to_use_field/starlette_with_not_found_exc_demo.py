import uvicorn
from pait import field
from pait.app.starlette import pait
from pait.exceptions import TipException
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return JSONResponse({"data": exc.errors()})
    return JSONResponse({"data": str(exc)})


@pait()
async def demo(
    demo_value: str = field.Query.i(),
    demo_value1: str = field.Query.i(not_value_exception=RuntimeError("not found data")),
) -> JSONResponse:
    return JSONResponse({"data": {"demo_value": demo_value, "demo_value1": demo_value1}})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)
app.add_exception_handler(Exception, api_exception)
uvicorn.run(app)
