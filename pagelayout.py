from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Canvas, RenderContext, Fbo, Color, Rectangle
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty, \
        NumericProperty, OptionProperty

fragment_header = '''
#ifdef GL_ES
precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;

/* uniform from page layout */
uniform float time;
uniform int t_direction;
uniform float t_alpha;
uniform vec2 size;
uniform vec2 uvsize;
'''

fragment_slide_previous = fragment_header + '''
void main() {
    vec2 uv = tex_coord0;
    uv.x -= transition * uvsize.x;
    gl_FragColor = frag_color * texture2D(texture0, uv);
}
'''

vertex_header = '''
#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* vertex attributes */
attribute vec2     vPosition;
attribute vec2     vTexCoords0;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;

/* uniform from page layout */
uniform float time;
uniform int t_direction;
uniform float t_alpha;
uniform vec2 size;
uniform vec2 uvsize;
'''

fragment_fade_previous = fragment_header + '''
void main(void) {
    vec4 c = frag_color * texture2D(texture0, tex_coord0);
    c.a = 1. - t_alpha;
    gl_FragColor = c;
}
'''

fragment_fade_current = fragment_header + '''
void main(void) {
    vec4 c = frag_color * texture2D(texture0, tex_coord0);
    c.a = t_alpha;
    gl_FragColor = c;
}
'''

vertex_slide_previous = vertex_header + '''
void main(void) {
  frag_color = color;
  tex_coord0 = vTexCoords0;
  vec2 pos = vPosition.xy;
  if (t_direction == 1)
    pos.x -= size.x * t_alpha;
  else
    pos.x += size.x * t_alpha;
  gl_Position = projection_mat * modelview_mat * vec4(pos, 0.0, 1.0);
}
'''

vertex_slide_current = vertex_header + '''
void main(void) {
  frag_color = color;
  tex_coord0 = vTexCoords0;
  vec2 pos = vPosition.xy;
  if (t_direction == 1)
    pos.x = (pos.x + size.x) - (size.x * t_alpha);
  else
    pos.x = (pos.x - size.x) + size.x * t_alpha;
  gl_Position = projection_mat * modelview_mat * vec4(pos, 0.0, 1.0);
}
'''

class PageLayout(FloatLayout):

    transition = StringProperty('slide')

    transition_alpha = NumericProperty(0.)

    transition_direction = OptionProperty(1., options=(-1., 0., 1.))

    transition_manual = BooleanProperty(False)

    animation_transition = StringProperty('out_quad')

    animation_duration = NumericProperty(.25)

    have_transition = BooleanProperty(False)

    page_previous = ObjectProperty(None)

    page_current = ObjectProperty(None)

    allow_touch_interaction = BooleanProperty(True)

    def __init__(self, **kwargs):
        self._animation_transition = None
        self.canvas = Canvas()
        with self.canvas:
            self.canvas_previous = RenderContext()
            self.canvas_current = RenderContext()

        #self.canvas_previous.shader.fs = fragment_slide_previous
        #self.canvas_current.shader.fs = fragment_slide_previous
        self.canvas_previous.shader.vs = vertex_slide_previous
        self.canvas_current.shader.vs = vertex_slide_current

        with self.canvas_previous:
            self.fbo_previous = Fbo(size=self.size)
            Color(1, 1, 1)
            self._r_previous = Rectangle(texture=self.fbo_previous.texture,
                                         pos=self.pos, size=self.size)

        with self.canvas_current:
            self.fbo_current = Fbo(size=self.size)
            Color(1, 1, 1)
            self._r_current = Rectangle(texture=self.fbo_current.texture,
                                        pos=self.pos, size=self.size)

        super(PageLayout, self).__init__(**kwargs)

        self.register_event_type('on_page_transition')

        Clock.schedule_interval(self._update_shaders, 1 / 60.)
        self.on_transition(self, self.transition)

    def on_size(self, instance, value):
        self.fbo_previous.size = self.fbo_current.size = value
        self.fbo_previous.texture.wrap = ''
        self.fbo_current.texture.wrap = ''
        self._r_previous.size = self._r_current.size = value
        self._r_previous.texture = self.fbo_previous.texture
        self._r_current.texture = self.fbo_current.texture

    def on_transition(self, instance, value):
        sp = self.canvas_previous.shader
        sc = self.canvas_current.shader
        if value == 'slide':
            sp.fs = sc.fs = None
            sp.vs = vertex_slide_previous
            sc.vs = vertex_slide_current
        elif value == 'fade':
            sp.vs = sc.vs = None
            sp.fs = fragment_fade_previous
            sc.fs = fragment_fade_current
        elif value == 'fade_and_slide':
            sp.vs = vertex_slide_previous
            sc.vs = vertex_slide_current
            sp.fs = fragment_fade_previous
            sc.fs = fragment_fade_current

    #
    # Controlers
    #

    def next_page(self, *l):
        children = self.children
        if not children:
            return
        page = (children.index(self.page_current) + 1) % len(children)
        self.select_page(children[page], direction=1.)

    def previous_page(self, *l):
        children = self.children
        if not children:
            return
        page = (children.index(self.page_current) - 1) % len(children)
        self.select_page(children[page], direction=-1.)

    def select_page(self, page_current, direction=None, manual=False):
        children = self.children
        if not children:
            return
        if page_current and not page_current in self.children:
            raise Exception('Selected page <%s> is not in children' %
                            str(page_current))

        # set correctly which page
        self.page_previous = self.page_current
        self.page_current = page_current

        # update graphics part
        self.fbo_current.clear()
        self.fbo_previous.clear()
        if self.page_previous:
            self.fbo_previous.add(self.page_previous.canvas)
        if self.page_current:
            self.fbo_current.add(self.page_current.canvas)

        # XXX FIXME
        if direction is None:
            direction = 1.

        self.transition_manual = manual
        if not manual:
            self.transition_alpha = 1.
            self.transition_direction = direction
            self._transition_stop()
            Clock.schedule_once(self._transition_start)

    #
    # prevent to add widget into graphics tree
    # we are controling the display and dispatch
    #

    def add_widget(self, widget):
        self.children.append(widget)
        widget.parent = self

    def remove_widget(self, widget):
        self.children.remove(widget)

    def on_touch_down(self, touch):
        page = self.page_current
        if not page:
            return
        if page.dispatch('on_touch_down', touch):
            return True
        if not self.allow_touch_interaction:
            return
        # manual control
        self._transition_stop()
        touch.grab(self)
        touch.ud['pagelayout.alpha'] = self.transition_alpha
        touch.ud['pagelayout.current'] = self.page_current
        return True

    def on_touch_move(self, touch):
        page = self.page_current
        if touch.grab_current != self:
            if page:
                return page.dispatch('on_touch_move', touch)
            return
        # manual control
        alpha = (touch.ox - touch.x) / self.width
        direction = 1. if alpha > 0 else -1.
        alpha = abs(alpha)

        # current page
        children = self.children
        page = touch.ud['pagelayout.current']
        index = (children.index(page) + int(direction)) % len(children)
        next_page = children[index]

        if next_page != self.page_current:
            self.select_page(next_page, manual=True)
        self.transition_direction = direction
        self.transition_alpha = 1. - alpha

        # FIXME this is require right now because even if we change teh
        # transition_alpha, the canvas is not updated directly (Clock ->
        # on_touch_* -> drawing.)
        self._update_shaders()

        return True

    def on_touch_up(self, touch):
        page = self.page_current
        if touch.grab_current != self:
            if page:
                return page.dispatch('on_touch_up', touch)
            return
        # manual control
        touch.ungrab(self)
        if self.transition_manual:
            self._transition_start()
        return True

    def on_children(self, instance, children):
        # assign a default widget current to display if the current
        # widget disapear or didn't been set yet
        if not children:
            self.select_page(None)
        else:
            current = self.page_current
            if not current or current not in children:
                self.select_page(children[0])

    def on_transition_alpha(self, instance, alpha):
        self.dispatch('on_page_transition', self.page_previous,
                      self.page_current, 1. - abs(alpha))

    def on_page_transition(self, page_previous, page_current, alpha):
        pass

    def _transition_stop(self):
        Clock.unschedule(self._transition_start)
        if self._animation_transition:
            self._animation_transition.stop(self)
            self._animation_transition = None

    def _transition_start(self, *largs):
        self._animation_transition = anim = Animation(
            transition_alpha=0., t=self.animation_transition,
            d=self.animation_duration)
        anim.bind(on_complete=self._on_transition_complete)
        anim.start(self)

    def _on_transition_complete(self, *largs):
        print 'transition done', self.page_current

    def _update_shaders(self, *largs):
        proj = Window.render_context['projection_mat']
        for c in (self.canvas_current, self.canvas_previous):
            c['projection_mat'] = proj
            c['time'] = Clock.get_boottime()
            c['size'] = map(float, self.size)
            c['uvsize'] = self.fbo_current.texture.uvsize
            c['t_alpha'] = 1. - abs(self.transition_alpha)
            c['t_direction'] = int(self.transition_direction)


if __name__ == '__main__':
    from kivy.uix.button import Button
    layout = PageLayout(size=Window.size)
    for x in xrange(4):
        btn = Button(text='Hello %d' % x, pos_hint={'x': .2, 'y': .2},
                     size_hint=(.6, .6))
        if x % 4 < 3:
            btn.bind(on_release=layout.next_page)
        else:
            btn.bind(on_release=layout.previous_page)
        layout.add_widget(btn)

    from kivy.base import runTouchApp
    runTouchApp(layout)

