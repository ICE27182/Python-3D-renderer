# Python-3D-renderer
## Demonstration
Youtube: https://youtu.be/_Oo5oqAyLD0?si=9ZLv9QcMqeIAYhDV  
Bilibili: https://www.bilibili.com/video/BV1UJ4m1h79P  

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
To use all the classes and funcs, import pyrender.py.  

Import control.py so you can have key input without interupting the real time rendering. 

You may check pymain.py and prefinal.py to have an idea on how to use it.  
  
Press wasd to move around, space to leap, 8456(numpad) to rotate the camera.  
If you do not have a numpad, it would still work with the numeric keys located at the top row of your keyboard, 
though it is not as intuitive as the numpad. You can remap the keys to keys like ijkl in the code.  

Other key mappings (not all): P - screenshot, Q - quit, r - refresh and resize, f - to enter vehicle, / - command mode, 
v - switch between first person and third person view in vehicle, W - dash(on foot) / high torque(on car), F - toggle 
FXAA, !(shift + 1) - mode 1(No texture), #(shift + 3) - mode 3(Texture with no lighting), $(shift + 4) - mode 4(Depth), %
(shift + 5) - mode 5(For shadow mapping exclusively), ^(shift + 6) - mode 6(Line frames. Faces whose normal pointing forward 
will be culled.), &(shift + 7) - mode 7(Line frames), + - zoom in, - - zoom out, ...  
For more specific key mappings, please check the code. They are the last part the code of the two files.  
  
Note: All keys are case-sentive.  

There is also a command system in these two files, with which you may run a basic 
benchmarking, take a screenshot (and store it in bmp), or change many other things
for debugging.  
For more details, check the code.  
  
Important: If you find the image shaking, too small, twisted (or whatever, just werid), press r(not R).  
  
You can also try playing around particles.py. I wrote it initially trying to do the tyndall effect in a kinda primitive way.  

Python version I was using while coding: 3.11.4  
  
## Standard libraries used
About the standard libraries imported in the project, most of them are not necessary for just rendering or can be easily replaced by code written in python.
### pyrenderer:  
- math: To calculate trigonometric functions and square root (math.sqrt is faster than n**0.5 in case you don't know)  
- os: To check if a file exists, to clear the screen and to get the size of the terminal so the rendering resolution can be decided automatically
- time: sleep to show warnings  
### prefinal.py  
- subprocess: To copy camera information to clipboard  
- math: the same as above  
- time: To get FPS and offer the time elapsed every frame to the physics calculation.  
### control.py:  
- msvcrt: To read keyboard input. Compared to input function, you don't need to press enter every time you input a key  
- threading: Just like input, msvcrt.getwch will also pause the program until you press the key. Put it in another threading helps making everything work as supposed when you are not pressing a key. (You would stuck in the air after jump if not it)  
### png.py  
- pickle: To accelerate loading png file after having read it once before by storing a pickle file  
- zlib: To decompress png file (maybe the most irreplaceable library if you are to render objects with texture)  
- binascii: To do crc32 check. Generally useless.  
- math: math.ceil

## Other matters
If you find the code rather difficult to read and understand, it's probably not your fault. It is huge project to me and I have zero experience on it. 
Plus, at the end phase of the project, I really wanted to end it asap since it had took me too much time and some fundamental flaws in it such as poor support for object are pretty hard to resolve.  
  
You may get confused by the code when reading pyrenderer.py. To optimized for performance, I replace many parts of code that could have been written with 
functions or loops with hardcoding. Also, to remove some of the if statements that do not necessarily have to run again and again during rendering, I put those statements at the very beginning of the function, leading to several parts of code looking quite similar with only a few tiny differences.  
