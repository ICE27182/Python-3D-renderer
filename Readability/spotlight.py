

from pyrender import *
from msvcrt import getwch
import subprocess

bias_scalar = 0.6

Object.default_obj_dir = "models/"
Object.load_obj(Object, "plane")
Object.objects[0].set_position(0, -4, 0)

Object.load_obj(Object, "torus and cone")
Object.load_obj(Object, "4cones")

cam = Camera(x=0.0, y = 0, z=-8, mode=0, obj_buffer=False,
                      fxaa=False,
                      )


Light.lights.append(
    Light(
        (0, 5, 0),
        (16, 16, 16),
        (0, -1, 0),
        120,
        2
    )
)

step = 0.4
do_add_light = False
keyboard_number_lookup={"!":1, "@":2, "#":3, "$":4, "%":5, "^":6, "&":7, ")":0}
from os import system
system("cls")
while True:
    print("\033[F" * 900, flush=True)
    frame, obj_buffer, _ = render(Object.objects, Light.lights, cam)
    if do_add_light:
        frame = add_lights(frame, cam, Light.lights, True)
    display(frame)
    print(cam, "\t\t", bias_scalar)

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
        display(frame)
        system("cls")
        cam.rendering_plane_z = cam.width * 0.5 / tan(cam.fov * pi / 360)
    
    elif key == "P":
        png.Png.write_as_bmp(frame, "screenshot.bmp")
    
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
        for obj in Object.objects:
            obj.hidden = False
    elif key == "t":
        if picked_obj != None:
            picked_obj.culling = not picked_obj.culling

    
    # shift + number
    elif key in "!@#$%^&)":
        cam.mode = keyboard_number_lookup[key]

    elif key == "B":
        Light.render_shadow(Light.lights, Object.objects)

    elif key == "l":
        do_add_light = not do_add_light
    
    elif key == "C":
        subprocess.run(["powershell", "Set-Clipboard", " -Value", repr(cam.stat())])

    elif key == "+":
        bias_scalar += 0.1
    elif key == "-":
        bias_scalar -= 0.1
    
    elif key == "D":
        display_gs = not display_gs

    elif key == "Q":
        break

    elif key == "/":
        while True:
            command = input("/").split()

            if command == []:
                continue

            elif command[0] == "shadow_map":
                if len(command) == 2 and command[1].lower() in ("l", "list", "-l", "--list") or len(command) == 1:
                    print("Shadow maps:")
                    for index, light in enumerate(Light.lights):
                        if light.type in (0, 2) and light.shadow_map0 != None:
                            print(f"\t- {index}\t{light}")
                        elif light.type == 1 and light.shadow_map1 != None:
                            print(f"\t- {index}\t{light}")
                            

                elif len(command) == 2 and command[1].isdecimal():
                    light = Light.lights[int(command[1])]
                    if light.type in (0, 2):
                        if light.shadow_map0 != None:
                            display(
                                convert_depth_to_frame(
                                    light.shadow_map0, *light.shadow_properties[1:3]
                                )
                            )
                        else:
                            print("Shadow map No Found")
                    elif light.type == 1:
                        if light.shadow_map1 != None:
                            display(
                                convert_depth_to_frame(
                                    light.shadow_map1, *light.shadow_properties[1:3]
                                )
                            )
                            display(
                                convert_depth_to_frame(
                                    light.shadow_map2, *light.shadow_properties[1:3]
                                )
                            )
                            display(
                                convert_depth_to_frame(
                                    light.shadow_map3, *light.shadow_properties[1:3]
                                )
                            )
                            display(
                                convert_depth_to_frame(
                                    light.shadow_map4, *light.shadow_properties[1:3]
                                )
                            )
                            display(
                                convert_depth_to_frame(
                                    light.shadow_map5, *light.shadow_properties[1:3]
                                )
                            )
                            display(
                                convert_depth_to_frame(
                                    light.shadow_map6, *light.shadow_properties[1:3]
                                )
                            )
                        else:
                            print("Shadow map No Found")
            
            elif command[0] == "set-cam":
                if len(command) in (4, 7):
                    try:
                        if len(command) == 4:
                            cam.x, cam.y, cam.z = eval(command[1]), eval(command[2]), eval(command[3]),
                        else:
                            cam.x, cam.y, cam.z = eval(command[1]), eval(command[2]), eval(command[3]),
                            cam.yaw, cam.pitch, cam.roll = eval(command[4]), eval(command[5]), eval(command[6]),
                            cam.get_rotation_mat()
                    except ValueError:
                        print("Check your syntax")
                    break
            
            elif command[0] == "set-obj":
                # CodeUndone VsCode
                obj:Object
                if len(command) >= 2:
                    for index, obj in enumerate(Object.objects):
                        if obj.name == command[1]:
                            break
                    else:
                        print("Object No Found")
                        continue
                if len(command) == 5:
                    obj.set_position(eval(command[2]), eval(command[3]), eval(command[4]))
                if len(command) == 3:
                    if command[2] in ("h", "hidden"):
                        obj.hidden = not obj.hidden
                    elif command[2] in ("s", "shadow"):
                        obj.shadow = not obj.shadow
                    elif command[2] in ("ss", "shade_smooth"):
                        obj.shade_smooth = not obj.shade_smooth
                    elif command[2] in ("c", "culling"):
                        obj.culling = not obj.culling
                    elif command[2] in ("DELETE"):
                        del Object.objects[index]

            
            elif command[0] == "obj":
                if len(command) == 1 or len(command) == 2 and command[1] in ("--list", "l", "-l"):
                    for index, obj in enumerate(Object.objects):
                        print(f"{index:{len(str(len(Object.objects)))}} | {obj}")

            
            elif command[0] == "render":
                if len(command) == 1:
                    high_resolution_cam = Camera(cam.x, cam.y, cam.z, cam.yaw, cam.pitch, cam.roll, 1280, 720, 0.01, 640, cam.fov, True, False, 0)
                    frame, _, _  = render(Object.objects, Light.lights, high_resolution_cam)
                    frame = fxaa(frame, channel=1)
                    png.Png.write_as_bmp(frame, "rendered image.bmp")
                elif len(command) == 3 and command[1].isdecimal and command[2].isdecimal:
                    high_resolution_cam = Camera(cam.x, cam.y, cam.z, cam.yaw, cam.pitch, cam.roll, int(command[1]), int(command[2]), 0.01, 640, cam.fov, True, False, 0)
                    frame, _, _  = render(Object.objects, Light.lights, high_resolution_cam)
                    frame = fxaa(frame, channel=1)
                    png.Png.write_as_bmp(frame, "rendered image.bmp")
                elif len(command) == 4 and command[1].isdecimal and command[2].isdecimal and command[3].isdecimal:
                    high_resolution_cam = Camera(cam.x, cam.y, cam.z, cam.yaw, cam.pitch, cam.roll, int(command[1]), int(command[2]), 0.01, 640, cam.fov, True, False, int(command[3]))
                    frame, _, _  = render(Object.objects, Light.lights, high_resolution_cam)
                    frame = fxaa(frame, channel=1)
                elif len(command) == 15:
                    high_resolution_cam = eval(f"Camera({' '.join(command[1:])})")
                    frame, _, _  = render(Object.objects, Light.lights, high_resolution_cam)
                    if cam.fxaa:
                        frame = fxaa(frame, channel=1)
                    png.Png.write_as_bmp(frame, "rendered image.bmp")
            
            elif command[0] == "command":
                if len(command):
                    try:
                        exec(" ".join(command[1:]))
                    except Exception as exception:
                        print(exception)
            
            elif " ".join(command) in ("q", "quit", "exit"):
                system("cls")
                break
            
            elif command == ["Q"]:
                exit()



