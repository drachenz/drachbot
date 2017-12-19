import bot

# Channel class

class Channel:
    channels = []
    num_channels = 0

    def __init__(self, bot, channel):
        self.channel = channel
        self.bot = bot
        self.on = False
        self.error = "joining"
        self.Join(self.channel)

    def __del__(self):
        pass

    def Send(self, text):
        self.bot.SendPrivmsg(self.channel, text)

    def Join(self, channel):
        self.channels.append(channel)
        num_channels += 1

    def UpdateStatus(self, status, error):
        pass
