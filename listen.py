import sseclient
import random


# integer = random.sample(range(1, 1000), 1)[0]
integer = 191
print(integer)
messages = sseclient.SSEClient('http://147.139.33.135:9006/stream', headers={'Authorization': 'za-warudo', 'Code': str(integer)})

for message in messages:
    if(message != "" and message != None and not message.data.startswith("202")):
        print(message.data)
    
    