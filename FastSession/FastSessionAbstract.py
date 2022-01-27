from fastapi import Request, Response
import uuid

class FastSessionAbstract:
    _timeout: int
    _sessionName: str = "SESSIONID"
    _lastSessionId: str = None
    _cookieTimeout:int = 86400 ##1 day    

    def __init__(self, timeout: int = 900):
        self._timeout = timeout        

    def id(self)->str:
        return self._lastSessionId

    def write(self, response: Response, data) -> None:
        self._lastSessionId = "fastapi_"+str(uuid.uuid4())
        self.writeHandler(self._lastSessionId, data)
        response.set_cookie(key=self._sessionName, value=self._lastSessionId, max_age=self._cookieTimeout)

    def read(self,request:Request):
        self._lastSessionId = request.cookies.get(self._sessionName)
        if self._lastSessionId is not None:
            return self.readHandler(self._lastSessionId)
        else:
            return None
        

    def kill(self,request:Request, response: Response)->None:
        self._lastSessionId = request.cookies.get(self._sessionName)
        if self._lastSessionId is not None:
            self.killHandler(self._lastSessionId)
        response.set_cookie(self._sessionName, value=None, max_age=0)

    def writeHandler(self, id:str, data):
        pass

    def readHandler(self, id:str):
        pass

    def killHandler(self, id:str):
        pass
