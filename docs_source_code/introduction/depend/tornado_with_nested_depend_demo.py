from pait import field
from pait.app.tornado import pait
from pait.exceptions import TipException
from pait.openapi.doc_route import AddDocRoute
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler


class _Handler(RequestHandler):
    def _handle_request_exception(self, exc: BaseException) -> None:
        if isinstance(exc, TipException):
            exc = exc.exc

        self.write({"data": str(exc)})
        self.finish()


fake_db_dict: dict = {"u12345": "so1n"}


def check_token(token: str = field.Header.i()) -> str:
    if len(token) != 6 and token[0] != "u":
        raise RuntimeError("Illegal Token")
    return token


async def get_user_by_token(token: str = field.Depends.i(check_token)) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


class DemoHandler(_Handler):
    @pait()
    async def get(self, token: str = field.Depends.i(get_user_by_token)) -> None:
        self.write({"user": token})


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)
app.listen(8000)
IOLoop.instance().start()