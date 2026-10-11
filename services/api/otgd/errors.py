from fastapi.responses import JSONResponse


class Problem(Exception):
    def __init__(
        self, status, code, message=None, retryable=False, headers=None, revision=None
    ):
        self.status = status
        self.code = code
        self.message = message or code.replace("_", " ").capitalize()
        self.retryable = retryable
        self.headers = headers or {}
        self.revision = revision


def response_problem(exc, request_id):
    body = dict(
        code=exc.code,
        message=exc.message,
        request_id=request_id,
        retryable=exc.retryable,
    )
    if exc.revision is not None:
        body["current_revision"] = exc.revision
    return JSONResponse(
        body,
        status_code=exc.status,
        headers={"Cache-Control": "no-store", **exc.headers},
    )
