import socket
import sys
import time

# Server class

class Server:

    def Connect(self, server, server_port, botnick):
        try:
            self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsock.connect((server, server_port))
            time.sleep(1)
            self.ircsock.send(bytes("USER " + botnick + " 8 * :"+botnick+"\r\n", "UTF-8"))
            time.sleep(1)
            self.ircsock.send(bytes("NICK " + botnick + "\r\n", "UTF-8"))
            time.sleep(1)

            time.sleep(60)
        except:
            print("Some error occurred")
            raise


    def Disconnect(self):
        pass

    def SendLine(self, text):
        pass

    def GetLine(self):
        pass

