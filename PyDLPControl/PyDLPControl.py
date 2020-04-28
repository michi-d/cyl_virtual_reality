import ctypes
import os

lcr = ctypes.cdll.LoadLibrary(os.path.join(os.path.split(os.path.realpath(__file__))[0], "LCR_Cmd_Interface_mod.dll"))

(SUCCESS,
FAIL,
ERR_OUT_OF_RESOURCE,
ERR_INVALID_PARAM,
ERR_NULL_PTR,
ERR_NOT_INITIALIZED,
ERR_DEVICE_FAIL,
ERR_DEVICE_BUSY,
ERR_FORMAT_ERROR,
ERR_TIMEOUT,
ERR_NOT_SUPPORTED,
ERR_NOT_FOUND) = map(ctypes.c_int, xrange(12))

ERRSTRLEN = 256

LCR_CMD_VERSION_STR_LEN		= 32
LCR_CMD_SOLUTION_NAME_LEN	= 32

ONE_BPP_PTN_SIZE		= 52046
TWO_BPP_PTN_SIZE		= 208006
THREE_BPP_PTN_SIZE		= 208022
FOUR_BPP_PTN_SIZE		= 208054
FIVE_BPP_PTN_SIZE		= 416054
SIX_BPP_PTN_SIZE		= 416182
SEVEN_BPP_PTN_SIZE		= 416438
EIGHT_BPP_PTN_SIZE		= 416950


REV_DM365 = 0x00
REV_FPGA = 0x10
REV_MSP430 = 0x20

(PWR_NORMAL,
PWR_STANDBY) = map(ctypes.c_int, xrange(2))

(LED_RED,
LED_GREEN,
LED_BLUE,
LED_DEFAULT) = map(ctypes.c_int, xrange(4))

(SOL_DELETE,
SOL_LOAD,
SOL_SET_DEFAULT) = map(ctypes.c_int, xrange(3))

(DISP_MODE_IMAGE,		#/* Static Image */
DISP_MODE_TEST_PTN,		#/* Internal Test pattern */
DISP_MODE_VIDEO,		#/* HDMI Video */
DISP_MODE_VIDEO_INT_PTN,	#/* Interleaved pattern */
DISP_MODE_PTN_SEQ,		#/* Pattern Sequence */
DISP_NUM_MODES) = map(ctypes.c_int, xrange(6))


(TEST_PTN_FINE_CHECKER,   	#/* 0x0 - Fine Checkerboard */
TEST_PTN_SOLID_BLACK,		#/* 0x1 - Solid black */
TEST_PTN_SOLID_WHITE,		#/* 0x2 - Solid white */
TEST_PTN_SOLID_GREEN,		#/* 0x3 - Solid green */
TEST_PTN_SOLID_BLUE,		#/* 0x4 - Solid blue */
TEST_PTN_SOLID_RED,			#/* 0x5 - Solid red */
TEST_PTN_VERTICAL_LINES,	#/* 0x6 - Vertical lines (1-white, 7-black) */
TEST_PTN_HORIZONTAL_LINES,  #/* 0x7 - Horizontal lines (1-white, 7-black) */
TEST_PTN_FINE_VERTICAL_LINES, #/* 0x8 - Vertical lines (1-white, 1-black) */
TEST_PTN_FILE_HORIZONTAL_LINES, #/* 0x9 - Horizontal lines (1-white, 1-black) */
TEST_PTN_DIAG_LINES,		#/* 0xA - Diagonal lines */
TEST_PTN_VERTICAL_RAMP,		#/* 0xB - Vertical Gray Ramps */
TEST_PTN_HORIZONTAL_RAMP,	#/* 0xC - Horizontal Gray Ramps */
TEST_PTN_ANXI_CHECKER,		#/* 0xD - ANSI 4x4 Checkerboard */
NUM_TEST_PTNS) =  map(ctypes.c_int, xrange(15))

(TRIGGER_TYPE_SW, TRIGGER_TYPE_AUTO, TRIGGER_TYPE_EXTRNAL, TRIGGER_TYPE_EXTRNAL_INV, TRIGGER_TYPE_CAMERA, TRIGGER_TYPE_CAMERA_INV, TRIGGER_TYPE_TRIG_EXP, NUM_TRIGGER_TYPES) = map(ctypes.c_int, xrange(8))
(TRIGGER_EDGE_POS, TRIGGER_EDGE_NEG) = map(ctypes.c_int, xrange(2))
(CAPTURE_STOP, CAPTURE_SINGLE, CAPTURE_STREAM) = map(ctypes.c_int, xrange(3))
(PTN_TYPE_NORMAL, PTN_TYPE_INVERTED, PTN_TYPE_HW) = map(ctypes.c_int, xrange(3))


LCR_PatternCount_t = ctypes.c_uint16(0)

class LCR_PatternSeqSetting_t(ctypes.Structure):
    _fields_ = [("BitDepth", ctypes.c_uint8),
                ("NumPatterns", ctypes.c_int),
                ("PatternType", ctypes.c_int),
                ("InputTriggerType", ctypes.c_int),
                ("InputTriggerDelay", ctypes.c_uint32),
                ("AutoTriggerPeriod", ctypes.c_uint32),
                ("ExposureTime", ctypes.c_uint32),
                ("LEDSelect", ctypes.c_int),
                ("Repeat", ctypes.c_uint8)]


class LCR_HWPattern_t(ctypes.Structure):
    _fields_ = [("Number", ctypes.c_uint8),
                ("Invert", ctypes.c_uint8)]


class LCR_HWPatternSeqDef_t(ctypes.Structure):
    _fields_ = [("index", ctypes.c_uint16),
                ("numOfPatn", ctypes.c_uint16),
                ("hwPatArray", ctypes.c_int*32)]


class LCR_VideoSetting_t(ctypes.Structure):
    _fields_ = [("ResolutionX", ctypes.c_uint16),
                ("ResolutionY", ctypes.c_uint16),
                ("FirstPix", ctypes.c_uint16),
                ("FirstLine", ctypes.c_uint16),
                ("ActiveWidth", ctypes.c_uint16),
                ("ActiveHeight", ctypes.c_uint16)]

class LCR_VideoModeSetting_t(ctypes.Structure):
    _fields_ = [("FrameRate", ctypes.c_uint8),
                ("BitDepth", ctypes.c_uint8),
                ("RGB", ctypes.c_uint8)]

class LCR_DisplaySetting_t(ctypes.Structure):
    _fields_ = [("Rotate", ctypes.c_uint8),
                ("LongAxisFlip", ctypes.c_uint8),
                ("ShortAxisFlip", ctypes.c_uint8)]

class LCR_LEDCurrent_t(ctypes.Structure):
    _fields_ = [("Red", ctypes.c_uint16),
                ("Green", ctypes.c_uint16),
                ("Blue", ctypes.c_uint16)]

class LCR_CamTriggerSetting_t(ctypes.Structure):
    _fields_ = [("Enable", ctypes.c_uint16),
                ("Source", ctypes.c_uint16),
                ("Polarity", ctypes.c_uint16),
                ("Delay", ctypes.c_uint32),
                ("PulseWidth", ctypes.c_uint32),
                ("Reserved", ctypes.c_uint8 * 12)]

class LCR_Setting_t(ctypes.Structure):
    _fields_ = [("DisplayMode", LCR_VideoModeSetting_t),
                ("Display", LCR_DisplaySetting_t),
                ("LEDCurrent", LCR_LEDCurrent_t),
                ("TestPattern", ctypes.c_int),
                ("Video", LCR_VideoSetting_t),
                ("PatternSeq", LCR_PatternSeqSetting_t),
                ("CamTrigger", LCR_CamTriggerSetting_t),
                ("VideoMode", LCR_VideoModeSetting_t),
                ("StaticColor", ctypes.c_uint32),
                ("Reserved", ctypes.c_uint8 * 32)]


# function declarations

class lcr_cmd_interface_base_error(Exception):
    """base class for all exceptions"""
    pass

def _get_error_message(ErrorCode):
    err_msg = ctypes.create_string_buffer(ERRSTRLEN)

    if ErrorCode == 1:
        err_msg.value = "FAIL"
    if ErrorCode == 2:
        err_msg.value = "ERR_OUT_OF_RESOURCE"
    if ErrorCode == 3:
        err_msg.value = "ERR_INVALID_PARAM"
    if ErrorCode == 4:
        err_msg.value = "ERR_NULL_PTR"
    if ErrorCode == 5:
        err_msg.value = "ERR_NOT_INITIALIZED"
    if ErrorCode == 6:
        err_msg.value = "ERR_DEVICE_FAIL"
    if ErrorCode == 7:
        err_msg.value = "ERR_DEVICE_BUSY"
    if ErrorCode == 8:
        err_msg.value = "ERR_FORMAT_ERROR"
    if ErrorCode == 9:
        err_msg.value = "ERR_TIMEOUT"
    if ErrorCode == 10:
        err_msg.value = "ERR_NOT_SUPPORTED"
    if ErrorCode == 11:
        err_msg.value = "ERR_NOT_FOUND"

    origerrstr = err_msg.value
    return origerrstr

class lcr_cmd_interface_error(lcr_cmd_interface_base_error):
    """error occurred within the C layer of Universal Library"""
    def __init__(self, ErrorCode):
        errstr = 'Error %d: %s'%(ErrorCode,_get_error_message(ErrorCode))
        self.errno = ErrorCode
        Exception.__init__(self, errstr)

def CHK(ErrorCode):
    """raise appropriate exception if error occurred"""
    if ErrorCode != int(SUCCESS.value):
        raise lcr_cmd_interface_error(ErrorCode)





### Connects to the DLP LightCrafter(TM) Hardware */
def LCR_CMD_Open(ip_host):
    CHK(lcr.LCR_CMD_Open(ip_host))

### Close the TCP Connection
def LCR_CMD_Close():
    CHK(lcr.LCR_CMD_Close())

### Read revision of MSP430, DM365 and FPGA
def LCR_CMD_GetRevision():
    print("Firmware Version:")
    v = ctypes.c_char_p('')
    CHK(lcr.LCR_CMD_GetRevision(REV_DM365,v))
    print('REV_DM365: ' + v.value + '')
    CHK(lcr.LCR_CMD_GetRevision(REV_FPGA,v))
    print('REV_FPGA: ' + v.value + '')
    CHK(lcr.LCR_CMD_GetRevision(REV_MSP430,v))
    print('REV_MSP430: ' + v.value + '')

### Change the Display Mode
def LCR_CMD_SetDisplayMode(Mode):
    Mode = ctypes.c_int(Mode)
    CHK(lcr.LCR_CMD_SetDisplayMode(Mode))

### Returns the Display Mode */
def LCR_CMD_GetDisplayMode():
    Mode = CHK(lcr.LCR_CMD_GetDisplayMode())
    print("Display Mode:" + str(Mode))
    return Mode

### Set the R,G,B LED current
def LCR_CMD_SetLEDCurrent(Red, Green, Blue):
    # MAXIMUM: 274
    if Red > 274 or Green > 274 or Blue > 274:
        print("Current too high (active cooling needed)")

    setting = LCR_LEDCurrent_t()
    setting.Red = ctypes.c_uint16(Red)
    setting.Green = ctypes.c_uint16(Green)
    setting.Blue = ctypes.c_uint16(Blue)

    CHK(lcr.LCR_CMD_SetLEDCurrent(ctypes.byref(setting)))

### Read the R,G,B LED current
def LCR_CMD_GetLEDCurrent():
    setting = LCR_LEDCurrent_t()
    CHK(lcr.LCR_CMD_GetLEDCurrent(ctypes.byref(setting)))
    print("LED Current:")
    print("Red: " + str(setting.Red))
    print("Green: " + str(setting.Green))
    print("Blue: " + str(setting.Blue))
    return setting

### Displays solid filed color image
def LCR_CMD_DisplayStaticColor(color32):
    color = ctypes.c_uint32(color32)
    CHK(lcr.LCR_CMD_DisplayStaticColor(color))

### Configures the displayed image on the DMD
def LCR_CMD_SetDisplaySetting(LongAxisFlip, ShortAxisFlip, Rotate):
    setting = LCR_DisplaySetting_t()
    setting.LongAxisFlip = ctypes.c_uint8(LongAxisFlip)
    setting.ShortAxisFlip = ctypes.c_uint8(ShortAxisFlip)
    setting.Rotate = ctypes.c_uint8(Rotate)

    CHK(lcr.LCR_CMD_SetDisplaySetting(ctypes.byref(setting)))

### Returns the existing display settings
def LCR_CMD_GetDisplaySetting():
    setting = LCR_DisplaySetting_t()
    CHK(lcr.LCR_CMD_GetDisplaySetting(ctypes.byref(setting)))
    print("Display Setting:")
    print("Long Axis Flip: " + str(setting.LongAxisFlip))
    print("Short Axis Flip: " + str(setting.ShortAxisFlip))
    print("Rotate: " + str(setting.Rotate))
    return setting

### Set Video Mode
def LCR_CMD_SetVideoMode(FrameRate, BitDepth, RGB):
    setting = LCR_VideoModeSetting_t()
    setting.FrameRate = ctypes.c_uint8(FrameRate)
    setting.BitDepth = ctypes.c_uint8(BitDepth)
    setting.RGB = ctypes.c_uint8(RGB)

    CHK(lcr.LCR_CMD_SetVideoMode(ctypes.byref(setting)))

### Return current video mode settings
def LCR_CMD_GetVideoMode():
    setting = LCR_VideoModeSetting_t()
    CHK(lcr.LCR_CMD_GetVideoMode(ctypes.byref(setting)))
    print("Video Setting:")
    print("Frame Rate: " + str(setting.FrameRate))
    print("Bit Depth: " + str(setting.BitDepth))
    print("RGB: " + str(setting.RGB))
    return setting