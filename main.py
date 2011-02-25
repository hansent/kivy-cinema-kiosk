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
    app = ObjectProperty(None)
    activated = BooleanProperty(False)
    transition = NumericProperty(1.0)

    def on_page_transition(self, instance, old_page, new_page, alpha):
        print old_page, new_page, alpha

class InfoScreen(AppScreen):
    '''Play random movies
    '''
    play = BooleanProperty(True)
    movie = ObjectProperty(None)
    progress = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)

    def on_movie(self, instance, m):
        self.title = m.title
        self.trailer = m.trailer
        self.progress = 0.0

    def on_progress(self, instance, value):
        print 'on_progress', value
        if value > 0.1:
            self.movie = self.app.get_random_movie()

    def on_parent(self, instance, parent):
        if parent is None or not isinstance(parent, PageLayout):
            return
        parent.bind(on_page_transition=self.on_page_transition)


class MovidSelectionScreen(AppScreen):
    '''Screen displayed after the selection screen
    '''
    play = BooleanProperty(True)
    movie = ObjectProperty(None)


class MovieThumbnail(Widget):
    '''Thumbnail movie used in Welcome screen
    '''
    play = BooleanProperty(True)
    app = ObjectProperty(None)
    movie = ObjectProperty(None)

class WelcomeScreen(AppScreen):
    play = BooleanProperty(True)
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

    def get_random_movie(self):
        return choice(movies.values())

    def select_movie(self, moviethumbnail, is_preload=False):
        # stop the welcome screen video, and add an info screen on the current
        # selected video
        if is_preload:
            # in preload, don't play, just preload.
            self.movie_selection_screen = MovidSelectionScreen(
                app=self, movie=moviethumbnail.movie, play=False)
        else:
            # if the current selection is different, or new
            if not self.movie_selection_screen or \
               self.movie_selection_screen.movie != moviethumbnail.movie:
                self.movie_selection_screen = MovidSelectionScreen(app=self, movie=moviethumbnail.movie)
            else:
                self.movie_selection_screen.play = True
            self.welcome.play = False
            self.root.add_widget(self.movie_selection_screen)
            self.root.select_page(self.movie_selection_screen)

    def show_welcome(self):
        self.root.select_page(self.welcome_screen)
        self.welcome_screen.play = True
        self.info_screen.play = False

    def build(self):
        root = PageLayout(allow_touch_interaction=False)

        # first screen that play random movie
        self.info_screen = InfoScreen(app=self, movie=self.get_random_movie())
        root.add_widget(self.info_screen)

        # welcome screen
        self.welcome_screen = WelcomeScreen(app=self, play=False)
        root.add_widget(self.welcome_screen)

        return root


if __name__ == '__main__':
    Factory.register('MovieThumbnail', cls=MovieThumbnail)
    CinemaKiosk().run()

