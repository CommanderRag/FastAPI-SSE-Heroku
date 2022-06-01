import time, sched, datetime, os
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
import uvicorn
from pydantic import BaseModel
from announcer import MessageAnnouncer, MessageQueue
from apscheduler.schedulers.background import BackgroundScheduler


announcer = MessageAnnouncer.MessageAnnouncer()
messageq = MessageQueue.MessageQueue()

TOKEN = "za-warudo"
CLIENT_QUIT_MESSAGE = "------QUIT------"
BREAK_CONN = "------BREAK------"


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

scheduler = BackgroundScheduler()

templates = Jinja2Templates(directory = "templates")

class Item(BaseModel):
    message: str

def format_sse(data:str , event=None) -> str:
    message = f'data: {data}\n\n'
    if event is not None:
        message = f'event: {event}\n{message}'

    return message 

def queueMessageForNotConnectedClients(msg):
    with open('uids.txt', 'r') as r:
        uids = r.readlines()
        for uid in uids:
            uid = uid.strip()
            connected_uids = []
            for x in announcer.connected_uids:
                connected_uids.append(x.get('uid'))
            if(uid not in connected_uids):
                print("Queueing message" +  " for uid " + uid)
                messageq.putInQueue(uid, msg)    
                    


def forbiddenResponse(request: Request):
    return templates.TemplateResponse('403.html', context={'request': request}, status_code=403)

def pollConnectedClients():
    #print("Polling!")
    for x in announcer.connected_uids:
        lastRefreshed = x.get('lastRefreshed')
        print(x, lastRefreshed)
        if(int((time.time() - lastRefreshed)) > 9):
            announcer.clientDisconnected(x.get('uid'))
            print("Removing", x)       

async def streamMessage(uid, uids, request):
    while True:
        announcer.refresh(uid)
        if await request.is_disconnected():
            print(uid + " disconnected!")
            announcer.clientDisconnected(uid)
            break
        
        if(uid in uids):
            messages = messageq.getInQueue(uid)
            if(messages != None):

                for the_message in messages:
                    yield the_message
                    time.sleep(0.9)  
                
                messageq.removeFromQueue(uid)

            if(messages == None and announcer.getMessage() != None):
                yield announcer.getMessage()  
                time.sleep(1)
                announcer.clearMessage()  

        message = announcer.getMessage()      

        if(message == BREAK_CONN):
            break

        if(message != None):
            announcer.clearMessage()
            yield message
            time.sleep(0.9)

        time.sleep(3)
            


@app.get('/')
async def index(request: Request):
    return forbiddenResponse(request)

@app.get('/stream', response_class=HTMLResponse)
async def stream(request: Request):

    token = request.headers.get('Authorization', None)
    uid = request.headers.get('Code', None)

    if(token == None or uid == None or token != TOKEN):
        return forbiddenResponse(request)

    uids = None

    with open('uids.txt', 'r') as f:
        uids = f.readlines()

        print("Uids", uids)

        if(len(uids) == 0 or uid not in uids):
            with open("uids.txt", 'a') as w:
                if(len(uids) != 0):
                    print("Writing uid on a new line", uid)
                    w.write('\n'+uid)
                else:
                    print("Writing uid on the first line", uid)
                    w.write(uid)


    announcer.clientConnected(uid)
    print(announcer.connected_uids)
    event_generator = streamMessage(uid=uid, request=request, uids=uids)
    return EventSourceResponse(event_generator)

@app.post('/generate', response_class=HTMLResponse)
async def generate(request: Request, item: Item):

    token = request.headers.get('Authorization', None)
    if(token == None or token != TOKEN):
        return forbiddenResponse(request)

    
    r = item.dict()
    message = r.get('message')
    
    #message = format_sse(data_msg)
    print("Announcing message", message)
    if(message == CLIENT_QUIT_MESSAGE):
        announcer.setMessage(BREAK_CONN)
    else:
        announcer.setMessage(message)
    
    queueMessageForNotConnectedClients(message)
    return PlainTextResponse("Success!")

@app.get('/ping', response_class=HTMLResponse)
async def ping(request: Request):
    token = request.headers.get('Authorization', None)
    if(token == None or token != TOKEN):
        return forbiddenResponse(request)

    announcer.setMessage('Pong!')
    return PlainTextResponse("Success!")   


@app.post('/clearuids', response_class=HTMLResponse)
async def clearUids(request: Request):
    token = request.headers.get('Authorization')

    if(token == None or token != TOKEN):
        return forbiddenResponse(request)

    with open('uids.txt', 'w+'):
        pass
    return PlainTextResponse("Success!")

scheduler.add_job(pollConnectedClients, 'interval', seconds=1)
scheduler.start()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=os.environ.get('PORT') or 8000)    
