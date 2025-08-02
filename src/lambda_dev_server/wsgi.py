from __future__ import annotations

import base64
import gzip
import json
import logging
from typing import TYPE_CHECKING
from typing import NamedTuple

from lambda_dev_server.simple_server import SimpleServer

if TYPE_CHECKING:
    from typing import Callable

    from lambda_dev_server._types import LambdaContextLike
    from lambda_dev_server._types import LambdaHttpEvent
    from lambda_dev_server._types import LambdaHttpResponse
    from lambda_dev_server.simple_server import SimpleRequestEvent
    from lambda_dev_server.simple_server import SimpleResponseEvent

logger = logging.getLogger(__name__)


class LambdaContextTuple(NamedTuple):
    aws_request_id: str = "aws_request_id"
    function_name: str = "function_name"
    memory_limit_in_mb: str = "memory_limit_in_mb"
    invoked_function_arn: str = "invoked_function_arn"


class SimpleLambdaHandler(NamedTuple):
    handler: Callable[[LambdaHttpEvent, LambdaContextLike], LambdaHttpResponse]

    def handle(self, /, event: SimpleRequestEvent) -> SimpleResponseEvent:
        lambda_event: LambdaHttpEvent = {
            "httpMethod": event["method"],
            "path": event["url"],
            "body": event["content"].decode("utf-8"),
            "isBase64Encoded": False,
            "headers": event["headers"],
            "queryStringParameters": {k: v[-1] for k, v in event["params"].items()},
            "multiValueQueryStringParameters": event["params"],
            "resource": event["url"],
            "requestContext": {"path": event["url"]},
        }
        context = LambdaContextTuple()
        logger.info("Lambda event: %s", json.dumps(lambda_event, indent=2))
        handler_response = self.handler(lambda_event, context)

        # https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
        # If you specify values for both headers and multiValueHeaders, API Gateway merges them into
        # a single list. If the same key-value pair is specified in both, only the values from
        # multiValueHeaders will appear in the merged list.
        multi_value_headers = {
            k: ",".join(v) for k, v in handler_response.get("multiValueHeaders", {}).items()
        }
        headers = {**handler_response.get("headers", {}), **multi_value_headers}

        status_code = handler_response["statusCode"]
        body = (handler_response.get("body") or "").encode("utf-8")
        if handler_response["isBase64Encoded"]:
            body = base64.b64decode(body)
        if "Content-Encoding" in headers and "gzip" in headers["Content-Encoding"]:
            body = gzip.decompress(body)

        return {
            "status_code": status_code,
            "headers": headers,
            "body": (body,),
        }


if __name__ == "__main__":

    def handler(event: LambdaHttpEvent, context: LambdaContextLike) -> LambdaHttpResponse:  # noqa: ARG001
        return {
            "statusCode": 200,
            "body": "Hello World",
            "headers": {"Content-Type": "text/plain"},
            "isBase64Encoded": False,
        }

    lambda_handler = SimpleLambdaHandler(handler)
    server = SimpleServer(lambda_handler.handle)
    server.serve_forever()
