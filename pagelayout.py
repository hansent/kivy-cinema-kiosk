from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Canvas, RenderContext, Fbo, Color, Rectangle
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty, \
        NumericProperty

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
uniform float transition;
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
uniform float transition;
uniform vec2 size;
uniform vec2 uvsize;
'''

vertex_slide_previous = vertex_header + '''
void main (void) {
  frag_color = color;
  tex_coord0 = vTexCoords0;
  vec2 pos = vPosition.xy;
  pos.x -= size.x * transition;
  gl_Position = projection_mat * modelview_mat * vec4(pos, 0.0, 1.0);
}
'''

vertex_slide_current = vertex_header + '''
void main (void) {
  frag_color = color;
  tex_coord0 = vTexCoords0;
  vec2 pos = vPosition.xy;
  pos.x = (pos.x + size.x) - (size.x * transition);
  gl_Position = projection_mat * modelview_mat * vec4(pos, 0.0, 1.0);
}
'''

class PageLayout(FloatLayout):

    transition = StringProperty('slide')

    transition_alpha = NumericProperty(1.)

    animation_transition = StringProperty('out_quad')

    animation_duration = NumericProperty(.25)

    have_transition = BooleanProperty(False)

    page_previous = ObjectProperty(None)

    page_current = ObjectProperty(None)

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

        Clock.schedule_interval(self._update_shaders, 1 / 60.)

    def on_size(self, instance, value):
        self.fbo_previous.size = self.fbo_current.size = value
        self.fbo_previous.texture.wrap = ''
        self.fbo_current.texture.wrap = ''
        self._r_previous.size = self._r_current.size = value
        self._r_previous.texture = self.fbo_previous.texture
        self._r_current.texture = self.fbo_current.texture

    #
    # Controlers
    #

    def next_page(self, *l):
        children = self.children
        if not children:
            return
        page_current = (children.index(self.page_current) + 1) % len(children)
        self.page_previous = self.page_current
        self.page_current = children[page_current]

    def previous_page(self, *l):
        children = self.children
        if not children:
            return
        page_current = (children.index(self.page_current) - 1) % len(children)
        self.page_previous = self.page_current
        self.page_current = children[page_current]

    #
    # prevent to add widget into graphics tree
    # we are controling the display and dispatch
    #

    def add_widget(self, widget):
        self.children.append(widget)

    def remove_widget(self, widget):
        self.children.remove(widget)

    def on_touch_down(self, touch):
        page = self.page_current
        if not page:
            return
        if page.dispatch('on_touch_down', touch):
            return True
        # manual control
        self._transition_stop()
        touch.grab(self)
        touch.ud['initial'] = self.transition_alpha
        return True

    def on_touch_move(self, touch):
        page = self.page_current
        if touch.grab_current != self:
            if page:
                return page.dispatch('on_touch_move', touch)
            return
        # manual control
        alpha = (touch.ox - touch.x) / self.width + touch.ud['initial']
        print alpha
        return True

    def on_touch_up(self, touch):
        page = self.page_current
        if touch.grab_current != self:
            if page:
                return page.dispatch('on_touch_up', touch)
            return
        # manual control
        return True

    def on_children(self, instance, children):
        # assign a default widget current to display if the current
        # widget disapear or didn't been set yet
        current = self.page_current
        if not children:
            self.page_previous = current
            self.page_current = None
            return
        if not current or current not in children:
            self.page_previous = current
            self.page_current = children[0]

    def on_page_current(self, instance, value):
        # a new widget current is set, start transition to the new one.
        self.fbo_current.clear()
        self.fbo_previous.clear()
        if self.page_previous:
            self.fbo_previous.add(self.page_previous.canvas)
        if self.page_current:
            self.fbo_current.add(self.page_current.canvas)
        self._transition_stop()
        self._transition_start(1.)

    def _transition_stop(self):
        if self._animation_transition:
            self._animation_transition.stop()
            self._animation_transition = None

    def _transition_start(self, to):
        self.transition_alpha = 0.
        anim = Animation(transition_alpha=to,
                         t=self.animation_transition,
                         d=self.animation_duration)
        self._animation_transition = anim.start(self)

    def _update_shaders(self, *largs):
        proj = Window.render_context['projection_mat']
        for c in (self.canvas_current, self.canvas_previous):
            c['projection_mat'] = proj
            c['time'] = Clock.get_boottime()
            c['size'] = map(float, self.size)
            c['uvsize'] = self.fbo_current.texture.uvsize
            c['transition'] = abs(self.transition_alpha)


if __name__ == '__main__':
    from kivy.core.window import Window
    from kivy.uix.button import Button
    layout = PageLayout(size=Window.size)
    for x in xrange(4):
        btn = Button(text='Hello %d' % x, pos_hint={'x': .2, 'y': .2},
                     size_hint=(.6, .6))
        btn.bind(on_release=layout.next_page)
        layout.add_widget(btn)

    from kivy.base import runTouchApp
    runTouchApp(layout)

