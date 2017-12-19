import configparser
import server
import channel
import message
import time
import datetime

# Bot class

class Bot:

    myversion = "drachbot 0.2-BETA"

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


        #testing
        time.sleep(1)
        self.ircserver.SendLine("JOIN #test")
        self.ircserver.SendLine("JOIN #drachbot")
        self.ircserver.SendLine("JOIN #frufru")

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
            curtime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
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
            elif command_part == "471":
                # cannot join channel (full)
                print ("Can't join channel "+text.split()[3]+ ": Channel is full (+l)")
                return
            elif command_part == "473":
                # cannot join channel (invite only)
                print ("Can't join channel "+text.split()[3]+ ": Must be invited (+i)")
                return
            elif command_part == "474":
                # cannot join channel (banned)
                print ("Can't join channel "+text.split()[3]+ ": Banned (+b)")
                return
            elif command_part == "475":
                # cannot join channel (bad key)
                print ("Can't join channel "+text.split()[3]+ ": Bad key (+k)")
                return
            elif command_part == "PRIVMSG":
                privmsg = message.Message(text)

                if privmsg.is_ctcp:
                    self.handle_ctcp(privmsg)
                    return

                if privmsg.destination == self.botnick:
                    # PRIVMSG to us 
                    self.handleBotPM(privmsg)
                else:
                    # PRIVMSG to channel
                    self.handleChannelPM(privmsg)


            elif command_part == "JOIN":
                irc_result = message.Message(text)
                if irc_result.nick == self.botnick:
                    print ("I joined "+ text.split()[2])
                else:
                    print (irc_result.nick + " joined " + text.split()[2])
            elif command_part == "KICK":
                irc_result = message.Message(text)
                if irc_result.nick == self.botnick:
                    print ("I kicked "+text.split()[3]+" from "+irc_result.destination)
                elif text.split()[3] == self.botnick:
                    print ("I was kicked from "+irc_result.destination+" by "+irc_result.nick)
                else:
                    print (text.split()[3]+" was kicked from "+irc_result.destination+" by "+irc_result.nick)
            elif command_part == "PART":
                irc_result = message.Message(text)
                if irc_result.nick == self.botnick:
                    print ("I left "+irc_result.destination)
                else:
                    print (irc_result.nick+" left "+irc_result.destination)
            elif command_part == "NOTICE":
                input_to_process = message.Message(text)
            else:
                return
                

            # do stuff ...

        except:
            raise

    def handle_ctcp(self, msg):
        if msg.message.startswith("VERSION"):
            self.SendCTCPReply(msg.nick, "VERSION "+ Bot.myversion)

    def is_channel(self, name):
        if name.startswith("#") or name.startswith("&"):
            return True
        else:
            return False
    
    def SendPrivmsg(self, dest, text):
        self.ircserver.SendLine("PRIVMSG " + dest + " :" + text)

    def SendNotice(self, dest, text):
        self.ircserver.SendLine("NOTICE " + dest + " :" + text)

    def SendCTCPReply(self, dest, text):
        self.SendNotice(dest, "\001"+text+"\001")

    def handleChannelPM(self, privmsg):
        self.SendPrivmsg(privmsg.destination, privmsg.nick + ": hi!")

    def handleBotPM(self, privmsg):
        self.SendPrivmsg(privmsg.nick, "how's it going, " + privmsg.nick + "?")
