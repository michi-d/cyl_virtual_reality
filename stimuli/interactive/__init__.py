
# All "interactive" stimuli have the mode "monitored" which means that the main (computer) monitor is not deactivated
# while the stimulus is presented.
# These stimuli are not to be used in "record" mode in the arenaGUI

__mode__ = "monitored"


__all__ = ["Flicker_window", "PDNDgrating_window", "RotateGrating"]


__params__ = {
              "Flicker_window": ['stimulus duration [sec]', 'pulse length [sec]', 'min_intensity', 'max_intensity', 'bg_intensity', 'phi [deg]', 'dphi [deg]', 'z', 'dz'],
              "PDNDgrating_window": ['rotation [deg]', 'wavelength [deg]', 'velocity [deg/sec]', 'mode [sq/sin]', 'min_intensity', 'max_intensity', 'bg_intensity', 'time of motion [sec]', 'pause time [sec]', 'phi [deg]', 'dphi [deg]', 'z', 'dz'],
              "RotateGrating": ["duration [sec]", "rotation [deg]", "wave length [deg]", "velocity [deg/sec]", "mode [sq/sin]", "min_intensity", "max_intensity"],

}

__standard_values__ = {
              "Flicker_window": [10.0,1.0,0,255, 51,90, 20., 0, 2],
              "PDNDgrating_window": [90.0, 10.0, 10.0,'sq', 0,255,51,3.0,0.5,90,20.,0,2],
              "RotateGrating": [10.0, 0.0, 30.0, 10.0, 'sq', 0, 255],
}