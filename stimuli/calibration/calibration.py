from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
#import PyDLPControl.ArenaControl as ArenaControl
import panda3d.core as pcore
import math

class calibration(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, duration, N_horizontal):

        arg = (duration, N_horizontal)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define stimulus name
        self.name = "calibration"

        # define parameter names
        self.parameter_names = ['duration [sec]', 'N_horizontal']

        # define geometry name
        self.geometry_name = 'calibration'

        # define parameters
        self.duration = float(duration)
        self.N_horizontal = float(N_horizontal)


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')

        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        self.cylinder.setScale(10,10,50)
        self.cylinder_height = 50
        self.cylinder_radius = 10

        chess_image = pcore.PNMImage(2,2)
        chess_image.setXelA(0,0,0,0,0,1)
        chess_image.setXelA(1,1,0,0,0,1)
        chess_image.setXelA(0,1,1,1,1,1)
        chess_image.setXelA(1,0,1,1,1,1)

        chess_tex = pcore.Texture()
        chess_tex.load(chess_image)
        chess_tex.setMagfilter(pcore.Texture.FTNearest)
        N_vertical = self.cylinder_height/(2*math.pi*self.cylinder_radius/self.N_horizontal)#1./(2*math.pi/N_horizontal)
        self.cylinder.setTexScale(pcore.TextureStage.getDefault(), self.N_horizontal, N_vertical)
        self.cylinder.setTexture(chess_tex)

        self.v_tex_offset_count = 0
        self.h_tex_offset_count = 0

        self.fov_right_diff = [0.0, 0.0]
        self.fov_left_diff = [0.0, 0.0]

        self.T = self.duration

    def run(self, time):


        self.trigger_routine(time)


