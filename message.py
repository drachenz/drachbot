# class to parse messages received by the client

class Message:

    def __init__(self, text):

        hostpart = text.split()[0]
        delim = hostpart.find("!")
        self.nick = hostpart[1:delim]
        identhost = hostpart[delim+1:]
        (self.ident, self.hostname) = identhost.split("@")

        self.command = text.split()[1]
        self.destination = text.split()[2]
        
        msgcontent = (text.split())[3:]
        self.message = " ".join(msgcontent)[1:]
