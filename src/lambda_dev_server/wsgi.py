from __future__ import annotations

import logging
from http import HTTPStatus
from typing import NamedTuple
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

if TYPE_CHECKING:
    from wsgiref.simple_server import WSGIServer

    from lambda_dev_server._types import LambdaHttpResponse
    from typing import Callable, Iterable
    from lambda_dev_server._types import LambdaContextLike, LambdaHttpEvent, StartResponse, Environ


class LambdaContextTuple(NamedTuple):
    aws_request_id: str = "aws_request_id"
    function_name: str = "function_name"
    memory_limit_in_mb: str = "memory_limit_in_mb"
    invoked_function_arn: str = "invoked_function_arn"


class WSGILambdaServer(NamedTuple):
    handler: Callable[[LambdaHttpEvent, LambdaContextLike], LambdaHttpResponse]

    def _extract_headers(self, environ: Environ | dict[str, str]) -> dict[str, str]:
        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                headers[key[5:].replace("_", "-")] = value
            elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                headers[key.replace("_", "-")] = value
        return headers  # type: ignore[return-value]

    def get_event(self, environ: Environ) -> LambdaHttpEvent:
        # import os

        # _final_dict = {
        #     key: value
        #     for key, value in environ.items()
        #     if key not in os.environ and not key.startswith(("wsgi.", "HTTP_", "CONTENT_"))
        # }
        query_params = parse_qs(environ["QUERY_STRING"])
        headers = self._extract_headers(environ)
        content_length = int(headers.get("CONTENT-LENGTH") or "0")
        body = environ["wsgi.input"].read(content_length).decode("utf-8")
        return {
            "httpMethod": environ["REQUEST_METHOD"],
            "path": environ["PATH_INFO"],
            "body": body,
            "isBase64Encoded": False,
            "headers": headers,
            "queryStringParameters": {k: v[-1] for k, v in query_params.items()},
            "multiValueQueryStringParameters": query_params,
        }

    def call_handler(self, environ: Environ) -> LambdaHttpResponse:
        event = self.get_event(environ)
        context = LambdaContextTuple()
        handler_response = self.handler(event, context)
        if isinstance(handler_response, dict) and "statusCode" in handler_response:
            return handler_response
        import json

        return {
            "statusCode": 200,
            "body": json.dumps(handler_response, default=str),
            "headers": {"Content-Type": "text/plain"},
            "isBase64Encoded": False,
        }

    def __call__(self, environ: Environ, start_response: StartResponse) -> Iterable[bytes]:
        response = self.call_handler(environ)
        status_code = response["statusCode"]
        phrase = HTTPStatus(status_code).phrase
        start_response(f"{status_code} {phrase}", list(response["headers"].items()))
        return [response["body"].encode("utf-8")]

    def make_server(self, host: str = "127.0.0.1", port: int = 3000) -> WSGIServer:
        from wsgiref.simple_server import make_server

        return make_server(host, port, self)  # type: ignore

    def serve_forever(self, host: str = "127.0.0.1", port: int = 3000) -> None:
        with self.make_server(host, port) as httpd:
            sa = httpd.socket.getsockname()
            server_host, server_port = sa[0], sa[1]
            logging.info("Running on http://%s:%d", server_host, server_port)
            httpd.serve_forever()


if __name__ == "__main__":

    def handler(event: LambdaHttpEvent, context: LambdaContextLike) -> LambdaHttpResponse:  # noqa: ARG001
        return {
            "statusCode": 200,
            "body": "Hello World",
            "headers": {"Content-Type": "text/plain"},
            "isBase64Encoded": False,
        }

    server = WSGILambdaServer(handler)
    server.serve_forever()
