# class to parse messages received by the client

class Message:

    def __init__(self, text):

        try:
            hostpart = text.split()[0]
            delim = hostpart.find("!")
            if delim < 0:
                # this is not a hostname
                self.is_server = True
            else:
                self.is_server = False
                self.nick = hostpart[1:delim]
                identhost = hostpart[delim+1:]
                (self.ident, self.hostname) = identhost.split("@")

            self.command = text.split()[1]
            self.destination = text.split()[2]

            if self.command == "PRIVMSG":
                msgcontent = (text.split())[3:]
        
                self.message = " ".join(msgcontent)[1:]
                if self.message[0] == "\x01":
                    self.is_ctcp = True
                    self.message = self.message.strip("\x01")
                else:
                    self.is_ctcp = False
        except IndexError:
            self.message = " "
            self.is_ctcp = False
        except Exception:
            raise
