import uvicorn  # type: ignore
from pait import field
from pait.app.starlette import pait
from pait.exceptions import TipException
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


async def api_exception(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, TipException):
        exc = exc.exc
    return JSONResponse({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


async def get_user_by_token(token: str = field.Header.i()) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


@pait(pre_depend_list=[get_user_by_token])
async def demo() -> JSONResponse:
    return JSONResponse({"msg": "success"})


app = Starlette(routes=[Route("/api/demo", demo, methods=["GET"])])
app.add_exception_handler(Exception, api_exception)


uvicorn.run(app)