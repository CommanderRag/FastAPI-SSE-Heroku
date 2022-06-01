class MessageQueue:

    def __init__(self):
        self.queue = []
    

    def putInQueue(self, uid, message):
        for messages in self.queue:
            if (messages.get('uid') == uid):
                msg_list = messages.get('message')
                msg_list.append(message)
                print("Messages putInQueue", self.queue)
                return
        self.queue.append({'uid': str(uid).strip(), 'message': [message]})        
        

    def getInQueue(self, uid):
        for msg in self.queue:
            if(msg.get('uid') == uid):
                print("Messages getInQueue", self.queue)
                return msg.get('message')
        return None

    def removeFromQueue(self, uid):
        for msg in self.queue:
            if(msg.get('uid') == uid):
                self.queue.remove(msg)

    def removeOneMessageFromQueue(self, uid, msg):
        for messages in self.queue:
            if(messages.get('uid') == uid):
                msg_list = messages.get('message')
                msg_list.remove(msg)
                break         