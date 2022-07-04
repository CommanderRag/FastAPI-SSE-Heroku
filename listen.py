import sseclient

integer = 1

messages = sseclient.SSEClient('http://localhost:8000/stream', headers={'Authorization': 'za-warudo', 'Code': str(integer)})

for message in messages:
    # if(message != "" and message != None and not message.data.startswith("202")):
    #     print(message.data)
    print(message)
