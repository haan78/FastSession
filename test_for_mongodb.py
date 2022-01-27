import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from pymongo import MongoClient

from FastSession.FastMongoSession import FastMongoSession

duration = 10
mongodbconnectionstring = "mongodb://root:12345@localhost";

fsm = FastMongoSession(MongoClient(mongodbconnectionstring).get_database("test").get_collection("session"), timeout=duration)

app = FastAPI()


def html(message: str):
    return message + """<br/>
    <ul>
        <li>Session duration is """+str(duration)+""" seconds</li>
        <li><a href="/write">Write Session</a></li>
        <li><a href="/read">Read Session</a></li>
        <li><a href="/kill">Kill Session</a></li>
    </ul>
    """


@app.get("/", response_class=HTMLResponse)
async def hello():
    return html("Hello Session Test")


@app.get("/write", response_class=HTMLResponse)
def write(response: Response):
    fsm.write(response, {
        "name": "Ali Baris Ozturk"
    })
    return html("Session write has been done!")


@app.get("/read", response_class=HTMLResponse)
async def read(request: Request):
    v = fsm.read(request)
    return html("The Session value is " + str(v))


@app.get("/kill", response_class=HTMLResponse)
async def kill(request:Request,response: Response):
    fsm.kill(request,response)
    return html("Session has been deleted!")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
