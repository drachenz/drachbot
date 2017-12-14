#!/usr/bin/env python3

import bot
import server
import channel
import time

if __name__ == "__main__":
    mybot = bot.Bot("drachbot.ini")
    while 1:
        try:
            mybot.Start()
        except ConnectionError:
            print("Connection error occurred... reconnecting")
            time.sleep(20)
        except:
            raise


