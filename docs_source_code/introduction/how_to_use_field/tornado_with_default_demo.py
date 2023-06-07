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
        self.write(str(exc))
        self.finish()


class DemoHandler(_Handler):
    @pait()
    def get(self, demo_value: str = field.Query.t(default="123")) -> None:
        self.write(demo_value)


class Demo1Handler(_Handler):
    @pait()
    def get(self, demo_value: str = field.Query.t()) -> None:
        self.write(demo_value)


app: Application = Application([(r"/api/demo", DemoHandler), (r"/api/demo1", Demo1Handler)])
AddDocRoute(app)
app.listen(8000)
IOLoop.instance().start()