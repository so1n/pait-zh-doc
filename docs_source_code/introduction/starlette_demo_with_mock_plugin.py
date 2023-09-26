from typing import Type

import uvicorn
from pait.app.starlette import pait
from pait.app.starlette.plugin.mock_response import MockPlugin
from pait.field import Body
from pait.model.response import JsonResponseModel
from pait.openapi.doc_route import AddDocRoute
from pydantic import BaseModel, Field
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


class DemoResponseModel(JsonResponseModel):
    class ResponseModel(BaseModel):
        uid: int = Field(example=999)
        username: str = Field()

    description: str = "demo response"
    response_data: Type[BaseModel] = ResponseModel


@pait(response_model_list=[DemoResponseModel], plugin_list=[MockPlugin.build()])
async def demo_post(  # type: ignore[empty-body]
    uid: int = Body.t(description="user id", gt=10, lt=1000),
    username: str = Body.t(description="user name", min_length=2, max_length=4),
) -> JSONResponse:
    pass


app = Starlette(routes=[Route("/api", demo_post, methods=["POST"])])
AddDocRoute(app)


if __name__ == "__main__":
    uvicorn.run(app)
