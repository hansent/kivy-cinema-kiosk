import feedparser
import subprocess
import urllib
import shelve
import movie





def download_trailer(url):
    #first lets just open URL using fake user agent, to see if 
    # resource exists
    class QuickTimeURLopener(urllib.FancyURLopener):
        version = "Quicktime"
    urllib._urlopener = QuickTimeURLopener()
    if urllib.urlopen(url).getcode() != 200:
        return False  # no usch file...just ignore it

    #ok, have wget download it in teh background (unless already there)
    wget_args = ['wget', '-q', '-N', '-U', 'QuickTime', url]
    subprocess.Popen(wget_args, cwd='trailers')
    return True


def get_movie_data():
    movie_shelve = shelve.open('movie.shelve')

    apple_rss = "http://trailers.apple.com/trailers/home/rss/newtrailers.rss"
    feed = feedparser.parse(apple_rss)
    for e in feed.entries:
        #check if its a trailer
        if not e.title.endswith('Trailer'):
            continue
        #hack url for actual trailer video file
        url = e.link.replace('apple.com/trailers', 'apple.com/movies')
        key = str(url.split('/')[-2])
        filename = key+'-tlr1_h720p.mov'
        if download_trailer(url+filename):
            title = e.title.rsplit('-',1)[0].strip() # only want movie title
            movie = Movie(title, e.summary, 'trailers/'+filename)
            movie_shelve[key] = movie

    movie_shelve.close()



if __name__ == "__main__":
    print "Pulling newest trailer feed from apple.com..."
    get_movie_data()











