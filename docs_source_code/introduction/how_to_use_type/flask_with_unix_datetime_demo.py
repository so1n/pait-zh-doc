import datetime
from typing import Callable, Generator, Union

from flask import Flask, Response, jsonify
from pait import field
from pait.app.flask import pait


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


@pait()
def demo(timestamp: UnixDatetime = field.Query.i()) -> Response:
    return jsonify({"time": timestamp.isoformat()})


app = Flask("demo")
app.add_url_rule("/api/demo", "demo", demo, methods=["GET"])
app.run(port=8000)
