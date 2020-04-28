import math

from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore




class Edges(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, rotation = 0.0, velocity = 10.0, bg_intensity = 0, edge_intensity = 255):

        arg = (rotation, velocity, bg_intensity, edge_intensity)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['rotation [deg]', 'velocity [deg/s]', 'bg_intensity', 'edge_intensity']

        # define parameters
        self.rotation    = float(rotation)              # rotation (degree)
        self.velocity    = float(velocity)              # velocity (degree / second (assumption: 60 Hz fps) )
        self.bg_intensity   = float(bg_intensity)     # min intensity
        self.edge_intensity   = float(edge_intensity)     # max intensity

        self.shared.arena_mode = 'default'


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')


        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        
        # define 4 quadrants for the rotation angle phi:
        #   a) 0 < phi < 90:
        #       standard configuration, edge starts from lower left
        #   b) 90 < phi < 180:
        #       rotate the cylinder AND flip it, edge starts from lower right
        #   c) 180 < phi < 270:
        #       rotate the cylinder, edge starts from upper right
        #   d) 270 < phi < 360:
        #       flip the cylinder, edge starts from upper left
        #
        # for each case define a new rotation angle phi_ (flip the sign if necessary)
        
        phi = self.rotation % 360.
        if (0.<=phi) and (phi<90.):
            phi_ = phi % 90.
        elif (90.<=phi) and (phi<180.):
            self.cylinder.setHpr(90,180,0)
            self.cylinder.setScale(self.cylinder_radius,self.cylinder_radius, -self.cylinder_height)
            self.cylinder.setAttrib(pcore.CullFaceAttrib.makeReverse())
            phi_ = 90 - (phi % 90.)
        elif (180.<=phi) and (phi<270.):
            self.cylinder.setHpr(90,180,0)
            phi_ = phi % 90.
        elif (270.<=phi) and (phi<360.):
            self.cylinder.setScale(self.cylinder_radius,self.cylinder_radius, -self.cylinder_height)
            self.cylinder.setAttrib(pcore.CullFaceAttrib.makeReverse())
            phi_ = 90 - (phi % 90.)
            
        # load texture
        self.wave_length = 600. # big enough that even at 50.38 degree (when the grating is oriented along the diagonal of the arena) one phase can cover the whole screen
        anti_alias_texture_size = int(math.ceil(608./(math.degrees(math.atan(self.cylinder_height/2./self.cylinder_radius))*2/self.wave_length/0.9) - 2*4)/2. + 2) # empirically
        self.tex = tools.create_grating_texture(anti_alias_texture_size, self.bg_intensity, self.edge_intensity)
        
        # use the same scaling and rotation convention as for gratings
        self.cylinder.setTexture(self.tex)
        self.cylinder.setTexScale(pcore.TextureStage.getDefault(), 360.0/self.wave_length, 360.0/self.wave_length/2./(10.*math.pi/26.))           
        #self.cylinder.setTexRotate(pcore.TextureStage.getDefault(), -self.rotation)
        self.cylinder.setTexRotate(pcore.TextureStage.getDefault(), -phi_)

        self.tex_offset = 0.0
        self.cylinder.setTexOffset(pcore.TextureStage.getDefault(), self.tex_offset, 0)

        # Define stimulus length as the time an edge travels across the whole azimuth times the ratio 
        # between the length of the diagonal and the azimuthal length plus 0.5 seconds
        # In this way the stimulus is longh enough for all orientations and the start and end trigger not too close to each other
        self.max_T = 180./math.fabs(self.velocity) * (math.sqrt(26.**2 + (10.*math.pi)**2)/(10.*math.pi))
        self.T     = self.max_T + 0.5
        

    def angle_function(self, time):

        ##
        if time < 0:
            angle = 0
        ##
        if 0 <= time < self.max_T:
            angle = -self.velocity * time
        ##
        if time >= self.max_T:
            angle = -self.velocity * self.max_T

        return angle

    def run(self, time):

        ang_cylinder = self.angle_function(time)
        self.cylinder.setTexOffset(pcore.TextureStage.getDefault(), (self.tex_offset + ang_cylinder)/self.wave_length % 1, 0)


        self.trigger_routine(time)