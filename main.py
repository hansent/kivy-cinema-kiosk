import kivy
kivy.require('1.0.4')

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ListProperty, \
        ObjectProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory

# load cached movie feed data
import shelve
from random import choice, randint
movies = shelve.open('movie.shelve')

# our widgets
from pagelayout import PageLayout


class AppScreen(FloatLayout):
    transition = NumericProperty(0.0)


class InfoScreen(AppScreen):
    play = BooleanProperty(True)
    app = ObjectProperty(None)
    movie = ObjectProperty(None)
    progress = NumericProperty(0.0)

    def __init__(self, app, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)

    def on_movie(self, instance, m):
        self.title = m.title
        self.trailer = m.trailer
        self.progress = 0.0

    '''XXX Thomas, dunno why the switch movie was needed
    if needed, pass again through the app controler
    def on_progress(self, instance, value):
        if value > 0.1:
            instance.switch_movie()
    '''


class MovieThumbnail(Widget):
    play = BooleanProperty(True)
    app = ObjectProperty(None)
    movie = ObjectProperty(None)

class WelcomeScreen(AppScreen):
    play = BooleanProperty(True)
    app = ObjectProperty(None)
    movies = ListProperty([None, None, None])

    def __init__(self, app, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        self.app = app
        self.get_random_movies()

    def get_random_movies(self):
        available = movies.values()[:]
        result = []
        for x in xrange(3):
            if not len(available):
                break
            index = randint(0, len(available) - 1)
            m = available.pop(index)
            result.append(m)
        self.movies = result

class CinemaKiosk(App):
    '''CinemaKiosk is the application controler.
    '''

    def select_movie(self, moviethumbnail, is_preload=False):
        print 'movie selected', moviethumbnail
        # stop the welcome screen video, and add an info screen on the current
        # selected video
        if is_preload:
            # in preload, don't play, just preload.
            self.infoscreen = InfoScreen(
                self, movie=moviethumbnail.movie, play=False)
        else:
            # if the current selection is different, or new
            if not self.infoscreen or \
               self.infoscreen.movie != moviethumbnail.movie:
                self.infoscreen = InfoScreen(self, movie=moviethumbnail.movie)
            else:
                self.infoscreen.play = True
            self.welcome.play = False
            self.root.add_widget(self.infoscreen)
            self.root.select_page(self.infoscreen)

    def build(self):
        # first, create our initial page layout
        root = PageLayout(allow_touch_interaction=False)
        self.welcome = WelcomeScreen(self)
        root.add_widget(self.welcome)
        return root


if __name__ == '__main__':
    Factory.register('MovieThumbnail', cls=MovieThumbnail)
    CinemaKiosk().run()

