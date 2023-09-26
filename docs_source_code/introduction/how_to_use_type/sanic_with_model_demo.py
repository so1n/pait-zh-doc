import uvicorn
from pait import field
from pait.app.sanic import pait
from pydantic import BaseModel, Field
from sanic import Sanic, json, response


class DemoModel(BaseModel):
    uid: str = Field(max_length=6, min_length=6, regex="^u")
    name: str = Field(min_length=4, max_length=10)
    age: int = Field(ge=0, le=100)


@pait()
async def demo(demo_model: DemoModel = field.Query.i(raw_return=True)) -> response.HTTPResponse:
    return json(demo_model.dict())


@pait()
async def demo1(demo_model: DemoModel = field.Body.i(raw_return=True)) -> response.HTTPResponse:
    return json(demo_model.dict())


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])
app.add_route(demo1, "/api/demo1", methods=["POST"])


if __name__ == "__main__":
    uvicorn.run(app)
