import requests
import sqlite3

# POST_URL = 'https://brass-cobra-cape.wayscript.cloud/postQueue'
# FETCH_URL = 'https://brass-cobra-cape.wayscript.cloud/getQueue'
# DELETE_URL = 'https://brass-cobra-cape.wayscript.cloud/clearUidQueue'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'za-warudo'
}

class MessageQueue:


    def postToQueue(self, uid: int, message:str):
        print("Posting to queue", uid, message)
        

        try:
            with sqlite3.connect('queue.db') as con:
                cur = con.cursor()
                cur.execute('INSERT INTO Queue (uid, message) VALUES (?,?)', [int(uid), message])

                con.commit()

        except Exception as e:
            print(str(e))
            con.rollback()

        finally:
            con.close()      

    def getInQueue(self, uid: int):

        print("Fetching queue for uid: ", uid)
        messages = None
        
        try:
            with sqlite3.connect('queue.db') as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM Queue WHERE uid=?', [int(uid)])
                messages = cur.fetchall()

        except Exception as e:
            print(str(e))
            con.rollback()

        finally:
            con.close()
        
        return messages

    def removeFromQueue(self, uid: int):



        try:
            with sqlite3.connect('queue.db') as con:
                cur = con.cursor()
                cur.execute('DELETE FROM Queue WHERE uid=?', [int(uid)])
                con.commit()
            
        except Exception as e:
            print(str(e))
            con.rollback()

        finally:
            con.close()