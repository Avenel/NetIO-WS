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

      client_data = payload
      if verbose_level >-1 :
          status = "################# client >" + client_ip + "< send >" + client_data + "<"
          print status
          log_buffer.append(status)

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
