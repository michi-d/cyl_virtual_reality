__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

from multiprocessing import Value, Array, Manager
import datetime
import os

class Shared:

    def __init__(self):

        manager = Manager()
        self.d = manager.dict()

        self.d['experiment_type'] = 'ephys'

        self.d['path'] = './'#'../data/'
        self.d['filename'] = 'data'

        self.arena_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        # automatic filename:
        # 0: prefix + year-month-day_hour_minute
        self.filename_automatic = Value('i', 0)
        self.d['filename_prefix'] = 'data'

        # beamer TCP control
        self.enable_TCP_control_beamer = Value('i', 0)
        self.pinger_running            = Value('i', 0)

        # MCC DAQ parameters
        self.MCC_DAQ_running         = Value('i', 0)
        self.MCC_DAQ_enabled         = Value('i', 0)
        self.save_protocol_enabled   = Value('i', 0)

        self.MCC_DAQ_lowChan         = Value('i', 0)
        self.MCC_DAQ_highChan        = Value('i', 2)
        self.MCC_DAQ_acquisitionRate = Value('i', 10000)
        self.MCC_DAQ_packageSize     = Value('i', 10000)

        self.MCC_CurrentInjection_enabled = Value('i', 0)
        self.MCC_CurrentInjection_ampere  = Value('i', 50) # pA

        # Online Stuff
        self.online_imaging_running         = Value('i', 0)
        self.online_imaging_enabled         = Value('i', 0)

        self.online_connection              = manager.dict()
        self.online_connection['host']      = ''
        self.online_connection['port']      = '0'


        self.d['MCC_DAQ_start_time'] = ''
        self.init_date = datetime.datetime.now()

        # arena mode (optogenetics etc...)
        self.arena_mode = 'default'

        # check readiness of all program parts
        # [arena, ExperimentFramework, MCC_DAQ]
        self.ready                      =  Array('i', [0, 0, 0])
        self.check_readiness            =  Array('i', [1, 1, 1])

        # p1p2 (for optogenetics)
        self.p1 = Array('f', [0., 0.])
        self.p1 = Array('f', [0., 0.])

        # camera control
        self.enable_camera_control = Value('i', 0)
        self.camera_control_running = Value('i', 0)
        self.camera_recording = Value('i', 0)

        # stimulus counter
        self.stimulus_counter = Value('i', 0)

        #
        self.experiment_running = Value('i', 0)

        # says if the trigger is on for all three subworlds (RGB) or not
        self.trigger_state = Value('i', 0)

        # time
        self.t = Value('f', 0)

        # make movie?
        self.make_movie = Value('i', 0)
        self.movie_started = Value('i', 0)

        # place to share some object or variable between the color worlds
        self.rgb_worlds_shared_variable = [0,0,0]
        self.rgb_worlds_shared_variable2 = [0,0,0]

        # virtual cell
        self.virtual_cell = ""
        self.virtual_cell_running = Value('i', 0)

        # new trigger protocol
        self.stimulus_protocol = []


    def set_automatic_filename(self):

        if self.filename_automatic.value == 0:
            #self.d['filename'] = self.d['filename_prefix'] + '_' + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H.%M')
            self.d['filename'] = os.path.join(self.d['path'], self.d['filename_prefix'] + '_' + datetime.datetime.strftime(self.init_date, '%Y-%m-%d_%H.%M'))



    def get_save_protocol(self):

        shared_protocol = {'DAQ start time': self.d['MCC_DAQ_start_time'],
                           'DAQ low channel': self.MCC_DAQ_lowChan.value,
                           'DAQ high channel': self.MCC_DAQ_highChan.value,
                           'DAQ acquisition rate': self.MCC_DAQ_acquisitionRate.value,
                           'DAQ package size': self.MCC_DAQ_packageSize.value,
                           'current injection amplitude [pA]': self.MCC_CurrentInjection_ampere.value}

        return shared_protocol





