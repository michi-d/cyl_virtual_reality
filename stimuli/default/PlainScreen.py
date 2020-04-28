import math

from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore


class PlainScreen(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, T = 10., intensity = 125.):

        arg = (T, intensity)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['time', 'intensity']

        # define parameters
        self.intensity = float(intensity)
        self.T = float(T)

        self.shared.arena_mode = 'default'

    def build(self):

        self.trigger_pixel.setColor(0,0,0,1)

        # configure beamer
        self.set_arena_mode('greenHDMI')
        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        self.cylinder.setColor(self.intensity/255., self.intensity/255., self.intensity/255., 1)


    def run(self, time):
        pass