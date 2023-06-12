from uuid import uuid4

import uvicorn
from pait import field
from pait.app.sanic import pait
from pydantic import BaseModel, Field
from sanic import Sanic, json, response


class DemoModel(BaseModel):
    uid: str = Field(..., max_length=6, min_length=6, regex="^u")
    name: str = Field(..., min_length=4, max_length=10)
    age: int = Field(..., ge=0, le=100)

    request_id: str = field.Header.i(default_factory=lambda: str(uuid4()))


@pait(default_field_class=field.Query)
async def demo(demo_model: DemoModel) -> response.HTTPResponse:
    return json(demo_model.dict())


@pait(default_field_class=field.Body)
async def demo1(demo_model: DemoModel) -> response.HTTPResponse:
    return json(demo_model.dict())


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])
app.add_route(demo1, "/api/demo1", methods=["POST"])
uvicorn.run(app)
