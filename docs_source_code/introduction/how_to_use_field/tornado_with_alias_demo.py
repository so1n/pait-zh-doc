from pait import field
from pait.app.tornado import pait
from pait.openapi.doc_route import AddDocRoute
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler


class DemoHandler(RequestHandler):
    @pait()
    async def get(self, content_type: str = field.Header.t(alias="Content-Type")) -> None:
        self.write(content_type)


app: Application = Application([(r"/api/demo", DemoHandler)])
AddDocRoute(app)
app.listen(8000)
IOLoop.instance().start()
