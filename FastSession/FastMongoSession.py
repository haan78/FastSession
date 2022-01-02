from datetime import datetime, timedelta
from fastapi import Request, Response
from bson import ObjectId
from FastSession.FastSessionAbstract import FastSessionAbstract
from pymongo.collection import Collection


class FastMongoSession(FastSessionAbstract):
    _coll: Collection = None
    _dbname: str = None

    def __init__(self, collection: Collection, timeout: int = 900):
        super(FastMongoSession, self).__init__(timeout)
        self._coll = collection
        self._createIndex()


    def __del__(self):
        self._coll = None

    def _createIndex(self):
        indexname = self._coll.name + "_time_index"
        cur = self._coll.list_indexes()
        for ind in cur:
            if str(ind["name"]) == indexname:
                if ("expireAfterSeconds" not in ind) or (ind["expireAfterSeconds"] != self._timeout):
                    self._coll.drop_index(index_or_name=indexname)
                    break
                else:
                    return

        self._coll.create_index([("time", 1)], name=indexname, expireAfterSeconds=self._timeout)


    def write(self, response: Response, data) -> str:

        res = self._coll.insert_one({
            "time": datetime.utcnow(),
            "data": data
        })
        self._lastSessionId = str(res.inserted_id)
        response.set_cookie(key=self._sessionName, value=self._lastSessionId, max_age=self._timeout)
        return self._lastSessionId

    def read(self, request: Request):
        _id = request.cookies.get(self._sessionName)
        if _id is not None:
            time = datetime.utcnow() - timedelta(seconds=self._timeout)
            res = self._coll.find_one({"_id": ObjectId(_id), "time": {"$gte": time}})
            if res is not None:
                self._coll.update_one({"_id": ObjectId(_id)}, {"$set": {"time": datetime.utcnow()}}, upsert=False)
                return res["data"]
            else:
                return None
        else:
            return None

    def kill(self, response: Response):
        super(FastMongoSession, self).kill(response)
        if self._lastSessionId is not None:
            self._coll.delete_one({"_id": ObjectId(self._lastSessionId)})
        self._lastSessionId = None
