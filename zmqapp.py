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


import kivy, zmq, inspect
kivy.require('1.0.4')
from kivy.app import App
from kivy.clock import Clock

class ZmqControlledApp(App):
    def __init__(self, **kwargs):
        super(ZmqControlledApp, self).__init__(**kwargs)

        #default port 5489 (kivy)
        self.zmq_controller_endp = kwargs.get('zmq_controller_endp', 'tcp://127.0.0.1:5489')
        
        self._zmq_context = zmq.Context()
        self._zmq_pull_socket = self._zmq_context.socket(zmq.PULL)
        self._zmq_pull_socket.connect(self.zmq_controller_endp)
        Clock.schedule_interval(self.pull_zmq_message, 0.1)

    def pull_zmq_message(self, *args):
        try:
            msg = self._zmq_pull_socket.recv_json(zmq.NOBLOCK)
            self.process_zmq_message(msg)
        except zmq.core.error.ZMQError:
            pass

    def process_zmq_message(self, msg):
            print "received", msg
            #methods = dict(inspect.getmembers(self , inspect.ismethod))
            #methods[msg]()


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
    while True:
        cmd = input("send message:")
        ctrl.send(cmd)
