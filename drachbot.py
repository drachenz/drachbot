#!/usr/bin/python3

import socket
import time
import sys
import datetime
import subprocess
import json
import requests
import configparser

# set to conf file name. default is drachbot.ini
confname = "drachbot.ini"
config = configparser.ConfigParser()
config.read(confname)

# get config settings from config file
server = config.get('bot', 'server')
server_port = int(config.get('bot', 'port'))
botnick = config.get('bot', 'nick')
adminname = config.get('bot', 'admin')
logfile = config.get('bot', 'logfile')
google_API = config.get('bot', 'google_api')
news_API = config.get('bot', 'news_api')
wunderground_API = config.get('bot', 'wunderground_api')

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

my_channels = []

def connect():
    ircsock.connect((server, server_port))
    time.sleep(1)
    ircsock.send(bytes("USER " + botnick + " 8 * :"+botnick+"\r\n", "UTF-8"))
    time.sleep(1)
    ircsock.send(bytes("NICK " + botnick + "\r\n", "UTF-8"))
    time.sleep(1)

def servermsg(msg):
    logmsg("> "+msg + "\n")
    send(msg)

def joinchan(channel):
    sendtxt = "JOIN " + channel
    #print(sendtxt)
    servermsg(sendtxt)

def logmsg(msg):
    file = open(logfile, 'at')
    curtime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
    file.write(curtime + " " + msg)
    file.close

def send(msg):
    ircsock.send(bytes(msg + "\r\n", "UTF-8"))

def getaline(socket):
    mybuffer = socket.recv(4096).decode("UTF-8")
    buffering = True
    while buffering:
        if "\r\n" in mybuffer:
            (line, mybuffer) = mybuffer.split("\r\n", 1)
            yield line + "\n"
        else:
            more = socket.recv(4096).decode("UTF-8")
            if not more:
                buffering = False
            else:
                mybuffer += more
    if mybuffer:
        yield mybuffer

def send_pong(txt):
    servermsg("PONG " + txt)

def send_quit(txt):
    servermsg("QUIT :" + txt)
    time.sleep(0.5)
    terminate()

def terminate():
    ircsock.close()
    exit()
    
def handle_joinevent(txt):
    fullhost, event, chan = txt.split()
    if fullhost[0] == ":":
        delim = fullhost.find("!")
        nick = fullhost[1:delim]
        identhost = fullhost[delim+1:]
        (ident, hostname) = identhost.split("@")
    else:
        delim = fullhost.find("!")
        nick = fullhost[0:delim]
        identhost = fullhost[delim+1:]
        (ident, hostname) = identhost.split("@")

    chan = chan[1:]

    if nick == botnick:
        logmsg("I JOINED "+chan +"\n")
        if chan in my_channels:
            logmsg("ODD: join event for channel i thought i was already in!\n")
        else:
            my_channels.append(chan)
    else:
        logmsg(nick + " JOINED " + chan + "\n")

def send_privmsg(dest, txt):
    servermsg("PRIVMSG "+dest+ " :"+txt)

def partchan(channel):
    servermsg("PART " + channel)

def sendaction(dest, txt):
    servermsg("PRIVMSG "+dest+" :"+ "\x01" + "ACTION "+txt+"\x01")

def handle_privmsg(txt):
    # determine if someone msg'd us
    try:
        if txt.split()[2] == botnick:
            # msg to us
            fullhost = txt.split()[0]
            if fullhost[0] == ":":
                delim = fullhost.find("!")
                nick = fullhost[1:delim]
                identhost = fullhost[delim+1:]
                (ident, hostname) = identhost.split("@")
            else:
                delim = fullhost.find("!")
                nick = fullhost[0:delim]
                identhost = fullhost[delim+1:]
                (ident, hostname) = identhost.split("@")
    
            
            msgcontent = (txt.split())[3:]
            restofmsg = " ".join(msgcontent)[1:]
    
            #print("Received PRIVMSG to us from " + nick + " ident " + ident + " hostname "+hostname +" saying: "+restofmsg)
    
            if restofmsg == ".quit" and nick == adminname:
            #    print("boss said to quit!")
                send_quit("woot")
            if restofmsg.find(".join #") != -1 and nick == adminname:
                msgparts = restofmsg.split()
                if msgparts[0] == ".join" and msgparts[1][0] == "#":
                    if msgparts[1] in my_channels:
                        send_privmsg(nick, "Already in channel "+msgparts[1])
                    else:
                        joinchan(msgparts[1])
            if restofmsg.find(".part #") != -1 and nick == adminname:
                msgparts = restofmsg.split()
                if msgparts[0] == ".part" and msgparts[1][0] == "#":
                    if msgparts[1] in my_channels:
                        partchan(msgparts[1])
                    else:
                        send_privmsg(nick, "Not in channel "+msgparts[1])
            if restofmsg.split()[0] == ".me":
                if restofmsg.split()[1][0] != "#":
                    send_privmsg(nick, "format: .me #channel txt")
                else:
                    sendaction(restofmsg.split()[1], " ".join(restofmsg.split()[2:]))
        else:
            # msg send to channel. check if it's a command (starts with !)
            msgcontent = (txt.split())[3:]
            restofmsg = " ".join(msgcontent)[1:]
            if restofmsg[0] == "!":
                # bot command rcvd
                if restofmsg.split()[0][1:].lower() == "fortune":
                    cmdout = subprocess.getoutput("fortune -s -o")
                    fmtcmd = " ".join(cmdout.split("\n"))
                    fmtcmd = fmtcmd.replace("\t", "")
                    send_privmsg(txt.split()[2], fmtcmd)
                if restofmsg.split()[0][1:].lower() == "news":
                    send_privmsg(txt.split()[2], get_news())
                if restofmsg.split()[0][1:].lower() == "tv":
                    send_privmsg(txt.split()[2], get_tvshow(" ".join(restofmsg.split()[1:])))
                if restofmsg.split()[0][1:].lower() == "w":
                    send_privmsg(txt.split()[2], get_weather(" ".join(restofmsg.split()[1:])))
    except IndexError:
        logmsg("IndexError caught")
 
def get_weather(location):
    # use autocomplete api
    try:
        cities = requests.get('http://autocomplete.wunderground.com/aq?query='+location)
        querydata = cities.json()

        if len(querydata['RESULTS']) < 1:
            return "No matches found"
        else:
            # get first match's api url
            apiurl = querydata['RESULTS'][0]['l']
            r = requests.get('http://api.wunderground.com/api/'+wunderground_API+'/conditions/forecast/alerts/'+apiurl+'.json')
            jsondata = r.json()
            locationname = jsondata['current_observation']['display_location']['full']
            locationcountry = jsondata['current_observation']['display_location']['country']
            obstime = jsondata['current_observation']['observation_time']
            conditions = jsondata['current_observation']['weather']
            tempstr = jsondata['current_observation']['temperature_string']
            wind = jsondata['current_observation']['wind_string']
            humidity = jsondata['current_observation']['relative_humidity']
            feelslike = jsondata['current_observation']['feelslike_string']

            # forecast info

            # if forecast country is US display non-metric string, otherwise go metric!


            todayfcst_day = jsondata['forecast']['txt_forecast']['forecastday'][0]['title']
            if jsondata['current_observation']['display_location']['country'] != "US":
                todayfcst_txt = jsondata['forecast']['txt_forecast']['forecastday'][0]['fcttext_metric']
            else:
                todayfcst_txt = jsondata['forecast']['txt_forecast']['forecastday'][0]['fcttext']

            # alerts

            if len(jsondata['alerts']) > 0:
                alertdesc = jsondata['alerts'][0]['description']
                alertexp = jsondata['alerts'][0]['expires']
                alerttxt = "ALERT: " + alertdesc + " until " + alertexp
            else:
                alerttxt = ""

            retstr = locationname+", "+locationcountry+" Conditions: "+conditions+" "+tempstr \
                +". Relative humidity: "+humidity + ". Wind: "+ wind + ". Feels like: " + feelslike \
                + ". " + obstime + " - " + todayfcst_day + ": " + todayfcst_txt + " " + alerttxt

            if len(querydata['RESULTS']) > 1:
                return retstr + " (multiple matches found, picked first result)"
            else:
               return retstr
     
    except ValueError:
        return "Can't find location"
    except KeyError:
        return "Can't find details for that location, try another location"

def get_news():
    r = requests.get('https://newsapi.org/v1/articles?source=associated-press&sortBy=top&apiKey='+news_API)
    jsondata = r.json()
    
    artnum=1
    artlist = ""
    for article in jsondata['articles']:
        if artnum <= 4:
            artlist += str(artnum)+") "+ article['title'] + " [" + shorturl(article['url'])+ "] "
            artnum = artnum + 1

    return artlist

def shorturl(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key='+google_API
    payload = {'longUrl': url}
    headers = {'Content-Type':'application/json'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    return r.json()['id']

def get_tvshow(showname):
    retval = ""
    try:
        r = requests.get('http://api.tvmaze.com/singlesearch/shows?q=' + showname)
        jsondata = r.json()

        title = jsondata['name']

        rating = jsondata['rating']['average']
        if jsondata['premiered'] is None:
            premieryr = jsondata['status']
        else:
            premieryr = jsondata['premiered'][:4]
        showtype = jsondata['type']
        if jsondata['genres'] == []:
            genres = jsondata['type']
        else:
            genres = jsondata['genres']
            genres = ",".join(genres)
            genres = showtype + ": "+ genres
        showlen = jsondata['runtime']

        if jsondata['network'] is None:
            if jsondata['webChannel'] is None:
                network = "N/A"
            else:
                network = jsondata['webChannel']['name']
                country = jsondata['webChannel']['country']['code']
        else:
            network = jsondata['network']['name']
            country = jsondata['network']['country']['code']

        if jsondata['status'] == "Ended":
            nextepstr = " ~ Show has ended"
        else:
            try:
                nextepurl = jsondata['_links']['nextepisode']['href']
                nr = requests.get(nextepurl)
                njsondata = nr.json()
                nextepname = njsondata['name']
                nextepseason = njsondata['season']
                nextepnum = njsondata['number']
                nextepairdate = njsondata['airdate']
                nextepstr = " ~ Next episode: S"+str(nextepseason)+"E"+str(nextepnum)+" \""+nextepname+"\" airs on "+nextepairdate
            except KeyError:
                nextepstr = " ~ Next episode unannounced"

        retval = "["+title+"] "+country+", "+premieryr+", "+network+", "+str(showlen)+"min. ~ " + genres + nextepstr

    except ValueError:
        retval = "can't find it"
    return retval

def handle_kickevent(txt):
    (fullhostname, cmd, channel, nick, reason) = txt.split(maxsplit=5)
    if nick == botnick:
       # we were kicked
       if channel in my_channels:
          my_channels.remove(channel)
       else:
          logmsg("ODD! kicked from a channel ("+channel+") i didn't even know I was in!\n")

def handle_partevent(txt):
    (fullhostname, cmd, channel) = txt.split(maxsplit=3)
    if fullhostname[0] == ":":
        delim = fullhostname.find("!")
        nick = fullhostname[1:delim]
        identhost = fullhostname[delim+1:]
        (ident, hostname) = identhost.split("@")
    else:
        delim = fullhostname.find("!")
        nick = fullhostname[0:delim]
        identhost = fullhostname[delim+1:]
        (ident, hostname) = identhost.split("@")

    if nick == botnick:
        logmsg("I parted "+channel+"\n")
        my_channels.remove(channel)
    else:
        logmsg(nick + " parted " + channel)

def process_input(txt):
    # handle input and determine how to reply

    # easiest case, send PONG reply
    if txt.find("PING") != -1:
        send_pong(txt.split()[1])

    if txt.split()[1] == "PRIVMSG":
        handle_privmsg(txt)

    if txt.split()[1] == "JOIN":
        handle_joinevent(txt)

    if txt.split()[1] == "KICK":
        handle_kickevent(txt)

    if txt.split()[1] == "PART":
        handle_partevent(txt)

def main():
    connect()

    while 1:
        time.sleep(0.1)
        
        for ircmsg in getaline(ircsock):
            logmsg(ircmsg)
            process_input(ircmsg)

      

main()

