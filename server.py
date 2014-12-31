#!/usr/bin/python
# -*- coding: utf-8 -*-
# server for netio server
# 2014-12-31 V2.1 by Martin Briewig
# Using NetIO core from Thomas Hoeser - Thank you!

###############################################################################
##
##  Copyright (C) 2013-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
                                       WebSocketServerFactory
from netio_config import HOST, PORT, light_dict,sensor_dict, time_multi, \
    debug_level,verbose_level,oscmd_Light, pickle_file,server_init_mode, \
    oscmd_Light2,timer_mode,t,lan_dict,log_level,log_file, openweather_path \


# Name to be used in NetIO for on and off
LightCmdOn     = "an"
LightCmdOff    = "aus"
LightCmdStatus = "status"
LightCmdStop   = "stop"

LanCmdOn     = "an"
LanCmdOff    = "aus"
LanCmdStatus = "status"

# The following dict looks odd - but I started wiht a different concept.
server_dict = { "read"   : "read",
                "licht"  : oscmd_Light,
                "licht2" : oscmd_Light2,
				"wetter" : "wetter",
				"temp"   : "Temp",
				"system" : "system",
				"timer"  : "Timer",
				"linux"	 : "Linux",
				"lan"    : "Lan",
				"log"	 : "Log",
				"gpio" : "gpio",
				"dict"   : "dict"
				}


# ring buffer for log entries
class RingBuffer:
    def __init__(self, size):
        self.data = [None for i in xrange(size)]
    def append(self, x):
        self.data.pop(0)
        self.data.append(x)
    def get(self):
        return self.data

max_log_entries = 100
log_buffer = RingBuffer(max_log_entries)
log_buffer.append("server definitions loaded")

id_dict_name = {
              '01d' : ['d_0_M','wolkenlos'],        # 'sky is clear'
              '01n' : ['n_0_M','wolkenlos'],        # 'sky is clear'
              '02d' : ['d_1_M','leicht_bewoelkt'],  # 'few clouds'
              '02n' : ['n_1_M','leicht_bewoelkt'],  # 'few clouds'
              '03d' : ['d_2_M','bewoelkt'],         # 'scattered clouds'
              '03n' : ['n_2_M','bewoelkt'],         # 'scattered clouds'
              '04d' : ['d_3_M','bedeckt'],          # 'broken clouds'
              '04n' : ['n_3_M','bedeckt'],          # 'broken clouds'
              '09d' : ['d_5_M','Schauer'],          # 'shower rain'
              '09n' : ['n_5_M','Schauer'],          # 'shower rain'
              '10d' : ['d_55_M','Regen'],           # 'Rain'
              '10n' : ['n_55_M','Regen'],           # 'Rain'
              '11d' : ['d_9_M','Gewitter'],         # 'Thunderstorm'
              '11n' : ['n_9_M','Gewitter'],         # 'Thunderstorm'
              '13d' : ['d_61_M','Schnee'],          # 'snow'
              '13n' : ['n_61_M','Schnee'],          # 'snow'
              '50d' : ['d_4_M','Nebel'],            # 'mist'
              '50n' : ['n_4_M','Nebel']             # 'mist'
                }

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        client_data = payload.decode('utf8')
        client_words = client_data.split(' ')
        client_cmd   = client_words[0]
        client_args  = len(client_words)

        if verbose_level >2 : print "client command >", client_cmd, "< with ", client_args, " arguments"

        # translate client command into server task
        client_cmd = client_cmd.lower()  # convert to lower case to avoid sensitivity
        server_cmd = str(server_dict.get(client_cmd))

        # if command is not listed in dictionary, return value is None
        if "None" == server_cmd:
            print "ERROR: client requested unknown command ", client_cmd
            print "-> please check spelling"
            print "-> commands are defined in server_dict{}, valid commands:"
            print server_dict.keys()
            print

            server_reply = "my dear client, your command is unknown: "
        else:
            if verbose_level >2 : print "client requested valid command", client_cmd
            # default message - should be set depending on command
            server_reply = "server will now process your command " + server_cmd

            # added "\n" for NetIO 2.0
            server_reply = server_reply + "\n"
            # send feedback to client
            if verbose_level >1: print "server reply: " , server_reply
            log_buffer.append(server_reply)

            # Netio - SetUp
            #   is sending "read commands" as a standard to poll status
            if ( "read" == client_cmd):
                # server_reply = "reply to netio std command " + client_cmd
                server_reply = 'listening'
                print server_reply

            # Netio - SetUp
            # 	Item			Label
            # 	reads			dict
            #   interval 		2000
            if ( "dict" == client_cmd):
                server_reply= str(light_state)

            if ( "log" == client_cmd):
                buff = "server log:\n"
                # ascending:
                # for i in log_buffer.get():
                #descending:
                for i in (max_log_entries-1,-1,-1):
                    if str(i) != 'None':
                        buff += str(i) + "\n"
                server_reply = buff
                print server_reply


            # NetIO - SetUp
            # 	Item			Switch
            #   onValue			1
            #   onText			An
            #   offText			Aus
            # 	onSend			Licht Wohnz An
            # 	offSend 	 	Licht Wohnz Aus
            # 	reads			Licht Wohnz Status
            #   parseResponse   \d+
            #   formatResponse  {0}
            if ( "licht" == client_cmd):
                server_reply = srvcmd_light(server_cmd,0,client_words,client_args)

            if ( "licht2" == client_cmd):
                server_reply = srvcmd_light(server_cmd,1,client_words,client_args)

            # NetIO - SetUp
            # 	Item			Switch
            # 	onSend			Timer Wohnz An 30
            # 	offSend 	 	Timer Wohnz Stop
            # 	reads			Timer Wohnz
            if ( "timer" == client_cmd):
                server_reply = srvcmd_timer(server_cmd,0,client_words,client_args)


            # NetIO - SetUp
            # 	Item			Label
            # 	reads			temp [Sensor Name]
            # 	interval 	 	2000
            # 	parseResponse	\d+
            #	formatResponse	{0},{1}°C
            if ( "temp" == client_cmd):
                Sensor = client_words[1]
                # print "die Temperatur wird vom 1-Wire Sensor oder aus der DB gelesen"
                server_reply = read_sensor(Sensor)

            # NetIO - SetUp
            # 	Item			Label
            # 	onSend			Linux [Sensor Name]
            if ( "linux" == client_cmd):
                server_reply = srvcmd_linux(server_cmd,client_words,client_args)

            # NetIO - SetUp
            # 	Item			Label
            # 	onSend			Lan [Host Name]
            if ( "lan" == client_cmd):
                server_reply = srvcmd_lan(server_cmd,client_words,client_args)


            if ( "wetter" == client_cmd):
                server_reply = srvcmd_weather(server_cmd,client_words,client_args)

            # NetIO - SetUp
            # 	Item			Label
            # 	reads			System CPU Temp
            if ( "system" == client_cmd):
                server_reply = systemInfo(server_cmd,client_words,client_args)

            # NetIO - SetUp
            # 	Item		Button
            # 	onSend  gpio set gpio7 1
            if ( "gpio" == client_cmd):
                server_reply = srvcmd_gpio(server_cmd,client_words,client_args)

        ## response to client
        self.sendMessage(server_reply, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

   try:
      import asyncio
   except ImportError:
      ## Trollius >= 0.3 was renamed
      import trollius as asyncio

   factory = WebSocketServerFactory("ws://localhost:9000", debug = False)
   factory.protocol = MyServerProtocol

   loop = asyncio.get_event_loop()
   coro = loop.create_server(factory, '127.0.0.1', 9000)
   server = loop.run_until_complete(coro)

   try:
      loop.run_forever()
   except KeyboardInterrupt:
      pass
   finally:
      server.close()
      loop.close()
