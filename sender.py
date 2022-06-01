import time
import requests

while True:
    message = input("Enter message to send:")
    if message == '':
        break
    msg_json = {'message': message}
    requests.post('http://0.0.0.0:8000/generate', json=msg_json, headers={'Authorization': 'za-warudo'})
