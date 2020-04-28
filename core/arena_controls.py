__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

from core.base import PreviewArena, StimulusArena, MovieArena
from experiment.Shared import Shared
from experiment.experiment import ExperimentFramework
#from experiment.OnlineFramework import OnlineFramework
import json
import os as os

def quick_preview_stimulus(params = [1.0, 'stimuli.default.Grating', 10.0, 0.0, 30.0, 10.0, 'sq', 0, 100], shared = [], setFrameRateMeter = True):


    if not shared:
        # define shared variables
        shared = Shared()
        shared.check_readiness = [1,1,0]

    # start arena framework
    arena = PreviewArena([], shared)
    arena.setFrameRateMeter(setFrameRateMeter)

    experiment = ExperimentFramework(arena, shared, click_window = False, vsync_adjust=False)
    experiment.enter_pressed = 1

    experiment.add_stimulus_new(*params)

    # run arena
    arena.run()


def quick_preview_protocol(params_list, shared = [], setFrameRateMeter = True):

    if not shared:
        # define shared variables
        shared = Shared()
        shared.check_readiness = [1,1,0]

    # start arena framework
    arena = PreviewArena([], shared)
    arena.setFrameRateMeter(setFrameRateMeter)

    experiment = ExperimentFramework(arena, shared, click_window = False, vsync_adjust=False)
    experiment.enter_pressed = 1

    for p in params_list:
        experiment.add_stimulus_new(*p)

    # run arena
    arena.run()


def show_stimulus_protocol(params_list, shared = [], win_origin = (1280, 0)):

    os.chdir(os.path.realpath(os.path.dirname(__file__)))

    #subprocess.call("displayswitch /external", shell=True)
    #time.sleep(1)

    user_profile = load_user_profile()
    calibration  = get_calibration(user_profile)

    if not shared:
        # define shared variables
        shared = Shared()
        shared.check_readiness = [1,1,0]
        shared.arena_mode = 'default'

    # start arena framework
    arena = StimulusArena(calibration, shared, win_origin = win_origin)

    experiment = ExperimentFramework(arena, shared, click_window = True, vsync_adjust=True)

    for p in params_list:
        experiment.add_stimulus_new(*p)

    # run arena
    arena.run()


import panda3d.core as pcore
import pandac.PandaModules as PandaModules

def make_movie_stimulus(params_list, shared = [], setFrameRateMeter = True):

    if not shared:
        # define shared variables
        shared = Shared()
        shared.check_readiness = [1,1,0]

    # start arena framework
    arena = MovieArena([], shared)
    arena.setFrameRateMeter(setFrameRateMeter)

    shared.make_movie.value = 1
    experiment = ExperimentFramework(arena, shared, click_window = False, vsync_adjust=False)
    experiment.enter_pressed = 1

    #experiment.add_stimulus_new(*params)
    for p in params_list:
        experiment.add_stimulus_new(*p)

    # Set up a Cylindrical Lens.
    # The following code is from https://discourse.panda3d.org/t/cylindricallens/1225/4

    screens = pcore.NodePath('dark_room')

    # Let's put a light in the scene, strictly so we can make sense out of
    # it if we call showDarkRoom().  (I guess the room's not so dark now.)
    #light = pcore.DirectionalLight('dark_room_light')
    #screens.attachNewNode(light)
    #screens.node().setAttrib(pcore.LightAttrib.make(pcore.LightAttrib.OAdd, light))

    # A node parented to the original camera node to hold all the new cube
    # face cameras.
    cubeCam = base.cam.attachNewNode('cubeCam')

    # Define the forward vector for the cube.  We have this up to the
    # upper right, so we can get away with using only the front, right,
    # and up faces if we want.

    #cubeForward = (1, 1, 1)
    cubeForward = (0, 1, 0)


    class CubeFace:
        def __init__(self, name, view, up, res):
            self.name = name

            # A camera, for viewing the world under render.
            self.camNode = pcore.Camera('cam' + self.name)
            self.camNode.setScene(base.render)
            self.cam = cubeCam.attachNewNode(self.camNode)

            # A projector, for projecting the generated image of the world
            # onto our screen.
            self.projNode = pcore.LensNode('proj' + self.name)
            self.proj = screens.attachNewNode(self.projNode)

            # A perspective lens, for both of the above.  The same lens is
            # used both to film the world and to project it onto the
            # screen.
            self.lens = pcore.PerspectiveLens()
            self.lens.setFov(92)
            self.lens.setNear(0.1)
            self.lens.setFar(10000)
            self.lens.setViewVector(view[0], view[1], view[2],
                                    up[0], up[1], up[2])

            self.camNode.setLens(self.lens)
            self.projNode.setLens(self.lens)

            # Now the projection screen itself, which is tied to the
            # projector.
            self.psNode = PandaModules.ProjectionScreen('ps' + self.name)
            self.ps = self.proj.attachNewNode(self.psNode)
            self.psNode.setProjector(self.proj)

            # Generate a flat, rectilinear mesh to project the image onto.
            self.psNode.regenerateScreen(self.proj, "screen", res[0], res[1], 10, 0.97)


    # Define the six faces.
    cubeFaces = [
        CubeFace('Right', (1, 0, 0), (0, 0, 1), (50, 50)),
        CubeFace('Back', (0, -1, 0), (0, 0, 1), (50, 50)),
        CubeFace('Left', (-1, 0, 0), (0, 0, 1), (50, 50)),
        CubeFace('Front', (0, 1, 0), (0, 0, 1), (50, 50)),
        CubeFace('Up', (0, 0, 1), (0, -1, 0), (50, 50)),
        CubeFace('Down', (0, 0, -1), (0, 1, 0), (50, 50)),
        ]

    # Indices into the above.
    cri = 0
    cbi = 1
    cli = 2
    cfi = 3
    cui = 4
    cdi = 5


    # Rotate the cube to the forward axis.
    cubeCam.lookAt(cubeForward[0], cubeForward[1], cubeForward[2])
    m = pcore.Mat4()
    m.invertFrom(cubeCam.getMat())
    cubeCam.setMat(m)

    # Get the base display region.
    dr = base.camNode.getDisplayRegion(0)

    # Now make a fisheye lens to view the whole thing.
    # fcamNode = Camera('fcam')
    # fcam = screens.attachNewNode(fcamNode)
    # flens = FisheyeLens()
    # flens.setViewVector(cubeForward[0], cubeForward[1], cubeForward[2],  0, 0, 1)
    # flens.setFov(180)
    # flens.setFilmSize(dr.getPixelWidth() / 2, dr.getPixelHeight())
    # fcamNode.setLens(flens)

    # And a cylindrical lens for fun.
    ccamNode = pcore.Camera('ccam')
    ccam = screens.attachNewNode(ccamNode)
    clens = PandaModules.CylindricalLens()
    clens.setViewVector(1, 0, 0 ,0, 0, 1)
    clens.setFov(180)
    clens.setFilmSize(dr.getPixelWidth(), dr.getPixelWidth()/(3.14159*5/13.5) * 180/180.) # 13.5 empirical
    ccamNode.setLens(clens)

    # Turn off the base display region and replace it with two
    # side-by-side regions.
    # dr.setActive(0)
    # window = dr.getWindow()
    # dr1 = window.makeDisplayRegion(0, 0.5, 0, 1)
    # dr1.setSort(dr.getSort())
    # dr2 = window.makeDisplayRegion(0.5, 1, 0, 1)
    # dr2.setSort(dr.getSort())

    # Set the fisheye lens on the left, and the cylindrical lens on the right.
    #dr2.setCamera(ccam)
    dr.setCamera(ccam)



    # And create the NonlinearImager to do all the fancy stuff.
    nli = PandaModules.NonlinearImager()
    nli.addViewer(dr)
    #nli.addViewer(dr2)

    for face in cubeFaces:
        i = nli.addScreen(face.ps, face.name)
        nli.setSourceCamera(i, face.cam)
        nli.setTextureSize(i, 512, 512)


    def hideAll():
        for i in range(6):
            nli.setScreenActive(i, 0)

    def showAll():
        for i in range(6):
            nli.setScreenActive(i, 1)

    hideAll()
    nli.setScreenActive(cfi, 1)
    nli.setScreenActive(cri, 1)
    nli.setScreenActive(cdi, 1)
    nli.setScreenActive(cbi, 1)
    nli.setScreenActive(cui, 1)
    #showAll()

    base.disableMouse()

    #### CRAZY STUFF ENDS HERE ####

    # run arena
    arena.run()


def load_user_profile():
    # load profile
    profile_f = open("..//profile.txt", "r")
    profileFile = profile_f.read()
    profile_f.close()

    f = open("..//" + profileFile, 'rb')
    user_profile = json.loads(f.read())
    f.close()

    return user_profile

def get_calibration(user_profile):

    calibration = [user_profile["beamer_left_X"],
                   user_profile["beamer_left_Y"],
                   user_profile["beamer_left_Z"],
                   user_profile["beamer_left_H"],
                   user_profile["beamer_left_P"],
                   user_profile["beamer_left_R"],
                   user_profile["beamer_right_X"],
                   user_profile["beamer_right_Y"],
                   user_profile["beamer_right_Z"],
                   user_profile["beamer_right_H"],
                   user_profile["beamer_right_P"],
                   user_profile["beamer_right_R"],
                   user_profile["beamer_left_FOV"],
                   user_profile["beamer_right_FOV"]]

    return calibration