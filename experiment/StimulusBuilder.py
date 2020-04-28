__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

import datetime
from numpy import abs as abs

class StimulusBuilder:

    def __init__(self, parent, shared, trigger_pixel, arg):

        self.parent = parent
        self.params = arg
        self.shared = shared
        self.first  = False
        self.trigger_pixel = trigger_pixel

        # trigger stuff
        self.last_trigger  = -1000. # time of last trigger pulse
        self.build_trigger = True
        self.start_trigger = True
        self.stop_trigger  = True

        self.protocol_write_header = True
        self.protocol_entry = {}

        self.trigger_start_times = []
        self.trigger_messages    = []
        self.trigger_dates       = []

        # bugfix for creating a StimulusBuilder instance without actually using it within the ArenaFramework
        # e.g.: to get the standard values for the parameters etc....
        if self.shared == 0:
            class empty_class: pass
            self.shared = empty_class

    def add_trigger(self, t, message):
        self.parent.Trigger.add_trigger_event(t, 0.1, message)

    def trigger_set_white(self):
        self.shared.trigger_state.value = 1
        #return time.clock()
        return datetime.datetime.now()

    def trigger_set_black(self):
        self.shared.trigger_state.value = 0

    def trigger_routine(self, time):

        if self.first:
            if self.build_trigger:
                if time < 0:
                    self.trigger_force_blink(time, 'build stimulus')
                    self.build_trigger = False
            if self.start_trigger:
                if time >= 0:
                    t = self.trigger_force_blink(time, 'start stimulus')
                    self.start_trigger = False
                    #self.shared.t1.value = t
            if self.stop_trigger:
                if time >= self.T:
                    t = self.trigger_force_blink(time, 'stop stimulus')
                    self.stop_trigger = False
                    #self.shared.t2.value = t
                    #print "TIME ELAPSED: " + str(self.shared.t2.value-self.shared.t1.value)

            if time - self.last_trigger > 0.0:
                self.trigger_set_black()
                #self.trigger_pixel.setColor(0,0,0,1)

            if self.shared.trigger_state.value == 1:
                #print "trigger! " + str(time)
                self.trigger_pixel.setColor(1,1,1,1)
            else:
                self.trigger_pixel.setColor(0,0,0,1)



    def trigger_force_blink(self, time, message):
            t = self.trigger_set_white()
            #self.trigger_pixel.setColor(1,1,1,1)
            self.last_trigger = time

            #self.trigger_dates.append(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H.%M.%S.%f'))
            self.trigger_dates.append(datetime.datetime.strftime(t, '%Y-%m-%d_%H.%M.%S.%f'))
            self.trigger_messages.append(message)
            self.trigger_start_times.append(time)

            self.update_protocol()
            print("TRIGGER : "  + str(message))

            return t


    def trigger_blink_now(self, time, message):
            if time - self.last_trigger > 0.1:
                if abs(time - 0) > 0.1 and abs(time - self.T) > 0.1: # don't overwrite start and stop trigger
                    self.trigger_set_white()
                    #self.trigger_pixel.setColor(1,1,1,1)
                    self.last_trigger = time

                    self.trigger_dates.append(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H.%M.%S.%f'))
                    self.trigger_messages.append(message)
                    self.trigger_start_times.append(time)

                    self.update_protocol()
                    print("TRIGGER : "  + str(message))
                    #print self.trigger_dates
                    #print self.trigger_messages
                    #print self.trigger_start_times


    def worlds_share(self, variable):
        # create a new list in shared named "name" to store the copies of the variable "variable" of each world in it
        i = int(self.parent.t_offset)
        self.shared.rgb_worlds_shared_variable[i] = variable

    def worlds_share2(self, variable):
        # create a new list in shared named "name" to store the copies of the variable "variable" of each world in it
        i = int(self.parent.t_offset)
        self.shared.rgb_worlds_shared_variable2[i] = variable


    def get_trigger_protocol(self):

        ind_order = sorted(range(len(self.trigger_start_times)), key=lambda k: self.trigger_start_times[k])

        trigger_start_times = [self.trigger_start_times[i] for i in ind_order]
        trigger_messages    = [self.trigger_messages[i] for i in ind_order]
        trigger_dates       = [self.trigger_dates[i] for i in ind_order]

        trigger_protocol_element = {}
        for i in range(len(trigger_messages)):
            trigger_protocol_element[i] = [trigger_messages[i], trigger_start_times[i], trigger_dates[i]]

        return trigger_protocol_element

    def set_arena_mode(self, mode):

        if self.shared.enable_TCP_control_beamer.value and self.first:

            right_i = [i for i in range(len(self.shared.beamer_position)) if self.shared.beamer_position[i] == "right"]
            left_i = [i for i in range(len(self.shared.beamer_position)) if self.shared.beamer_position[i] == "left"]
            opto_i = [i for i in range(len(self.shared.beamer_position)) if self.shared.beamer_position[i] == "opto"]


            # normal arena mode
            if mode == 'greenHDMI':
                if right_i:
                    ArenaControl.set_green(self.shared.control_beamers[right_i[0]])
                if left_i:
                    ArenaControl.set_green(self.shared.control_beamers[left_i[0]])
            if mode == 'redHDMI':
                if right_i:
                    ArenaControl.set_red(self.shared.control_beamers[right_i[0]])
                if left_i:
                    ArenaControl.set_red(self.shared.control_beamers[left_i[0]])
            if mode == 'blueHDMI':
                if right_i:
                    ArenaControl.set_blue(self.shared.control_beamers[right_i[0]])
                if left_i:
                    ArenaControl.set_blue(self.shared.control_beamers[left_i[0]])

            ### optogenetics
            if mode == 'optogreenHDMI':
                if opto_i:
                    ArenaControl.set_green(self.shared.control_beamers[opto_i[0]])
                if left_i:
                    ArenaControl.set_green(self.shared.control_beamers[left_i[0]])
            if mode == 'optoredHDMI':
                if opto_i:
                    ArenaControl.set_red(self.shared.control_beamers[opto_i[0]])
                if left_i:
                    ArenaControl.set_green(self.shared.control_beamers[left_i[0]])
            if mode == 'optoblueHDMI':
                if opto_i:
                    ArenaControl.set_blue(self.shared.control_beamers[opto_i[0]])
                if left_i:
                    ArenaControl.set_green(self.shared.control_beamers[left_i[0]])
            if mode == 'optoRGBHDMI':
                if opto_i:
                    ArenaControl.set_rgb(self.shared.control_beamers[opto_i[0]])
                if left_i:
                    ArenaControl.set_green(self.shared.control_beamers[left_i[0]])

    def get_protocol(self):
        # older function for stimulus protocol used in older versions (not OnlineFramework)

        #name = self.name

        name = self.__module__
        props = self.params
        props_name = self.parameter_names

        count = self.shared.stimulus_counter.value

        stimulus_props = {'name': name, 'count': count}
        i = 0
        for n in props_name:
            stimulus_props[n] = props[i]
            i += 1

        trigger_protocol = self.get_trigger_protocol()
        return stimulus_props, trigger_protocol

    def update_protocol(self):
        # new function for stimulus protocol used from sep 2017 on in the OnlineFramework

        if self.first:
            # write header
            if self.protocol_write_header:
                # the "header" contains all the stimulus information and is written at the time of the "build stimulus" trigger
                # into the protocol

                self.protocol_write_header = False

                name = self.__module__
                props = self.params
                props_name = self.parameter_names

                count = self.shared.stimulus_counter.value

                self.protocol_entry['name'] = name
                self.protocol_entry['count'] = count
                i = 0
                for n in props_name:
                    self.protocol_entry[n] = props[i]
                    i += 1
                self.protocol_entry["start pause [sec]"] = self.start_pause

                self.shared.stimulus_protocol.append(self.protocol_entry) # write this stimulus into the protocol


            trigger_protocol = self.get_trigger_protocol()
            self.protocol_entry["triggers"] = trigger_protocol

            self.shared.stimulus_protocol[-1]["triggers"] =  trigger_protocol
