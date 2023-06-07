from typing import List

import uvicorn  # type: ignore
from flask import Flask, jsonify
from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException
from pydantic import ValidationError


def api_exception(exc: Exception) -> str:
    if isinstance(exc, TipException):
        exc = exc.exc
    if isinstance(exc, ValidationError):
        return jsonify({"data": exc.errors()})
    return jsonify({"data": str(exc)})


@pait()
def demo(
    demo_value: List[int] = field.MultiQuery.i(min_items=1, max_items=2),
) -> dict:
    return {"data": demo_value}


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)
app.run(port=8000)
