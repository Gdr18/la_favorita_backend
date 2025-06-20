from flask import jsonify, Response
from typing import Union, Literal
import json


def success_json_response(
    resource: str,
    action: Literal[
        "añadido",
        "añadida",
        "actualizado",
        "actualizada",
        "eliminado",
        "eliminada",
        "realizado",
        "realizada",
        "confirmado",
        "confirmada",
        "reenviado",
        "reenviada",
    ],
    status_code: int = 200,
) -> tuple[Response, int]:
    return (
        jsonify(msg=f"{resource.capitalize()} {action} de forma satisfactoria"),
        status_code,
    )


def db_json_response(response: Union[list, dict]) -> tuple[Response, int]:
    return Response(json.dumps(response)), 200
