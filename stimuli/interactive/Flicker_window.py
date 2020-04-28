
from experiment.StimulusBuilder import StimulusBuilder
import core.tools as tools
import panda3d.core as pcore

# NOTE: This stimulus is based on default.Flicker_window. It shows a flickering window on the arena, the position of which
#       can be moved using the arrow keys on the keyboard.


class Flicker_window(StimulusBuilder):

    def __init__(self, parent, shared, trigger_pixel, T = 10.0, phase_length = 1.0, min_intensity = 0, max_intensity = 255, bg_intensity = 51, phi = 90, dphi = 20., z = 0, dz = 2):

        arg = (T, phase_length, min_intensity, max_intensity, bg_intensity, phi, dphi, z, dz)
        StimulusBuilder.__init__(self, parent, shared, trigger_pixel, arg)

        # define parameter names
        self.parameter_names = ['stimulus duration [sec]', 'pulse length [sec]', 'min_intensity', 'max_intensity', 'background color', 'phi [deg]', 'dphi [deg]', 'z [cm]', 'dz [cm]']


        # define parameters
        self.T = float(T)                      # duration [sec]
        self.phase_length = float(phase_length)
        self.max_intensity   = float(max_intensity)
        self.bg_intensity   = float(bg_intensity)
        self.min_intensity   = float(min_intensity)
        self.phi         = int(float(phi))
        self.dphi        = int(float(dphi))
        self.z           = float(z)
        self.dz          = float(dz)

        self.shared.arena_mode = 'monitored'

    def build(self):

        # configure beamer
        self.set_arena_mode('greenHDMI')


        self.cylinder_height, self.cylinder_radius, self.cylinder = tools.standard_cylinder(self.parent.mainNode)

        self.cylinder_height = self.cylinder_height + self.dz * 2
        self.cylinder.setScale(self.cylinder_radius,self.cylinder_radius,self.cylinder_height)

        self.ts_window = pcore.TextureStage('ts_window')
        self.plain_tex = tools.create_plain_texture(self.bg_intensity)
        self.cylinder.setTexture(self.ts_window, self.plain_tex)

        self.nr_before = 0

        self.z = self.z * 10/5.
        self.dz = self.dz * 10/5.
        if self.dz > 26:
            self.dz = 26
        if self.dphi > 360.:
            self.dphi = 360.


        self.tex_windowA = tools.create_window_texture_set_size(self.dphi, self.dz, self.max_intensity, self.bg_intensity, 360, int(self.cylinder_height/0.1))
        self.tex_windowB = tools.create_window_texture_set_size(self.dphi, self.dz, self.min_intensity, self.bg_intensity, 360, int(self.cylinder_height/0.1))

        self.cylinder.setTexOffset(self.ts_window, -(-self.dphi/2./360. + self.phi/360.), 0.5 - self.dz/2./self.cylinder_height - self.z/self.cylinder_height)

        # set up shared variables for synchronizing all color worlds
        self.shared.phi = self.phi
        self.shared.z   = self.z
        self.shared.factor = 1

        # set up keyboard commands for moving the window
        base.accept("arrow_right", self.increase_phi)
        base.accept("arrow_left", self.decrease_phi)
        base.accept("arrow_up", self.increase_z)
        base.accept("arrow_down", self.decrease_z)
        base.accept("arrow_right-repeat", self.increase_phi)
        base.accept("arrow_left-repeat", self.decrease_phi)
        base.accept("arrow_up-repeat", self.increase_z)
        base.accept("arrow_down-repeat", self.decrease_z)



    def increase_phi(self):
        self.shared.phi += 0.2 * self.shared.factor
        print("phi: " + str(self.shared.phi) +', z: ' + str(self.shared.z / 2.))

    def decrease_phi(self):
        self.shared.phi -= 0.2 * self.shared.factor
        print("phi: " + str(self.shared.phi) +', z: ' + str(self.shared.z / 2.))

    def increase_z(self):
        self.shared.z += 0.1 * self.shared.factor
        print("phi: " + str(self.shared.phi) +', z: ' + str(self.shared.z / 2.))

    def decrease_z(self):
        self.shared.z -= 0.1 * self.shared.factor
        print("phi: " + str(self.shared.phi) +', z: ' + str(self.shared.z / 2.))



    def update_pos(self):
        self.phi = self.shared.phi
        self.z   = self.shared.z

    def run(self, time):

        if time < 0:
            self.cylinder.setTexture(self.ts_window, self.tex_windowB)

        if 0 <= time < self.T:
              T = self.phase_length

              self.update_pos()
              self.cylinder.setTexOffset(self.ts_window, -(-self.dphi/2./360. + self.phi/360.), 0.5 - self.dz/2./self.cylinder_height - self.z/self.cylinder_height)

              nr = int(time/T % 2)

              if nr == 0:
                 self.cylinder.setTexture(self.ts_window, self.tex_windowA)
                 if not self.nr_before - nr == 0:
                    self.trigger_blink_now(time, "ON" + str(time))
                    #print "phi: " + str(self.phi) +', z: ' + str(self.z / 2.)
              if nr == 1:
                 self.cylinder.setTexture(self.ts_window, self.tex_windowB)
                 if not self.nr_before - nr == 0:
                    self.trigger_blink_now(time, "OFF" + str(time))
                    #print "phi: " + str(self.phi) +', z: ' + str(self.z / 2.)

              self.nr_before = nr

        if time >= self.T:
              self.cylinder.setTexture(self.ts_window, self.plain_tex)

        self.trigger_routine(time)
