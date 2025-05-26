from __future__ import annotations

import logging

__HELPER_FILE_PREFIX = "__TEMP_LAMBDA_DEV_SERVER_HELPER_DO_NOT_CHECK_INTO_GIT__"

logger = logging.getLogger(__name__)


def _delete_helper_files() -> None:
    import os
    from contextlib import suppress

    for file in os.listdir(os.getcwd()):
        if file.startswith(__HELPER_FILE_PREFIX):
            with suppress(FileNotFoundError):
                os.remove(file)


def run_uvicorn(*, package: str, module: str, host: str, port: int) -> None:
    import os
    import tempfile
    from textwrap import dedent

    import uvicorn

    _delete_helper_files()

    wsgi_app = "wsgi_app"
    file_content = dedent(f"""\
        from {package} import {module} as handler
        from lambda_dev_server.wsgi import SimpleLambdaHandler
        from lambda_dev_server.simple_server import SimpleServer

        simple_lambda_handler = SimpleLambdaHandler(handler)
        {wsgi_app} = SimpleServer(simple_lambda_handler.handle)
    """)

    with tempfile.NamedTemporaryFile(
        "w", dir=os.getcwd(), prefix=__HELPER_FILE_PREFIX, suffix=".py"
    ) as tempf:
        tempf.write(file_content)
        tempf.flush()
        helper_module = os.path.basename(tempf.name).rsplit(".py")[0]
        uvicorn.run(
            f"{helper_module}:{wsgi_app}", reload=True, interface="wsgi", host=host, port=port
        )


def run_wsgi(*, package: str, module: str, host: str, port: int) -> None:
    from lambda_dev_server.simple_server import SimpleServer
    from lambda_dev_server.wsgi import SimpleLambdaHandler

    mod = __import__(package, fromlist=["_trash"])
    handler = getattr(mod, module)
    simple_lambda_handler = SimpleLambdaHandler(handler)
    wsgi_app = SimpleServer(simple_lambda_handler.handle)
    wsgi_app.serve_forever(host=host, port=port)


prog = None


def main(argv: list[str] | tuple[str, ...] | None = None) -> int:
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(
        prog=prog, description="Run a local server to test AWS Lambda functions."
    )
    parser.add_argument("handler")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind the server to (default: %(default)s)",
    )
    parser.add_argument(
        "--port", type=int, default=3000, help="Port to bind the server to (default: %(default)s)"
    )
    parser.add_argument(
        "--workdir",
        help="Working directory to run the server in (default: %(default)s)",
        default="./",
    )
    args = parser.parse_args(argv)
    package, module = args.handler.rsplit(".", 1)
    port: int = args.port
    host: str = args.host
    sys.path.append(os.path.realpath(args.workdir))

    try:
        run_uvicorn(package=package, module=module, host=host, port=port)
    except ModuleNotFoundError:
        logger.info("uvicorn not found, falling back to wsgiref")
        logger.info("Install uvicorn for hot-reloading support")
    else:
        return 0
    try:
        run_wsgi(package=package, module=module, host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Shutting down...")

    return 0


if __name__ == "__main__":
    prog = "python3 -m lambda_dev_server"
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    raise SystemExit(main())
