from fastapi import Request, Response
from FastSession import FastSessionAbstract
import redis
import uuid
import json


class FastRedisSession(FastSessionAbstract):
    _conn: redis.Redis = None

    def __init__(self, connection: redis.Redis, timeout: int = 900):
        super(FastRedisSession, self).__init__(timeout)
        self._conn = connection

    def __del__(self):
        self._conn.close()

    def write(self, response: Response, data) -> str:
        _id = str(uuid.uuid4())
        jdata = json.dumps(data)
        self._conn.set(_id, jdata, ex=self._timeout)
        response.set_cookie(key=self._sessionName, value=_id)
        self._lastSessionId = _id
        return _id

    def read(self, request: Request):
        _id = request.cookies.get(self._sessionName)
        if _id is not None:
            res = self._conn.get(name=_id)
            self._conn.expire(name=_id, time=self._timeout)
            if res is not None:
                data = json.loads(res)
                return data
            else:
                return None
        else:
            return None

    def kill(self, response: Response):
        super(FastRedisSession, self).kill(response)
        if self._lastSessionId is not None:
            self._conn.delete(self._lastSessionId)
        self._lastSessionId = None
