from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools

class FieldFlicker(StimulusBuilder):


    def __init__(self, parent, shared, trigger_pixel, T = 10.0, phase_length = 1.0, min_intensity = 0, max_intensity = 255):

        arg = (T, phase_length, min_intensity, max_intensity)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['stimulus duration [s]', 'pulse length [sec]', 'min_intensity', 'max_intensity']

        # define parameters
        self.T = float(T)                           # duration [sec]
        self.phase_length = float(phase_length)     # length of one phase (dark or bright, [sec])
        self.min_intensity   = float(min_intensity) /255.  # minimum intensity (during start pause)
        self.max_intensity   = float(max_intensity) /255.  # maximum intensity (first after stimulus onset)

        self.shared.arena_mode = 'default'


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')
        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)

        self.tex = tools.create_plain_texture(255)
        self.cylinder.setTexture(self.tex)
        self.cylinder.setColor(self.min_intensity,self.min_intensity,self.min_intensity,1)

        # initialize binary variable to memorize the current phase of the flicker
        self.nr_before = 0


    def run(self, time):

        if time < 0:
            self.cylinder.setColor(self.min_intensity, self.min_intensity, self.min_intensity, 1)

        if 0 <= time < self.T:

              T = self.phase_length
              nr = int(time/T % 2)

              if nr == 0:
                 # if time is within the first two second (or periodic) show max_intensity
                 self.cylinder.setColor(self.max_intensity, self.max_intensity, self.max_intensity, 1)
                 if not self.nr_before - nr == 0:
                    # if phase of flicker has changed, generate a trigger
                    #self.trigger_blink_now(time, "ON" + str(time))
                    pass

              if nr == 1:
                  # if time is within the second two seconds (or periodic) show min_intensity
                 self.cylinder.setColor(self.min_intensity, self.min_intensity, self.min_intensity, 1)
                 if not self.nr_before - nr == 0:
                     # if phase of flicker has changed, generate a trigger
                    #self.trigger_blink_now(time, "OFF" + str(time))
                    pass

              # memorize current phase of the flicker
              self.nr_before = nr

        if time >= self.T:
              self.cylinder.setColor(self.min_intensity, self.min_intensity, self.min_intensity, 1)

        self.trigger_routine(time)
