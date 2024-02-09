import pyrender
import subprocess

# pyrender.Light.shadow_properties = (2048, 0.01, 1000, 1024)

pyrender.Object.default_obj_dir = "models/"
pyrender.Object.load_obj(pyrender.Object, "plane")
# pyrender.Object.objects[0].calculate_smooth_shading_normals()
# pyrender.Object.objects[0].shade_smooth = True
pyrender.Object.load_obj(pyrender.Object, "torus and cone")
pyrender.Object.objects[1].calculate_smooth_shading_normals()
pyrender.Object.objects[1].shade_smooth = True
pyrender.Object.load_obj(pyrender.Object, "4cones")
# pyrender.Object.load_obj(pyrender.Object, "axis")

# pyrender.Object.load_obj(pyrender.Object, "fox")
# pyrender.Object.objects[1].calculate_smooth_shading_normals()
# pyrender.Object.objects[1].shade_smooth = True

# pyrender.Object.load_obj(pyrender.Object, "models/Final/Porsche 911")
# pyrender.Object.load_obj(pyrender.Object, "muscle car 3904 tris")
for obj in pyrender.Object.objects:
    obj.shade_smooth = True
    obj.calculate_smooth_shading_normals()


cam = pyrender.Camera(x=0.0, y = 0, z=-8, mode=1, obj_buffer=True,
                      fxaa=False,
                      )

cam = pyrender.Camera(x=-28.146239760044658, y=27.85461356722811, z=26.230155650760807, yaw=-45.0, pitch=-25.0, roll=0.0, width=154, height=78, z_near=0.05, z_far=100.0, fov=100, fxaa=False, obj_buffer=True, mode=6)
cam = pyrender.Camera(x=17.900746916870048, y=14.03502646815646, z=-19.417756945865527, yaw=130.0, pitch=-25.0, roll=0.0, z_near=0.05, z_far=800.0, fov=100, fxaa=False, obj_buffer=True, mode=1)
cam = pyrender.Camera(x=11.300097930733683, y=9.047692424249316, z=-11.62869769883726, yaw=130.0, pitch=-25.0, roll=0.0, width=131, height=63, z_near=0.05, z_far=800.0, fov=100, fxaa=False, obj_buffer=True, mode=1)
pyrender.Light.lights.append(
    pyrender.Light(
        (3, 12, 3),
        (156 // 2, 220 // 2, 256 // 2,)
    )
)
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (3, 3, 3),
#         (4, 2.4, 0.1)
#     )
# )  
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (-3, -3, -3),
#         (1.8, 1.0, 0.1)
#     )
# )
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (-0.713, 0.662, -4.281),
#         (0.1, 1, 2)
#     )
# )

# pyrender.Light.lights.append(
#     pyrender.Light(
#         (3, 3, 3),
#         (0.3, 0.25, 0.2),
#         (0, -1, 0),
#         0
#     )
# )
pyrender.Light.lights.append(
    pyrender.Light(
        (0, 16, 0),
        (0.01 * 1, 0.005 * 1, 0.015 * 1,),
        (0, -1, 0),
        0
    )
)
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (0, 8, 0),
#         (1, 1, 1),
#         (0, -1, 1),
#         0
#     )
# )

# pyrender.Light.lights.append(
#     pyrender.Light(
#         (0, 0, 0),
#         (156, 220, 256,),
#     )
# )
# pyrender.Light.lights[-1].shadow_properties = (128, 0.01, 100, 64)

from msvcrt import getwch
from time import time

def v_dot_u(v, u):
    return v[0]*u[0] + v[1]*u[1] + v[2]*u[2]
def len_v(v):
    return pyrender.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

step = 0.4
picked_obj = None
do_add_light = False
display_gs = False
# 8&9 are reserved, because shift+8 is *, which will conflict with that in the numpad,
# and it's weird if only 8 is disabled so shift + 9 is also now.
keyboard_number_lookup={"!":1, "@":2, "#":3, "$":4, "%":5, "^":6, "&":7, ")":0}
from os import system
system("cls")
while True:
    start = time()


    # pyrender.Light.lights[-1].x = cam.x + cam.rotation[2][0] * 10 - cam.rotation[1][0] * 5
    # pyrender.Light.lights[-1].y = cam.y + cam.rotation[2][1] * 10 - cam.rotation[1][1] * 5
    # pyrender.Light.lights[-1].z = cam.z + cam.rotation[2][2] * 10 - cam.rotation[1][2] * 5
    
    # pyrender.Light.lights[0].shadow = False
    # pyrender.Light.lights[1].shadow = False
    # pyrender.Light.render_shadow(pyrender.Light.lights, pyrender.Object.objects)
    # pyrender.Light.lights[0].shadow = True
    # pyrender.Light.lights[1].shadow = True


    print("\033[F" * 900, flush=True)
    frame, obj_buffer, _ = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, cam)
    if do_add_light:
        frame = pyrender.add_lights(frame, cam, pyrender.Light.lights, True)
    if cam.fxaa:
        frame = pyrender.fxaa(frame, channel=0)
    frame[cam.height//2][cam.width//2] = (156, 220, 255)
    looking_at = obj_buffer[cam.height//2][cam.width//2] if obj_buffer != None else None
    if display_gs:
        pyrender.display_gs(frame)
    else:
        pyrender.display(frame)
    print(cam, "\t\t", pyrender.bias_scalar)
    print(f"Looking at: {looking_at}        |        Picked Object: {picked_obj.name if picked_obj!= None else 'None':{cam.width}}",)
    print(f"{1/time_elapsed if (time_elapsed:=time() - start) > 0 else 0:.3f}fps")
    
    

    # print(pyrender.Light.lights[0].rotation0, "  " * 50
        #   f"{v_dot_u(pyrender.Light.lights[0].rotation0[0], pyrender.Light.lights[0].rotation0[1]):.3f}",
        #   f"{v_dot_u(pyrender.Light.lights[0].rotation0[1], pyrender.Light.lights[0].rotation0[2]):.3f}",
        #   f"{v_dot_u(pyrender.Light.lights[0].rotation0[0], pyrender.Light.lights[0].rotation0[2]):.3f}",
        #   f"{len_v(pyrender.Light.lights[0].rotation0[0]):.3f}",
        #   f"{len_v(pyrender.Light.lights[0].rotation0[1]):.3f}",
        #   f"{len_v(pyrender.Light.lights[0].rotation0[2]):.3f}",
        #   )
    # break
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
        cam.rotate(yaw = step * 12.5)
    elif key == "6":
        cam.rotate(yaw = step * -12.5)
    elif key == "8":
        cam.rotate(pitch = step * 12.5)
    elif key == "5":
        cam.rotate(pitch = step * -12.5)
    
    elif key == "F":
        cam.fxaa = not cam.fxaa
    
    elif key == "r":
        cam.width, cam.height = cam.get_width_and_height(height_reserved=6)
        w, h = cam.get_width_and_height()
        w += 3
        h += 3
        frame = [[(0, 0, 0)] * w for _ in range(h)]
        pyrender.display(frame)
        system("cls")
        cam.rendering_plane_z = cam.width * 0.5 / pyrender.tan(cam.fov * pyrender.pi / 360)
    
    elif key == "P":
        pyrender.png.Png.write_as_bmp(frame, "screenshot.bmp")
    
    elif key == "\r":
        picked_obj = obj_buffer[cam.height//2][cam.width//2] if obj_buffer != None else None

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

    elif key == "B":
        pyrender.Light.render_shadow(pyrender.Light.lights, pyrender.Object.objects)
    
    elif key == "(":
        system('cls')
        pyrender.display(pyrender.convert_depth_to_frame(
            pyrender.Light.lights[-1].shadow_map0, 0.01, 20
        ))
        pyrender.sleep(5)
        system('cls')

    elif key == "l":
        do_add_light = not do_add_light
    
    elif key == "C":
        subprocess.run(["powershell", "Set-Clipboard", " -Value", repr(cam.stat())])

    elif key == "T":
        display_tm = time()
        pyrender.display(frame)
        pyrender.display(frame)
        pyrender.display(frame)
        pyrender.display(frame)
        pyrender.display(frame)
        display_tm = time() - display_tm
        display2_tm = time()
        pyrender.display2(frame)
        pyrender.display2(frame)
        pyrender.display2(frame)
        pyrender.display2(frame)
        pyrender.display2(frame)
        display2_tm = time() - display2_tm
        print(display_tm, display2_tm)
        pyrender.Beep(1000, 10**3 * 10)

    elif key == "+":
        pyrender.bias_scalar += 0.1
    elif key == "-":
        pyrender.bias_scalar -= 0.1
    
    elif key == "D":
        display_gs = not display_gs

    elif key == "Q":
        break