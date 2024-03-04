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
I just do not want to spend more time on this project, at least for now, so it's pretty messy looking.  
  
To use all the classes and funcs, import Readability/pyrender.py and Readability/png.py (I wrote it too and it is required for loading textures and normal maps).  
You may check Readability/pymain.py and Readability/prefinal.py to have an idea on how to use it.  
Import Readability/control.py so you can have key input without interupting the real time rendering.  
You can also try playing around Readability/particles.py. I wrote it initially trying to do the tyndall effect in a kinda primitive way.  
note.md is a note I took when coding so as to sort out my mind, more or less.  
  
Ironically, codes in "Readability" aren't quite readable nor good in performace. At first, I thought I wrote something that was easy to read and understand, and then another version optimized for performance (by putting some functions straight into the code, altering some calculation steps so it takes less multiplications and divisions, copying and pasting code from one loop to get rid of it and its cost on performace and so on)  

