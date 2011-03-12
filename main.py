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
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.utils import kvquery

from kivy.graphics import *
from kivy.properties import *


from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.video import Video
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import ScatterPlane, Scatter
from kivy.animation import Animation
from functools import partial





# local impots & globals ##############################################
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




class Viewport(ScatterPlane):
    def __init__(self, **kwargs):
        kwargs['do_scale'] = False
        kwargs['do_rotation'] = False
        kwargs['do_translation'] = False
        kwargs['size_hint'] = (None, None)
        super(Viewport, self).__init__(**kwargs)

    def fit_to_window(self, *args):
        if Window.height > Window.width:
            self.scale = Window.width/float(self.width)
        else:
            self.scale = Window.height/float(self.width)
            self.rotation = 90
        self.pos = (0,0)
        for sc in self.children:
            for s in sc.children:
                print s.__class__, s.size


'''
class MovieView(BoxLayout):
    __metaclass__ = KivyWidgetMetaClass

    video = ObjectProperty(None)
    muted = BooleanProperty(True)
    movie = ObjectProperty(None)
    movie_title   = StringProperty('N/A')
    movie_summary = StringProperty('N/A')
    movie_trailer = StringProperty('')
        
    def setup(self, *args):
        self.video = kvquery(self, kvid='video').next()

    def play(self, *args):
        if self.video:
            self.video.source = ''
            self.video.source = self.movie.trailer
            self.video.play = True
            print self.muted, "ASASASAS"
            if self.muted:
                print "MUTING"
                self.video.volume = 0

    def stop(self, *args):
        if self.video:
            self.video.play = False

    def on_movie(self, instace, movie):
        self.movie_title   = movie.title
        self.movie_summary = movie.summary

        if self.video:
            self.video.source = ''
            self.video.source = movie.trailer
            self.video.play = False


class FeaturedMovie(MovieView):
    pass
'''




class AppScreen(BoxLayout):
    app = ObjectProperty(None)

    def hide(self, *args):
        anim = Animation(x=-1080.0, t='out_quad')
        anim.start(self)

    def show(self, *args):
        self.x = 1080
        anim = Animation(x=0.0, t='out_quad')
        anim.start(self)



class InfoScreen(AppScreen):
    movie = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        self.fixed_layer = Widget(size_hint=(0,0), size=(0,0))
        self.add_widget(self.fixed_layer)

        self.video = Video(text="video", pos=(0,900), size=(1080, 620))
        self.video.volume = 1.0
        self.fixed_layer.add_widget(self.video)
        self.movie = self.app.get_random_movie()

        def print_self(*args):
            print self.pos, self.size, self.video.pos
        Clock.schedule_interval(print_self, 1.0)

        self.size = (1080,1921)

    def hide(self, *args):
        anim = Animation(x=-1080.0, t='out_quad')
        anim.start(self)
        anim.start(self.video)
        self.video.play = False

    def show(self, *args):
        self.x = 1080
        self.video.x = 1080
        anim = Animation(x=0.0, t='out_quad')
        anim.start(self)
        anim.start(self.video)



    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.app.goto(self.app.movie_screen)



    def on_movie(self, *args):
        self.video.play = False
        self.video.source = ''
        self.video.source = self.movie.trailer
        self.video.bind(on_eos=self.on_movie)
        self.video.play = True
        



class ThumbnailTitle(Label):
    pass
class ThumbnailDetails(Label):
    pass
class ThumbnailVideo(Video):
    pass

class MovieThumbnail(BoxLayout):
    movie = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MovieThumbnail, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.title = ThumbnailTitle(text='Movie Title')
        self.video = ThumbnailVideo()
        self.details = ThumbnailDetails(text='Movie Details')
        self.add_widget(self.title)
        self.add_widget(self.video)
        self.add_widget(self.details)
        self.add_widget(Widget()) #padding

    def on_movie(self, *args):
        if not self.movie:
            return

        self.title.text = self.movie.title
        self.title.text_size = (250, None)
        self.details.text = self.movie.summary[:200]+'...'
        self.details.text_size = (300, None)
        self.video.source = ''
        self.video.source = self.movie.trailer
        self.video.volume = 0
        self.video.play = False
        self.video.bind(on_eos=self.on_movie)
        Clock.schedule_once(self.play, 0.5)

    def play(self, *args):
        self.video.play = True

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.parent.select_movie()
            return True

class MovieTitle(Label):
    pass

class MovieSummary(Label):
    pass

class MovieVideo(Video):
    pass

class BuyButton(Button):
    pass

class BuyingOverlay(BoxLayout):
    num_adults = NumericProperty(2)
    num_kids = NumericProperty(0)

    def finish_buy(self, *args):
        self.parent.parent.finish_buy(*args)

class MovieScreen(AppScreen):
    '''MovieScreen, lets user select a movie, and see related movies
    '''
    def __init__(self, **kwargs):
        super(MovieScreen, self).__init__(**kwargs)
        def print_self(*args):
            print self.pos, self.size, self.video.pos
        Clock.schedule_interval(print_self, 1.0)

        self.movie = self.app.get_random_movie()

        self.fixed_layer = Widget()
        self.add_widget(self.fixed_layer)

        #video player
        self.video = MovieVideo(text="video", pos=(1080,1000), size=(1080, 620))
        self.video.volume = 1.0
        self.fixed_layer.add_widget(self.video)

        self.movie_title = MovieTitle(text='Movie Title', pos=(1080,850), width=1080)
        self.fixed_layer.add_widget(self.movie_title)

        self.movie_text = MovieSummary(text='Summary', x=1080, width=1080)
        self.fixed_layer.add_widget(self.movie_text)


        #buying tickets
        self.buy_btn = BuyButton(size=(1080*.3,100), pos=(1080*.7,850))
        self.buy_btn.bind(on_release=self.start_buy)
        self.fixed_layer.add_widget(self.buy_btn)

        self.buy_widget = BuyingOverlay(x=1080)
        self.fixed_layer.add_widget(self.buy_widget)


        #ADD Images
        self.ad_image = Image(pos=(1080,1920*0.4), size=(1080,1920*0.6))
        self.fixed_layer.add_widget(self.ad_image)
        self.select_ad()

        #movie_suggestions
        self.bottom_layer = BoxLayout(size=(1080,1920*0.4))
        self.fixed_layer.add_widget(self.bottom_layer)

        self.trailer1 = MovieThumbnail(text="trailer 1")
        self.trailer1.movie = self.app.get_random_movie()
        self.bottom_layer.add_widget(self.trailer1)

        self.trailer2 = MovieThumbnail(text="trailer 2")
        self.trailer2.movie = self.app.get_random_movie()
        self.bottom_layer.add_widget(self.trailer2)

        self.trailer3 = MovieThumbnail(text="trailer 3")
        self.trailer3.movie = self.app.get_random_movie()
        self.bottom_layer.add_widget(self.trailer3)

        #self.movie_view =  kvquery(self, kvid='feature').next()
    def select_movie(self, *args):
        anim = Animation(y=-400, t='out_quad')
        anim.start(self.bottom_layer)

        anim2 = Animation(x=-1080, t='out_quad')
        anim2.start(self.ad_image)

        anim3 = Animation(x=(1080*.7 -10), t='out_quad')
        anim3.start(self.buy_btn)


        anim4 = Animation(x=0, t='out_quad')
        anim4.start(self.video)
        anim4.start(self.movie_title)
        anim4.start(self.movie_text)

        self.movie = self.app.get_random_movie()
        self.movie_title.text = self.movie.title
        self.movie_title.text_size = (1030,500)
        self.movie_title.halign = 'left'
        self.movie_text.text = self.movie.summary[:800]
        
        self.movie_text.text_size = (1030,500)
        self.video.play = False
        self.video.source = ''
        self.video.source = self.movie.trailer
        self.video.play = True



    def select_ad(self, *args):
        self.ad_image.source = self.app.get_random_ad()
        Clock.schedule_once(self.select_ad, 2.0)

    def finish_buy(self, *args):
        self.app.goto(self.app.thank_you_screen)

    def start_buy(self, touch):
        anim = Animation(x=0, t='out_elastic')
        anim.start(self.buy_widget)


    def next_movie(self, *args):
        pass
        #self.movie_view.movie = self.app.get_random_movie()
        #self.movie_view.play()
 
    def hide(self, *args):
        self.video.play = False
        anim = Animation(x=-1080, t='out_quad')
        anim.start(self.bottom_layer)

        anim2 = Animation(x=-1080, t='out_quad')
        anim2.start(self.ad_image)

        anim3 = Animation(x=-1080, t='out_quad')
        anim3.start(self.video)
    
        self.buy_btn.x = 1920
        self.movie_title.x=1080
        self.movie_text.x=1080
        self.buy_widget.x=1080


    def show(self, *args):

        self.buy_btn.x = 1920
        self.bottom_layer.pos = (1080,0)
        self.ad_image.x = 1080
        self.video.x = 1080

        anim = Animation(x=0, t='out_quad')
        anim.start(self.bottom_layer)
 
        anim2 = Animation(x=0, t='out_quad')
        anim2.start(self.ad_image)

        self.movie_title.x=1080
        self.movie_text.x=1080


class ThankYouScreen(AppScreen):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.app.goto(self.app.info_screen)






class MovieKiosk(zmqapp.ZmqControlledApp):
    '''MovieKioskApp is the application controler.
    '''

    def get_random_movie(self):
        return random.choice(movies.values())
     
    def get_random_movies(self, n=3):
        return random.sample(movies.values(), n)



    def get_random_ad(self):
        return random.choice(['images/ad1.png', 'images/ad2.png'])


    def goto(self, screen, animation=True):
        if screen == self.active_screen:
            return
        
        self.active_screen.hide()
        self.layout.remove_widget(screen)
        self.layout.add_widget(screen)
        screen.show()
        self.active_screen = screen


    def start(self, *args):
        self.movie_screen.hide()
        self.thank_you_screen.hide()
        self.info_screen.show()
        self.active_screen = self.info_screen


    def build(self):

        root = Widget(size=(1080,1920), size_hint=(None, None))
        

        self.info_screen = InfoScreen(app=self)
        root.add_widget(self.info_screen)

        self.movie_screen = MovieScreen(app=self)
        root.add_widget(self.movie_screen)

        self.thank_you_screen = ThankYouScreen(app=self)
        root.add_widget(self.thank_you_screen)

        self.layout = root
        viewport = Viewport(size=(1080,1920))
        Clock.schedule_once(viewport.fit_to_window)
        viewport.add_widget(Image(source='images/mainbg.png', pos=(0,0), size=(1080,1920)))
        viewport.add_widget(root)
        viewport.add_widget(Image(source='images/logo.png', y=1620, size=(1080,300)))

        Clock.schedule_once(self.start)
        return viewport


if __name__ == '__main__':
    MovieKiosk().run()

