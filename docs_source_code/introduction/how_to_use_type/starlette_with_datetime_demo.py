import datetime

import uvicorn
from pait import field
from pait.app.starlette import pait
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


@pait()
async def demo(timestamp: datetime.datetime = field.Query.i()) -> JSONResponse:
    return JSONResponse({"time": timestamp.isoformat()})


app = Starlette(
    routes=[
        Route("/api/demo", demo, methods=["GET"]),
    ]
)
uvicorn.run(app)
