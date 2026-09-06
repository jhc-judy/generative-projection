"""Instanced flat geometry; no depth, perspective, lighting or texture assets."""
from pathlib import Path
import moderngl
from .simulation import Simulation, ASPECT, RADIUS


class RollingColorsRenderer:
    def __init__(self,width,height,shader_name="shader_03_rolling_colors"):
        self.width,self.height = width,height
        self.ctx = moderngl.create_context(require=330)
        folder = Path(__file__).resolve().parent
        self.program = self.ctx.program(
            vertex_shader=(folder/'shader.vert').read_text(),
            fragment_shader=(folder/'shader.frag').read_text())
        self.sim = Simulation()
        self.buffer = self.ctx.buffer(reserve=1024*9*4,dynamic=True)
        self.vao = self.ctx.vertex_array(self.program,[(self.buffer,
            '2f 2f 3f 1f 1f /i','i_position','i_size','i_color','i_angle','i_kind')])
        self.clock = 0.
        self.previous_time = None
        self.resize(width,height)
        print('Loaded shader: Rolling Colors — 2D')

    def resize(self,width,height):
        self.width,self.height = max(1,width),max(1,height)
        aspect = self.width/self.height
        self.program['u_view'].value = (max(ASPECT,aspect),max(1.,ASPECT/aspect))
        self.ctx.viewport = (0,0,self.width,self.height)

    def render(self,time_value,activity=0.,uniforms=None):
        speed = max(.01,float((uniforms or {}).get('u_speed',1.)))
        current = float(time_value)
        if self.previous_time is None:
            self.clock = current*speed
        else:
            self.clock += max(0.,current-self.previous_time)*speed
        self.previous_time = current
        self.sim.advance(self.clock)
        data = self.sim.instances()
        if data.nbytes > self.buffer.size:
            self.buffer.orphan(data.nbytes)
        self.buffer.write(data.tobytes())
        self.program['u_ball'].value = tuple(self.sim.ball_position())
        self.program['u_spin'].value = float(self.sim.spin)
        self.program['u_radius'].value = float(getattr(self.sim,'visible_radius',RADIUS))
        self.ctx.screen.use()
        self.ctx.viewport = (0,0,self.width,self.height)
        self.ctx.disable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
        self.ctx.clear(.045,.052,.067,1.)
        self.vao.render(mode=moderngl.TRIANGLES,vertices=6,instances=len(data))
        self.ctx.disable(moderngl.BLEND)


Renderer = RollingColorsRenderer
