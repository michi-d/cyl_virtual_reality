## Cylindrical virtual reality setup

The virtual reality is based on two micro-projectors (DLP Lightcrafter 3000, 684x608 pixels) which are mounted on a rigid frame so that they project each on one half of a cylindrical projection screen. The software provided renders a panoramic image of a virtual world from the point of view of a virtual observer and automatically takes care of pre-distorting the projection so that they appear regularly when viewed from the center point of the physical cylinder. The system is optimized for fly vision and increases the native framerate of 60Hz of the projectors to 180 Hz. This is achieved by rendering different time points of the stimulus (offset by 1/180 sec) into the different color channels of the RGB image. If the projector are then modified to use only one LED as a light source, this results effectively in a three time higher image refresh rate of 180Hz.

The following picture summarizes the geometrical pre-distortion principles which are used. Fast rendering of 3D scenes is achieved by using the Python library Panda3D.

<img src="https://github.com/michi-d/cyl_virtual_reality/blob/master/doc/virtual_worlds.png" alt="drawing" width="600"/>
doc/virtual_worlds.png
