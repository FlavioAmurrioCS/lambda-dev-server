from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import MutableMapping

    from _typeshed.wsgi import ErrorStream
    from _typeshed.wsgi import InputStream
    from typing_extensions import NotRequired
    from typing_extensions import Protocol
    from typing_extensions import TypedDict

    Environ = TypedDict(
        "Environ",
        {
            "REQUEST_METHOD": str,
            "SCRIPT_NAME": str,
            "PATH_INFO": str,
            "QUERY_STRING": str,
            "SERVER_PROTOCOL": str,
            "wsig.version": tuple[int, int],
            "wsgi.url_scheme": str,
            "wsgi.input": InputStream,
            "wsgi.errors": ErrorStream,
            "wsgi.multithread": bool,
            "wsgi.multiprocess": bool,
            "wsgi.run_once": bool,
            "SERVER_NAME": str,
            "SERVER_PORT": int,
            "REMOTE_ADDR": str,
        },
    )

    ################################################################
    class LambdaContextLike(Protocol):
        @property
        def aws_request_id(self) -> str: ...
        @property
        def function_name(self) -> str: ...
        @property
        def memory_limit_in_mb(self) -> str: ...
        @property
        def invoked_function_arn(self) -> str: ...

        # @property
        # def function_version(self)-> str: ...
        # @property
        # def log_group_name(self)-> str: ...
        # @property
        # def log_stream_name(self)-> str: ...

    class LambdaHttpEventRequestContext(TypedDict):
        path: str

    class LambdaHttpEvent(TypedDict):
        httpMethod: str
        path: str
        body: str
        isBase64Encoded: bool
        headers: Mapping[str, str]
        queryStringParameters: Mapping[str, str]
        multiValueQueryStringParameters: Mapping[str, list[str]]
        resource: NotRequired[str]
        requestContext: NotRequired[LambdaHttpEventRequestContext]

    # https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
    class LambdaHttpResponse(TypedDict):
        body: str | None
        statusCode: int
        isBase64Encoded: bool
        headers: NotRequired[MutableMapping[str, str]]
        multiValueHeaders: NotRequired[MutableMapping[str, list[str]]]

    class LambdaHttpHandler(Protocol):
        def __call__(
            self, event: LambdaHttpEvent, context: LambdaContextLike
        ) -> LambdaHttpResponse: ...
