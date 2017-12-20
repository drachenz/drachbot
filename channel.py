import bot

# Channel class

class Channel:

    def __init__(self, name, key=False):
        self.name = name
        self.key = key
        self.on = False

    def __del__(self):
        pass

