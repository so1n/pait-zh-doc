import datetime

import uvicorn
from pait import field
from pait.app.sanic import pait
from sanic import Sanic, json, response


@pait()
async def demo(timestamp: datetime.datetime = field.Query.i()) -> response.HTTPResponse:
    return json({"time": timestamp.isoformat()})


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])
uvicorn.run(app)
