from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore
import math



class HPassingBar(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, velocity = 30.0, dphi = 10.0, z = 0.0, dz = 2.0, bar_intensity = 255.0, bg_intensity=0.0):

        arg = (velocity, dphi, z, dz, bar_intensity, bg_intensity)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['velocity [deg/sec]', 'dphi [deg]', 'z [cm]', 'dz [cm]', 'intensity', 'bg_intensity']

        # define parameters
        self.velocity = float(velocity)         # velocity of the bar in [deg/sec]
        self.dphi = float(dphi)                 # size of the bar in azimuth
        self.z = float(z)                       # position of the bar in z-axis (cylindric coordinates)
        self.dz = float(dz)                     # size of the bar on z-axis (cylindric coordinates)
        self.bar_intensity = float(bar_intensity)  # bar intensity value
        self.bg_intensity = float(bg_intensity)    # background intensity value

        self.shared.arena_mode = 'default'


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')

        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        self.cylinder.setColor(self.bg_intensity/255.,self.bg_intensity/255.,self.bg_intensity/255.,1)

        self.z = self.z * 10/5.
        self.dz = self.dz * 10/5.
        if self.dz > 26.:
            self.dz = 26.
        if self.dphi > 360.:
            self.dphi = 360.


        self.ts_window = pcore.TextureStage('ts_bar')
        tex_window = tools.create_window_texture(self.dphi, self.dz, self.bar_intensity, self.bg_intensity)
        self.cylinder.clearColor()
        self.cylinder.setTexture(self.ts_window, tex_window)

        # set starting point of bar depending if it will go rightwards or leftwards
        if self.velocity > 0:
            self.phi0 = -(90. + self.dphi/2.)
        elif self.velocity <= 0:
            self.phi0 = +(90. + self.dphi/2.)

        self.cylinder.setTexOffset(self.ts_window, -0.25 + self.dphi/2./360. - self.phi0/360., 0.5 - self.dz/2./26. - self.z/26.)

        self.T = (180. + self.dphi)/math.fabs(self.velocity)


    def run(self, time):

        if time < 0:
            phi = self.phi0

        if 0 <= time < self.T:
            phi = self.phi0 + time * self.velocity

        if time >= self.T:
            phi = self.phi0 + (180. + self.dphi) * math.copysign(1,self.velocity)

        self.cylinder.setTexOffset(self.ts_window, -0.25 + self.dphi/2./360. - phi/360., 0.5 - self.dz/2./26. - self.z/26.)

        self.trigger_routine(time)


