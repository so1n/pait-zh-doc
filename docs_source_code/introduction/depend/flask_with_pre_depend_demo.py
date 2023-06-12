from flask import Flask, jsonify
from pait import field
from pait.app.flask import pait
from pait.exceptions import TipException


def api_exception(exc: Exception) -> str:
    if isinstance(exc, TipException):
        exc = exc.exc
    return jsonify({"data": str(exc)})


fake_db_dict: dict = {"u12345": "so1n"}


def get_user_by_token(token: str = field.Header.i()) -> str:
    if token not in fake_db_dict:
        raise RuntimeError(f"Can not found by token:{token}")
    return fake_db_dict[token]


@pait(pre_depend_list=[get_user_by_token])
def demo() -> dict:
    return {"msg": "success"}


app = Flask("demo")
app.add_url_rule("/api/demo", view_func=demo, methods=["GET"])
app.errorhandler(Exception)(api_exception)
app.run(port=8000)
