from typing import Type

import uvicorn
from pait.app.sanic import pait
from pait.field import Body
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute
from pydantic import BaseModel, Field
from sanic.app import Sanic
from sanic.response import HTTPResponse, json


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field()
        user_name: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel])
async def demo_post(
    uid: int = Body.t(description="user id", gt=10, lt=1000),
    username: str = Body.t(description="user name", min_length=2, max_length=4),
) -> HTTPResponse:
    return json({"uid": uid, "user_name": username})


app = Sanic(name="demo")
app.add_route(demo_post, "/api", methods=["POST"])
AddDocRoute(app)


if __name__ == "__main__":
    uvicorn.run(app)
