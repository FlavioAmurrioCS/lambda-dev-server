from __future__ import annotations

import logging

__HELPER_FILE_PREFIX = "__TEMP_LAMBDA_DEV_SERVER_HELPER_DO_NOT_CHECK_INTO_GIT__"


def _delete_helper_files() -> None:
    import os
    from contextlib import suppress

    for file in os.listdir(os.getcwd()):
        if file.startswith(__HELPER_FILE_PREFIX):
            with suppress(FileNotFoundError):
                os.remove(file)


def run_uvicorn(*, package: str, module: str, host: str, port: int) -> None:
    import uvicorn
    import tempfile
    import os
    from textwrap import dedent

    _delete_helper_files()

    wsgi_app = "wsgi_app"
    file_content = dedent(f"""\
        from {package} import {module} as handler
        from lambda_dev_server.wsgi import WSGILambdaServer

        {wsgi_app} = WSGILambdaServer(handler)
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
    from lambda_dev_server.wsgi import WSGILambdaServer

    mod = __import__(package, fromlist=["_trash"])
    handler = getattr(mod, module)
    wsgi_app = WSGILambdaServer(handler)
    wsgi_app.serve_forever(host=host, port=port)


prog = None


def main(argv: list[str] | tuple[str, ...] | None = None) -> int:
    import argparse
    import sys
    import os

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
        logging.info("uvicorn not found, falling back to wsgiref")
        logging.info("Install uvicorn for hot-reloading support")
    else:
        return 0
    try:
        run_wsgi(package=package, module=module, host=host, port=port)
    except KeyboardInterrupt:
        logging.info("Shutting down...")

    return 0


if __name__ == "__main__":
    prog = "python3 -m lambda_dev_server"
    raise SystemExit(main())
