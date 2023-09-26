import uvicorn
from pait import field
from pait.app.starlette import pait
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route


@pait()
async def demo(content_type: str = field.Header.t(alias="Content-Type")) -> PlainTextResponse:
    return PlainTextResponse(content_type)


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    uvicorn.run(app)
