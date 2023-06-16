from typing import List

import uvicorn
from pait.app.sanic import pait
from pait.field import Query
from pait.model.response import BaseResponseModel
from pait.openapi.doc_route import AddDocRoute
from pydantic import BaseModel, Field
from sanic.app import Sanic
from sanic.response import HTTPResponse, json


class MyJsonResponseModel(BaseResponseModel):
    class ResponseModel(BaseModel):
        class UserModel(BaseModel):
            name: str = Field(..., example="so1n")
            uid: int = Query.t(description="user id", gt=10, lt=1000)
            age: int = Field(..., gt=0)

        code: int = Field(..., ge=0)
        msg: str = Field(...)
        data: List[UserModel]

    class HeaderModel(BaseModel):
        x_token: str = Field(..., alias="X-Token")
        content_type: str = Field(..., alias="Content-Type")

    response_data = ResponseModel
    description = "demo json response"
    media_type = "application/json; charset=utf-8"
    header = HeaderModel
    status_code = (200, 201, 404)


@pait(response_model_list=[MyJsonResponseModel])
async def demo(
    uid: int = Query.t(description="user id", gt=10, lt=1000),
    age: int = Query.t(description="age", gt=0),
    username: str = Query.t(description="user name", min_length=2, max_length=4),
) -> HTTPResponse:
    resp = json({"code": 0, "msg": "", "data": [{"name": username, "uid": uid, "age": age}]})

    resp.headers.add("X-Token", "12345")
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])
AddDocRoute(app)
uvicorn.run(app)
