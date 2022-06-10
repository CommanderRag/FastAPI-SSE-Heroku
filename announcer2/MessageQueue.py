class MessageQueue:
    def __init__(self):
        self.queue = []


    def addToQueue(self, uid, message):

        alreadyInQueue = False
        for msg in self.queue:
            if(msg.get('uid' == uid)):
                messages = list(msg.get('messages'))
                messages.append(message)
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
            i = dict(i)
            del self.queue[i]

    def clearQueue(self):
        self.queue.clear()