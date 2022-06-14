import requests

POST_URL = 'https://brass-cobra-cape.wayscript.cloud/postQueue'
FETCH_URL = 'https://brass-cobra-cape.wayscript.cloud/getQueue'
DELETE_URL = 'https://brass-cobra-cape.wayscript.cloud/clearUidQueue'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'za-warudo'
}

class MessageQueue:


    def postToQueue(self, uid: int, message:str):
        print("Posting to queue", uid, message)
        

        data = {
            'uid': uid,
            'message': message
        }

        try: 
            r = requests.post(POST_URL, headers=headers, json=data)
            print(r.status_code)
            r.close()

        except Exception as e:
            return -1    

    def getInQueue(self, uid: int):

        print("Fetching queue for uid: ", uid)

        data = {
            'uid': uid,
        }

        try:
            r = requests.post(FETCH_URL, headers=headers, json=data)
            data = r.json()
            print(r.status_code)
            r.close() 
    
            return data

        except Exception as e:
            return -1    

    def removeFromQueue(self, uid: int):

        data = {'uid': uid}

        try:
        
            r = requests.post(DELETE_URL, headers=headers, json=data)
            print(r.status_code)
            r.close()

        except Exception as e:
            return -1    