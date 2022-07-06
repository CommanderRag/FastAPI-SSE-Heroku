import time
import requests

while True:
    message = input("Enter message to send:")
    if message == '':
        break
    msg_json = {'message': message}
    requests.post('https://fastapi-sse-heroku.naxeq.repl.co/generate', json=msg_json, headers={'Authorization': 'za-warudo', 'Content-Type': 'application/json'})
