from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore
import numpy as np


class BinaryNoise_DiscreteTime(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, T = 30.0, N_phi = 64,  N_z = -1, delta_s = 1, contrast = 250.):

        sampling_phi = 180./int(N_phi)

        if int(N_z) == -1: # -1 means: automatically round such that pixel are appoximately squares
            N_z_  = np.float(26./(sampling_phi/360. * 2 * np.pi * 10))
            N_z   = np.round(N_z_, 2).astype(np.int)
            print("Number of pixels in elevation: " + str(N_z_) + ", rounded to: " + str(N_z))
        else:
            N_z         = int(N_z)

        arg = (T, N_phi, N_z, delta_s, contrast)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['duration', 'N_phi', 'N_z', 'delta_sample', 'contrast']

        self.T           = float(T)            # duration
        self.N_phi       = int(N_phi)        # number of pixels along azimuth
        self.N_z         = int(N_z)
        self.delta_s     = int(delta_s)
        self.contrast    = float(contrast)


    def build(self):

        N_z   = self.N_z
        N_phi = self.N_phi
        self.N = N_z*N_phi

        # Texture: Background
        self.bg_tex_shape    = (N_z, N_phi)

        # configure beamer
        self.set_arena_mode('greenHDMI')

        # generate standard cylinder
        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        self.cylinder.setScale(self.cylinder_radius, self.cylinder_radius, self.cylinder_height*1)

        # like in default.PDNDgrating
        self.T = self.T

        # INITIALIZE CYLINDER TEXTURE for the start frame (first N samples counting from random seed 0)
        self.framecount = 0
        np.random.seed(0)
        try:
            self.tex = self.shared.texture
        except:
            ###
            #self.shared.control_values = np.zeros( (1000,) + self.bg_tex_shape )
            ###
            self.shared.texture = self.generate_texture(0)

        # leading color world gets initialized again and jumps N random numbers (because the start frame was already generated)
        if self.first:
            np.random.seed(0)
            np.random.randint(0,2, self.bg_tex_shape)
            self.framecount = 1

        # set texture in all color worlds
        self.tex = self.shared.texture
        self.cylinder.setTexture(pcore.TextureStage.getDefault(), self.tex)
        self.cylinder.setTexScale(pcore.TextureStage.getDefault(), 2., 1.)



    def generate_texture(self, current_frame):

        noise_frame = np.floor_divide(current_frame, self.delta_s)
        diff = self.framecount - noise_frame

        #print(noise_frame, current_frame)

        if diff > 0:
            # if number of generated frames is more than number of displayed frames, wait one frame
            #print("wait a frame")
            return None

        elif diff == 0:
            # if number of generated frames equals number of displayes frames -> all good, generate next frame

            # get new random numbers and apply 1st order LP filter
            numbers = np.random.randint(0,2,self.bg_tex_shape) # get new numbers
            self.framecount += 1

            ###
            #self.shared.control_values[current_frame, :, :] = numbers
            ###

            # transform random numbers to stimulus -> map 95% of the values to the range between 0 - 255
            image = numbers
            #image[image==1] = int(125 + self.contrast/2.)
            #image[image==0] = int(125 - self.contrast/2.)
            image = ((image-0.5)*self.contrast + 125).astype(np.int) # transform 0 and 1 to contrast values

            # transform image into a Panda3D texture
            tex = np.tile(image, (3, 1, 1)).swapaxes(0, 1).swapaxes(1, 2).astype(np.uint8)

            texture = pcore.Texture("image")
            texture.setup2dTexture(tex.shape[1], tex.shape[0], pcore.Texture.TUnsignedByte, pcore.Texture.FRgb8)

            p = pcore.PTAUchar.emptyArray(0)
            p.setData(tex.tostring())
            texture.setRamImage(pcore.CPTAUchar(p))

            texture.setMagfilter(pcore.Texture.FTNearest)
            texture.setMinfilter(pcore.Texture.FTNearest)

            return texture


        elif diff < 0:
            # if number of generated frames is smaller than number of "should have been"-displayed frames
            # -> jump the difference and continue generating frames from there
            np.random.randint(0,2,self.bg_tex_shape)
            self.framecount += np.abs(diff)
            #print("jump " + str(np.abs(diff)))

            return self.generate_texture(current_frame)


    def run(self, time):

        #
        if self.first:
            if time < 0:
                pass
            else:
                current_frame  = np.round( time/(1/60.) ).astype(np.int) # number of frames that should have been displayed according to Panda3D's timer
                #print "frame: ", current_frame
                new_tex        = self.generate_texture(current_frame)
                if new_tex:
                    self.shared.texture = new_tex

        #
        self.tex = self.shared.texture
        self.cylinder.setTexture(pcore.TextureStage.getDefault(), self.tex)

        self.trigger_routine(time)

        #if time > self.T:
        #    np.save("test_BinaryNoise_DiscreteTime.npy", self.shared.control_values)