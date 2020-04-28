from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore
import math

class VPassingBar(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, velocity = 3.0, phi = 0.0, dphi = 10.0, dz = 2.0, bar_intensity = 255.0, bg_intensity=0.0):

        arg = (velocity, phi, dphi, dz, bar_intensity, bg_intensity)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['velocity [cm/sec]', 'phi [deg]', 'dphi [deg]', 'dz [units]', 'intensity', 'bg_intensity']

        # define parameters
        self.velocity = float(velocity)     # velocity of the bar in [deg/sec]
        self.phi = float(phi)               # position of the bar at the azimuth
        self.dphi = float(dphi)             # size of the bar in azimuth
        self.dz = float(dz)                 # size of the bar on z-axis (cylindric coordinates)
        self.bar_intensity = float(bar_intensity)       # bar intensity value
        self.bg_intensity = float(bg_intensity)         # background intensity value

        self.shared.arena_mode = 'default'


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')

        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        self.cylinder.setColor(self.bg_intensity/255.,self.bg_intensity/255.,self.bg_intensity/255.,1)

        # scale cylinder up in height in case the window texture is overlapping the edges
        self.cylinder_height = self.cylinder_height + self.dz * 2
        self.cylinder.setScale(self.cylinder_radius,self.cylinder_radius,self.cylinder_height)

        self.dz = self.dz * 10/5.
        self.velocity = self.velocity * 10/5.
        if self.dz > 26.:
            self.dz = 26.
        if self.dphi > 360.:
            self.dphi = 360.
        self.ts_window = pcore.TextureStage('ts_bar')


        tex_window = tools.create_window_texture_set_size(self.dphi, self.dz, self.bar_intensity, self.bg_intensity, 360, int(self.cylinder_height/0.1))
        self.cylinder.clearColor()
        self.cylinder.setTexture(self.ts_window, tex_window)

        # set starting point depending whether direction is downwards or upwards
        if self.velocity > 0:
            self.z0 = -(13 + self.dz/2.)
        elif self.velocity <= 0:
            self.z0 = (13 + self.dz/2.)


        self.cylinder.setTexOffset(self.ts_window, -0.25 + self.dphi/2./360. - self.phi/360., 0.5 - self.dz/2./self.cylinder_height - self.z0/self.cylinder_height)

        self.T = (26. + self.dz)/math.fabs(self.velocity)


    def run(self, time):

        if time < 0:
            z = self.z0

        if 0 <= time < self.T:
            z = self.z0 + time * self.velocity

        if time >= self.T:
            z = self.z0 * -1

        self.cylinder.setTexOffset(self.ts_window, -0.25 + self.dphi/2./360. - self.phi/360., 0.5 - self.dz/2./self.cylinder_height - z/self.cylinder_height)

        self.trigger_routine(time)


