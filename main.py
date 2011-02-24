import kivy
kivy.require('1.0.4')

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.label import Label

#load cached movie feed data
import shelve, random
from movie import Movie
movies = shelve.open('movie.shelve')




class InfoScreen(FloatLayout):
    progress = NumericProperty(0.0)
    def on_progress(self, instance, value):
        print value
        if value > 0.1:

            m = random.choice(movies.values())
            self.title = m.title
            self.trailer = m.trailer



class CinemaKiosk(App):

    def build(self):
        info_screen = InfoScreen()
        info_screen.movie_name = 'apollo18'
        return info_screen



CinemaKiosk().run()



