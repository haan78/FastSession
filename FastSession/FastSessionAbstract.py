from fastapi import Request, Response


class FastSessionAbstract:
    _timeout: int
    _sessionName: str = "SESSIONID"
    _lastSessionId: str = None

    def __init__(self, timeout: int = 900):
        self._timeout = timeout

    def write(self, response: Response, data) -> str:
        pass

    def read(self, request: Request):
        pass

    def kill(self, response: Response):
        response.set_cookie(self._sessionName, value=None, max_age=0)
