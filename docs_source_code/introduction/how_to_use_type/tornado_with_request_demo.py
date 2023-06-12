from pait.app.tornado import pait
from tornado.httputil import HTTPServerRequest
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler


class DemoHandler(RequestHandler):
    @pait()
    def get(self, req: HTTPServerRequest) -> None:
        self.write({"url": req.full_url(), "method": req.method})


app: Application = Application(
    [
        (r"/api/demo", DemoHandler),
    ]
)
app.listen(8000)
IOLoop.instance().start()
