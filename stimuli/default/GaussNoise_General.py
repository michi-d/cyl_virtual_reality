from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore
import numpy as np
import time


class GaussNoise_General(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, T = 30.0, N_phi = 64, N_z = -1, tau = 0.0):

        sampling_phi = 180./int(N_phi)
        if int(N_z) == -1: # -1 means: automatically round such that pixel are appoximately squares
            N_z_  = np.float(26./(sampling_phi/360. * 2 * np.pi * 10))
            N_z   = np.round(N_z_, 2).astype(np.int)
            print("Number of pixels in elevation: " + str(N_z_) + ", rounded to: " + str(N_z))
        else:
            N_z         = int(N_z)

        arg = (T, N_phi, N_z, tau)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['duration', 'N_phi', 'N_z', 'tau']

        self.T           = float(T)            # duration
        self.N_phi       = int(N_phi)        # number of pixels along azimuth
        self.N_z         = int(N_z)
        self.tau         = float(tau)

        tau_fs           = self.tau*60. # time constant in frames
        self.alpha       = (tau_fs / (tau_fs + 1.)) # low-pass filter parameter alpha
        self.scaling_fac = np.sqrt((1-self.alpha)/(1+self.alpha))

    def build(self):

        N_z   = self.N_z
        N_phi = self.N_phi
        self.N = N_z*N_phi

        # Texture: Background
        self.bg_tex_shape    = (N_z, N_phi)

        # set inital condition for lowpass filter
        np.random.seed(0)
        self.frame_memory = np.random.normal(0,self.scaling_fac,self.bg_tex_shape)
        np.random.seed(0)

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
            self.generate_texture(0)
            self.framecount = 1

        # set texture in all color worlds
        self.tex = self.shared.texture
        self.cylinder.setTexture(pcore.TextureStage.getDefault(), self.tex)
        self.cylinder.setTexScale(pcore.TextureStage.getDefault(), 2., 1.)


        #print "alpha: ", self.alpha


    def generate_texture(self, current_frame):

        diff = self.framecount - current_frame
        #print self.framecount, current_frame

        if diff > 0:
            # if number of generated frames is more than number of displayed frames, wait one frame
            #rint("wait a frame")
            return None

        elif diff == 0:
            # if number of generated frames equals number of displayes frames -> all good, generate next frame

            # get new random numbers and apply 1st order LP filter
            numbers = np.random.normal(0,1,self.bg_tex_shape) # get new numbers
            numbers = numbers * (1-self.alpha) + self.frame_memory * self.alpha # apply 1 step of a 1st order LP filter (recursive formula)
            self.frame_memory = np.copy(numbers) # memorize new numbers for the next time step

            #print numbers.std(), numbers.std()/self.scaling_fac, self.scaling_fac

            ###
            #self.shared.control_values[self.framecount, :, :] = numbers/self.scaling_fac
            ###
            self.framecount += 1

            # transform random numbers to stimulus -> map 95% of the values to the range between 0 - 255
            image = np.copy(numbers)/self.scaling_fac
            image[image<-2] = -2
            image[image>2]  = 2
            image = (image + 2)*(255/4.)

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
            np.random.normal(0,1,np.abs(diff)*self.N)
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
        #    np.save("test_GaussNoise_General.npy", self.shared.control_values)