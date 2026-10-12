#!/usr/bin/env python3
"""Small AWS Lambda Runtime API client for the locked Python worker image."""
from __future__ import annotations
from datetime import datetime, timezone
import importlib
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'services/api'))
ALLOWED = {'otgd.serverless_worker.sqs_handler', 'otgd.serverless_worker.maintenance_handler',
           'otgd.serverless_worker.control_handler', 'otgd.serverless_worker.dispatch_handler'}
MAX_EVENT = 6 * 1024 * 1024


class Context:
    def __init__(self, headers):
        self.aws_request_id = headers['Lambda-Runtime-Aws-Request-Id']
        self.invoked_function_arn = headers.get('Lambda-Runtime-Invoked-Function-Arn', '')
        self.deadline = int(headers['Lambda-Runtime-Deadline-Ms'])
        self.function_name = os.environ.get('AWS_LAMBDA_FUNCTION_NAME', '')
        self.memory_limit_in_mb = os.environ.get('AWS_LAMBDA_FUNCTION_MEMORY_SIZE', '')

    def get_remaining_time_in_millis(self):
        return max(0, self.deadline - int(time.time() * 1000))


def exchange(endpoint, handler, opener=None):
    """Execute one actual invocation; errors reveal only type, never event/secrets."""
    opener = opener or urllib.request.build_opener(urllib.request.ProxyHandler({}))
    base = 'http://' + endpoint + '/2018-06-01/runtime/invocation/'
    with opener.open(base + 'next', timeout=960) as response:
        raw = response.read(MAX_EVENT + 1)
        context = Context(response.headers)
        trace = response.headers.get('Lambda-Runtime-Trace-Id')
    if trace:
        os.environ['_X_AMZN_TRACE_ID'] = trace
    else:
        os.environ.pop('_X_AMZN_TRACE_ID', None)
    try:
        if len(raw) > MAX_EVENT:
            raise ValueError('Oversized invocation')
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError('Object invocation required')
        result = handler(event, context)
        body = json.dumps(result, allow_nan=False, separators=(',', ':')).encode()
        destination = base + context.aws_request_id + '/response'
        headers = {'Content-Type': 'application/json'}
    except Exception as error:
        body = json.dumps({'errorType': type(error).__name__,
                          'errorMessage': 'Serverless operation failed; inspect protected aggregate evidence'}).encode()
        destination = base + context.aws_request_id + '/error'
        headers = {'Content-Type': 'application/json', 'Lambda-Runtime-Function-Error-Type': 'Unhandled'}
    request = urllib.request.Request(destination, data=body, headers=headers, method='POST')
    with opener.open(request, timeout=10) as response:
        response.read(8192)


def main():
    endpoint = os.environ.get('AWS_LAMBDA_RUNTIME_API', '')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+:[0-9]{1,5}', endpoint):
        raise RuntimeError('AWS Lambda Runtime API is unavailable')
    name = os.environ.get('OTGD_LAMBDA_HANDLER') or (sys.argv[1] if len(sys.argv) == 2 else '')
    if name not in ALLOWED:
        raise RuntimeError('Unsupported worker entrypoint')
    module, function = name.rsplit('.', 1)
    handler = getattr(importlib.import_module(module), function)
    while True:
        exchange(endpoint, handler)


if __name__ == '__main__':
    main()
