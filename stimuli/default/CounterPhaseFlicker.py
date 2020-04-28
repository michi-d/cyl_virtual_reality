import math

from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore


class CounterPhaseFlicker(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, T = 10.0, rotation = 0.0, wave_length = 30.0 , velocity = 10.0, min_intensity = 0, max_intensity = 255):

        arg = (T, rotation, wave_length, velocity, min_intensity, max_intensity)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['stimulus duration [s]', 'rotation [deg]', 'wavelength [deg]', 'velocity [deg/s]', 'min_intensity', 'max_intensity']

        # define parameters
        self.T = float(T)                               # duration [sec]
        self.rotation    = float(rotation)              # rotation (degree)
        self.wave_length = float(wave_length)           # wave length (degree)
        self.velocity    = float(velocity)              # velocity (degree / second (assumption: 60 Hz fps) )
        self.min_intensity   = float(min_intensity)/2.     # min intensity
        self.max_intensity   = float(max_intensity)/2.     # max intensity

        self.shared.arena_mode = 'default'


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')


        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)

        # paint the cylinder black on the ground
        tex_ground = tools.create_plain_texture(0)
        self.ts_ground = pcore.TextureStage('ts_ground')
        self.cylinder.setTexture(self.ts_ground, tex_ground)

        # generate textures
        anti_alias_texture_size = int(math.ceil(608./(math.degrees(math.atan(self.cylinder_height/2./self.cylinder_radius))*2/self.wave_length/0.9) - 2*4)/2. + 2) # empirically

        # unfortunately, MAdd Texture mode does not work together with the setColorScale - command from base.py
        # this means, that those textures that are added onto another one cannot be tinted in a certain color
        # hence, here we generate differently coloured texture from the beginning, depending on the temporal offset of the Stimulus World
        if self.t_offset == 0.:
            color_vector = [0,0,1] # blue
        elif self.t_offset == 1.:
            color_vector = [1,0,0] # red
        elif self.t_offset == 2.:
            color_vector = [0,1,0] # green

        # generate two sine gratings that are anti-phasic
        # then in the beginning everything is gray and on the left edge (phi = 0) the first polarity is dark
        self.tex = tools.create_coloured_sine_grating_texture(anti_alias_texture_size, self.min_intensity, self.max_intensity, color_vector=color_vector)
        self.tex2 = tools.create_coloured_sine_grating_texture(anti_alias_texture_size, self.max_intensity, self.min_intensity, color_vector=color_vector)

        # add the two sine gratings onto each other to generate a counterphase flicker
        self.ts1 = pcore.TextureStage('ts1')
        self.ts1.setMode(pcore.TextureStage.MAdd)
        self.ts2 = pcore.TextureStage('ts2')
        self.ts2.setMode(pcore.TextureStage.MAdd)

        self.cylinder.setTexture(self.ts1, self.tex)
        self.cylinder.setTexScale(self.ts1, 360.0/self.wave_length, math.degrees(math.atan(self.cylinder_height/2./self.cylinder_radius))*2/self.wave_length)
        self.cylinder.setTexRotate(self.ts1, -self.rotation)

        self.cylinder.setTexture(self.ts2, self.tex2)
        self.cylinder.setTexScale(self.ts2, 360.0/self.wave_length, math.degrees(math.atan(self.cylinder_height/2./self.cylinder_radius))*2/self.wave_length)
        self.cylinder.setTexRotate(self.ts2, -self.rotation)

        self.tex_offset = 0.
        self.cylinder.setTexOffset(self.ts1, (self.tex_offset + self.angle_function(0))/self.wave_length % 1, 0)
        self.cylinder.setTexOffset(self.ts2, (self.tex_offset - self.angle_function(0))/self.wave_length % 1, 0)

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
        self.cylinder.setTexOffset(self.ts1, (self.tex_offset + ang_cylinder)/self.wave_length % 1, 0)
        self.cylinder.setTexOffset(self.ts2, (self.tex_offset - ang_cylinder)/self.wave_length % 1, 0)


        self.trigger_routine(time)