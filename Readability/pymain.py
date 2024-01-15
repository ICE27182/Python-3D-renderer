import pyrender

pyrender.Object.default_obj_dir = "models/"
pyrender.Object.load_obj(pyrender.Object, "sphere")
pyrender.Object.objects[-1].calculate_smooth_shading_normals()
pyrender.Object.objects[-1].shade_smooth = True
pyrender.Object.load_obj(pyrender.Object, "torus and cone")

cam = pyrender.Camera(x=0.0, y = 0, z=-1.8, mode=1, obj_buffer=True,
                    #   width=100, height=60,
                      )
cam.height -= 3

pyrender.Light.lights.append(
    pyrender.Light(
        (3, 3, 3),
        (1, 1.5, 2)
    )
)
pyrender.Light.lights.append(
    pyrender.Light(
        (-3, -3, -3),
        (2, 1.0, 1)
    )
)
pyrender.Light.lights.append(
    pyrender.Light(
        (3, 3, 3),
        (0.3, 0.25, 0.2),
        (0, -1, 0),
        0
    )
)
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (3, 3, 3),
#         (1, 0.5, 0.5),
#         (1, 1, 1),
#         0
#     )
# )

from msvcrt import getwch
step = 0.2
picked_obj = None
# 8&9 are reserved, because shift+8 is *, which will conflict with that in the numpad,
# and it's weird if only 8 is disabled so shift + 9 is also now.
keyboard_number_lookup={"!":1, "@":2, "#":3, "$":4, "%":5, "^":6, "&":7, ")":0}
from os import system
system("cls")
while True:
    print("\033[F" * 300)
    frame, obj_buffer = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, cam)
    if cam.fxaa:
        frame = pyrender.fxaa(frame, channel=0)
    frame[cam.height//2][cam.width//2] = (156, 220, 255)
    looking_at = obj_buffer[cam.height//2][cam.width//2]
    pyrender.display(frame)
    print(cam)
    print(f"Looking at: {looking_at}        |        Picked Object: {picked_obj.name if picked_obj!= None else 'None':{cam.width}}",)
    
    # print(pyrender.Light.lights[0].dirx, pyrender.Light.lights[0].diry, pyrender.Light.lights[0].dirz)
    key = getwch()
    if key == "w":
        cam.x += cam.rotation[2][0] * step
        cam.y += cam.rotation[2][1] * step
        cam.z += cam.rotation[2][2] * step
    elif key == "s":
        cam.x -= cam.rotation[2][0] * step
        cam.y -= cam.rotation[2][1] * step
        cam.z -= cam.rotation[2][2] * step
    elif key == "a":
        cam.x -= cam.rotation[0][0] * step
        cam.y -= cam.rotation[0][1] * step
        cam.z -= cam.rotation[0][2] * step
    elif key == "d":
        cam.x += cam.rotation[0][0] * step
        cam.y += cam.rotation[0][1] * step
        cam.z += cam.rotation[0][2] * step
    elif key == "c":
        cam.x -= cam.rotation[1][0] * step
        cam.y -= cam.rotation[1][1] * step
        cam.z -= cam.rotation[1][2] * step
    elif key == " ":
        cam.x += cam.rotation[1][0] * step
        cam.y += cam.rotation[1][1] * step
        cam.z += cam.rotation[1][2] * step
    elif key == "4":
        cam.rotate(yaw = step * 25)
    elif key == "6":
        cam.rotate(yaw = step * -25)
    elif key == "8":
        cam.rotate(pitch = step * 25)
    elif key == "5":
        cam.rotate(pitch = step * -25)
    
    elif key == "F":
        cam.fxaa = not cam.fxaa
    
    elif key == "r":
        cam.width, cam.height = cam.get_width_and_height(height_reserved=6)
    
    elif key == "P":
        pyrender.png.Png.write_as_bmp(frame, "screenshot.bmp")
    
    elif key == "\r":
        picked_obj = obj_buffer[cam.height//2][cam.width//2]
    elif key == "S":
        if picked_obj != None:
            picked_obj.shade_smooth = not picked_obj.shade_smooth
            if picked_obj.svn == []:
                picked_obj.calculate_smooth_shading_normals()
    elif key == "h":
        if picked_obj != None:
            picked_obj.hidden = not picked_obj.hidden
    elif key == "H":
        for obj in pyrender.Object.objects:
            obj.hidden = False
    
    # shift + number
    elif key in "!@#$%^&)":
        cam.mode = keyboard_number_lookup[key]
    


    elif key == "Q":
        break
