from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
#import panda3d.core as pcore
import numpy as np
from math import copysign

class FigureGroundDisA(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, velocity = 30., dphi = 20., z = 0., dz = 2., N_pixels = 36, c_on = 100, c_off = 0., color = 'g'):

        arg = (velocity, dphi, z, dz, N_pixels, c_on, c_off, color)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['velocity [deg/sec]', 'dphi [deg]', 'z [cm]', 'dz [cm]', 'N pixels azimuth', 'intensity ON', 'intensity OFF', 'color']

        # define parameters
        self.color   = str(color)                   # color of the arena
        self.velocity = float(velocity)             # azimuthal velocity of the object
        self.dphi = float(dphi)                     # azimuth width of the object
        self.z   = float(z)                         # elevation position of the object
        self.dz   = float(dz)                       # elevation width of the object
        self.N_pixels = int(float(N_pixels))        # number of pixels to part the screen in
        self.c_on   = int(float(c_on))              # intensity of bright pixels
        self.c_off   = int(float(c_off))            # intensity of dark pixels

        self.shared.arena_mode = 'default'


    def build(self):

        self.N_phi = self.N_pixels

        # configure beamer
        if self.color == 'b':
            self.set_arena_mode('optoblueHDMI')
        elif self.color == 'r':
            self.set_arena_mode('optoredHDMI')
        elif self.color == 'g':
            self.set_arena_mode('optogreenHDMI')

        # generate background cylinder
        _, _, self.bg_cylinder = tools.standard_cylinder(self.parent.mainNode)
        bg_cylinder_radius = 10
        bg_cylinder_height = 50
        self.bg_cylinder.setScale(bg_cylinder_radius,bg_cylinder_radius,bg_cylinder_height)
        phi_width = 180./self.N_phi

        z_height  = phi_width/360. * 2 * np.pi * bg_cylinder_radius
        self.N_z       = np.ceil(bg_cylinder_height/z_height)

        # take only one and the same noise for all color copys of this world!!
        try:
            self.bg_noise = self.shared.noise
        except:
            self.bg_noise = (np.random.randint(size = (int(self.N_phi*2), int(self.N_z)), low = 0, high = 2))*(self.c_on - self.c_off) + self.c_off
            self.shared.noise = self.bg_noise

        self.noise_tex = tools.make_matrix_to_texture(self.bg_noise)
        self.bg_cylinder.setTexture(self.noise_tex)

        cylinder_radius = 10
        # generate first cylinder segment
        self.obj = tools.create_cylinder_segment(self.parent.mainNode, self.dphi)
        self.obj.setScale(cylinder_radius,cylinder_radius,self.dz * 2)
        self.obj.setHpr(90,0,0)

        N_phi = np.ceil(self.dphi/phi_width).astype(np.int)
        N_z = np.ceil(self.dz*2/z_height).astype(np.int)


        # take only one and the same noise for all color copys of this world!!
        try:
            self.obj_noise = self.shared.obj_noise
        except:
            self.obj_noise = (np.random.randint(size = (N_phi,N_z), low = 0, high = 2))*(self.c_on - self.c_off) + self.c_off
            self.shared.obj_noise = self.obj_noise

        self.obj_tex = tools.make_matrix_to_texture(self.obj_noise)

        #baum_tex = loader.loadTexture("../stimuli/default/baum.jpg")
        #self.obj.setTexture(baum_tex)
        self.obj.setTexture(self.obj_tex)

        self.obj.setBin("fixed", 20) # render object first (even before trigger_pixel! <40!)
        self.obj.setDepthTest(False)
        self.obj.setDepthWrite(False)

        # set starting point of bar depending if it will go rightwards or leftwards
        if self.velocity > 0:
            self.phi0 = -self.dphi/2.
        elif self.velocity <= 0:
            self.phi0 = 180.+self.dphi/2.
        self.setPos(self.phi0, self.z)

        self.T = (180. + self.dphi)/np.abs(self.velocity)

    def setPos(self, phi, z):
            self.obj.setHpr(90. +  self.dphi/2. - phi,0,0)
            self.obj.setPos(0,0,z * 2)

    def run(self, time):

        if time < 0:
            phi = self.phi0

        if 0 <= time < self.T:
            phi = self.phi0 + time * self.velocity

        if time >= self.T:
            phi = self.phi0 + (180. + self.dphi) * copysign(1,self.velocity)

            # delete noise texture
            try:
                del self.shared.noise
                del self.shared.obj_noise
            except:
                pass

        self.setPos(phi, self.z)

        self.trigger_routine(time)

