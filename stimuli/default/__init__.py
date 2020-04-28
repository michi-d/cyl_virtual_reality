

__mode__ = "default"


__all__ = ["PlainScreen","Grating", "LoomingSphere", "PDNDgrating", "FieldFlicker", "tunnel", "FullFieldONPulse", "PDNDgrating_window", "Flicker_window", "Flicker_letter", "Flicker_circle", "HPassingBar", "VPassingBar", "CircleFrameFlash60", "FullFieldFrameFlash60", "BarFrameFlash60", "HPassingTexture", "CounterPhaseFlicker", "ApparentMotion", "ApparentMotionNsteps", "FigureGroundDisA", "Edges", "Edges_window","EdgesPDND_window", "tuning_rphi_v_1", "HGrating_phase", "GaussNoise_General", "BinaryNoise_DiscreteTime"]


__params__ = {
              "PlainScreen": ["time", "intensity"],
              "Grating": ["duration [sec]", "rotation [deg]", "wave length [deg]", "velocity [deg/sec]", "mode [sq/sin]", "min_intensity", "max_intensity"],
              "FieldFlicker": ["duration [sec]", "pulse length [sec]", "min_intensity", "max_intensity"],
              "LoomingSphere": ["velocity [cm/sec]", "radius [cm]", "start distance [cm]", "color"],
              "PDNDgrating": ["rotation [deg]", "wave length [deg]", "velocity [deg/sec]", "mode [sq/sin]", "min_intensity", "max_intensity", "time of motion [sec]", "pause duration [sec]"],
              "tunnel": ["duration [sec]", "velocity"],
              "FullFieldONPulse": ["pulse length [sec]", "intensity", "bg_intensity"],
              "PDNDgrating_window": ['rotation [deg]', 'wavelength [deg]', 'velocity [deg/s]', 'mode [sq/sin]', 'min_intensity', 'max_intensity', 'bg_intensity', 'time of motion [sec]', 'pause time [sec]', 'phi [deg]', 'dphi [deg]', 'z', 'dz'],
              "Flicker_window": ['stimulus duration [sec]', 'pulse length [sec]', 'min_intensity', 'max_intensity', 'bg_intensity', 'phi [deg]', 'dphi [deg]', 'z', 'dz'],
              "Flicker_letter": ['stimulus duration [sec]', 'pulse length [sec]', 'min_intensity', 'max_intensity', 'bg_intensity', 'phi [deg]', 'dphi [deg]', 'z', 'dz', 'letter'],
              "Flicker_circle": ['stimulus duration [sec]', 'pulse length [sec]', 'min_intensity', 'max_intensity', 'bg_intensity', 'phi [deg]', 'z', 'radius [deg]'],
              "HPassingBar": ['velocity [deg/sec]', 'dphi [deg]',  'z [cm]', 'dz [cm]', 'intensity', 'bg_intensity'],
              "VPassingBar": ['velocity [cm/sec]', 'phi [deg]', 'dphi [deg]', 'dz [cm]', 'intensity', 'bg_intensity'],
              #"Edge": ['velocity [deg/sec]', 'orientation [h/v]', 'edge intensity', 'background intensity'],
              #"white_noise": ['stimulus duration [sec]', 'frame length [sec]', 'precision [deg]'],
              #"sparse_noise": ['stimulus duration [sec]', 'frame length [sec]', 'precision [deg]'],
              #"white_noise_extreme": ['stimulus duration [sec]', 'frame length [sec]', 'precision [deg]'],
              "CircleFrameFlash60": ["stimulus duration [sec]", "multiple", "phi [deg]" , "z [cm]", "dphi [deg]", "bg_intensity", "min_intensity", "max_intensity", "color"],
              "FullFieldFrameFlash60": ["stimulus duration [sec]", "multiple", "min_intensity", "max_intensity", "color"],
              "BarFrameFlash60": ["stimulus duration [sec]", "multiple", "phi [deg]" , "z [cm]", "dphi [deg]", "dz [cm]", "bg_intensity", "min_intensity", "max_intensity", "color"],
              "HPassingTexture": ['velocity [deg/sec]', 'dphi [deg]',  'z [cm]', 'dz [cm]', 'texture_path', 'bg_intensity'],
              "CounterPhaseFlicker": ["duration [sec]", "rotation [deg]", "wave length [deg]", "velocity [deg/sec]", "min_intensity", "max_intensity"],
              "ApparentMotion": ["phi1", "phi2", "z1" , "z2", "dphi", "dz", "t1", "dt", "t2", "intensity ON", "intensity OFF", "intensity BG", "color"],
              "ApparentMotionNsteps": ["phi0", "z0", "direction", "dphi", "dz", "dt", "c_on", "c_off", "c_bg", "n_steps"],
              "FigureGroundDisA": ['velocity [deg/sec]', 'dphi [deg]', 'z [cm]', 'dz [cm]', 'N pixels azimuth', 'intensity ON', 'intensity OFF', 'color'],
              "Edges": ["rotation [deg]", "velocity [deg/sec]", "bg_intensity", "edge_intensity"],
              "Edges_window": ["rotation [deg][4dirsonly]", "velocity [deg/sec]", "bg_intensity", "window_intensity", "edge_intensity", 'phi [deg]', 'dphi [deg]', 'z', 'dz'],
              "EdgesPDND_window": ["rotation [deg][4dirsonly]", "velocity [deg/sec]", "bg_intensity", "window_intensity", "edge_intensity", 'phi [deg]', 'dphi [deg]', 'z', 'dz'],
              "tuning_rphi_v_1": ["stimulus duration [s]", "direction", "wave_length", "rotation", "bg_intensity", "contrast", "jump_v_effective", "jump_dist", "flicker_on"],
              "HGrating_phase": ["duration [sec]", "wave length [deg]", "velocity [deg/sec]", "mode [sq/sin]", "min_intensity", "max_intensity", "phi", "phase_offset"],
              "GaussNoise_General": ["duration", "N_phi", "N_z", "tau"],
              "BinaryNoise_DiscreteTime": ["duration", "N_phi", "N_z", "delta_sample", "contrast"],
             }


__standard_values__ = {
                       "PlainScreen": [10.0, 125],
                       "Grating": [10.0, 0.0, 30.0,10.0,'sq',0,255],
                       "FieldFlicker": [10.0, 1.0, 0, 255],
                       "LoomingSphere": [10.0,10.0,50.0,255.0],
                       "PDNDgrating": [90.0,10.0,10.0,'sq',0,255,3.0,0.5],
                       "tunnel": [10.0,5.0],
                       "FullFieldONPulse": [5.,255.,0],
                       "PDNDgrating_window": [90.0,10.0,10.0,'sq',0,255,51,3.0,0.5,90,20.,0,2],
                       "Flicker_window": [10.0,1.0,255,0,0,90,20.,0,2],
                       "Flicker_letter": [10.0,1.0,255,0,0,90,20.,0,2,'A'],
                       "Flicker_circle": [10.0,1.0,255,0,0,90,0,20.],
                       "HPassingBar": [30.0,10.0,0.0,2.0,255.0,0.0],
                       "VPassingBar": [3.0,0.0,10.0,2.0,255.0,0.0],
                       #"Edge": ['velocity [deg/sec]', 'orientation [h/v]', 'edge intensity', 'background intensity'],
                       "CircleFrameFlash60": [2.,1.,90.,0.,10.,51,0,100,'b'],
                       "FullFieldFrameFlash60": [2.,1.,0,100,'b'],
                       "BarFrameFlash60": [2.,1.,90.,0.,10.,2.,51,0,100,'b'],
                       "HPassingTexture": [30.0,10.0,0.0,2.0, "stimuli/default/test.png",0.0],
                       "CounterPhaseFlicker": [10.0,0.0,30.0,10.0,0,255],
                       "ApparentMotion": [90.,100.,1.,1.,5.,0.436,1.,0.5,1.,255,0.,50,'g'],
                       "ApparentMotionNsteps": [90., 0., 'h', 5., 0.436, 0.5, 255, 0., 50, 3],
                       "FigureGroundDisA": [30.,20.,0.,2.,36,100,0.,'g'],
                       "Edges": [0.0,10.0,0,255],
                       "Edges_window": [0.0,10.0,0,0,255,90,15,0.,1.5],
                       "EdgesPDND_window": [0.0,10.0,0,0,255,90,15,0.,1.5],
                       "tuning_rphi_v_1": [5.,1.,30.,0.,127.,1.0,32.,4.,1],
                       "HGrating_phase": [10.0, 30.0,10.0,'sq',0,255, 90, 0.0],
                       "GaussNoise_General": [30.0, 64, -1, 0.0],
                       "BinaryNoise_DiscreteTime": [30.0, 64, -1, 1, 250]

}