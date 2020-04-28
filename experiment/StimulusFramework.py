#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on 11/10/2014

@author: "Michael Drews"

"""

__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

from direct.task import Task
import importlib

from panda3d.core import Point3, Vec3
from os.path import join

import sys, warnings


class StimulusFramework():

    def __init__(self, parent_render, parent_camera, parent_taskMgr, trigger_render, t_offset = 0, shared = []):

        self.parent_render   = parent_render    # parent render node
        self.parent_camera   = parent_camera    # nodepath of camera
        self.parent_taskMgr  = parent_taskMgr   # parent task manager

        self.shared = shared

        self.trigger_render = trigger_render

        self.t_offset   = t_offset              # temporal offset in frames (0,1 or 2)
        self.time_zoom  = 3                     # 3 color channels (RGB)
        self.assumed_frame_rate = 60.0          # Hz
        self.max_color = 255.0
        self.min_color = 0.

        self.stimulus_active = 0
        self.pause_active = 0
        self.start_pause = 0.
        self.this_is_the_end = 0
        self.time_zero_date_trigger = 1
        self.pre_time = 0.0
        self.vsync_adjust = 0
        self.m = None # if vsync_adjust == True...also a mouse pointer must be defined externally! (reason: not import PyMouse-package for every instance of StimulusFramework)
        self.start_daq = False


    def build_stimulus(self, start_pause, name, *arg):

        self.name = name
        self.start_pause    = float(start_pause)
        self.arg  = arg

        stimulus_node = self.parent_render.findAllMatches("stimulus" + str(self.t_offset))
        if not stimulus_node:
            stimulus_node = self.parent_render.attachNewNode("stimulus" + str(self.t_offset))
        else:
            stimulus_node = stimulus_node[0]
        self.mainNode = stimulus_node
        self.mainNode.setPos(0,0,0)

        # make sure a variable "trigger_pixel" exists:
        try:
            self.trigger_pixel
        except AttributeError:
            self.trigger_pixel = None

        self.make_trigger()

        # call specific stimulus subclass
        arguments = (self,) + (self.shared, self.trigger_pixel) + self.arg[0]

        StimulusBuilder = importlib.import_module(self.name)
        s = self.name.split('.')[-1]
        self.stimulus = eval("StimulusBuilder." + s)(*arguments)
        self.make_trigger()

        self.stimulus.t_offset    = self.t_offset
        self.stimulus.start_pause = self.start_pause

        if self.t_offset == 0.0:
            self.stimulus.first = True

        self.mainNode.removeNode()
        self.old_geometry = []

        self.mainNode = self.parent_render.attachNewNode("stimulus" + str(self.t_offset))
        self.mainNode.setPos(0,0,0)

        self.parent_camera.setPos(0,0,0)
        self.parent_camera.setHpr(0, 0, 0)

        self.old_geometry = self.stimulus.build()#self.old_geometry)

        self.shared.t.value = 0


    def vsync_pre_task(self, task):

        # This task simulates alternating mouse clicks onto the two sides of the arena in order to alternately activate
        # the two rendering windows. This is - for unknown reasons - necessary in order to make vsync work properly and
        # hence to avoid judder. This task is executed first when a new instance of StimulusWorld is run and occupies some
        # seconds before the actual stimulus appears.

        t = (task.time * self.time_zoom + self.t_offset / self.assumed_frame_rate) / self.time_zoom

        #self.x_dim, self.y_dim = self.m.screen_size()

        out = Task.cont
        if t >= self.pre_time:
            
            if sys.platform == "win32":
                # get virtual screen size
                from win32api import GetSystemMetrics                        
                x_dim = GetSystemMetrics(78)
                y_dim = GetSystemMetrics(79)
                # move mouse away
                #self.m.move(x_dim, y_dim)
            else:
                warnings.warn("WARNING: Mouse control only working on WIN32-systems.")
            out = Task.done

        return out


    def general_stimulus_task(self, task):

        if self.stimulus.first:
            self.shared.t.value += globalClock.getDt()

        t_ = (task.time * self.time_zoom + self.t_offset / self.assumed_frame_rate) / self.time_zoom  # corrected time for the specific color channel
        t = t_- self.pre_time - self.start_pause  # time point zero adjustment
        # first "pre-task" for first stimulus or when a stimulus world is built newly

        if self.vsync_adjust:
            self.parent_taskMgr.add(self.vsync_pre_task, "vsync_adjustment_task")
            self.vsync_adjust = False

        out = Task.cont

        if -self.pre_time - self.start_pause < t < - self.start_pause:
            pass
        elif - self.start_pause < t:

            if self.shared.make_movie.value is 1:
                if self.shared.movie_started.value is 0:
                    base.movie(self.name, duration = self.stimulus.T + self.start_pause, fps = 60, format = 'bmp', sd = 6)
                    #base.movie(self.name, duration = 100000000, fps = 60, format = 'bmp', sd = 6)
                    self.shared.movie_started.value = 1

            t_more = 0.5
            self.stimulus_active = t < self.stimulus.T + t_more # 0.3 # +0.1 to allow end-trigger be visible

            if self.stimulus_active:
                self.stimulus.run(t)
                out = Task.cont
            else:
                out = Task.done
                self.this_is_the_end = 1

        return out


    def make_trigger(self):
        # generate rectangle in the lower left corner of the left side
        if not self.trigger_pixel:

            model_path = join(self.shared.arena_path, "plane");
            model_path = model_path.replace('\\', '/').replace('C:/', '/c/')
            obj = loader.loadModel(model_path)
            obj.reparentTo(self.mainNode)

            self.trigger_pixel = obj
            self.trigger_pixel.setColor(0,0,0,1)


        if self.shared.arena_mode == "default":
            self.trigger_pixel.reparentTo(self.parent_camera)
            self.trigger_pixel.setPos(Point3(-10.5, 0, -13.3))
            self.trigger_pixel.setScale(6, 1,4)

            self.trigger_pixel.setTwoSided(True)
            self.trigger_pixel.lookAt(self.parent_camera)

            self.trigger_pixel.setBin("fixed", 40)
            self.trigger_pixel.setDepthTest(False)
            self.trigger_pixel.setDepthWrite(False)

        if self.shared.arena_mode == "monitored":
            self.trigger_pixel.reparentTo(self.parent_camera)
            self.trigger_pixel.setPos(Point3(-10.5, 0, -13.3))
            self.trigger_pixel.setScale(6, 1,4)

            self.trigger_pixel.setTwoSided(True)
            self.trigger_pixel.lookAt(self.parent_camera)

            self.trigger_pixel.setBin("fixed", 40)
            self.trigger_pixel.setDepthTest(False)
            self.trigger_pixel.setDepthWrite(False)

        if self.shared.arena_mode == "opto":

            self.trigger_pixel.reparentTo(self.parent_render)
            self.trigger_pixel.setPos(Point3(1, 50, -12.5))
            self.trigger_pixel.setScale(2, 1,3)
            self.trigger_pixel.setHpr(Vec3(0, 0, 0 ) )
            self.trigger_pixel.setTwoSided(True)

            self.trigger_pixel.setBin("fixed", 40)
            self.trigger_pixel.setDepthTest(False)
            self.trigger_pixel.setDepthWrite(False)

        if self.shared.arena_mode == "movie":
            self.trigger_pixel.reparentTo(self.parent_camera)
            self.trigger_pixel.setPos(Point3(-100.5, 0, -130.3)) # far far away


        if self.shared.make_movie.value is 1:
            self.trigger_pixel.setPos(0,0,2000)

    def get_protocol(self):

        stimulus_protocol, trigger_protocol = self.stimulus.get_protocol()

        stimulus_protocol["start pause [sec]"] = self.start_pause
        stimulus_protocol["triggers"] = trigger_protocol

        return stimulus_protocol



