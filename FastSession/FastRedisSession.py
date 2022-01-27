from FastSession.FastSessionAbstract import FastSessionAbstract
import redis
import json


class FastRedisSession(FastSessionAbstract):
    _conn: redis.Redis = None

    def __init__(self, connection: redis.Redis, timeout: int = 900):
        super(FastRedisSession, self).__init__(timeout)
        self._conn = connection

    def __del__(self):
        self._conn.close()

    def writeHandler(self, id: str, data) ->None:
        jdata = json.dumps(data)
        self._conn.set(id, jdata, ex=self._timeout)

    def readHandler(self, id:str):
        res = self._conn.get(name=id)        
        if res is not None:            
            data = json.loads(res)
            self._conn.expire(name=id, time=self._timeout)
            return data
        else:
            return None

    def killHandler(self, id:str):
        self._conn.delete(id)
