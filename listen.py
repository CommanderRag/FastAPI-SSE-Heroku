import sseclient

integer = 1

messages = sseclient.SSEClient('https://fastapi-sse-heroku.naxeq.repl.co/stream', headers={'Authorization': 'za-warudo', 'Code': str(integer)})

for message in messages:
    # if(message != "" and message != None and not message.data.startswith("202")):
    #     print(message.data)
    print(message)
