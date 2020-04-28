
__mode__ = "default"

__all__ = ["ApparentMotion"]

__params__ = {
              "ApparentMotion": ["stimulus_duration", "N_steps", "dt", "phi0", "z0", "direction", "width", "height", "step_length", "c_on", "c_off", "c_bg"],
             }

__standard_values__ = {
                       "ApparentMotion": [5, 5, 0.5, 90., 0., 45., 10., 40., 20., 255, 0., 125],
}