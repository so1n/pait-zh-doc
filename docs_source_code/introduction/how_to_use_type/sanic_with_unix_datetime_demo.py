import datetime
from typing import Callable, Generator, Union

import uvicorn
from pait import field
from pait.app.sanic import pait
from sanic import Sanic, json, response


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
async def demo(timestamp: UnixDatetime = field.Query.i()) -> response.HTTPResponse:
    return json({"time": timestamp.isoformat()})


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])


if __name__ == "__main__":
    uvicorn.run(app)
