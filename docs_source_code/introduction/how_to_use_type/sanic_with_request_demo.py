import uvicorn
from pait.app.sanic import pait
from sanic import Request, Sanic, json, response


@pait()
async def demo(req: Request) -> response.HTTPResponse:
    return json({"url": req.url, "method": req.method})


app = Sanic(name="demo")
app.add_route(demo, "/api/demo", methods=["GET"])
uvicorn.run(app)
