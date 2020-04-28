__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

import numpy as np
from direct.task.Task import Task
import sys, warnings
import json
import os
from experiment.StimulusFramework import StimulusFramework

SPRITE_POS = 55
RGB_OFFSET = [1., 2., 0.]

class ExperimentFramework:

    def __init__(self, arena, shared, click_window = True, vsync_adjust=True):

        self.arena = arena
        self.vsync_adjust = vsync_adjust
        self.RGB_POVs = arena.RGB_POVs
        self.shared = shared

        self.taskMgr = self.arena.taskMgr
        self.trigger_render = self.arena.trigger_render

        self.stimulus_protocol = []

        self.pause_after_stimulus = 1.
        self.watch_stimulus_status = True
        self.startup = True
        self.click_window = click_window
        self.everything_ready = False

        # set up StimulusFramework for each color channel
        self.stimulus_worlds = []
        for i in range(3):
            self.stimulus_worlds.append(StimulusFramework(self.arena.RGB_POVs[i].render, self.arena.RGB_POVs[i].camera_rig, self.taskMgr, self.trigger_render, RGB_OFFSET[i], self.shared))
            self.arena.update_colors()

        # set up EventManager
        self.EventManager = EventManager(self.taskMgr)

        # start with enter
        self.enter_pressed = False

        self.task_active = False

        # run
        self.taskMgr.add(self.run_new, 'run ExperimentFramework')
        self.shared.ready[1] = 1 # set readiness value for ExperimentFramework

        #self.taskMgr.add(self.test_cell, 'testcell')
        
        # NOTE: THIS WORKS ONLY FOR WINDOWS SYSTEMS
        # sets the priority of all running python processes to high
        os.system("wmic process where name='python.exe' CALL setpriority 'high priority'")
        
        

    def activate_enter(self):
        self.enter_pressed = True


    def check_readiness(self):

        ready  =  self.shared.ready
        check_readiness = self.shared.check_readiness

        check_values = np.array([ready[i] for i in np.nonzero(np.array(check_readiness))[0]])
        return check_values.all()


    def test_cell(self, task):

        tex = base.win.getScreenshot()
        Xsize = tex.getXSize()
        Ysize = tex.getYSize()

        data = tex.getRamImage().getData()

        n_bytes = tex.getComponentWidth()
        if n_bytes == 1:
            pic = np.fromstring(data, dtype=np.uint8)
        elif n_bytes == 2:
            pic = np.fromstring(data, dtype=np.uint16)

        pic = pic.reshape((Ysize, Xsize, 4))
        cell_response = pic[300,300,0]
        print("cell = " + str(cell_response))

        return Task.cont


    def run_new(self, task):

        if not self.everything_ready:
            #print("check")

            self.everything_ready = self.check_readiness()
            if self.everything_ready:

                if self.click_window:
                    
                    if sys.platform == "win32":
                        # get virtual screen size
                        from win32api import GetSystemMetrics                        
                        x_dim = GetSystemMetrics(78)
                        y_dim = GetSystemMetrics(79)
                        
                        # click window with the mouse
                        m = PyMouse()
                        #x_dim, y_dim = m.screen_size()
                        m.click(x_dim - 2*608+100, 100, 1)
                        self.click_window = False
                    else:
                        warnings.warn("WARNING: Mouse control only working on WIN32-systems.")

                self.arena.accept('enter', self.activate_enter)
                print("READY")

        if self.arena.go_arena and self.everything_ready:

            self.shared.experiment_running.value = 1

            if self.enter_pressed:

                go_on = True
                if self.startup:
                    if self.shared.MCC_DAQ_enabled.value:
                        self.shared.MCC_DAQ_running.value = 1
                    if self.shared.online_imaging_enabled.value:
                        self.shared.online_imaging_running.value = 1

                    self.startup = False

                if not self.task_active:
                    self.task_active = True
                    go_on = self.EventManager.execute_next()

                if self.watch_stimulus_status:
                    # watch for stimulus end
                    if self.stimulus_worlds[-1].this_is_the_end:
                        self.shared.camera_recording.value = 0
                        self.watch_stimulus_status = False
                        self.stimulus_protocol.append(self.stimulus_worlds[-1].get_protocol())

                        self.save_experiment_protocol()

                        self.taskMgr.add(self.wait_after_stimulus, 'wait', extraArgs = [self.pause_after_stimulus], appendTask = True)


                if not go_on:
                    self.shared.MCC_DAQ_running.value = 0
                    self.shared.online_imaging_running.value = 0
                    self.shared.experiment_running.value = 0
                    self.save_experiment_protocol()


        return Task.cont


    def update_StimulusFramework(self, start_pause, name, *arg):
        arg = arg[0:-1] # discard task argument in the end

        for i in range(3):
            self.stimulus_worlds[i].__init__(self.arena.RGB_POVs[i].render, self.arena.RGB_POVs[i].camera_rig, self.taskMgr, self.trigger_render, RGB_OFFSET[i], self.shared)
            self.stimulus_worlds[i].build_stimulus(start_pause, name, arg)

        # vsync adjust for very first stimulus
        if self.vsync_adjust:
            self.stimulus_worlds[-1].vsync_adjust = True
            #self.stimulus_worlds[-1].m = PyMouse()
            for i in range(3):
                self.stimulus_worlds[i].pre_time = 0.1 # used to be 5! vsync is not used anymore!
            self.vsync_adjust = False

        return Task.done


    def start_StimulusFramework(self, task):

        self.shared.stimulus_counter.value += 1
        self.shared.camera_recording.value = 1
        for i in range(3):
            self.taskMgr.add(self.stimulus_worlds[i].general_stimulus_task, 'general_stimulus_task' + str(i))

        self.watch_stimulus_status = True

        return Task.done



    def add_stimulus_new(self, start_pause, name, *arg):

        start_pause = float(start_pause)

        # create stimulus
        self.EventManager.add_event(0.0, self.update_StimulusFramework, [start_pause, name] + list(arg), 'last')

        # start stimulus
        self.EventManager.add_event(1, self.start_StimulusFramework, [], 'same')


    def wait_after_stimulus(self, pause, task):

        if task.time > pause:
            self.task_active = False
            out =  Task.done
        else:
            out = Task.cont

        return out


    def save_experiment_protocol(self):

        if self.shared.save_protocol_enabled.value:

            shared_protocol = self.shared.get_save_protocol()

            filename = self.shared.d['filename']
            path = os.path.split(filename)[0]
            if not os.path.exists(path): os.makedirs(path)

            file = filename + '.sti'
            with open(file, 'wb') as outfile:
                json.dump({'shared': shared_protocol, 'stimulus protocol': self.stimulus_protocol}, outfile, indent = 4)

class EventManager:

    def __init__(self, taskMgr):

        self.taskMgr = taskMgr   # task manager object which is in operation

        self.event            = []      # events to be done
        self.event_extraArgs  = []      # parameters for the events
        self.event_startdelay = []      # start delay before the event is executed
        self.event_order      = np.array([])      # order number of the event

        self.current_order    = 0

    def add_event(self, startdelay, function, params, where):

        if len(self.event_order) > 0:
            if where == 'last':
                order = max(self.event_order) + 1
            elif where == 'first':
                order = min(self.event_order) - 1
            elif where == 'same':
                order = self.event_order[-1]
        else:
            order = 1

        self.event_order = np.append(self.event_order, order)

        self.event_startdelay.append(startdelay)
        self.event.append(function)
        self.event_extraArgs.append(params)

        self.current_order = min(self.event_order) - 1

    def execute_next(self):

        self.current_order += 1
        #print(self.current_order)

        indices = np.nonzero(self.event_order == self.current_order)[0]
        for i in indices:
            self.taskMgr.doMethodLater(self.event_startdelay[i], self.event[i], str(i), self.event_extraArgs[i], appendTask=True)


        go = self.current_order <= max(self.event_order)
        return go




