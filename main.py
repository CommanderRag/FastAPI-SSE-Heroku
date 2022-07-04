from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from fastapi.templating import Jinja2Templates
import time, uvicorn, threading, json
from announcer2 import MessageAnnouncer
from announcer2 import MessageQueue

AUTHORIZATION = 'za-warudo'

DISCONNECT_THRESHOLD = 60 # 60 seconds, i.e 1 minute

announcer = MessageAnnouncer.MessageAnnouncer()
messageq = MessageQueue.MessageQueue()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory = "templates")

def pollConnectedClients():
    while True:
        if(len(announcer.connected_uids) == 0):
            announcer.clearMessage()
        for x in announcer.connected_uids:
            lastRefreshed = x.get('lastRefreshed')

            if(int((time.time() - lastRefreshed)) > DISCONNECT_THRESHOLD): #wait for 6 seconds and announce uid disconnected.
                announcer.clientDisconnected(x['uid'])
                print("Removing", x)  

        time.sleep(3)


def queueMessageForNotConnectedClients(message: str):

    with open('uids.txt', 'r') as f:
        readUids = f.read()
        readUids = readUids.split('\n')

        uids = []
        for uid in readUids:
            if(uid):
                uids.append(uid)

        print(uids)
        # for uid in uids:
        #     uid = int(uid)
        #     if uid not in announcer.listeners:
        #         messageq.postToQueue(uid, message)

        
        uids = list(map(int, uids))
        print("Connected uids", announcer.connected_uids)
        con_uids = [x['uid'] for x in announcer.connected_uids] 
        con_uids = list(map(int, con_uids))
        print(uids, con_uids)
        for uid in uids:
            if(uid not in con_uids):
                print("Queueing for uid", uid)
                messageq.postToQueue(uid, message)

def forbiddenResponse(request: Request):
    return templates.TemplateResponse('403.html', context={'request': request}, status_code=403)

async def streamMessage(uid: int, request: Request):
    while True:

        if(await request.is_disconnected()):
            print(str(uid) + " Disconnected..")
            announcer.clientDisconnected(uid)
            break

        announcer.refresh(uid)
        if(announcer.isNewlyConnected(uid) == True):
            data = messageq.getInQueue(uid)
            print("Data:", data)
            if(data != None and len(data) != 0):
                messages = list(data)

                if(len(messages) == 0):
                    break

                # print(messages)

                for i in range(len(messages)):
                    yield messages[i][1] # index 0 is uid, index 1 is the message.
                    time.sleep(1.2)

                messageq.removeFromQueue(uid) 

            announcer.switchNewlyConnected(uid)


        message = announcer.getMessage()
        if(message):
            print("Announcing", message)
            try:
                yield message
                time.sleep(0.9)

            except Exception as e:
                print(str(e))
                messageq.postToQueue(uid, message)

            announcer.clearMessage()


        time.sleep(1.8)        

@app.get('/')
async def index(request: Request):
    return forbiddenResponse(request)

@app.get('/stream', response_class=HTMLResponse)
async def stream(request: Request):

    auth = request.headers.get('Authorization', None)
    uid = request.headers.get('Code', None)

    if(auth == None or uid == None or auth != AUTHORIZATION or bool(int(uid)) == False):
        return forbiddenResponse(request)      

    announcer.appendUid(uid)

    announcer.clientConnected(int(uid))                

    event_generator = streamMessage(uid=uid, request=request)
    return EventSourceResponse(event_generator)


@app.post('/generate', response_class=HTMLResponse)
async def generate(request: Request):
    json = await request.json()

    announcer.setMessage(str(json))
    queueMessageForNotConnectedClients(str(json))


    return PlainTextResponse('Success!')

@app.get('/ping')
async def ping(request: Request, response_class=HTMLResponse):
    auth = request.headers.get('Authorization', None)

    if(auth == None or auth != AUTHORIZATION):
        return forbiddenResponse(request)

    queueMessageForNotConnectedClients('Pong!')

    announcer.setMessage('Pong!')

    
    return PlainTextResponse('Success!')


@app.get('/clearUids')
async def clearUids(request: Request, response_class=HTMLResponse):
    auth = request.headers.get('Authorization', None)

    if(auth == None or auth != AUTHORIZATION):
        return forbiddenResponse(request)

    announcer.clearKnownUids()

    return PlainTextResponse('Success!')


thread = threading.Thread(target=pollConnectedClients)
thread.start()    


# uvicorn.run(app)