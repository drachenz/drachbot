import socket
import sys
import time
import bot

# Server class

class Server:

    def __init__(self, botinst):
        self.bot = botinst
    
    def Connect(self, server, server_port):
        try:
            self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ircsock.connect((server, server_port))
            botnick = self.bot.botnick
            time.sleep(1)
            self.SendLine("USER " + botnick + " 8 * :"+botnick)
            time.sleep(1)
            self.SendLine("NICK " + botnick)
            time.sleep(1)

        except:
            print("Some error occurred")
            raise


    def Disconnect(self):
        pass

    def SendLine(self, text):
        try:
            self.ircsock.send(bytes(text+"\r\n", "UTF-8"))
            self.bot.Log(">"+text+"\r\n")
        except:
            print("Some error occurred in Server.SendLine")
            raise


    def GetLine(self):
        try:
            mybuffer = self.ircsock.recv(4096).decode("UTF-8")
            buffering = True
            while buffering:
                if "\r\n" in mybuffer:
                    (line, mybuffer) = mybuffer.split("\r\n", 1)
                    yield line + "\n"
                else:
                    more = self.ircsock.recv(4096).decode("UTF-8")
                    if not more:
                        buffering = False
                    else:
                        mybuffer += more
            if not mybuffer:
                raise ConnectionError("Connection lost")
            else:
                yield mybuffer
        
        except:
            raise


