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


class AppScreen(FloatLayout):
    transition = NumericProperty(0.0)
    def __init__(self, **kwargs):
        super(AppScreen, self).__init__(**kwargs)
        self.setup()
    def setup(self):
        pass



class InfoScreen(AppScreen):
    title = StringProperty('Movie Title')
    trailer = StringProperty('')

    def setup(self):
        self.switch_movie()

    def switch_movie(self, movie_name="_random_"):
        m = movies.get(movie_name, random.choice(movies.values()) )
        self.title = m.title
        self.trailer = m.trailer
        self.progress = 0.0

    progress = NumericProperty(0.0)
    def on_progress(self, instance, value):
        if value > 0.1:
            instance.switch_movie()



class WelcomeScreen(AppScreen):
    title = StringProperty('Movie Title')
    summary = StringProperty('Summary...')
    trailer = StringProperty('')

    def setup(self):
        self.switch_movie()

    def switch_movie(self, movie_name="_random_"):
        m = movies.get(movie_name, random.choice(movies.values()) )
        self.title = m.title
        self.summary = m.summary[:min(100,len(m.summary))]
        self.trailer = m.trailer




class CinemaKiosk(App):

    def build(self):
        info_screen = WelcomeScreen()
        #info_screen.movie_name = 'apollo18'
        return info_screen


CinemaKiosk().run()



