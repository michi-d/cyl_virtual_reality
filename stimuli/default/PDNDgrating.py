import math

from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore


class PDNDgrating(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, rotation = 90.0, wave_length = 10.0, velocity = 10.0, mode = 'sq', min_intensity = 0, max_intensity = 255, motion_T = 3.0, pause = 0.5):

        arg = (rotation, wave_length, velocity, mode, min_intensity, max_intensity, motion_T, pause)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['rotation [deg]', 'wavelength [deg]', 'velocity [deg/s]', 'mode [sq/sin]', 'min_intensity', 'max_intensity', 'time of motion [sec]', 'pause time [sec]']

        self.rotation    = float(rotation)              # rotation (degree)
        self.wave_length = float(wave_length)           # wave length (degree)
        self.velocity    = float(velocity)              # velocity (degree / second (assumption: 60 Hz fps) )
        self.mode        = str(mode)                    # grating type (sine or square)
        self.min_intensity   = float(min_intensity)     # min intensity value
        self.max_intensity   = float(max_intensity)     # max intensity value
        self.motion_T    = float(motion_T)              # motion time
        self.pause       = float(pause)                 # pause length

        self.shared.arena_mode = 'default'

    def build(self):#, old_geometry):

        # configure beamer
        self.set_arena_mode('greenHDMI')

        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)

        self.T = self.motion_T*2 + self.pause

        # load texture (same as in default.Grating)
        anti_alias_texture_size = int(math.ceil(608./(math.degrees(math.atan(self.cylinder_height/2./self.cylinder_radius))*2/self.wave_length/0.9) - 2*4)/2. + 2) # empirically
        if self.mode == 'sin':
            self.tex = tools.create_sine_grating_texture(anti_alias_texture_size, self.min_intensity, self.max_intensity)
        elif self.mode == 'sq':
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
        self.velocity = -self.velocity

        self.tex_offset = 0.
        self.cylinder.setTexOffset(pcore.TextureStage.getDefault(), (self.tex_offset + self.angle_function(0))/self.wave_length % 1, 0)

        # set up variables to memorize which triggers have been made already
        self.stop1stdirection_trigger = True
        self.start2ndirection_trigger = True


    def angle_function(self, time):

        ##
        if time < 0:
            angle = 0

        ##
        if 0 <= time < self.T:
            t = time
            if t <= (self.motion_T):
                angle = self.velocity*t
            elif t <= (self.motion_T + self.pause):
                if self.stop1stdirection_trigger:
                    self.trigger_blink_now(time, "stop 1st direction")
                    self.stop1stdirection_trigger = False
                angle = self.velocity*self.motion_T
            elif t <= (2*self.motion_T + self.pause):
                if self.start2ndirection_trigger:
                    self.trigger_blink_now(time, "start 2nd direction")
                    self.start2ndirection_trigger = False
                angle = self.velocity*self.motion_T - self.velocity*(t - (self.motion_T + self.pause))
            else:
                angle = 0.
        ##
        if time >= self.T:
            angle = self.velocity*self.motion_T - self.velocity*(self.T - (self.motion_T + self.pause))

        return angle


    def run(self, time):

        ang_cylinder = self.angle_function(time)
        self.cylinder.setTexOffset(pcore.TextureStage.getDefault(), (self.tex_offset + ang_cylinder)/self.wave_length % 1, 0)

        self.trigger_routine(time)