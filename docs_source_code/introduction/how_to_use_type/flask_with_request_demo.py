from flask import Flask, Request, Response, jsonify
from pait.app.flask import pait


@pait()
def demo(req: Request) -> Response:
    return jsonify({"url": req.url, "method": req.method})


app = Flask("demo")
app.add_url_rule("/api/demo", "demo", demo, methods=["GET"])
app.run(port=8000)