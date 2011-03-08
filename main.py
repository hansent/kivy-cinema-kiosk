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

# general imports ###################################################
import random
import shelve
import zmqapp # zeroMQ for inter processes communication


# kivy imports ######################################################
import kivy
kivy.require('1.0.4')

from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.utils import kvquery

from kivy.graphics import *
from kivy.properties import *


from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout






# local impots & globals ##############################################
from pagelayout import PageLayout
movies = shelve.open('movie.shelve')


class KivyWidgetMetaClass(type):  
    def __new__(cls, name, bases, attrs):  
        #replacement for original __init__ function
        original_init = attrs.get('__init__', bases[0].__init__)
        def alternate_init(self,*args,**kwargs):  
            original_init(self,*args,**kwargs)  
            if name == self.__class__.__name__: #dont call for each base class
                Clock.schedule_once(self.setup) #call setup next loop iteration
        attrs['__init__'] = alternate_init 
        return super(KivyWidgetMetaClass, cls).__new__(cls, name, bases, attrs)

    def __init__(self, name, bases, attrs):  
        super(KivyWidgetMetaClass, self).__init__(name, bases, attrs)
        Factory.register(name, self)
        print "Registered %s in kivy Widget Factory" % name 




class MovieView(BoxLayout):
    __metaclass__ = KivyWidgetMetaClass

    video = ObjectProperty(None)
    movie = ObjectProperty(None)
    movie_title   = StringProperty('N/A')
    movie_summary = StringProperty('N/A')
    movie_trailer = StringProperty('')
        
    def setup(self, *args):
        self.video = kvquery(self, kvid='video').next()
        Clock.schedule_interval(self.print_progress, 2.0)

    def print_progress(self, *args):
        print "\n:update:", self.video.play
        print self.video.eos
        print self.video.position
        print self.video.duration


    def on_movie(self, instace, movie):
        self.movie_title   = movie.title
        self.movie_summary = movie.summary

        if self.video:
            self.video.source = ''
            self.video.source = movie.trailer
            self.video.play = True
            self.video.volume = 0.00001
            self.video.bind(eos=self.parent.next_movie)

class FeaturedMovie(MovieView):
    pass





class AppScreen(FloatLayout):
    app = ObjectProperty(None)
    activated = BooleanProperty(False)
    transition = NumericProperty(1.0)

    def on_parent(self, instance, parent):
        if parent and isinstance(parent, PageLayout):
            parent.bind(on_page_transition=self.on_page_transition)

    def on_page_transition(self, instance, old_page, new_page, alpha):
        self.activated = (self == new_page)
        self.transition = alpha if self.activated else 1. - alpha


class MovieScreen(AppScreen):
    '''MovieScreen, lets user select a movie, and see related movies
    '''
    def __init__(self, **kwargs):
        super(MovieScreen, self).__init__(**kwargs)
        self.featured_mov =  kvquery(self, kvid='feature').next()

    def next_movie(self, *args):
        self.featured_mov.movie = self.app.get_random_movie()
 
            




class MovieKiosk(zmqapp.ZmqControlledApp):
    '''MovieKioskApp is the application controler.
    '''

    def get_random_movie(self):
        return random.choice(movies.values())
     
    def get_random_movies(self, n=3):
        return random.sample(movies.values(), n)

    def build(self):
        root = PageLayout(allow_touch_interaction=False)

        self.movie_screen = MovieScreen(app=self)
        root.add_widget(self.movie_screen)

        return root


if __name__ == '__main__':
    MovieKiosk().run()

