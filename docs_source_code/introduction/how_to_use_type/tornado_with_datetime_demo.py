import datetime

from pait import field
from pait.app.tornado import pait
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler


class DemoHandler(RequestHandler):
    @pait()
    def get(self, timestamp: datetime.datetime = field.Query.i()) -> None:
        self.write({"time": timestamp.isoformat()})


app: Application = Application(
    [
        (r"/api/demo", DemoHandler),
    ]
)
app.listen(8000)
IOLoop.instance().start()
