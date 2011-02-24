class Movie(object):
    def __init__(self, title, summary, trailer):
        self.title = title
        self.summary = summary
        self.trailer = trailer

    def __repr__(self):
        return "Title:%s | Trailer:%s" % (self.title, self.trailer)
