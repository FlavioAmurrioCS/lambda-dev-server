from __future__ import annotations

from typing import NamedTuple
from typing import TYPE_CHECKING

from lambda_dev_server.simple_server import SimpleServer


if TYPE_CHECKING:
    from lambda_dev_server.simple_server import SimpleRequestEvent, SimpleResponseEvent
    from lambda_dev_server._types import LambdaHttpResponse
    from typing import Callable
    from lambda_dev_server._types import LambdaContextLike, LambdaHttpEvent


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
        }
        context = LambdaContextTuple()
        handler_response = self.handler(lambda_event, context)
        headers = handler_response["headers"]
        status_code = handler_response["statusCode"]
        body = (handler_response["body"].encode("utf-8"),)

        return {
            "status_code": status_code,
            "headers": headers,
            "body": body,
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
