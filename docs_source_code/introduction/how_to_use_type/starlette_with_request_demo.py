import uvicorn
from pait.app.starlette import pait
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route


@pait()
async def demo(req: Request) -> JSONResponse:
    return JSONResponse({"url": str(req.url), "method": req.method})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    uvicorn.run(app)
