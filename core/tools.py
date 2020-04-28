__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

import math
import numpy as np
import panda3d.core as pcore
from os.path import join, normpath

def create_rectangle(parent_node, r, phi, theta, Dphi, Dtheta, color):

    cm = pcore.CardMaker('card')
    card = parent_node.attachNewNode(cm.generate())

    width = 2 * math.tan(math.radians(Dphi)/2.) * r
    height = 2 * math.tan(math.radians(Dtheta)/2.) * r

    card.setHpr(90.+phi,90.+theta,0)

    card.setScale(width, 1, height)
    card.setPos(r*math.sin(math.radians(theta)) * math.cos(math.radians(phi)), r*math.sin(math.radians(theta)) * math.sin(math.radians(phi)) - width/2, r*math.cos(math.radians(theta)) + height/2. )

    card.setTwoSided(True)
    card.setColor(color/255., color/255., color/255.,1)

    return card


def create_striped_texture(c1, c2, nearest=True):
    texture = pcore.Texture("stripes")

    Pic = np.r_[np.tile(c1,(1,1)), np.tile(c2,(1,1))]

    Pic1 =  np.array([Pic], dtype=np.uint8)

    texture.setup2dTexture(Pic1.shape[1], Pic1.shape[0], pcore.Texture.TUnsignedByte, pcore.Texture.FRgb8)
    if nearest:
        texture.setMagfilter(pcore.Texture.FTNearest)
    texture.setMinfilter(pcore.Texture.FTLinearMipmapLinear)
    texture.setAnisotropicDegree(16)

    p1 = pcore.PTAUchar(); p1.setData(Pic1); c1= pcore.CPTAUchar(p1)
    texture.setRamImage(c1)

    return texture


def create_grating_texture(n, min_value, max_value):

    # generate grating texture
    image = pcore.PNMImage(n*2, 1)
    for i in range(n):
        image.setXelA(i,0,min_value/255.,min_value/255.,min_value/255.,1)
        #if i < 50:
        #    image.setXelA(i,0,50/255.,50/255.,50/255.,1)
    for i in range(n, n*2):
        image.setXelA(i,0,max_value/255.,max_value/255.,max_value/255.,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setAnisotropicDegree(16)
    #image.write(pcore.Filename("test.png"))

    return tex

def create_sine_grating_texture(n, min_value, max_value):

    # generate grating texture
    image = pcore.PNMImage(n*2, 1)
    for i in range(n*2):
        value = (math.sin(float(i)/(2*n)*2*math.pi) + 1)/2. * (max_value - min_value) + min_value
        image.setXelA(i,0,value/255.,value/255.,value/255.,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setAnisotropicDegree(16)
    #image.write(pcore.Filename("test.png"))

    return tex

def create_coloured_sine_grating_texture(n, min_value, max_value, color_vector):

    # generate grating texture
    image = pcore.PNMImage(n*2, 1)
    for i in range(n*2):
        value = (math.sin(float(i)/(2*n)*2*math.pi) + 1)/2. * (max_value - min_value) + min_value
        image.setXelA(i,0,value/255.*color_vector[0],value/255.*color_vector[1],value/255.*color_vector[2],1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setAnisotropicDegree(16)
    #image.write(pcore.Filename("test.png"))

    return tex


def create_bar_texture(angular_width, color, color_bg):

    # generate bar texture
    image = pcore.PNMImage(360, 1) # only 1 degree steps for the width of the bar
    for i in range(int(angular_width)):
        image.setXelA(i,0,color/255.,color/255.,color/255.,1)
    for i in range(int(angular_width), 360):
       image.setXelA(i, 0, color_bg/255., color_bg/255., color_bg/255., 1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setAnisotropicDegree(16)

    return tex


def create_window_texture(angular_width, z_width, color, color_bg):
    # this creates a texture of size (360 X 260) in pixels
    # this correspond to a precision of 1 degree in azimuth and 1mm in the z-axis in arena coordinates
    # one subregion of the texture of size (angular_width X z_width) is colored with "color"
    # the rest of the texture is colored with "color_bg"

    # generate bar texture
    image = pcore.PNMImage(360, 260) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    image.fill(color_bg/255.)
    for i in range(int(angular_width)):
        for j in range(int(np.round(z_width/0.1))):
            image.setXelA(i,j,color/255.,color/255.,color/255.,1)
    for i in range(int(angular_width), 360):
        for j in range(int(np.round(z_width/0.1))):
            image.setXelA(i, 0, color_bg/255., color_bg/255., color_bg/255., 1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex


def create_content_texture(content, color_bg):
    # this creates a texture of size (360 X 260) in pixels
    # this correspond to a precision of 1 degree in azimuth and 1mm in the z-axis in arena coordinates
    # one subregion of the texture gets a given content
    # the rest is filled with background

    angular_width, z_width = content.shape

    # generate bar texture
    image = pcore.PNMImage(360, 260) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    image.fill(color_bg/255.)
    for i in range(int(angular_width)):
        for j in range(int(np.round(z_width))):
            image.setXelA(i,j,content[i,j]/255.,content[i,j]/255.,content[i,j]/255.,1)
    #for i in range(int(angular_width), 360):
    #    for j in range(int(np.round(z_width/0.1))):
    #        image.setXelA(i, 0, color_bg/255., color_bg/255., color_bg/255., 1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex

def create_window_texture_set_size(angular_width, z_width, color, color_bg, size_phi, size_z):
    # this creates a texture of size (size_phi X size_z) in pixels
    # one subregion of the texture of size (angular_width X z_width) is colored with "color"
    # the rest of the texture is colored with "color_bg"

    # generate bar texture
    image = pcore.PNMImage(size_phi, size_z) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    image.fill(color_bg/255.)
    for i in range(int(angular_width)):
        for j in range(int(np.round(z_width/0.1))):
            image.setXelA(i,j,color/255.,color/255.,color/255.,1)
    for i in range(int(angular_width), size_phi):
        for j in range(int(np.round(z_width/0.1))):
            image.setXelA(i, 0, color_bg/255., color_bg/255., color_bg/255., 1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex


def create_circular_window_texture(angular_width, color, color_bg):

    # generate bar texture
    image = pcore.PNMImage(360*3, 260*2) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    #z_width = (angular_width/360. * 2 * math.pi*10) / 26 * (np.degrees(np.arctan(13/10.)) * 2)
    z_width = np.radians(angular_width) * 10  # Kleinwinkelnaeherung / approximation for small angular widths
    #print z_width

    image.fill(color_bg/255.)
    for i in range( min([360*3, int(angular_width)*3]) ):
        for j in range( min([260*2, int(np.round(z_width/0.1*2))]) ):
            if (i - angular_width/2.*3)**2/(angular_width/2.*3)**2  + (j - z_width/0.1/2.*2)**2/(z_width/0.1/2.*2)**2 <= 1:
                image.setXelA(i,j,color/255.,color/255.,color/255.,1)


    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTNearest)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex


def create_ellipse_window_texture(angular_width, z_width, color, color_bg):

    # analogue to create_circular_window_texture, only width an additional z_width
    # (used to account for perspective distortions when showing larger angles).

    # generate bar texture

    precision = 0.2

    image = pcore.PNMImage(360*3, 260*2) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    #z_width = (angular_width/360. * 2 * math.pi*10) / 26 * (np.degrees(np.arctan(13/10.)) * 2)
    #z_width = np.radians(angular_width) * 10  # Kleinwinkelnaeherung / approximation for small angular widths
    #print z_width

    image.fill(color_bg/255.)
    for i in range( min([360*3, int(angular_width)*3]) ):
        for j in range( min([260*2, int(np.round(z_width/precision*2))]) ):
            if (i - angular_width/2.*3)**2/(angular_width/2.*3)**2  + (j - z_width/precision/2.*2)**2/(z_width/precision/2.*2)**2 <= 1:
                image.setXelA(i,j,color/255.,color/255.,color/255.,1)

    print("zwidth")
    print(z_width)

    # SHOW BORDERS OF THE LOOP FROM ABOVE
    #for i in range(0,360*3):
    #        image.setXelA(i,0,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-3,color/255.,color/255.,color/255.,1)
    #for j in range(0,260*2):
    #        image.setXelA(0,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-3,j,color/255.,color/255.,color/255.,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTNearest)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex


def create_ellipse_window_texture_transparent_bg(angular_width, z_width, color, color_bg):

    # analogue to create_circular_window_texture, only width an additional z_width
    # (used to account for perspective distortions when showing larger angles).

    # generate bar texture

    precision = 0.2

    image = pcore.PNMImage(360*3, 260*2) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    #z_width = (angular_width/360. * 2 * math.pi*10) / 26 * (np.degrees(np.arctan(13/10.)) * 2)
    #z_width = np.radians(angular_width) * 10  # Kleinwinkelnaeherung / approximation for small angular widths
    #print z_width

    image.fill(color_bg/255.)
    image.alphaFillVal(0.)
    for i in range( min([360*3, int(angular_width)*3]) ):
        for j in range( min([260*2, int(np.round(z_width/precision*2))]) ):
            if (i - angular_width/2.*3)**2/(angular_width/2.*3)**2  + (j - z_width/precision/2.*2)**2/(z_width/precision/2.*2)**2 <= 1:
                image.setXelA(i,j,color/255.,color/255.,color/255.,1)

    print("zwidth")
    print(z_width)
    # SHOW BORDERS OF THE LOOP FROM ABOVE
    #for i in range(0,360*3):
    #        image.setXelA(i,0,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-3,color/255.,color/255.,color/255.,1)
    #for j in range(0,260*2):
    #        image.setXelA(0,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-3,j,color/255.,color/255.,color/255.,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTNearest)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex


def create_ellipse_window_texture_transparent_fg(angular_width, z_width, color, color_bg):

    # analogue to create_circular_window_texture, only width an additional z_width
    # (used to account for perspective distortions when showing larger angles).

    # generate bar texture

    precision = 0.2

    image = pcore.PNMImage(360*3, 260*2) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    #z_width = (angular_width/360. * 2 * math.pi*10) / 26 * (np.degrees(np.arctan(13/10.)) * 2)
    #z_width = np.radians(angular_width) * 10  # Kleinwinkelnaeherung / approximation for small angular widths
    #print z_width

    image.fill(color_bg/255.)
    image.alphaFillVal(255)
    for i in range( min([360*3, int(angular_width)*3]) ):
        for j in range( min([260*2, int(np.round(z_width/precision*2))]) ):
            if (i - angular_width/2.*3)**2/(angular_width/2.*3)**2  + (j - z_width/precision/2.*2)**2/(z_width/precision/2.*2)**2 <= 1:
                image.setXelA(i,j,color/255.,color/255.,color/255.,0)
                #image.setAlphaVal(i,j,0.1)

    print("zwidth")
    print(z_width)
    # SHOW BORDERS OF THE LOOP FROM ABOVE
    #for i in range(0,360*3):
    #        image.setXelA(i,0,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-3,color/255.,color/255.,color/255.,1)
    #for j in range(0,260*2):
    #        image.setXelA(0,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-3,j,color/255.,color/255.,color/255.,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTNearest)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex

def create_ellipse_annulus_texture(angular_width, z_width, center_width, color, color_bg, color_annulus):

    # analogue to create_ellipse_window_texture:
    #
    # center_width gives the width of the center part
    # color gives the color of the center part
    # color_bg gives the color of the background
    # color_annulus gives the color of the annulus

    center_width_z = z_width/float(angular_width)*center_width # same dphi/dz ratio for the center

    precision = 0.2
    image = pcore.PNMImage(360*3, 260*2) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    #z_width = (angular_width/360. * 2 * math.pi*10) / 26 * (np.degrees(np.arctan(13/10.)) * 2)
    #z_width = np.radians(angular_width) * 10  # Kleinwinkelnaeherung / approximation for small angular widths
    #print z_width

    image.fill(color_bg/255.)
    for i in range( min([360*3, int(angular_width)*3]) ):
        for j in range( min([260*2, int(np.round(z_width/precision*2))]) ):

            # big circle
            if (i - angular_width/2.*3)**2/(angular_width/2.*3)**2  + (j - z_width/precision/2.*2)**2/(z_width/precision/2.*2)**2 <= 1:
                image.setXelA(i,j,color_annulus/255.,color_annulus/255.,color_annulus/255.,1)

            # center circle
            if (i - angular_width/2.*3)**2/(center_width/2.*3)**2  + (j - z_width/precision/2.*2)**2/(center_width_z/precision/2.*2)**2 <= 1:
                image.setXelA(i,j,color/255.,color/255.,color/255.,1)

    #print "color annulu"
    #print color_annulus
    #print "color center"
    #print color
    # SHOW BORDERS OF THE LOOP FROM ABOVE
    #for i in range(0,360*3):
    #        image.setXelA(i,0,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-1,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-2,color/255.,color/255.,color/255.,1)
    #        image.setXelA(i,int(np.round(z_width/0.1*2))-3,color/255.,color/255.,color/255.,1)
    #for j in range(0,260*2):
    #        image.setXelA(0,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-1,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-2,j,color/255.,color/255.,color/255.,1)
    #        image.setXelA(int(angular_width)*3-3,j,color/255.,color/255.,color/255.,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTNearest)
    tex.setBorderColor(pcore.Vec4(color_bg/255., color_bg/255., color_bg/255., 1))
    tex.setWrapU(pcore.Texture.WM_border_color)
    tex.setWrapV(pcore.Texture.WM_border_color)
    tex.setAnisotropicDegree(16)

    return tex


def make_matrix_to_texture(M):

    # generate bar texture
    image = pcore.PNMImage(M.shape[0], M.shape[1]) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    for i in range(int(M.shape[0])):
        for j in range(int(M.shape[1])):
            image.setXelA(i,j,M[i,j]/255.,M[i,j]/255.*1,M[i,j]/255.*1,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTNearest)
    tex.setAnisotropicDegree(16)

    return tex



def set_texture(cylinder, ts, image):
    # by Aljoska

    image = np.clip(image, 0.0, 1.0) * 255.0

    tex = np.tile(image, (3, 1, 1)).swapaxes(0, 1).swapaxes(1, 2).astype(np.uint8)

    texture = pcore.Texture("image")
    texture.setup2dTexture(tex.shape[1], tex.shape[0], pcore.Texture.TUnsignedByte, pcore.Texture.FRgb8)

    p = pcore.PTAUchar.emptyArray(0)
    p.setData(tex.tostring())
    texture.setRamImage(pcore.CPTAUchar(p))

    texture.setMagfilter(pcore.Texture.FTNearest)
    texture.setMinfilter(pcore.Texture.FTNearest)

    cylinder.setTexture(ts, texture)
    #cylinder.setTexScale(ts, 1., 1.)



def create_test_texture(angular_width, z_width, color, color_bg, size_phi, size_z):

    # generate bar texture
    image = pcore.PNMImage(size_phi, size_z) # only 1 degree steps for the width of the window and 0.1 units steps for the height of the window
    image.fill(color_bg/255.)
    # for i in range(0, 20):
    #     for j in range(int(size_z)-20, int(size_z)):
    #         image.setXelA(i,j,color/255.,color/255.,color/255.,1)

    for i in range(0, size_phi):
        image.setXelA(i, 0, color_bg/255., color_bg/255., color_bg/255., 1)
        image.setXelA(i, size_z-1, color/255., color/255., color/255., 1)
    for i in range(0, size_z):
        image.setXelA(0, i, color_bg/255., color_bg/255., color_bg/255., 1)
        image.setXelA(size_phi-1, i, color/255., color/255., color/255., 1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setAnisotropicDegree(16)

    return tex


def create_plain_texture(color):

    image = pcore.PNMImage(1, 1)
    image.setXelA(0,0,color/255.,color/255.,color/255.,1)

    tex = pcore.Texture()
    tex.load(image)
    tex.setMagfilter(pcore.Texture.FTLinearMipmapLinear)
    tex.setAnisotropicDegree(16)

    return tex


def create_cylinder_segment(parent_node, delta_azimuth):

    vdata = pcore.GeomVertexData('name', pcore.GeomVertexFormat.getV3t2(), pcore.Geom.UHDynamic)

    vertex_writer = pcore.GeomVertexWriter(vdata, 'vertex')
    texcoord_writer = pcore.GeomVertexWriter(vdata, 'texcoord')

    prim_wall = pcore.GeomTristrips(pcore.Geom.UHStatic)

    unit_count = int(delta_azimuth)
    units = 360#360
    #print unit_count
    for i in range(unit_count):

        angle1 = i/float(units)*2*3.1452#/float(parts)
        angle2 = (i+1)/float(units)*2*3.1452#/float(parts)

        x1 = math.sin(angle1)
        y1 = math.cos(angle1)

        x2 = math.sin(angle2)
        y2 = math.cos(angle2)

        vertex_writer.addData3f(x1, y1, 1/2.)
        vertex_writer.addData3f(x1, y1, -1/2.)
        vertex_writer.addData3f(x2, y2, 1/2.)
        vertex_writer.addData3f(x2, y2, -1/2.)

        #texcoord_writer.addData2f(i/float(units),1)
        #texcoord_writer.addData2f(i/float(units),0)
        #texcoord_writer.addData2f((i+1)/float(units),1)
        #texcoord_writer.addData2f((i+1)/float(units),0)
        texcoord_writer.addData2f(i/float(unit_count),1)
        texcoord_writer.addData2f(i/float(unit_count),0)
        texcoord_writer.addData2f((i+1)/float(unit_count),1)
        texcoord_writer.addData2f((i+1)/float(unit_count),0)

        prim_wall.addConsecutiveVertices(i*4, 4)
        prim_wall.closePrimitive()

    geom_wall = pcore.Geom(vdata)
    geom_wall.addPrimitive(prim_wall)

    cylinder_parts = []

    cylinder = parent_node.attachNewNode("cylinder")

    cylinder_geomnode_part = pcore.GeomNode('cylinder_part')
    cylinder_geomnode_part.addGeom(geom_wall)

    cylinder_part = cylinder.attachNewNode(cylinder_geomnode_part)
    cylinder_parts.append(cylinder_part)

    return cylinder



def create_cylinder_parts(parent_node, parts, units):
    vdata = pcore.GeomVertexData('name', pcore.GeomVertexFormat.getV3t2(), pcore.Geom.UHDynamic)

    vertex_writer = pcore.GeomVertexWriter(vdata, 'vertex')
    texcoord_writer = pcore.GeomVertexWriter(vdata, 'texcoord')

    prim_wall = pcore.GeomTristrips(pcore.Geom.UHStatic)

    for i in range(units):

        angle1 = i/float(units)*2*3.1452/float(parts)
        angle2 = (i+1)/float(units)*2*3.1452/float(parts)

        x1 = math.sin(angle1)
        y1 = math.cos(angle1)

        x2 = math.sin(angle2)
        y2 = math.cos(angle2)

        vertex_writer.addData3f(x1, y1, 0.5)
        vertex_writer.addData3f(x1, y1, -0.5)
        vertex_writer.addData3f(x2, y2, 0.5)
        vertex_writer.addData3f(x2, y2, -0.5)

        texcoord_writer.addData2f(i/float(units),1)
        texcoord_writer.addData2f(i/float(units),0)
        texcoord_writer.addData2f((i+1)/float(units),1)
        texcoord_writer.addData2f((i+1)/float(units),0)

        prim_wall.addConsecutiveVertices(i*4, 4)
        prim_wall.closePrimitive()

    geom_wall = pcore.Geom(vdata)
    geom_wall.addPrimitive(prim_wall)

    cylinder_parts = []

    cylinder = parent_node.attachNewNode("cylinder")

    for part in range(parts):
        cylinder_geomnode_part = pcore.GeomNode('cylinder_part %d'%part)
        cylinder_geomnode_part.addGeom(geom_wall)

        cylinder_part = cylinder.attachNewNode(cylinder_geomnode_part)
        cylinder_parts.append(cylinder_part)

    if parts > 1:
        return (cylinder, cylinder_parts)
    else:
        return cylinder


def standard_cylinder(parent_node):

    cylinder_height = 26
    cylinder_radius = 10

    cylinder = create_cylinder_parts(parent_node, 1, 360)
    cylinder.reparentTo(parent_node)
    cylinder.setPos(0,0,0)
    cylinder.setScale(cylinder_radius,cylinder_radius,cylinder_height)
    cylinder.setHpr(90,0,0)

    return cylinder_height, cylinder_radius, cylinder



def create_sphere(parent_node, units):

        vdata = pcore.GeomVertexData('name', pcore.GeomVertexFormat.getV3t2(), pcore.Geom.UHDynamic)

        vertex_writer = pcore.GeomVertexWriter(vdata, 'vertex')
        texcoord_writer = pcore.GeomVertexWriter(vdata, 'texcoord')

        prim_wall = pcore.GeomTriangles(pcore.Geom.UHStatic)

        vertex_count = 0
        for i in range(units):

            phi1 = i/float(units)*2*3.1452
            phi2 = (i+1)/float(units)*2*3.1452

            for j in range(int(np.floor(units/2))):

                theta1 = j/float(units/2)*1*3.1452
                theta2 = (j+1)/float(units/2)*1*3.1452

                x1 = math.cos(phi1) * math.sin(theta1)
                y1 = math.sin(phi1) * math.sin(theta1)
                z1 = math.cos(theta1)

                x2 = math.cos(phi2) * math.sin(theta1)
                y2 = math.sin(phi2) * math.sin(theta1)
                z2 = math.cos(theta1)

                x3 = math.cos(phi1) * math.sin(theta2)
                y3 = math.sin(phi1) * math.sin(theta2)
                z3 = math.cos(theta2)

                x4 = math.cos(phi2) * math.sin(theta2)
                y4 = math.sin(phi2) * math.sin(theta2)
                z4 = math.cos(theta2)

                vertex_writer.addData3f(x1, y1, z1)
                vertex_writer.addData3f(x2, y2, z2)
                vertex_writer.addData3f(x3, y3, z3)

                texcoord_writer.addData2f(math.sin(theta1) * math.cos(phi1), math.sin(theta1) * math.sin(phi1))
                texcoord_writer.addData2f(math.sin(theta1) * math.cos(phi2), math.sin(theta1) * math.sin(phi2))
                texcoord_writer.addData2f(math.sin(theta2) * math.cos(phi1), math.sin(theta2) * math.sin(phi1))

                vertex_count = vertex_count + 3

                prim_wall.addConsecutiveVertices(vertex_count - 3, 3)
                prim_wall.closePrimitive()

                vertex_writer.addData3f(x2, y2, z2)
                vertex_writer.addData3f(x3, y3, z3)
                vertex_writer.addData3f(x4, y4, z4)

                texcoord_writer.addData2f(math.sin(theta1) * math.cos(phi2), math.sin(theta1) * math.sin(phi2))
                texcoord_writer.addData2f(math.sin(theta2) * math.cos(phi1), math.sin(theta2) * math.sin(phi1))
                texcoord_writer.addData2f(math.sin(theta2) * math.cos(phi2), math.sin(theta2) * math.sin(phi2))

                vertex_count = vertex_count + 3

                prim_wall.addConsecutiveVertices(vertex_count - 3, 3)
                prim_wall.closePrimitive()


        geom_wall = pcore.Geom(vdata)
        geom_wall.addPrimitive(prim_wall)

        sphere = parent_node.attachNewNode("sphere")

        sphere_geomnode = pcore.GeomNode("sphere")
        sphere_geomnode.addGeom(geom_wall)

        sphere_model = sphere.attachNewNode(sphere_geomnode)

        return (sphere, sphere_model)



def make_panda3d_path(arena_path, subpath):
        outpath = join(normpath(arena_path), subpath)
        outpath = normpath(outpath)
        sep = normpath('s/s')[1]
        outpath = outpath.replace(sep, '/')
        outpath = outpath.replace('C:/', '/c/')
        return outpath