from datetime import datetime
from bson import ObjectId
from FastSession.FastSessionAbstract import FastSessionAbstract
from pymongo.collection import Collection


class FastMongoSession(FastSessionAbstract):
    _coll: Collection = None

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
                #Check If index exist with the same name, same attribute(expireAfterSeconds)  and same attribute value(self._timeout)                
                if ("expireAfterSeconds" not in ind) or (ind["expireAfterSeconds"] != self._timeout):
                    ##Sometihn wron on index. Delete it!
                    self._coll.drop_index(index_or_name=indexname)
                    break
                else:                    
                    #Everythin fine just leave here
                    return

        self._coll.create_index([("time", 1)], name=indexname, expireAfterSeconds=self._timeout)

    def writeHandler(self, id: str, data):        
        self._coll.insert_one({
            "_id" : ObjectId(id),
            "time": datetime.utcnow(),
            "data": data
        })        

    def readHandler(self, id: str):        
        res = self._coll.find_one({"_id": ObjectId(id)})
        if res is not None:
            self._coll.update_one({"_id": ObjectId(id)}, {"$set": {"time": datetime.utcnow()}}, upsert=False)
            return res["data"]
        else:
            return None

    def killHandler(self, id: str):
        self._coll.delete_one({"_id": ObjectId(id)})

