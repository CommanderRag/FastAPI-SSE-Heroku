from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

import time, uvicorn, threading
from announcer2 import MessageAnnouncer
from announcer2 import MessageQueue

AUTHORIZATION = 'za-warudo'

announcer = MessageAnnouncer.MessageAnnouncer()
messageq = MessageQueue.MessageQueue()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")



def pollConnectedClients():
    while True:
        print('Polling!')
        for x in announcer.connected_uids:
            lastRefreshed = x.get('lastRefreshed')
            print(x)

            if(int((time.time() - lastRefreshed)) > 9):
                announcer.clientDisconnected(x.get('uid'))
                print("Removing", x)  

        time.sleep(3)


async def queueMessageForNotConnectedClients(message: str):
    f = open('uids.txt', 'r')

    readUids = f.readlines()
    uids = []
    f.close()


    for uid in readUids:
        uids.append(str(uid).strip())

    for uid in uids:
        if(uid not in announcer.connected_uids):
            messageq.addToQueue(uid, message)
     


def forbiddenResponse(request: Request):
    return templates.TemplateResponse('403.html', context={'request': request}, status_code=403)

async def streamMessage(uid: str):
    while True:

        announcer.refresh(uid)

        # if(uid in announcer.connected_uids):
        #     data = messageq.getMessage(uid)
        #     if(data != None):
        #         messages = data.get('messages')
        #         for message in messages:
        #             yield message


        for connected in announcer.connected_uids:
            connected = dict(connected)
            con_uid = connected.get('uid')
            
                
            if(con_uid == uid and connected.get('newlyConnected') == True):
                yield "Hello"
                announcer.switchNewlyConnected(uid)
                data = messageq.getInQueue(uid)

                if(data != None):
                    messages = list(data.get('messages'))
                    if(len(messages) == 0):
                        break

                    for message in messages:
                        yield message
                        time.sleep(1.2)

                    messageq.removeFromQueue(uid)    


        message = announcer.getMessage()
        print(message)
        
        if(message):
            print("Announcing", message)
            yield message
            time.sleep(1)

            announcer.clearMessage()


        time.sleep(3)        

@app.get('/stream', response_class=HTMLResponse)
async def stream(request: Request):

    auth = request.headers.get('Authorization', None)
    uid = request.headers.get('Code', None)

    if(auth == None or uid == None or auth != AUTHORIZATION):
        return forbiddenResponse(request)    


    with open('uids.txt', 'r') as f:
        readUids = f.readlines()
        uids = []
        #strip off new lines

        uid = uid.strip()        

        for uid in readUids:
            uids.append(str(uid).strip())

        print("Uids", uids)

        if(uids == None or len(uids) == 0):
            with open('uids.txt', 'w+') as fw:
                fw.write(str(uid) + "\n")

        else:
            if(uid not in uids):
                with open('uids.txt', 'a') as fw:
                    fw.write(str(uid) + "\n")   


    announcer.clientConnected(uid)                

    event_generator = streamMessage(uid=uid)
    return EventSourceResponse(event_generator)


@app.post('/generate', response_class=HTMLResponse)
async def generate(request: Request):
    json = await request.json()

    message = json.get('message')
    print(announcer.setMessage(message))
    print(announcer.getMessage())


    await queueMessageForNotConnectedClients(message)


    return PlainTextResponse('Success!')

@app.get('/ping')
async def ping(request: Request, response_class=HTMLResponse):
    auth = request.headers.get('Authorization', None)

    if(auth == None or auth != AUTHORIZATION):
        return forbiddenResponse(request)

    announcer.setMessage('Pong!')
    return PlainTextResponse('Success!')


@app.get('/clearUids')
async def clearUids(request: Request, response_class=HTMLResponse):
    auth = request.headers.get('Authorization', None)

    if(auth == None or auth != AUTHORIZATION):
        return forbiddenResponse(request)

    with open('uids.txt', 'w+') as f:
        pass

    return PlainTextResponse('Success!')


thread = threading.Thread(target=pollConnectedClients)
thread.start()

# uvicorn.run(app)