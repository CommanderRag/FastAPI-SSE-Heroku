import queue
import time

class MessageAnnouncer:


    def __init__(self):
        self.listeners = []
        self.message = None
        self.connected_uids = []

    def listen(self):
        q = queue.Queue(maxsize = 6)
        self.listeners.append(q)
        return q

    def setMessage(self, message):
        self.message = message

    def clearMessage(self):
        self.message = None

    def getMessage(self):
        return self.message        

    def announce(self, message):

        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put(message)
            except queue.Full:
                print("Removing", i)
                del self.listeners[i]

    def clientConnected(self, uid):
        print("Adding", uid)
        self.connected_uids.append({'uid': uid, 'lastRefreshed': time.time()})            

    def clientDisconnected(self, uid):
        print("Removing", uid)
        for x in self.connected_uids:
            if(x.get('uid') == uid):
                self.connected_uids.remove(x)  

    def refresh(self, uid):
        for x in self.connected_uids:
            if(x.get('uid') == uid):
                x['lastRefreshed'] = time.time()