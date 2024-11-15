# lambda-dev-server

[![PyPI - Version](https://img.shields.io/pypi/v/lambda-dev-server.svg)](https://pypi.org/project/lambda-dev-server)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lambda-dev-server.svg)](https://pypi.org/project/lambda-dev-server)

-----

A lightweight development server for AWS Lambda, `lambda-dev-server` emulates the Lambda environment locally by creating events and contexts for any app handler. It processes requests, generates Lambda events, and returns parsed responses—ideal for development and debugging, with hot-reloading for rapid iteration. Not intended for production use. This has been tested with lambdas that use `aws-lambda-powertools` as well with lambdas that return in the shape of `{"statusCode": 200, "body": "Hello World"}`.

## Table of Contents

- [lambda-dev-server](#lambda-dev-server)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Debbuging](#debbuging)
  - [License](#license)

## Installation

To install `lambda-dev-server`, use pip:

```sh
pip install lambda-dev-server
```

## Usage

```bash
# Given a Lambda handler named handler in app.py
lambda-dev-server app.handler
```

## Debbuging

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python Debugger: Module",
      "type": "debugpy",
      "request": "launch",
      "module": "lambda_dev_server",
      "args": ["app.handler"]
    }
  ]
}
```

## License

`lambda-dev-server` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
