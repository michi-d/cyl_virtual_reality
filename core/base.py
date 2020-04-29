#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 2/13/2014

@author: "Michael Drews"

"""
__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"


import math as math
import sys as sys
import numpy as np
import subprocess

import panda3d.core as pcore

from direct.showbase.ShowBase import ShowBase

from .FirstPersonCamera import FirstPersonCamera
from .CoordinateSystem import CoordinateSystem
from .gridProjection import gridProjection

from experiment.StimulusFramework import StimulusFramework

import json as json

import os as os


class CylindricArena(ShowBase):

    '''
    Base class for the cylindrical VR setup.
    Pre-distortion of images for projection onto a curved screen.
    '''

    def __init__(self, calibration):

        ShowBase.__init__(self)
        #super(CylindricArena, self).__init__()
        self.shared = []

        self.accept('escape', self.exitarena)
        self.render.setAntialias(pcore.AntialiasAttrib.MMultisample)
        self.trigger_render = self.render

        # define center of (projected) world
        self.center = self.render.attachNewNode("center")
        self.center.setPos(0,0,0)

        # mouse move
        #base.win.movePointer(0, 10, 10)

        #self.cam.setPos(30,-5, 15	)
        #self.cam.lookAt(self.center)
        self.displayRegion0 = base.camNode.getDisplayRegion(0)
        #dr.setActive(0)
        
        # generate coordinate system
        self.cosy = CoordinateSystem(self.render, length = 30, key = 'c')     
        
        # set up WASD first person camera control
        self.mouseLook = FirstPersonCamera(self, self.cam, self.render)
                 
        # show frame rate (fps)
        self.setFrameRateMeter(False)
          
        # define projection screen
        self.cylinder_radius = 5.
        self.cylinder_height = 13.#13.46
        
        (_, [self.screen_right, self.screen_left, cyl3, cyl4]) = self.create_cylinder_parts(4, 90) 
        #self.screen = self.create_cylinder_parts(1, 360)
        cyl3.removeNode()
        cyl4.removeNode()
                
        self.screen_right.setPos(0,0,0)
        self.screen_right.setScale(self.cylinder_radius,self.cylinder_radius,self.cylinder_height)
        self.screen_right.setHpr(-90,0,0)
        self.screen_right.setTwoSided(True) 
        #self.screen_right.setAttrib(pcore.CullFaceAttrib.make(pcore.CullFaceAttrib.MCullCounterClockwise))
        
        self.screen_left.setPos(0,0,0)
        self.screen_left.setScale(self.cylinder_radius,self.cylinder_radius,self.cylinder_height)
        self.screen_left.setHpr(0,0,0)
        self.screen_left.setTwoSided(True)
        #self.screen_left.setAttrib(pcore.CullFaceAttrib.make(pcore.CullFaceAttrib.MCullCounterClockwise))
        
        # define position and orientation of the right projector (for the right part of the screen)
        self.lens_fly = pcore.PerspectiveLens()
        self.lens_fly.setFov(90, 130)
        self.lens_fly.setNearFar(1,50)
        
        self.proj_right = render.attachNewNode(pcore.LensNode('proj'))    
        self.proj_right.node().setLens(self.lens_fly)
        self.proj_right.reparentTo(render)
        self.proj_right.setPos(0,0,0)
        self.proj_right.setHpr(-90-45,0,0)
        #self.proj_right.node().showFrustum()
        
        # define position and orientation of the left projector (for the left part of the screen)
        self.lens_fly = pcore.PerspectiveLens()
        self.lens_fly.setFov(90, 130)
        self.lens_fly.setNearFar(1,50)
        
        self.proj_left = render.attachNewNode(pcore.LensNode('proj'))    
        self.proj_left.node().setLens(self.lens_fly)
        self.proj_left.reparentTo(render)
        self.proj_left.setPos(0,0,0)
        self.proj_left.setHpr(-90+45,0,0)

        self.ts1_left = pcore.TextureStage('ts1_left')
        self.ts2_left = pcore.TextureStage('ts2_left')
        self.ts3_left = pcore.TextureStage('ts3_left')
        self.ts4_left = pcore.TextureStage('ts4_left')
        self.ts_left = [self.ts1_left, self.ts2_left, self.ts3_left, self.ts4_left]

        self.ts1_right = pcore.TextureStage('ts1_right')
        self.ts2_right = pcore.TextureStage('ts2_right')
        self.ts3_right = pcore.TextureStage('ts3_right')
        self.ts4_right = pcore.TextureStage('ts4_right')
        self.ts_right = [self.ts1_right, self.ts2_right, self.ts3_right, self.ts4_right]
        #self.proj_left.node().showFrustum()       

        # define angular aperture of the beamers
        self.omega_h = 34.915  # 34.915 (from Throw Ratio 1.66 as in DLP Lightcrafter description) # 33.50 measured with a ruler
        self.omega_v = 19.430  # 19.430 (from Throw Ratio 1.66 as in DLP Lightcrafter description) # 19.82 measured with a ruler

        # define right beamer point of view
        self.rig_beamer_right = pcore.NodePath('rig_beamer_right')

        self.beamer_right_d   = 20.6
        self.beamer_right_phi = - 45.#math.degrees(math.asin(math.tan(math.radians(self.omega_v/2.))*self.beamer_right_d/self.cylinder_radius))
        self.beamer_right_b   = math.cos(math.radians(self.beamer_right_phi))*self.cylinder_radius
        self.beamer_right_h   = 0
        
        self.rig_beamer_right.setPos((self.beamer_right_d+self.beamer_right_b)*math.cos(math.radians(self.beamer_right_phi)),(self.beamer_right_d+self.beamer_right_b)*math.sin(math.radians(self.beamer_right_phi)),self.beamer_right_h)
        self.rig_beamer_right.lookAt(self.center)
        self.rig_beamer_right.setR(self.rig_beamer_right.getR() - 90)
        self.rig_beamer_right.reparentTo(self.render)
        #self.beamer_right_model = self.loader.loadModel('camera.egg')
        #self.beamer_right_model.reparentTo(self.rig_beamer_right)  
        
        self.lens_beamer_right = pcore.PerspectiveLens()
        self.lens_beamer_right.setFov(self.omega_h, self.omega_v)
        self.cam_beamer_right = pcore.Camera('cam_beamer_right')
        self.cam_beamer_right_NP = pcore.NodePath(self.cam_beamer_right)
        self.cam_beamer_right_NP.reparentTo(self.rig_beamer_right)
        self.cam_beamer_right.setLens(self.lens_beamer_right)
        self.cam_beamer_right_NP.setPos(0,0,0)
        if calibration:
            self.cam_beamer_right_NP.setPos(calibration[6], calibration[7], calibration[8])
            self.cam_beamer_right_NP.setHpr(calibration[9], calibration[10], calibration[11])
            self.lens_beamer_right.setFov(self.omega_h + calibration[13][0], self.omega_v + calibration[13][1])
        
        self.projection_right = gridProjection(self, self.screen_right, self.cam_beamer_right_NP, self.lens_beamer_right, "1", [1, 0, 0, 0])
        self.cosy_right_beamer = CoordinateSystem(self.rig_beamer_right, length = 5, key = 'x')
        

        # define left beamer point of view
        self.rig_beamer_left = pcore.NodePath('rig_beamer_left')#
        self.beamer_left_d   = 20.6
        self.beamer_left_phi = 45.#math.degrees(math.asin(math.tan(math.radians(self.omega_v/2.))*self.beamer_left_d/self.cylinder_radius))
        self.beamer_left_b   = math.cos(math.radians(self.beamer_left_phi))*self.cylinder_radius
        self.beamer_left_h   = 0

        self.rig_beamer_left.setPos((self.beamer_left_d+self.beamer_left_b)*math.cos(math.radians(self.beamer_left_phi)),(self.beamer_left_d+self.beamer_left_b)*math.sin(math.radians(self.beamer_left_phi)),self.beamer_left_h)

        self.rig_beamer_left.lookAt(self.center)
        self.rig_beamer_left.setR(self.rig_beamer_left.getR() - 90)
        self.rig_beamer_left.reparentTo(render)
        #self.beamer_left_model = self.loader.loadModel('camera.egg')
        #self.beamer_left_model.reparentTo(self.rig_beamer_left)       
        
        self.lens_beamer_left = pcore.PerspectiveLens()
        self.lens_beamer_left.setFov(self.omega_h, self.omega_v)
        self.cam_beamer_left = pcore.Camera('cam_beamer_left')
        self.cam_beamer_left_NP = pcore.NodePath(self.cam_beamer_left)
        self.cam_beamer_left_NP.reparentTo(self.rig_beamer_left)
        self.cam_beamer_left.setLens(self.lens_beamer_left)
        self.cam_beamer_left_NP.setPos(0,0,0)
        if calibration:
            self.cam_beamer_left_NP.setPos(calibration[0], calibration[1], calibration[2])
            self.cam_beamer_left_NP.setHpr(calibration[3], calibration[4], calibration[5])
            self.lens_beamer_left.setFov(self.omega_h + calibration[12][0], self.omega_v + calibration[12][1])

        self.projection_left = gridProjection(self, self.screen_left, self.cam_beamer_left_NP, self.lens_beamer_left, "2", [0, 0, 1, 0])
        self.cosy_left_beamer = CoordinateSystem(self.rig_beamer_left, length = 5, key = 'v')


    def exitarena(self):
        
        #with disable_file_system_redirection():
        subprocess.call("displayswitch /extend", shell=True)
            
        self.taskMgr.stop()

        self.shared.MCC_DAQ_running.value = 0
        self.shared.experiment_running.value = 0
        self.shared.camera_control_running.value = 0
        self.shared.pinger_running.value = 0
        self.shared.virtual_cell_running.value = 0

        # print "arena PID:"
        # print os.getpid()
        # os.kill(os.getpid(), 9)

        sys.exit()
        #self.userExit()

    def startarena(self):
        self.run()


    def create_cylinder_parts(self, parts, units):
        
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
                
        cylinder = self.center.attachNewNode("cylinder")
                    
        for part in range(parts):
            cylinder_geomnode_part = pcore.GeomNode('cylinder_part %d'%part)
            cylinder_geomnode_part.addGeom(geom_wall)
                    
            cylinder_part = cylinder.attachNewNode(cylinder_geomnode_part)
            cylinder_parts.append(cylinder_part)
                
        if parts > 1:
            return (cylinder, cylinder_parts)
        else:
            return cylinder  


class StimulusArena(CylindricArena):

    def __init__(self, calibration, shared, win_origin):
        print(win_origin)
        if shared.arena_mode != "monitored":
            pcore.loadPrcFileData("","""
                load-display pandagl
                #sync-video 1
                win-size 1216 684
                win-origin """ + str(win_origin[0]) + " " + str(win_origin[1]) + """
                #fullscreen t
                undecorated 1
                audio-library-name null
                """)


            if len(shared.virtual_cell) > 0:

                pcore.loadPrcFileData("","""
                    load-display pandagl
                    #sync-video 1
                    win-size 1216 684
                    win-origin""" + str(win_origin[0]) + " " + str(win_origin[1]) + """
                    #fullscreen t
                    undecorated 1
                    audio-library-name null
                    clock-mode limited
                    clock-frame-rate 20
                    """)

                print("THIS IS A VIRTUAL CELL")

                from pandac.PandaModules import ClockObject
                FPS = 20
                globalClock = ClockObject.getGlobalClock()
                globalClock.setMode(ClockObject.MLimited)
                globalClock.setFrameRate(FPS)

        else:

            pcore.loadPrcFileData("","""
                load-display pandagl
                #sync-video 1
                win-size 1216 684
                win-origin""" + str(win_origin[0]) + " " + str(win_origin[1]) + """
                #fullscreen t
                undecorated 1
                audio-library-name null
                """)


        CylindricArena.__init__(self, calibration)
        self.shared = shared

        # # set up second window
        # wp = pcore.WindowProperties()
        # wp.setSize(608, 684)
        # wp.setOrigin(0 + 608, 0)
        # wp.setUndecorated(True)
        #
        # self.win2 = self.graphicsEngine.makeOutput(self.pipe, 'win2', 0,
        #              pcore.FrameBufferProperties.getDefault(),
        #              wp,
        #              0,
        #              gsg = self.win.getGsg())
        #
        #
        # self.displayRegion1 = self.win2.makeDisplayRegion()
        #
        # self.displayRegion1.setCamera(self.cam_beamer_left_NP)
        # self.displayRegion0.setCamera(self.cam_beamer_right_NP)

        self.camNode.getDisplayRegion(0).setDimensions(0, 0.5, 0, 1)
        #self.displayRegion0 = self.win.makeDisplayRegion(0,0.5,0,1)
        self.displayRegion1 = self.win.makeDisplayRegion(0.5,1,0,1)

        self.displayRegion0.setCamera(self.cam_beamer_right_NP)
        self.displayRegion1.setCamera(self.cam_beamer_left_NP)

        base.setBackgroundColor(0,0,0)

        # set up RGB color world copies
        self.red_world = FlyPointOfView((2**10,2**10))
        self.green_world = FlyPointOfView((2**10,2**10))
        self.blue_world = FlyPointOfView((2**10,2**10))
        self.RGB_POVs = [self.red_world, self.green_world, self.blue_world]

        for i in np.arange(len(self.RGB_POVs)):
            self.RGB_POVs[i].projectOntoArena(self.ts_left[i], self.ts_right[i], self.proj_right, self.proj_left, self.screen_right, self.screen_left, i != 0)
        self.update_colors()
        self.go_arena = True
        self.shared.ready[0] = 1 # set readiness value for ExperimentFramework

        winprops = pcore.WindowProperties()
        winprops.setForeground(True)
        base.win.requestProperties(winprops)

        # NOTE: THIS WORKS ONLY FOR WINDOWS SYSTEMS
        # sets the priority of all running python processes to high
        os.system("wmic process where name='python.exe' CALL setpriority 'high priority'")



    def update_colors(self):
        self.red_world.render.setColorScale(1,0,0,1)
        self.green_world.render.setColorScale(0,1,0,1)
        self.blue_world.render.setColorScale(0,0,1,1)


    def show_stimulus(self, start_pause, name, *arg):

        RGB_OFFSET = [1., 2., 0.]
        self.rgb_stimulus = []
        for i in range(3):
            self.rgb_stimulus.append(StimulusFramework(self.RGB_POVs[i].render, self.RGB_POVs[i].camera_rig, self.taskMgr, RGB_OFFSET[i]))
        self.update_colors()

        for i in range(3):
            self.rgb_stimulus[i].build_stimulus(start_pause, name, arg)
            self.rgb_stimulus[i].parent_taskMgr.add(self.rgb_stimulus[i].general_stimulus_task, 'general_stimulus_task' + str(i))


class PreviewArena(CylindricArena):

    def __init__(self, calibration, shared):

        pcore.loadPrcFileData("","""
            load-display pandagl
            #sync-video 1
            #win-size 304 342
            #win-size 600 600
            win-origin 100 100
            #fullscreen t
            undecorated 0
            audio-library-name null
            """)



        CylindricArena.__init__(self, calibration)
        self.shared = shared
        self.cam.setPos(-25,0,0)
        self.cam.lookAt(self.center)

        # set up RGB color world copies
        self.red_world = FlyPointOfView((2**10,2**10))
        self.green_world = FlyPointOfView((2**10,2**10))
        self.blue_world = FlyPointOfView((2**10,2**10))
        self.RGB_POVs = [self.red_world, self.green_world, self.blue_world]

        for i in np.arange(len(self.RGB_POVs)):
            self.RGB_POVs[i].projectOntoArena(self.ts_left[i], self.ts_right[i], self.proj_right, self.proj_left, self.screen_right, self.screen_left, i != 0)
        self.update_colors()
        self.go_arena = True
        self.shared.ready[0] = 1 # set readiness value for ExperimentFramework

        winprops = pcore.WindowProperties()
        winprops.setForeground(True)
        base.win.requestProperties(winprops)

        self.accept('tab', self.change_view)
        self.view = 0
        self.last_virtual_world_pos = pcore.Vec3(0,0,0)
        self.last_virtual_world_hpr = pcore.Vec3(0,0,0)

        self.cosy_virtual = CoordinateSystem(self.red_world.render, length = 30, key = 'c')

        # self.cam.reparentTo(self.red_world.render)
        # # self.cam.setPos(0,0,0)
        # # self.cam.setHpr(-90,0,0)
        # self.red_world.cam_right.node().showFrustum()
        # self.red_world.cam_left.node().showFrustum()
        # #self.mouseLook = FirstPersonCamera(self, self.cam, self.red_world.render)

        self.shared.test = self.red_world.graphics_buffer_right

    def change_view(self):

        if self.view == 1: #
            self.last_virtual_world_pos = self.cam.getPos()
            self.last_virtual_world_hpr = self.cam.getHpr()
            self.cam.reparentTo(self.render)
            self.cam.setPos(-25,0,0)
            self.cam.lookAt(self.center)
            self.view = 0
        elif self.view == 0:
            self.cam.reparentTo(self.red_world.render)
            self.cam.setPos(self.last_virtual_world_pos)
            self.cam.setHpr(self.last_virtual_world_hpr)
            self.red_world.cam_right.node().showFrustum()
            self.red_world.cam_left.node().showFrustum()
            self.view = 1


    def update_colors(self):
        self.red_world.render.setColorScale(1,1,1,1)
        self.green_world.render.setColorScale(0,0,0,0)
        self.blue_world.render.setColorScale(0,0,0,0)



class FlyPointOfView:
    """"""

    #----------------------------------------------------------------------
    def __init__(self, siz):

        self.render = pcore.NodePath("fly render")

        #self.cosy = CoordinateSystem(self.render, length = 30, key = 'c')

        self.camera_rig = pcore.NodePath("camera_rig")
        self.camera_rig.reparentTo(self.render)
        self.camera_rig.setPos(0,0,0)
        self.camera_rig.setHpr(-90,0,0)

        # right field of view
        self.graphics_buffer_right = base.win.makeTextureBuffer("buffer_right", siz[0], siz[1])
        self.graphics_buffer_right.setClearColor(pcore.Vec4(0,0,0,1))


        self.cam_right = base.makeCamera(self.graphics_buffer_right)
        self.cam_right.reparentTo(self.camera_rig)
        self.cam_right.setPos(0,0,0)
        self.cam_right.setHpr(-45,0,0) #225

        self.lens_right = pcore.PerspectiveLens()
        self.lens_right.setFov(90, 130)
        self.lens_right.setNearFar(1,100)

        self.cam_right.node().setLens(self.lens_right)
        #self.cam_right.node().showFrustum()

        # left field of view
        self.graphics_buffer_left = base.win.makeTextureBuffer("buffer_left", siz[0], siz[1])
        self.graphics_buffer_left.setClearColor(pcore.Vec4(0,0,0,1))


        self.cam_left = base.makeCamera(self.graphics_buffer_left)
        self.cam_left.reparentTo(self.camera_rig)
        self.cam_left.setPos(0,0,0)
        self.cam_left.setHpr(45,0,0) # -45

        self.lens_left = pcore.PerspectiveLens()
        self.lens_left.setFov(90, 130)
        self.lens_left.setNearFar(1,100)

        self.cam_left.node().setLens(self.lens_left)
        #self.cam_left.node().showFrustum()


    def projectOntoArena(self, ts_right, ts_left, projector_right, projector_left, screen_right, screen_left, addflag):

        # right screen
        #self.ts_right = pcore.TextureStage('ts_right')
        self.tex_proj_right = self.graphics_buffer_right.getTexture()
        print(self.tex_proj_right)
        self.tex_proj_right.setWrapU(pcore.Texture.WMBorderColor)
        self.tex_proj_right.setWrapV(pcore.Texture.WMBorderColor)

        # left screen
        #self.ts_left = pcore.TextureStage('ts_left')
        self.tex_proj_left = self.graphics_buffer_left.getTexture()
        self.tex_proj_left.setWrapU(pcore.Texture.WMBorderColor)
        self.tex_proj_left.setWrapV(pcore.Texture.WMBorderColor)

        if addflag:
            ts_right.setMode(pcore.TextureStage.MAdd)
            ts_left.setMode(pcore.TextureStage.MAdd)


        screen_right.projectTexture(ts_right, self.tex_proj_right, projector_right)
        screen_left.projectTexture(ts_left, self.tex_proj_left, projector_left)




class MovieArena(CylindricArena):

    def __init__(self, calibration, shared):

        import pandac.PandaModules as PandaModules

        pcore.loadPrcFileData("","""
            load-display pandagl
            #sync-video 1
            win-size 1024 815
            win-origin 0 0
            #fullscreen t
            undecorated 1
            audio-library-name null
            """)

        CylindricArena.__init__(self, calibration)
        self.shared = shared

        # self.camNode.getDisplayRegion(0).setDimensions(0, 0.5, 0, 1)
        # #self.displayRegion0 = self.win.makeDisplayRegion(0,0.5,0,1)
        # self.displayRegion1 = self.win.makeDisplayRegion(0.5,1,0,1)
        #
        # self.displayRegion0.setCamera(self.cam_beamer_right_NP)
        # self.displayRegion1.setCamera(self.cam_beamer_left_NP)

        base.setBackgroundColor(0,0,0,0)

        # set up RGB color world copies
        self.red_world = FlyPointOfView((2**10,2**10))
        self.green_world = FlyPointOfView((2**10,2**10))
        self.blue_world = FlyPointOfView((2**10,2**10))
        self.RGB_POVs = [self.red_world, self.green_world, self.blue_world]

        for i in np.arange(len(self.RGB_POVs)):
            self.RGB_POVs[i].projectOntoArena(self.ts_left[i], self.ts_right[i], self.proj_right, self.proj_left, self.screen_right, self.screen_left, i != 0)
        self.update_colors()
        self.go_arena = True
        self.shared.ready[0] = 1 # set readiness value for ExperimentFramework

        winprops = pcore.WindowProperties()
        winprops.setForeground(True)
        base.win.requestProperties(winprops)


    def update_colors(self):
        self.red_world.render.setColorScale(1,1,1,1)
        self.green_world.render.setColorScale(0,0,0,0)
        self.blue_world.render.setColorScale(0,0,0,0)


    def show_stimulus(self, start_pause, name, *arg):

        RGB_OFFSET = [1., 2., 0.]
        self.rgb_stimulus = []
        for i in range(3):
            self.rgb_stimulus.append(StimulusFramework(self.RGB_POVs[i].render, self.RGB_POVs[i].camera_rig, self.taskMgr, RGB_OFFSET[i]))
        self.update_colors()

        for i in range(3):
            self.rgb_stimulus[i].build_stimulus(start_pause, name, arg)
            self.rgb_stimulus[i].parent_taskMgr.add(self.rgb_stimulus[i].general_stimulus_task, 'general_stimulus_task' + str(i))





##############################################################################
# CALIBRATION ################################################################
##############################################################################

class CalibrationArena(CylindricArena):

    def __init__(self, calibration, shared):

        pcore.loadPrcFileData("","""
            load-display pandagl
            #sync-video 1
            win-size 608 684
            win-origin 10 10
            #fullscreen t
            undecorated 0
            audio-library-name null
            """)

        CylindricArena.__init__(self, calibration)

        self.shared = shared

        from direct.gui.DirectGui import DirectEntry, DirectButton
        from direct.gui.OnscreenText import OnscreenText
        import importlib
        import pickle

        # set up second window
        wp2 = pcore.WindowProperties()
        wp2.setSize(608, 684)
        wp2.setOrigin(2560 + 0, 0)
        #wp2.setOrigin(608, 0)
        wp2.setUndecorated(True)

        self.win2 = self.graphicsEngine.makeOutput(self.pipe, 'win2', 0,
                     pcore.FrameBufferProperties.getDefault(),
                     wp2,
                     0,
                     gsg = self.win.getGsg())


        self.displayRegion2 = self.win2.makeDisplayRegion()

        self.displayRegion2.setCamera(self.cam_beamer_left_NP)
        #self.displayRegion2.setCamera(self.cam_beamer_right_NP)

        # set up first window
        wp1 = pcore.WindowProperties()
        wp1.setSize(608, 684)
        wp1.setOrigin(2560 + 608, 0)
        #wp.setOrigin(608, 0)
        wp1.setUndecorated(True)

        self.win1 = self.graphicsEngine.makeOutput(self.pipe, 'win1', 0,
                     pcore.FrameBufferProperties.getDefault(),
                     wp1,
                     0,
                     gsg = self.win.getGsg())

        self.displayRegion1 = self.win1.makeDisplayRegion()
        self.displayRegion1.setCamera(self.cam_beamer_right_NP)
        #self.displayRegion1.setCamera(self.cam_beamer_left_NP)

        # create calibration pattern

        self.flyworld = FlyPointOfView((2**10,2**10))
        for i in range(3):
            self.flyworld.projectOntoArena(self.ts_left[i], self.ts_right[i], self.proj_right, self.proj_left, self.screen_right, self.screen_left, i !=0)

        #self.stimulus_world = arenaStimulus.Stimulus(self.flyworld, self, 0)
        #self.stimulus_world.generate_stimulus('calibration', 1, 0.1)
        self.shared.arena_mode = "default"
        self.stimulus_world = StimulusFramework(self.flyworld.render, self.flyworld.camera_rig, self.taskMgr, self.trigger_render, 0, self.shared)
        self.stimulus_world.build_stimulus(2, "stimuli.calibration.calibration", (1e10, 10))


        # self.stimulus_world.stimulus.N_horizontal = 28
        # self.stimulus_world.stimulus.cylinder_height = 0
        # self.stimulus_world.stimulus.cylinder_radius = 0
        # self.stimulus_world.stimulus.h_tex_offset_count = 0
        # self.stimulus_world.stimulus.v_tex_offset_count = 0
        # self.stimulus_world.stimulus.fov_right_diff = 0
        # self.stimulus_world.stimulus.fov_left_diff = 0

        # if self.t_offset == 0.0:
        #     self.stimulus.first = True

        # calibration GUI

        self.stimulus_world.stimulus.fov_left_diff  = list(calibration[12])
        self.stimulus_world.stimulus.fov_right_diff = list(calibration[13])

        def update_position(textEntered, nodepath, side):
            try:
                 if side == 'right':
                     posX = float(x_right_entry.get())
                     posY = float(y_right_entry.get())
                     posZ = float(z_right_entry.get())
    
                 if side == 'left':
                     posX = float(x_left_entry.get())
                     posY = float(y_left_entry.get())
                     posZ = float(z_left_entry.get())
    
                 nodepath.setPos(posX, posY, posZ)
            except:
                print("ERROR: Check for unvalid input")

        def update_orientation(textEntered, nodepath, side):
            try:
                 if side == 'right':
                     H = float(h_right_entry.get())
                     P = float(p_right_entry.get())
                     R = float(r_right_entry.get())
    
                 if side == 'left':
                     H = float(h_left_entry.get())
                     P = float(p_left_entry.get())
                     R = float(r_left_entry.get())
    
                 nodepath.setHpr(H, P, R)
            except:
                print("ERROR: Check for unvalid input")

        def resize_pattern(textEntered):
            try:
                self.stimulus_world.stimulus.N_horizontal = float(textEntered)
                self.stimulus_world.stimulus.N_horizontal = float(textEntered)
                self.stimulus_world.stimulus.N_horizontal = float(textEntered)
    
                N_vertical   = self.stimulus_world.stimulus.cylinder_height/(2*math.pi*self.stimulus_world.stimulus.cylinder_radius/self.stimulus_world.stimulus.N_horizontal)
    
                self.stimulus_world.stimulus.cylinder.setTexScale(pcore.TextureStage.getDefault(), self.stimulus_world.stimulus.N_horizontal, N_vertical)
                self.stimulus_world.stimulus.cylinder.setTexScale(pcore.TextureStage.getDefault(), self.stimulus_world.stimulus.N_horizontal, N_vertical)
                self.stimulus_world.stimulus.cylinder.setTexScale(pcore.TextureStage.getDefault(), self.stimulus_world.stimulus.N_horizontal, N_vertical)
            except:
                print("ERROR: Check for unvalid input")

        def resize_cylinder(textEntered):
            try:
                cylinder_radius = float(textEntered)
                cylinder_height = 22.46
                self.screen_right.setScale(cylinder_radius,cylinder_radius,cylinder_height)
                self.screen_left.setScale(cylinder_radius,cylinder_radius,cylinder_height)
            except:
                print("ERROR: Check for unvalid input")

        def shift_pattern(direction):
            h_offset = self.stimulus_world.stimulus.h_tex_offset_count
            v_offset = self.stimulus_world.stimulus.v_tex_offset_count
            step = 0.01
            if direction == 'up':
                v_offset -= 1
            elif direction == 'down':
                v_offset += 1
            elif direction == 'left':
                h_offset += 1
            elif direction == 'right':
                h_offset -= 1

            self.stimulus_world.stimulus.cylinder.setTexOffset(pcore.TextureStage.getDefault(), h_offset*step, v_offset*step)

            self.stimulus_world.stimulus.h_tex_offset_count = h_offset
            self.stimulus_world.stimulus.v_tex_offset_count = v_offset

        def adjust_right_vertical_aperture(extraArgs):
            try:
                fov_right_diff = self.stimulus_world.stimulus.fov_right_diff
                fov_right = [self.omega_h + fov_right_diff[0], self.omega_v + fov_right_diff[1]]
                ratio = self.omega_v/self.omega_h
                if extraArgs == 'up':
                    self.lens_beamer_right.setFov(fov_right[0], fov_right[1] + 0.03*ratio)
                    self.stimulus_world.stimulus.fov_right_diff = [fov_right_diff[0], fov_right_diff[1] + 0.03*ratio]
                elif extraArgs == 'down':
                    self.lens_beamer_right.setFov(fov_right[0], fov_right[1] - 0.03*ratio)
                    self.stimulus_world.stimulus.fov_right_diff = [fov_right_diff[0], fov_right_diff[1] - 0.03*ratio]
    
                right_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[0]))
                right_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[1]))
            except:
                print("ERROR: Check for unvalid input")


        def adjust_right_horizontal_aperture(extraArgs):
            try:
                fov_right_diff = self.stimulus_world.stimulus.fov_right_diff
                fov_right = [self.omega_h + fov_right_diff[0], self.omega_v + fov_right_diff[1]]
                ratio = self.omega_v/self.omega_h
                if extraArgs == 'up':
                    self.lens_beamer_right.setFov(fov_right[0] + 0.03, fov_right[1])
                    self.stimulus_world.stimulus.fov_right_diff = [fov_right_diff[0] + 0.03, fov_right_diff[1]]
                elif extraArgs == 'down':
                    self.lens_beamer_right.setFov(fov_right[0] - 0.03, fov_right[1])
                    self.stimulus_world.stimulus.fov_right_diff = [fov_right_diff[0] - 0.03, fov_right_diff[1]]
    
                right_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[0]))
                right_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[1]))
            except:
                print("ERROR: Check for unvalid input")

        def enter_right_fov_h(textEntered):
            try:
                fov_right_diff = self.stimulus_world.stimulus.fov_right_diff
                fov_right_diff[0] = float(textEntered)
                fov_right = [self.omega_h + fov_right_diff[0], self.omega_v + fov_right_diff[1]]
                self.lens_beamer_right.setFov(fov_right[0], fov_right[1])
                self.fov_right_diff = [fov_right_diff[0], fov_right_diff[1]]
    
                right_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[0]))
                right_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[1]))
            except:
                print("ERROR: Check for unvalid input")
                
                
        def enter_right_fov_v(textEntered):
            try: 
                fov_right_diff = self.stimulus_world.stimulus.fov_right_diff
                fov_right_diff[1] = float(textEntered)
                fov_right = [self.omega_h + fov_right_diff[0], self.omega_v + fov_right_diff[1]]
                self.lens_beamer_right.setFov(fov_right[0], fov_right[1])
                self.fov_right_diff = [fov_right_diff[0], fov_right_diff[1]]
    
                right_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[0]))
                right_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_right_diff[1]))
            except:
                print("ERROR: Check for unvalid input")

        def adjust_left_horizontal_aperture(extraArgs):
            try:
                fov_left_diff = self.stimulus_world.stimulus.fov_left_diff
                fov_left = [self.omega_h + fov_left_diff[0], self.omega_v + fov_left_diff[1]]
                ratio = self.omega_v/self.omega_h
                if extraArgs == 'up':
                    self.lens_beamer_left.setFov(fov_left[0] + 0.03, fov_left[1])
                    self.stimulus_world.stimulus.fov_left_diff = [fov_left_diff[0] + 0.03, fov_left_diff[1]]
                elif extraArgs == 'down':
                    self.lens_beamer_left.setFov(fov_left[0] - 0.03, fov_left[1])
                    self.stimulus_world.stimulus.fov_left_diff = [fov_left_diff[0] - 0.03, fov_left_diff[1]]
    
                left_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[0]))
                left_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[1]))
            except:
                print("ERROR: Check for unvalid input")
                
                
        def enter_left_fov_h(textEntered):
            try:
                fov_left_diff = self.stimulus_world.stimulus.fov_left_diff
                fov_left_diff[0] = float(textEntered)
                fov_left = [self.omega_h + fov_left_diff[0], self.omega_v + fov_left_diff[1]]
                self.lens_beamer_left.setFov(fov_left[0], fov_left[1])
                self.fov_right_diff = [fov_left_diff[0], fov_left_diff[1]]
    
                left_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[0]))
                left_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[1]))
            except:
                print("ERROR: Check for unvalid input")

        def adjust_left_vertical_aperture(extraArgs):
            try:
                fov_left_diff = self.stimulus_world.stimulus.fov_left_diff
                fov_left = [self.omega_h + fov_left_diff[0], self.omega_v + fov_left_diff[1]]
                ratio = self.omega_v/self.omega_h
                if extraArgs == 'up':
                    self.lens_beamer_left.setFov(fov_left[0], fov_left[1] + 0.03*ratio)
                    self.stimulus_world.stimulus.fov_left_diff = [fov_left_diff[0], fov_left_diff[1] + 0.03*ratio]
                elif extraArgs == 'down':
                    self.lens_beamer_left.setFov(fov_left[0], fov_left[1] - 0.03*ratio)
                    self.stimulus_world.stimulus.fov_left_diff = [fov_left_diff[0], fov_left_diff[1] - 0.03*ratio]
    
                left_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[0]))
                left_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[1]))
            except:
                print("ERROR: Check for unvalid input")

        def enter_left_fov_v(textEntered):
            try:
                fov_left_diff = self.stimulus_world.stimulus.fov_left_diff
                fov_left_diff[1] = float(textEntered)
                fov_left = [self.omega_h + fov_left_diff[0], self.omega_v + fov_left_diff[1]]
                self.lens_beamer_left.setFov(fov_left[0], fov_left[1])
                self.fov_right_diff = [fov_left_diff[0], fov_left_diff[1]]
    
                left_fov_h_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[0]))
                left_fov_v_entry.enterText(str(self.stimulus_world.stimulus.fov_left_diff[1]))
            except:
                print("ERROR: Check for unvalid input")

        def save_calibration():

            import os
            dirname = os.getcwd()
            filename = 'tmp_calib.json'
            path = dirname + '\\' + filename

            leftPos = self.cam_beamer_left_NP.getPos()
#            calibration[0] = leftPos[0]
#            calibration[1] = leftPos[1]
#            calibration[2] = leftPos[2]
            leftHpr = self.cam_beamer_left_NP.getHpr()
#            calibration[3] = leftHpr[0]
#            calibration[4] = leftHpr[1]
#            calibration[5] = leftHpr[2]
            rightPos = self.cam_beamer_right_NP.getPos()
#            calibration[6] = rightPos[0]
#            calibration[7] = rightPos[1]
#            calibration[8] = rightPos[2]
            rightHpr = self.cam_beamer_right_NP.getHpr()
#            calibration[9] = rightHpr[0]
#            calibration[10] = rightHpr[1]
#            calibration[11] = rightHpr[2]
            leftFov = (self.stimulus_world.stimulus.fov_left_diff[0], self.stimulus_world.stimulus.fov_left_diff[1])
#            calibration[12] = leftFov
            rightFov = (self.stimulus_world.stimulus.fov_right_diff[0], self.stimulus_world.stimulus.fov_right_diff[1])
#            calibration[13] = rightFov
#
#            f = open(path, 'wb')
#            pickle.dump(calibration, f)
#            f.close()
#            
            out_dict = {
                 "beamer_right_X": rightPos[0], 
                 "beamer_right_Y": rightPos[1], 
                 "beamer_right_Z": rightPos[2], 
                 
                 "beamer_right_H": rightHpr[0], 
                 "beamer_right_P": rightHpr[1], 
                 "beamer_right_R": rightHpr[2], 

                 "beamer_left_X": leftPos[0], 
                 "beamer_left_Y": leftPos[1], 
                 "beamer_left_Z": leftPos[2], 
                                  
                 "beamer_left_H": leftHpr[0], 
                 "beamer_left_P": leftHpr[1], 
                 "beamer_left_R": leftHpr[2], 

                 "beamer_right_FOV": rightFov, 
                 "beamer_left_FOV": leftFov,
                         }
            
            with open(path, 'w') as fp:
                json.dump(out_dict, fp)


        ################################################
        # Create Calibration GUI
        ################################################

        # adjust right beamer position
        right_text = OnscreenText(text = 'right beamer', pos = (-0.75, 1.04))
        z_right_text = OnscreenText(text = 'Z', pos = (-0.95, 0.95))
        x_right_text = OnscreenText(text = 'X', pos = (-0.95, 0.85))
        y_right_text = OnscreenText(text = 'Y', pos = (-0.95, 0.75))
        z_right_entry = DirectEntry(initialText = str(self.cam_beamer_right_NP.getZ()), scale = 0.05, width = 6, pos = (-0.90,0,0.95), command = update_position, extraArgs = [self.cam_beamer_right_NP, 'right'])
        x_right_entry = DirectEntry(initialText = str(self.cam_beamer_right_NP.getX()), scale = 0.05, width = 6, pos = (-0.90,0,0.85), command = update_position, extraArgs = [self.cam_beamer_right_NP, 'right'])
        y_right_entry = DirectEntry(initialText = str(self.cam_beamer_right_NP.getY()), scale = 0.05, width = 6, pos = (-0.90,0,0.75), command = update_position, extraArgs = [self.cam_beamer_right_NP, 'right'])

        # adjust right beamer orientation
        h_right_text = OnscreenText(text = 'H', pos = (-0.45, 0.95))
        p_right_text = OnscreenText(text = 'P', pos = (-0.45, 0.85))
        r_right_text = OnscreenText(text = 'R', pos = (-0.45, 0.75))
        h_right_entry = DirectEntry(initialText = str(self.cam_beamer_right_NP.getH()), scale = 0.05, width = 6, pos = (-0.40,0,0.95), command = update_orientation, extraArgs = [self.cam_beamer_right_NP, 'right'])
        p_right_entry = DirectEntry(initialText = str(self.cam_beamer_right_NP.getP()), scale = 0.05, width = 6, pos = (-0.40,0,0.85), command = update_orientation, extraArgs = [self.cam_beamer_right_NP, 'right'])
        r_right_entry = DirectEntry(initialText = str(self.cam_beamer_right_NP.getR()), scale = 0.05, width = 6, pos = (-0.40,0,0.75), command = update_orientation, extraArgs = [self.cam_beamer_right_NP, 'right'])

        # adjust left beamer position
        left_text = OnscreenText(text = 'left beamer', pos = (0.23, 1.04))
        z_left_text = OnscreenText(text = 'Z', pos = (0.05, 0.95))
        x_left_text = OnscreenText(text = 'X', pos = (0.05, 0.85))
        y_left_text = OnscreenText(text = 'Y', pos = (0.05, 0.75))
        z_left_entry = DirectEntry(initialText = str(self.cam_beamer_left_NP.getZ()), scale = 0.05, width = 6, pos = (0.10,0,0.95), command = update_position, extraArgs = [self.cam_beamer_left_NP, 'left'])
        x_left_entry = DirectEntry(initialText = str(self.cam_beamer_left_NP.getX()), scale = 0.05, width = 6, pos = (0.10,0,0.85), command = update_position, extraArgs = [self.cam_beamer_left_NP, 'left'])
        y_left_entry = DirectEntry(initialText = str(self.cam_beamer_left_NP.getY()), scale = 0.05, width = 6, pos = (0.10,0,0.75), command = update_position, extraArgs = [self.cam_beamer_left_NP, 'left'])

        # adjust left beamer orientation
        h_left_text = OnscreenText(text = 'H', pos = (0.55, 0.95))
        p_left_text = OnscreenText(text = 'P', pos = (0.55, 0.85))
        r_left_text = OnscreenText(text = 'R', pos = (0.55, 0.75))
        h_left_entry = DirectEntry(initialText = str(self.cam_beamer_left_NP.getH()), scale = 0.05, width = 6, pos = (0.60,0,0.95), command = update_orientation, extraArgs = [self.cam_beamer_left_NP, 'left'])
        p_left_entry = DirectEntry(initialText = str(self.cam_beamer_left_NP.getP()), scale = 0.05, width = 6, pos = (0.60,0,0.85), command = update_orientation, extraArgs = [self.cam_beamer_left_NP, 'left'])
        r_left_entry = DirectEntry(initialText = str(self.cam_beamer_left_NP.getR()), scale = 0.05, width = 6, pos = (0.60,0,0.75), command = update_orientation, extraArgs = [self.cam_beamer_left_NP, 'left'])


        # adjust chess pattern size and position
        chesspattern_text = OnscreenText(text = 'pattern', pos = (-0.85, 0.6))
        patternsize_text = OnscreenText(text = 'N', pos = (-0.95, 0.5))
        patternsize_entry = DirectEntry(initialText = str(self.stimulus_world.stimulus.N_horizontal), scale = 0.05, pos = (-0.90,0,0.5), width = 5, command = resize_pattern)
        up_button = DirectButton(text = (""), scale = 0.25, pos =  (-0.54,0,0.55),  command = shift_pattern, extraArgs = ['up'])
        down_button = DirectButton(text = (""), scale = 0.25, pos =  (-0.54,0,0.50),  command = shift_pattern, extraArgs = ['down'])
        left_button = DirectButton(text = (""), scale = 0.25, pos =  (-0.59,0,0.525),  command = shift_pattern, extraArgs = ['left'])
        right_button = DirectButton(text = (""), scale = 0.25, pos =  (-0.49,0,0.525),  command = shift_pattern, extraArgs = ['right'])


        # adjust cylinder size
        cylindersize_text = OnscreenText(text = 'cylinder radius', pos = (-0.73, 0.3))
        cylindersize_entry = DirectEntry(initialText = str(self.cylinder_radius), scale = 0.05, pos = (-0.96,0,0.20), width = 5, command = resize_cylinder)

        # adjust FOV
        right_fov_h_text = OnscreenText(text = 'horizontal FOV', pos = (-0.73, 0.08))
        right_fov_h_entry = DirectEntry(initialText = str(self.stimulus_world.stimulus.fov_right_diff[0]), scale = 0.05, pos = (-0.95,0,-0.02), width = 3, command = enter_right_fov_h)

        adjust_right_fov_up_h = DirectButton(text = (""), scale = 0.25, pos =  (-0.72,0,0.03),  command = adjust_right_horizontal_aperture, extraArgs = ['up'])
        adjust_right_fov_down_h = DirectButton(text = (""), scale = 0.25, pos =  (-0.72,0,-0.02),  command = adjust_right_horizontal_aperture, extraArgs = ['down'])

        right_fov_v_text = OnscreenText(text = 'vertical FOV', pos = (-0.77, -0.12))
        right_fov_v_entry = DirectEntry(initialText = str(self.stimulus_world.stimulus.fov_right_diff[1]), scale = 0.05, pos = (-0.95,0,-0.22), width = 3, command = enter_right_fov_v)

        adjust_right_fov_up_v = DirectButton(text = (""), scale = 0.25, pos =  (-0.72,0,-0.17),  command = adjust_right_vertical_aperture, extraArgs = ['up'])
        adjust_right_fov_down_v = DirectButton(text = (""), scale = 0.25, pos =  (-0.72,0,-0.22),  command = adjust_right_vertical_aperture, extraArgs = ['down'])

        # adjust FOV
        left_fov_h_text = OnscreenText(text = 'horizontal FOV', pos = (0.73, 0.08))
        left_fov_h_entry = DirectEntry(initialText = str(self.stimulus_world.stimulus.fov_left_diff[0]), scale = 0.05, pos = (0.77,0,-0.02), width = 3, command = enter_left_fov_h)

        adjust_left_fov_up_h = DirectButton(text = (""), scale = 0.25, pos =  (0.71,0,0.03),  command = adjust_left_horizontal_aperture, extraArgs = ['up'])
        adjust_left_fov_down_h = DirectButton(text = (""), scale = 0.25, pos =  (0.71,0,-0.02),  command = adjust_left_horizontal_aperture, extraArgs = ['down'])

        left_fov_v_text = OnscreenText(text = 'vertical FOV', pos = (0.77, -0.12))
        left_fov_v_entry = DirectEntry(initialText = str(self.stimulus_world.stimulus.fov_left_diff[1]), scale = 0.05, pos = (0.77,0,-0.22), width = 3, command = enter_left_fov_v)

        adjust_left_fov_up_v = DirectButton(text = (""), scale = 0.25, pos =  (0.71,0,-0.17),  command = adjust_left_vertical_aperture, extraArgs = ['up'])
        adjust_left_fov_down_v = DirectButton(text = (""), scale = 0.25, pos =  (0.71,0,-0.22),  command = adjust_left_vertical_aperture, extraArgs = ['down'])


        # save/open calibration file
        save_button = DirectButton(text = ("save"), scale = 0.07, pos =  (-0.88,0,-0.50), command = save_calibration)
