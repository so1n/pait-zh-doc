import uvicorn
from pait import field
from pait.app.sanic import pait
from sanic import HTTPResponse, Sanic


@pait()
async def demo(content_type: str = field.Header.t(alias="Content-Type")) -> HTTPResponse:
    return HTTPResponse(content_type)


app = Sanic("demo")
app.add_route(demo, "/api/demo", methods={"GET"})
uvicorn.run(app)
