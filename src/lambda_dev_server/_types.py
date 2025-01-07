from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import MutableMapping
    from collections.abc import Iterator
    from typing import Any, Iterable
    from typing_extensions import TypedDict
    from typing_extensions import Protocol
    from typing_extensions import TypeAlias
    from typing_extensions import NotRequired
    from typing import Callable

    from types import TracebackType

    _ExcInfo: TypeAlias = "tuple[type[BaseException], BaseException, TracebackType]"
    _OptExcInfo: TypeAlias = "_ExcInfo | tuple[None, None, None]"

    class StartResponse(Protocol):
        def __call__(
            self,
            status: str,
            headers: list[tuple[str, str]],
            exc_info: _OptExcInfo | None = ...,
            /,
        ) -> Callable[[bytes], object]: ...

    WSGIEnvironment: TypeAlias = "dict[str, Any]"
    WSGIApplication: TypeAlias = Callable[[WSGIEnvironment, StartResponse], Iterable[bytes]]

    Environ = TypedDict(
        "Environ",
        {
            "REQUEST_METHOD": str,
            "SCRIPT_NAME": str,
            "PATH_INFO": str,
            "QUERY_STRING": str,
            "SERVER_PROTOCOL": str,
            "wsig.version": tuple[int, int],  # type: ignore[misc]
            "wsgi.url_scheme": str,
            "wsgi.input": "InputStream",
            "wsgi.errors": "ErrorStream",
            "wsgi.multithread": bool,
            "wsgi.multiprocess": bool,
            "wsgi.run_once": bool,
            "SERVER_NAME": str,
            "SERVER_PORT": int,
            "REMOTE_ADDR": str,
        },
    )

    class InputStream(Protocol):
        def read(self, size: int = ..., /) -> bytes: ...
        def readline(self, size: int = ..., /) -> bytes: ...
        def readlines(self, hint: int = ..., /) -> list[bytes]: ...
        def __iter__(self) -> Iterator[bytes]: ...

    class ErrorStream(Protocol):
        def flush(self) -> object: ...
        def write(self, s: str, /) -> object: ...
        def writelines(self, seq: list[str], /) -> object: ...

    class _Readable(Protocol):
        def read(self, size: int = ..., /) -> bytes: ...

        # Optional: def close(self) -> object: ...

    class FileWrapper(Protocol):
        def __call__(
            self,
            file: _Readable,
            block_size: int = ...,
            /,
        ) -> Iterable[bytes]: ...

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

    class LambdaHttpEvent(TypedDict):
        httpMethod: str
        path: str
        body: str
        isBase64Encoded: bool
        headers: Mapping[str, str]
        queryStringParameters: Mapping[str, str]
        multiValueQueryStringParameters: Mapping[str, list[str]]

    # https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-output-format
    class LambdaHttpResponse(TypedDict):
        body: str
        statusCode: int
        isBase64Encoded: bool
        headers: NotRequired[MutableMapping[str, str]]
        multiValueHeaders: NotRequired[MutableMapping[str, list[str]]]

    class LambdaHttpHandler(Protocol):
        def __call__(
            self, event: LambdaHttpEvent, context: LambdaContextLike
        ) -> LambdaHttpResponse: ...
