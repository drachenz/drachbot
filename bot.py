import configparser
import server
import channel

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
        self.ircserver = server.Server()
        self.ircserver.Connect(self.server, self.server_port, self.botnick)

    def Exit(self):
        pass


