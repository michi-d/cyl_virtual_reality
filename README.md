## Cylindrical virtual reality setup

The virtual reality is based on two micro-projectors (DLP Lightcrafter 3000, 684x608 pixels) which are mounted on a rigid frame so that they project each on one half of a cylindrical projection screen. The software provided renders a panoramic image of a virtual world from the point of view of a virtual observer and automatically takes care of pre-distorting the projection so that they appear regularly when viewed from the center point of the physical cylinder. The system is optimized for fly vision and increases the native framerate of 60Hz of the projectors to 180 Hz. This is achieved by rendering different time points of the stimulus (offset by 1/180 sec) into the different color channels of the RGB image. If the projector are then modified to use only one LED as a light source, this results effectively in a three time higher image refresh rate of 180Hz.

Fast rendering of 3D scenes is achieved by using the Python library Panda3D. The system has been tested using the GeForce GTX 1070 and GTX 970 graphics cards. 

### How to test:

An example script **vr_runt_test.py** is provided. This script renders a virtual circular tunnel through which the observer is passing at a constant speed.

View of the stimulus screen from outside:
<img src="https://github.com/michi-d/cyl_virtual_reality/blob/master/doc/tunnel_outside.png" alt="drawing" width="300"/>

View of the virtual reality with the virtual observer moving through the tunnel (white lined indicating field of view):
<img src="https://github.com/michi-d/cyl_virtual_reality/blob/master/doc/tunnel_outside.png" alt="drawing" width="300"/>

More functions for control of the display are included in **arena_controls.py**. 

### How to use:

For use in a new virtual reality, the geometry of the pre-distortion pipeline must correspond to the geometry of the physical setup. Geometrical properties of the scene are specified in **core.base**.

The following picture summarizes the geometrical pre-distortion principles which were used here. 

<img src="https://github.com/michi-d/cyl_virtual_reality/blob/master/doc/virtual_worlds.png" alt="drawing" width="600"/>

More information on this system is available in 
* Drews, M. (2019). Linear and Non-Linear Receptive Fields in _Drosophila_ Motion Vision (Doctoral dissertation, LMU Munich).
