import kivy
kivy.require('1.0.4')

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.label import Label

#load cached movie feed data
import shelve, random
from movie import Movie
movies = shelve.open('movie.shelve')




class InfoScreen(FloatLayout):
    title = StringProperty("Arthur")
    trailer = StringProperty("trailers/arthur-tlr1_h720p.mov")
    progress = NumericProperty(0.0)
    def on_progress(self, instance, value):
        print value
        if value > 0.1:
            
            m = random.choice(movies.values())
            instance.title = m.title
            instance.trailer = m.trailer
            instance.progress = 0.0



class CinemaKiosk(App):

    def build(self):
        info_screen = InfoScreen()
        info_screen.movie_name = 'apollo18'
        return info_screen



CinemaKiosk().run()



