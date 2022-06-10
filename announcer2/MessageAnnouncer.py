import time

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []
        self.connected_uids = []

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
        for i in range(len(self.connected_uids)):
            if(self.connected_uids[i]['uid'] == str(uid)):
                self.connected_uids[i].pop('newlyConnected')
                          

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
        with open('uids.txt', 'r') as f:
            uids = f.read()
            print("Uids", uids)
            if(uid not in uids):
                with open('uids.txt', 'a') as fw:
                    fw.write(uid + "\n")

    def getKnownUids(self):
        return self.known_uids

    def clearKnownUids(self):
        self.known_uids.clear()            