import math

from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore


class HGrating_phase(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, T = 10.0, wave_length = 30.0 , velocity = 10.0, mode = 'sq', min_intensity = 0, max_intensity = 255, phi = 90., phase_offset = 0.):

        arg = (T, wave_length, velocity, mode, min_intensity, max_intensity, phi, phase_offset)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['stimulus duration [s]', 'wavelength [deg]', 'velocity [deg/s]', 'mode [sq/sin]', 'min_intensity', 'max_intensity', 'phi', 'phase_offset']

        # define parameters
        self.T = float(T)                               # duration [sec]
        self.rotation    = float(0.0)                   # rotation (degree)
        self.wave_length = float(wave_length)           # wave length (degree)
        self.velocity    = float(velocity)              # velocity (degree / second (assumption: 60 Hz fps) )
        self.mode        = str(mode)                    # grating type
        self.min_intensity   = float(min_intensity)     # min intensity
        self.max_intensity   = float(max_intensity)     # max intensity
        self.phi             = float(phi)               # receptive field position
        self.phase_offset    = float(phase_offset)      # relative phase offset to the receptive field center

        self.shared.arena_mode = 'default'


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')


        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)

        # load texture
        # for horizontal gratings the edge is at the left edge of the arena (phi = 0)
        # for vertical gratings the edge is at the bottom edge of the arena (z = -6.5)
        anti_alias_texture_size = int(math.ceil(608./(math.degrees(math.atan(self.cylinder_height/2./self.cylinder_radius))*2/self.wave_length/0.9) - 2*4)/2. + 2) # empirically
        if self.mode == 'sin':
            # starts always at the edge of the texture with phase = 0 of the sine wave (rescaled to the range between max_intensity and min_intensity)
            self.tex = tools.create_sine_grating_texture(anti_alias_texture_size, self.max_intensity, self.min_intensity)
        elif self.mode == 'sq':
            # starts always at the edge of the texture with the black stripe
            self.tex = tools.create_grating_texture(anti_alias_texture_size, self.min_intensity, self.max_intensity)


        # generate wavelength by rescaling the texture ( which contains exact one period of the grating) in relation to the desired wavelength
        # for the horizontal component the scaling factor is given by the ratio between the cylinder width (360 degree) and the wavelength
        # for the vertical component the scaling factor is given by the ratio between 180 degree (because we would see the whole texture if the scaling factor would be 1)
        #       and the wavelength times the aspect ratio of the arena screen (such that 45 degree remains 45 degree)
        #
        # NOTE: Using this convention the vertical scaling factor is given by the requirement that 45 degree generates exactly 45 degree on the arena screen
        #       This scaling factor also defines how wide the bars will be in vertical direction.
        #       Hence, the wavelength is strictly speaking defined only for horizontal gratings moving along the azimuth

        self.cylinder.setTexture(self.tex)
        #self.cylinder.setTexScale(pcore.TextureStage.getDefault(), 360.0/self.wave_length, math.degrees(math.atan(self.cylinder_height/2./self.cylinder_radius))*2/self.wave_length)
        self.cylinder.setTexScale(pcore.TextureStage.getDefault(), 360.0/self.wave_length, 360.0/self.wave_length/2./(10.*math.pi/26.))
        self.cylinder.setTexRotate(pcore.TextureStage.getDefault(), -self.rotation)

        #self.tex_offset = 0.
        self.tex_offset = -self.phi - self.phase_offset/360.*self.wave_length
        self.cylinder.setTexOffset(pcore.TextureStage.getDefault(), (self.tex_offset + self.angle_function(0))/self.wave_length % 1, 0)


    def angle_function(self, time):

        ##
        if time < 0:
            angle = 0
        ##
        if 0 <= time < self.T:
            angle = -self.velocity * time
        ##
        if time >= self.T:
            angle = -self.velocity * self.T

        return angle


    def run(self, time):

        ang_cylinder = self.angle_function(time)
        self.cylinder.setTexOffset(pcore.TextureStage.getDefault(), (self.tex_offset + ang_cylinder)/self.wave_length % 1, 0)


        self.trigger_routine(time)