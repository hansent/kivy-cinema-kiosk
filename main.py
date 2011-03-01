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

import kivy
kivy.require('1.0.4')

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ListProperty, \
        ObjectProperty, BooleanProperty
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory

#zeroMQ for communicating with other processes 
import zmqapp

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

    def on_parent(self, instance, parent):
        if parent is None or not isinstance(parent, PageLayout):
            return
        parent.bind(on_page_transition=self.on_page_transition)

    def on_page_transition(self, instance, old_page, new_page, alpha):
        self.activated = (self == new_page)
        self.transition = alpha if self.activated else 1. - alpha


class IntroScreen(AppScreen):
    '''Play random movies
    '''
    movie = ObjectProperty(None)
    progress = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)

    def on_movie(self, instance, m):
        self.title = m.title
        self.trailer = m.trailer
        self.progress = 0.0

    def on_progress(self, instance, value):
        if value > 0.1:
            self.movie = self.app.get_random_movie()


class MovieScreen(AppScreen):
    '''Screen displayed after the selection screen
    '''
    movie = ObjectProperty(None)
    movies = ListProperty([None, None, None])



class MovieThumbnail(Widget):
    '''Thumbnail movie used in Welcome screen
    '''
    play = BooleanProperty(True)
    app = ObjectProperty(None)
    movie = ObjectProperty(None)


class WelcomeScreen(AppScreen):
    movies = ListProperty([None, None, None])

    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        self.movies = self.app.get_random_movies()



class CinemaKiosk(zmqapp.ZmqControlledApp):
    '''CinemaKiosk is the application controler.
    '''

    def get_random_movie(self):
        return choice(movies.values())


    def process_zmq_message(self, msg):
        person_count = msg.get('person_count', 0)
        if person_count == 0:
            self.show_intro()
            return

        if self.root.page_current == self.intro_screen:
            self.show_welcome()
        

    def get_random_movies(self, n=3):
        available = movies.values()[:]
        result = []
        for x in xrange(n):
            if not len(available):
                break
            index = randint(0, len(available) - 1)
            m = available.pop(index)
            result.append(m)
        return result

    def select_movie(self, moviethumbnail):
        print "selecting", moviethumbnail.movie.title
        self.movie_screen.movies = self.get_random_movies()
        self.movie_screen.movie = moviethumbnail.movie
        self.root.select_page(self.movie_screen)

    def show_welcome(self):
        self.root.select_page(self.welcome_screen)

    def show_intro(self):
        self.root.select_page(self.intro_screen)

    def build(self):
        root = PageLayout(allow_touch_interaction=False)

        # first screen that play random movie
        self.intro_screen = IntroScreen(app=self, movie=self.get_random_movie())
        root.add_widget(self.intro_screen)

        # welcome screen
        self.welcome_screen = WelcomeScreen(app=self)
        root.add_widget(self.welcome_screen)

        #movie screen
        self.movie_screen = MovieScreen(app=self, movie=self.get_random_movie())
        root.add_widget(self.movie_screen)

        return root


if __name__ == '__main__':
    Factory.register('MovieThumbnail', cls=MovieThumbnail)
    CinemaKiosk().run()

