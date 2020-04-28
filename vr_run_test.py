from core import arena_controls

from stimuli.default.tunnel import tunnel
stimulus        = tunnel(0,0,0)    # generate temporary instance of stimulus class
standard_params =  stimulus.params # get standard parameters
arg             = [1.0, "stimuli.default.tunnel"] + list(standard_params)

stimulus_protocol = [arg] * 10 # repeat 10 times

# QUICK PREVIEW
arena_controls.quick_preview_protocol(stimulus_protocol) # render in preview window

# UNCOMMENT FOR USE IN VR
#win_origin = (0,0) # set to zero for test purpose / adjust to x position of extended screen
#arena_controls.show_stimulus_protocol([arg]*10, win_origin = win_origin) # show stimulus on VR screen