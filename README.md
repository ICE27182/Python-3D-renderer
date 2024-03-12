# Python-3D-renderer
## A 3D renderer written completely in Python, without using any 3rd-party libraries
- Support loading from .obj file
- Support mesh transformation
- Support texture
- Support normal map
- Support smooth shading
- Lighting(difused): parallel, spot, point
- Shadow: shadow mapping
- Anti-aliasing: FXAA (Not recommanded in low resolution)

## Using
I just do not want to spend more time on this project, at least for now, so the code has a pretty messy looking.  
  
To use all the classes and funcs, import pyrender.py.  

You may check pymain.py and prefinal.py to have an idea on how to use it.  
Import control.py so you can have key input without interupting the real time rendering.  

Important: If you find the image shaking(or whatever, just werid), press r(not R).

You can also try playing around particles.py. I wrote it initially trying to do the tyndall effect in a kinda primitive way.  
note.md is a note I took when coding so as to sort out my mind, more or less.  
  
You may get confused with the code when checking pyrenderer.py. To optimized for performance, I replace many parts of code that could have been written with 
functions or loops with hardcode. Also, to remove some of the if statements that do not necessarily have to run again and again during rendering, I put those statements
at the very beginning of the function, leading to several parts looking alike and
kinda redundant.  
The code is pretty messy indeed and not very well commented. I just think I've spent
too much time on this "meanless" project and decided to end it. Therefore, unfortunately, there is unlikely to be a major update for a long time.

