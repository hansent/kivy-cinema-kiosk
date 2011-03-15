#This file is part of the Kivy Cinema Kiosk Demo.
#    Copyright (C) 2010 by 
#    Thomas Hansen  <thomas@kivy.org>
#    Mathieu Virbel <mat@kivy.org>
#
#    The Kivy Cinema Kiosk Demo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Kivy Cinema Kiosk Demo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Kivy Cinema Kiosk Demo.  If not, see <http://www.gnu.org/licenses/>.

import sys, json, pprint
import zmq, inspect





class ZmqAppController(object):
    def __init__(self, endpoint='tcp://127.0.0.1:5489'):
        self.endpoint = endpoint
        self._zmq_context = zmq.Context()
        self._zmq_push_socket = self._zmq_context.socket(zmq.PUSH)
        self._zmq_push_socket.bind(endpoint)

    def send(self, msg):
        self._zmq_push_socket.send_json(msg)
        
    


if __name__ == "__main__":
    ctrl = ZmqAppController()
    kiosk_ctrl_msg = json.loads(open(sys.argv[1]).read())
    print "sending message:"
    pprint.pprint(kiosk_ctrl_msg)
    ctrl.send(kiosk_ctrl_msg)
