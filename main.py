import kivy
kivy.require('1.0.4')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.video import Video

import shelve
from movie import Movie

movies = shelve.open('movie.shelve')


class CinemaKiosk(App):

    def build(self):
        print "available movie trailers:", movies.keys()
        self.root.children[-1].source = movies.values()[0].trailer

        return self.root




CinemaKiosk().run()



