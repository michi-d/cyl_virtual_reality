from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools


class LoomingSphere(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, velocity = 10.0, radius = 10.0, distance_0 = 50.0, color = 255.0):

        arg = (velocity, radius, distance_0, color)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['velocity [cm/sec]', 'radius [cm]', 'initial distance [cm]', 'color']

        # define parameters
        self.velocity = float(velocity) * 10/5
        self.radius = float(radius) * 10/5
        self.distance_0 = float(distance_0) * 10/5
        self.color = float(color)

        self.shared.arena_mode = 'default'


    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')

        (_, self.sphere) = tools.create_sphere(self.parent.mainNode, 100)

        # define moving sphere
        self.sphere.setScale(self.radius, self.radius, self.radius)
        self.sphere.setTwoSided(True)
        self.sphere.setColor(self.color/255., self.color/255., self.color/255., 1)

        self.sphere.setPos(0, self.distance_0, 0)

        self.T = self.distance_0/self.velocity + 0.1


    def run(self, time):

        ##
        if time < 0:
            new_distance = self.distance_0
        ##
        if 0 <= time:
            new_distance = self.distance_0 - time * self.velocity

        if new_distance > 0:
            self.sphere.setPos(0, new_distance, 0)

        self.trigger_routine(time)
