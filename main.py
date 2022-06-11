from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from fastapi.templating import Jinja2Templates
import time, uvicorn, threading
from announcer2 import MessageAnnouncer
from announcer2 import MessageQueue

AUTHORIZATION = 'za-warudo'

DISCONNECT_THRESHOLD = 6 # 6 seconds

announcer = MessageAnnouncer.MessageAnnouncer()
messageq = MessageQueue.MessageQueue()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory = "templates")

def pollConnectedClients():
    while True:
        for x in announcer.connected_uids:
            lastRefreshed = x.get('lastRefreshed')
            print(x)

            if(int((time.time() - lastRefreshed)) > DISCONNECT_THRESHOLD): #wait for 6 seconds and announce uid disconnected.
                announcer.clientDisconnected(x.get('uid'))
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


        for uid in uids:
            lambda uid : messageq.addToQueue(uid, message) if uid not in announcer.connected_uids else None
     

def forbiddenResponse(request: Request):
    return templates.TemplateResponse('403.html', context={'request': request}, status_code=403)

async def streamMessage(uid: int, request: Request):
    while True:

        if(await request.is_disconnected()):
            print(str(uid) + " Disconnected.")
            announcer.clientDisconnected(uid)
            break

        announcer.refresh(uid)


        for connected in announcer.connected_uids:
            connected = dict(connected)
            con_uid = connected.get('uid')
            
                
            if(con_uid == uid and connected.get('newlyConnected') == True):
                yield "Welcome!"
                announcer.switchNewlyConnected(uid)
                data = messageq.getInQueue(uid)

                if(data != None):
                    messages = list(data.get('messages'))
                    if(len(messages) == 0):
                        break
                    print(messages)
                    for i in range(len(messages)):
                        yield messages[i]
                        time.sleep(1.2)

                    messageq.removeFromQueue(uid)    


        message = announcer.getMessage()
        print(message)
        
        if(message):
            print("Announcing", message)
            yield message
            time.sleep(1.2)

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

    print(str(uid) + " Connected.")
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