class MessageQueue:

    def __init__(self):
        self.queue = []

    def addToQueue(self, uid: str, message:str):
        print("Adding to queue", uid, message)
        alreadyInQueue = False
        for msg in self.queue:
            print(msg)
            if(msg.get('uid') == uid):
                messages = list(msg.get('messages'))
                messages.append(str(message))
                alreadyInQueue = True   

        if(not alreadyInQueue):
            self.queue.append({'uid': str(uid), 'messages': [str(message)]})

    def getInQueue(self, uid):
        for msg in self.queue:
            msg = dict(msg)
            if(msg.get('uid') == uid):
                return msg 

        return None        

    def removeFromQueue(self, uid):
        for i in self.queue:
            if(i.get('uid') == uid):
                self.queue.remove(i)

    def clearQueue(self):
        self.queue.clear()
