
from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore


# NOTE: This stimulus shows a Full Field Flash with parameters for time and contrast
# IMPORTANT: This stimulus can be used for impulse responses because the length of presentation is
#            defined here as a multiple of the length of one frame given a beamer refresh rate of 60 Hz
#            multiple = 1    means   1/60 seconds
#            multiple = 2    means   2/60 seconds
#            and so on ...

class FullFieldFrameFlash60(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, T = 2., multiple = 1., min_intensity = 0, max_intensity = 100, color = 'b'):

        arg = (T, multiple, min_intensity, max_intensity, color)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ["stimulus duration [sec]", "multiple", "min_intensity", "max_intensity", "color"]

        # define parameters
        self.T = float(T)           # stimulus duration in seconds (length of the whole stimulus)
        self.color   = str(color)   # color of the arena
        self.multiple = float(int(float(multiple)))  # flash duration (length of the pulse in multiples of frames)
        self.min_intensity = float(min_intensity)    # minimum intensity (during start pause)
        self.max_intensity = float(max_intensity)    # maximum intensity (first after stimulus onset)

        self.shared.arena_mode = 'default'



    def build(self):

        # configure beamer
        if self.color == 'b':
            self.set_arena_mode('optoblueHDMI')
        elif self.color == 'r':
            self.set_arena_mode('optoredHDMI')
        elif self.color == 'g':
            self.set_arena_mode('optogreenHDMI')

        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)
        self.cylinder.setColor(self.min_intensity/255.,self.min_intensity/255.,self.min_intensity/255.,1) # set background color

        self.min_intensity = (self.min_intensity)/255.
        self.max_intensity = (self.max_intensity)/255.
        self.bg_intensity = self.min_intensity

        # create window
        self.ts_window = pcore.TextureStage('ts_window')
        #self.ts_window.setMode(pcore.TextureStage.MBlend)


        self.worlds_share(self.cylinder) # store cylinder in shared space to change its color synchronously in all color worlds
        self.pulse_done = False
        self.pulse_end = False


    def set_all_worlds_color(self, color):
        # sets the color of the texture in all color worlds at the same time
        for ts in self.shared.rgb_worlds_shared_variable:
            ts.setColor(pcore.Vec4(color, color, color, 1))


    def run(self, time):

        ##
        if time < 0:
            self.set_all_worlds_color(self.min_intensity)

        ##
        # check in first color world if time has passed over t = 0 (stimulus onset)
        if (0 <= time < self.multiple * 1/60.) and (self.first) and (self.pulse_done == False):
            self.set_all_worlds_color(self.max_intensity)
            self.pulse_done = True

        # check in first color world if time has passed over t = multiple * 1/60 (stimulus offset)
        if (time >= self.multiple * 1/60.) and (self.first) and (self.pulse_end == False):
            self.set_all_worlds_color(self.min_intensity)
            self.pulse_end = True


        self.trigger_routine(time)


