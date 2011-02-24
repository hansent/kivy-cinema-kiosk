import kivy
import feedparser
import subprocess


class Movie(object):
    def __init__(self, title, summary, trailer):
        self.title = title
        self.summary = summary
        self.trailer = trailer

    def __repr__(self):
        return "Title:%s trailer:%s" % (self.title, self.trailer)



def download_trailer(url):
    wget_args = ['wget', '-nv', '-N', '-U', 'QuickTime', url]
    subprocess.Popen(wget_args, cwd='trailers')


def get_movie_data():
    movies = []
    apple_rss = "http://trailers.apple.com/trailers/home/rss/newtrailers.rss"
    feed = feedparser.parse(apple_rss)
    for e in feed.entries:
        url = e.link.replace('apple.com/trailers', 'apple.com/movies')
        filename = url.split('/')[-2]+'-tlr1_h720p.mov'
        download_trailer(url+filename)
        m = Movie(e.title, e.summary, 'trailers/'+filename)
        movies.append(m)

    return movies


get_movie_data()












