import sseclient

integer = 1
print(integer)
messages = sseclient.SSEClient('http://fastapi-sse.herokuapp.com/stream', headers={'Authorization': 'za-warudo', 'Code': str(integer)})

for message in messages:
    if(message != "" and message != None and not message.data.startswith("202")):
        print(message.data)