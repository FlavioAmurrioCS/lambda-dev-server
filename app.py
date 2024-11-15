from __future__ import annotations

from typing import Any


def handler(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG001
    return {
        "statusCode": 200,
        "body": "Hello World",
        "headers": {"Content-Type": "text/plain"},
        "isBase64Encoded": False,
    }
