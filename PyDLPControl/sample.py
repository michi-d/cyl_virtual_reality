from PyDLPControl import *
import matplotlib.cm as cm
from time import sleep

ip_host = "192.168.1.115"

# connect to hardware
LCR_CMD_Open(ip_host)

# set display mode to static image
LCR_CMD_SetDisplayMode(0)

# show rainbow colors
for i in range(255):
    t = cm.rainbow(i)
    r = format(int(t[0]*255), '02x')
    g = format(int(t[1]*255), '02x')
    b = format(int(t[2]*255), '02x')
    color = int(r + g + b, 16)

    LCR_CMD_DisplayStaticColor(color)

    sleep(0.005)


# close connection
LCR_CMD_Close()