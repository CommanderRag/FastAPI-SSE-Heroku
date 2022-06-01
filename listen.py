import sseclient

messages = sseclient.SSEClient('http://fastapi-sse.herokuapp.com/stream', headers={'Authorization': 'za-warudo', 'Code': str(1)})

for message in messages:
    if(message != "" and message != None and not message.data.startswith("202")):
        print(message.data)