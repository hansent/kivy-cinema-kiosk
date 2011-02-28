
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
            msg = self._zmq_pull_socket.recv_pyobj(zmq.NOBLOCK)
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
        self._zmq_push_socket.send_pyobj(msg)


if __name__ == "__main__":
    ctrl = ZmqAppController()
    while True:
        cmd = input("send message:")
        ctrl.send(cmd)
