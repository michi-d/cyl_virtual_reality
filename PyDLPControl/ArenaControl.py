__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

from PyDLPControl import *
import subprocess
from multiprocessing import Process
import time
import sys

#list_of_ips = ["192.168.1.100", "192.168.1.105", "192.168.1.115"]

def set_red(ip_host):
        LCR_CMD_Close()
        LCR_CMD_Open(str(ip_host))
        LCR_CMD_SetDisplayMode(2)
        LCR_CMD_SetVideoMode(60, 7, 2)
        LCR_CMD_Close()

def set_green(ip_host):
        LCR_CMD_Close()
        LCR_CMD_Open(str(ip_host))
        LCR_CMD_SetDisplayMode(2)
        LCR_CMD_SetVideoMode(60, 7, 3)
        LCR_CMD_Close()

def set_blue(ip_host):
        LCR_CMD_Close()
        LCR_CMD_Open(str(ip_host))
        LCR_CMD_SetDisplayMode(2)
        LCR_CMD_SetVideoMode(60, 7, 4)
        LCR_CMD_Close()

def set_rgb(ip_host):
        LCR_CMD_Close()
        LCR_CMD_Open(str(ip_host))
        LCR_CMD_SetDisplayMode(2)
        LCR_CMD_SetVideoMode(60, 4, 1)
        LCR_CMD_Close()

def ping_beamers(list_of_ips):
    connection = []
    for ip in list_of_ips:
        ping = subprocess.Popen(["ping", "-n", "3",ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping.communicate()
        out = out.strip()
        error = error.strip()
        print(out)
        print(error)

        s = out.find('Approximate round trip times in milli-seconds')
        if s == -1:
            connection.append(False)
        else:
            connection.append(True)

    return connection


class Pinger(Process):

    def __init__(self, shared, dt = 5.):
        super(Pinger, self).__init__()
        self.shared = shared
        self.dt = dt

    def run(self):

        while self.shared.pinger_running.value == 1 and self.shared.enable_TCP_control_beamer.value == 1:
            ping_beamers(self.shared.control_beamers)
            time.sleep(self.dt)
        sys.exit()



