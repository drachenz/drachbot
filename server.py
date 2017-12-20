import socket
import sys
import time
import bot
import ssl

# Server class

class Server:

    def __init__(self, botinst):
        self.bot = botinst
    
    def Connect(self, server, server_port, local_host, local_port):
        try:
            if self.bot.use_ipv6:
                self.ircsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if self.bot.use_ssl:
                self.ircsock = ssl.wrap_socket(self.ircsock)

            if local_host == "any":
                self.ircsock.bind((socket.gethostname(), local_port))
            else:
                self.ircsock.bind((local_host, local_port))

            self.ircsock.connect((server, server_port))
            botnick = self.bot.botnick
            time.sleep(1)
            self.SendLine("USER " + botnick + " 8 * :"+botnick)
            time.sleep(1)
            self.SendLine("NICK " + botnick)
            time.sleep(1)

        except Exception:
            raise


    def Disconnect(self):
        self.ircsock.close()

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


