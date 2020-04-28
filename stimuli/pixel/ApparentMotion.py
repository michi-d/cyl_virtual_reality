from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore
import numpy as np


class ApparentMotion(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, T = 5, N_steps = 5, dt = 0.5, phi0 = 90., z0 = 0., direction = 45., width = 10., height = 40., step_length = 20, c_on = 255, c_off = 0, c_bg = 125):

        self.sampling_phi = 0.5 # degrees per pixel (will be true for both phi and z)
        self.N_phi = np.round(180/self.sampling_phi).astype(np.int)

        # automatically round N_z such that pixel are appoximately squares
        N_z_  = np.float(26./(self.sampling_phi/360. * 2 * np.pi * 10))
        N_z   = np.round(N_z_, 2).astype(np.int)
        print("Number of pixels in elevation: " + str(N_z_) + ", rounded to: " + str(N_z))
        self.N_z = N_z

        arg = (T, N_steps, dt, phi0, z0, direction, width, height, step_length, c_on, c_off, c_bg)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ["stimulus_duration", "N_steps", "dt", "phi0", "z0", "direction", "width", "height", "step_length", "c_on", "c_off", "c_bg"]

        #self.T           = float(int(N_steps)*float(dt)) # duration
        self.T           = float(T)  # duration
        self.N_steps     = int(N_steps)
        self.dt          = float(dt)
        self.phi0        = float(phi0)
        self.z0          = float(z0)
        self.direction   = float(direction)
        self.width       = float(width)
        self.height      = float(height)
        self.step_length = float(step_length)
        self.c_on        = int(float(c_on))
        self.c_off       = int(float(c_off))
        self.c_bg        = int(float(c_bg))

    def build(self):


        # configure beamer
        self.set_arena_mode('greenHDMI')

        # generate standard cylinder
        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        self.cylinder.setScale(self.cylinder_radius, self.cylinder_radius, self.cylinder_height*1)

        ## PRE-RENDER background texture for all steps
        self.bg_tex_shape    = (self.N_z, self.N_phi, self.N_steps + 1)
        self.bg_tex_npy      = np.ones(self.bg_tex_shape)*(self.c_bg) # initialize as negative number (important to set BG color later)

        x0 =    self.phi0/self.sampling_phi # find x,y values for the center of the first box
        y0 =    0.5*self.N_z + self.N_z/13.0 * self.z0

        width    = self.width/self.sampling_phi # width and height of the box
        height   = self.height/self.sampling_phi

        mask_list = []
        for i in range(1,self.bg_tex_npy.shape[2]):
            n0    = np.array([np.sin(np.radians(self.direction)), np.cos(np.radians(self.direction))]) #  normal vector
            yn,xn = self.step_length / self.sampling_phi * n0 * (i-1) + np.array([y0,x0]) # center coordinates for n-th box

            mask = self.get_box_mask(self.N_phi, self.N_z, xn, yn, width/2., height/2., self.direction) # get pixels inside the box
            mask_list.append(mask) # remember each pixel mask for each time step

        for i in range(1,self.bg_tex_npy.shape[2]): # first, color all pixel during times where the box is OFF with c_off
            mask = mask_list[i-1]
            self.bg_tex_npy[mask,:i]     = self.c_off
            self.bg_tex_npy[mask,i+1:]   = self.c_off

        for i in range(1,self.bg_tex_npy.shape[2]): # second, color all pixel during times where the box is ON with c_on
            mask = mask_list[i-1]
            self.bg_tex_npy[mask,i]    = self.c_on

        self.texture_list = [] # convert the numpy array to actual panda3D textures and store them in a list for each time step
        for i in range(0, self.bg_tex_npy.shape[2]):
            self.texture_list.append(self.convert_npy_to_texture(self.bg_tex_npy[:,:,i]))

        # INITIALIZE CYLINDER TEXTURE for the start frame
        self.n_before = -1
        self.tex = self.texture_list[0]
        self.cylinder.setTexture(pcore.TextureStage.getDefault(), self.tex)
        self.cylinder.setTexScale(pcore.TextureStage.getDefault(), 2., 1.)


    def get_box_mask(self, N_X, N_Y, x0, y0, width, height, phi):

        '''
        This function calculates which image pixel are inside the box.
        For that, vector calculations in 2D are used. In particular, the edges of the box are expressed in
        the "Hesse-Normal form" for the definition of a straight line in 2D space. Pixels inside the box are then
        calculated by logic combination of all pixels lying on the inner side of the 4 box edges.

        :param N_X: image size in X
        :param N_Y: image size in Y
        :param x0: center of the box X coordinate
        :param y0: center of the box Y coordinate
        :param width: half width of the box (distance from center to edge)
        :param height: half height of the box (distance from center to edge)
        :param phi: orientation of the box
        :return: a binary mask indicating all the pixels inside the box
        '''

        X,Y = np.meshgrid(np.arange(N_X), np.arange(N_Y))
        R    = np.dstack((Y,X)) # create coordinate system

        n0_h = np.array([np.sin(np.radians(phi)), np.cos(np.radians(phi))])  # horizontal normal vector
        n0_v = np.array([np.cos(np.radians(phi)), -np.sin(np.radians(phi))]) # vertical normal vector

        # define hesse-normal form for the line corresponding to the right edge of the box
        v  = np.array([y0, x0]) + width * n0_h
        d_right  = np.dot(v,n0_h)

        # define hesse-normal form for the line corresponding to the left edge of the box
        v  = np.array([y0, x0]) - width * n0_h
        d_left = np.dot(v,n0_h)

        # define hesse-normal form for the line corresponding to the top edge of the box
        v  = np.array([y0, x0]) + height * n0_v
        d_top = np.dot(v,n0_v)

        # define hesse-normal form for the line corresponding to the bottom edge of the box
        v  = np.array([y0, x0]) - height * n0_v
        d_bottom = np.dot(v,n0_v)

        mask = ((np.dot(R, n0_h) - d_right) <= 0) & ((np.dot(R, n0_h) - d_left) >= 0) & ((np.dot(R, n0_v) - d_top) <= 0) & ((np.dot(R, n0_v) - d_bottom) >= 0) # get all pixel inside the box

        return mask


    def convert_npy_to_texture(self, image_npy):
        '''
        This function converts a 3D numpy array into a Panda3D texture that can be put onto the surface of an object
        :param image_npy: the input 2D numpy array
        :return: resulting Panda3D Texture
        '''

        tex = np.tile(image_npy, (3, 1, 1)).swapaxes(0, 1).swapaxes(1, 2).astype(np.uint8) # re-arrange axes and convert to 8-bit

        texture = pcore.Texture("image") # setup 2D Pandas Texture
        texture.setup2dTexture(tex.shape[1], tex.shape[0], pcore.Texture.TUnsignedByte, pcore.Texture.FRgb8)

        p = pcore.PTAUchar.emptyArray(0) # cryptic Panda3D stuff
        p.setData(tex.tostring())
        texture.setRamImage(pcore.CPTAUchar(p))

        texture.setMagfilter(pcore.Texture.FTNearest) # interpolation options for magnification and minification
        texture.setMinfilter(pcore.Texture.FTNearest)

        return texture


    def run(self, time):

        if (time < 0):
            pass
        elif (0 <= time < self.N_steps*self.dt):
            n_now = int(np.floor(time/self.dt)) # calculate the current time step (multiple of the step length dt)

            if n_now > self.n_before: # if a new step is reached, change the texture
                self.cylinder.setTexture(pcore.TextureStage.getDefault(), self.texture_list[n_now + 1])

            self.n_before = n_now # remember where we are

        elif (time >= self.N_steps*self.dt):
            self.cylinder.setTexture(pcore.TextureStage.getDefault(), self.texture_list[0])

        self.trigger_routine(time)
