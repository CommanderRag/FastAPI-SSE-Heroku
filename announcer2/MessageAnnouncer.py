import time

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []
        self.connected_uids = []
        self.known_uids = []

    def clientConnected(self, uid: str):
        for clients in self.connected_uids:
            if(clients.get('uid') == uid):
                self.connected_uids.remove(clients)
        self.connected_uids.append({'uid': uid, 'lastRefreshed': time.time(), 'newlyConnected': True})

    def clientDisconnected(self, uid: str):
        for x in self.connected_uids:
            if(x.get('uid') == uid):
                self.connected_uids.remove(x)

    def switchNewlyConnected(self, uid: str):
        for clients in self.connected_uids:
            if(clients.get('uid') == uid):
                clients['newlyConnected'] = False           

    def setMessage(self, message: str):
        with open('message.txt', 'w+') as f:
            f.write(message)
        return message

    def clearMessage(self):
        with open('message.txt', 'w+') as f:
            pass

    def getMessage(self):
        with open('message.txt', 'r') as f:
            return str(f.readline())

    def announce(self, message):
        for i in reversed(range(len(self.listeners))):
            self.listeners[i].append(message) 

    def refresh(self, uid: str):
        for x in self.connected_uids:
            if(x.get('uid') == uid):
                x['lastRefreshed'] = time.time()


    def appendUid(self, uid: str):
        print(self.known_uids)
        uidExists = False
        for known_uid in self.known_uids:
            if(known_uid == uid):
                uidExists = True

        if(not uidExists):
            self.known_uids.append(uid)          

    def getKnownUids(self):
        return self.known_uids

    def clearKnownUids(self):
        self.known_uids.clear()            