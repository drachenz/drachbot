import configparser
import server
import channel
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
