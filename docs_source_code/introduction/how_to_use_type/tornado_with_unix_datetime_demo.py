import datetime
from typing import Callable, Generator, Union

from pait import field
from pait.app.tornado import pait
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler


# 这里只展示Pydantic V1的UnixDatetime
class UnixDatetime(datetime.datetime):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]:
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[int, str]) -> datetime.datetime:
        if isinstance(v, str):
            v = int(v)
        return datetime.datetime.fromtimestamp(v)


class DemoHandler(RequestHandler):
    @pait()
    def get(self, timestamp: UnixDatetime = field.Query.i()) -> None:
        self.write({"time": timestamp.isoformat()})


app: Application = Application(
    [
        (r"/api/demo", DemoHandler),
    ]
)
app.listen(8000)
IOLoop.instance().start()
