import time

class MessageAnnouncer:

    def __init__(self):
        self.message = None
        self.connected_uids = []

    def clientConnected(self, uid: int):
        print(str(uid) + " Connected.")
        self.connected_uids.append({'uid': uid, 'lastRefreshed': time.time(), 'newlyConnected': True})

    def clientDisconnected(self, uid: int):
        print(str(uid) + " Disconnected.")
        for x in self.connected_uids:
            if(str(x.get('uid')) == str(uid)):
                self.connected_uids.remove(x)

    def isNewlyConnected(self, uid: int):
        for i in self.connected_uids:
            if(str(i['uid']) == str(uid)):
                if(i.get('newlyConnected') != None):
                    return i['newlyConnected']

    def switchNewlyConnected(self, uid: int):
        for i in self.connected_uids:
            if(str(i['uid']) == str(uid)):
                if(i.get('newlyConnected') != None):
                    del i['newlyConnected']
                          

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

    def refresh(self, uid: int):
        for x in self.connected_uids:
            if(int(x['uid']) == int(uid)):
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