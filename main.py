import kivy
kivy.require('1.0.4')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.video import Video



class CinemaKiosk(App):

    def build(self):
        return self.root




CinemaKiosk().run()



