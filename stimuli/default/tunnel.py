import math

from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore


class tunnel(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, T = 10.0, velocity = 5.0):

        arg = (T, velocity)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['stimulus duration [s]', 'velocity']

        # define parameters
        self.T = float(T)                      # duration [sec]
        self.velocity = float(velocity)

        self.shared.arena_mode = 'default'

    def build(self):#, old_geometry):

        # configure beamer
        self.set_arena_mode('greenHDMI')

        #new_geometry = []

        self.off_center = self.parent.mainNode.attachNewNode("off_center")
        self.off_center.setPos(205,0,0)

        # define cylinder 1
        self.cylinder1_height = 10
        self.cylinder1_radius = 200

        self.cylinder1 = tools.create_cylinder_parts(self.parent.mainNode, 1, 360)
        self.cylinder1.reparentTo(self.off_center)
        self.cylinder1.setPos(0,0,0)
        self.cylinder1.setScale(self.cylinder1_radius, self.cylinder1_radius, self.cylinder1_height)
        self.cylinder1.setHpr(0,0,0)
        self.cylinder1.setAttrib(pcore.CullFaceAttrib.make(pcore.CullFaceAttrib.MCullCounterClockwise))

        # define cylinder 2
        self.cylinder2_height = 10
        self.cylinder2_radius = 210

        self.cylinder2 = tools.create_cylinder_parts(self.parent.mainNode, 1, 360)
        self.cylinder2.reparentTo(self.off_center)
        self.cylinder2.setPos(0,0,0)
        self.cylinder2.setScale(self.cylinder2_radius, self.cylinder2_radius, self.cylinder2_height)
        self.cylinder2.setHpr(0,0,0)

        # define top
        cm = pcore.CardMaker('top')
        self.top = self.off_center.attachNewNode(cm.generate())
        self.top.setPos(-220,220,5)
        self.top.setHpr(0,90,0)
        self.top.setScale(440,1,440)

        # define bottom
        self.bottom = self.off_center.attachNewNode(cm.generate())
        self.bottom.setPos(-220,-220,-5)
        self.bottom.setHpr(0,-90,0)
        self.bottom.setScale(440,1,440)

        # load wall textures
        N_vertical = 1.
        N_horizontal = self.cylinder1_radius*2*math.pi / self.cylinder1_height
        self.cylinder1.setTexScale(pcore.TextureStage.getDefault(), N_horizontal, N_vertical)
        self.cylinder2.setTexScale(pcore.TextureStage.getDefault(), N_horizontal, N_vertical)

        baum_file = tools.make_panda3d_path(self.shared.arena_path, "stimuli/default/baum.jpg")
        baum_tex = loader.loadTexture(baum_file)
        self.cylinder1.setTexture(baum_tex)

        berg_file = tools.make_panda3d_path(self.shared.arena_path, "stimuli/default/baum.jpg")
        berg_tex = loader.loadTexture(berg_file)
        self.cylinder2.setTexture(berg_tex)

        # load top texture
        sky_file = tools.make_panda3d_path(self.shared.arena_path, "stimuli/default/sky.jpg")
        sky_tex = loader.loadTexture(sky_file)
        self.top.setTexture(sky_tex)
        self.top.setTexScale(pcore.TextureStage.getDefault(), 220, 220)

        # generate chessboard texture / bottom texture
        chess_image = pcore.PNMImage(2,2)
        chess_image.setXelA(0,0,0,0,0,1)
        chess_image.setXelA(1,1,0,0,0,1)
        chess_image.setXelA(0,1,1,1,1,1)
        chess_image.setXelA(1,0,1,1,1,1)

        chess_tex = pcore.Texture()
        chess_tex.load(chess_image)
        chess_tex.setMagfilter(pcore.Texture.FTNearest)

        # set bottom texture
        self.bottom.setTexScale(pcore.TextureStage.getDefault(), 220, 220)
        self.bottom.setTexture(chess_tex)


    def run(self, time):

        ##
        if time < 0:
            angleDegrees = 0

        ##
        if 0 <= time < self.T:
            angleDegrees = time * self.velocity
        ##
        if time >= self.T:
            angleDegrees = self.T * self.velocity

        angleRadians = angleDegrees * (math.pi / 180.0)

        self.parent.parent_camera.setPos(205 + 205.*math.cos(angleRadians), 205.*math.sin(angleRadians), 0)
        self.parent.parent_camera.setHpr(angleDegrees, 0, 0)

        # if time >= self.T:
        #     self.parent.parent_camera.setPos(1000, 1000, 1000)

        self.trigger_routine(time)


