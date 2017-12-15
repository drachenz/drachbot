import configparser
import server
import channel
import message
import time
import datetime

# Bot class

class Bot:

    def __init__(self,config_file):
        # read the conf file
        try:
            config = configparser.ConfigParser()
            config.read(config_file)

            self.server = config.get('bot', 'server')
            self.server_port = int(config.get('bot', 'port'))
            self.botnick = config.get('bot', 'nick')
            self.adminname = config.get('bot', 'admin')
            self.logfile = config.get('bot', 'logfile')
            self.google_API = config.get('bot', 'google_api')
            self.news_API = config.get('bot', 'news_api')
            self.wunderground_API = config.get('bot', 'wunderground_api')
            self.use_ipv6 = config.getboolean('bot', 'use_ipv6')
            self.use_ssl = config.getboolean('bot', 'use_ssl')
        except configparser.Error:
            # add more specific exceptions later
            print ("some error occurred with the config file")
            raise

    def Start(self):
        self.ircserver = server.Server(self)
        self.ircserver.Connect(self.server, self.server_port)

        while 1:
            time.sleep(0.1)

            for ircmsg in self.ircserver.GetLine():
                self.Log(ircmsg)
                self.process_input(ircmsg)

    def Exit(self):
        pass

    def Log(self, text):
        try:
            logf = open(self.logfile, 'at')
            curtime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
            logf.write(curtime + " " + text)
            logf.close
        except:
            print ("Some error occurred in Bot.Log")
            raise

    def process_input(self, text):
        # here's where things start getting complicated
        if text.startswith("PING"):
            self.ircserver.SendLine("PONG " + text.split()[1])
            return

        try:
            command_part = text.split()[1]

            # check key server errors first
            if command_part == "433":
                # NICK in use error, try to modify
                self.botnick = self.botnick+"_"
                self.ircserver.SendLine("NICK " + self.botnick)
            elif command_part == "432":
                # erroneous NICK... give up and let the user reconfig
                print ("Server reported we are giving it an invalid NICK... please reconfigure")
                exit(1)
            elif command_part == "PRIVMSG":
                input_to_process = message.Message(text)
            elif command_part == "JOIN":
                input_to_process = message.Message(text)
            elif command_part == "KICK":
                input_to_process = message.Message(text)
            else:
                return
                

            # do stuff ...

        except:
            raise


