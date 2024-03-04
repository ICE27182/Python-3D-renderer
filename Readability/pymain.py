import pyrender
import subprocess
# import particles
import control

# pyrender.Light.shadow_properties = (2048, 0.01, 1000, 1024)
# PARTICLES = particles.Particles(density=2,
#                                 position=(19.6, 0, 12.5),
#                                 size=6)
pyrender.Object.default_obj_dir = "models/"
# pyrender.Object.load_obj(pyrender.Object, "plane")
# pyrender.Object.objects[0].set_position(0, -4, 0)
# pyrender.Object.objects[0].calculate_smooth_shading_normals()
# pyrender.Object.objects[0].shade_smooth = True
# pyrender.Object.load_obj(pyrender.Object, "torus and cone")
# pyrender.Object.objects[1].calculate_smooth_shading_normals()
# pyrender.Object.objects[1].shade_smooth = True
# pyrender.Object.objects[1].set_position(20, 8, 16)
# pyrender.Object.objects[0].set_position(20, 8, 16)
# pyrender.Object.load_obj(pyrender.Object, "4cones")
# pyrender.Object.load_obj(pyrender.Object, "axis")

# pyrender.Object.load_obj(pyrender.Object, "fox")
# pyrender.Object.objects[1].calculate_smooth_shading_normals()
# pyrender.Object.objects[1].shade_smooth = True
# pyrender.Object.load_obj(pyrender.Object, "models/Crafting_table/Crafting_table")
pyrender.Object.load_obj(pyrender.Object, "E:/Programming/Python/Python-3D-renderer/models/Furniture/Furniture.obj")
# pyrender.Object.load_obj(pyrender.Object, "models/Final/Porsche 911")
# for obj in pyrender.Object.objects:
#     obj.set_position(24, 0, 12)
# pyrender.Object.load_obj(pyrender.Object, "models/Final/Scene")
# for obj in pyrender.Object.objects:
#     if obj.name == "Road_light":
#         obj.culling = False
#         obj.shadow = False
#     elif "shadow_wall" in obj.name:
#         obj.hidden = True
#     elif obj.name == "Shop":
#         obj.culling = False
#     elif obj.name == "Shop_top":
#         obj.culling == False
# pyrender.Object.load_obj(pyrender.Object, "muscle car 3904 tris")
# for obj in pyrender.Object.objects:
#     obj.shade_smooth = True
#     obj.calculate_smooth_shading_normals()



# cam = pyrender.Camera(x=0.0, y = 0, z=-8, mode=1, obj_buffer=True,
#                       fxaa=False,
#                       )

# cam = pyrender.Camera(x=-28.146239760044658, y=27.85461356722811, z=26.230155650760807, yaw=-45.0, pitch=-25.0, roll=0.0, width=154, height=78, z_near=0.05, z_far=100.0, fov=100, fxaa=False, obj_buffer=True, mode=6)
# cam = pyrender.Camera(x=17.900746916870048, y=14.03502646815646, z=-19.417756945865527, yaw=130.0, pitch=-25.0, roll=0.0, z_near=0.05, z_far=800.0, fov=100, fxaa=False, obj_buffer=True, mode=1)
# cam = pyrender.Camera(x=18.509956849826306, y=1.6113281707861065, z=2.0788881229208043, yaw=60.0, pitch=0.0, roll=0.0, z_near=0.05, z_far=100.0, fov=75, fxaa=False, obj_buffer=True, mode=0)

# Sun
# cam = pyrender.Camera(x=20.0, y=53.0, z=-49.0, yaw=90, pitch=-30.0, roll=0.0, z_near=0.05, z_far=400.0, fov=75, fxaa=False, obj_buffer=True, mode=0)

# Road Light
# cam = pyrender.Camera(x=16.417402301967005, y=1.6666998900608736, z=7.570605831743421, yaw=50.0, pitch=5.0, roll=0.0, width=101, height=48, z_near=0.05, z_far=320.0, fov=75, fxaa=False, obj_buffer=True, mode=0)
# Porsche 911
# cam = pyrender.Camera(x=3.561785821438346, y=2.453259551717273, z=0.8332828471152594, yaw=185.0, pitch=-30.0, roll=0.0, width=119, height=60, z_near=0.05, z_far=100.0, fov=90, fxaa=False, obj_buffer=True, mode=0)
# Appartment shadow wall
# cam = pyrender.Camera(x=21.404801545093772, y=4.511871930093861, z=58.16332792734175, yaw=-10.0, pitch=-15.0, roll=0.0, z_near=0.05, z_far=400.0, fov=75, fxaa=False, obj_buffer=True, mode=0)
# Shop shadow wall
# cam = pyrender.Camera(x=25.157257635129216, y=3.781792359259011, z=16.092293680160843, yaw=-180.0, pitch=-10.0, roll=0.0, width=154, height=80, z_near=0.05, z_far=400.0, fov=75, fxaa=False, obj_buffer=True, mode=0)
# Walking
# cam = pyrender.Camera(x=27.0, y=1.75, z=27.0, yaw=180, pitch=0, roll=0.0, z_near=0.05, z_far=400.0, fov=75, fxaa=False, obj_buffer=True, mode=0)
# cam = pyrender.Camera(x=13.568108617885507, y=1.75, z=20.88376423897999, yaw=334.0, pitch=8.0, roll=0.0, z_near=0.05, z_far=400.0, fov=75, fxaa=False, obj_buffer=True, mode=0)

# # Particles
# cam = pyrender.Camera(x=27.280528766180414, y=1.75, z=27.024152598698304, yaw=250.0, pitch=8.0, roll=0.0, z_near=0.05, z_far=400.0, fov=75, fxaa=False, obj_buffer=True, mode=0)

# Driving
# -0.434, 1.094, 1.887

# pyrender.Object.load_obj(pyrender.Object, "Orthographic test")
# cam = pyrender.Camera(0, 100, 0, yaw=90, pitch=-90.0, roll=0.0, z_near=0.05, z_far=500, fov=90, fxaa=False, obj_buffer=True, mode=0)

# Sunset
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (20.0, 53.0, -48.0),
#         (255 / 512, 121 / 512, 7 / 512,),
#         (0, -0.5, 3**0.5*0.5),
#         type=0
#     )
# )

# Road Light
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (23.1, 6.25, 16.0),
#         (16, 16, 16),
#         (0, -1, 0),
#         120,
#         2
#     )
# )
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (24.0681, 6.16, 16),
#         (256 // 32, 220 // 32, 156 // 32,),
#     )
# )

# pyrender.Light.lights.append(
#     pyrender.Light(
#         (3, 3, 3),
#         (156 // 32, 220 // 32, 256 // 32,)
#     )
# )
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
#         type = 0
#     )
# )
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (0, 16, 0),
#         (0.01 * 4, 0.005 * 4, 0.015 * 4,),
#         (0, -1, 0),
#         type = 0
#     )
# )
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (0, 50, 0),
#         (1, 1, 1),
#         (0, -1, 0),
#         type = 0
#     )
# )

# pyrender.Light.lights.append(
#     pyrender.Light(
#         (0, 0, 0),
#         (156, 220, 256,),
#     )
# )
# pyrender.Light.lights[-1].shadow_properties = (128, 0.01, 100, 64)

pyrender.Light.lights.append(
    pyrender.Light(
        (6, 5, 2),
        (238 * 2.4, 138 * 2.4, 43 * 2.4,),
    )
)
# x=-2.6842192755654612, y=3.6094236373901367, z=4.945387839223564, yaw=304.0, pitch=-20.0, roll=0.0, width=1920, height=1080, z_near=0.05, z_far=100.0, fov=75, fxaa=False, obj_buffer=True, mode=0
pyrender.Light.lights.append(
    pyrender.Light(
        (0, 50, 0),
        (0.08, 0.06, 0.05),
        (0, -1, 0),
        shadow=False,
        type = 0
    )
)
pyrender.Light.lights.append(
    pyrender.Light(
        (0, 50, 0),
        (0.5, 0.5, 0.5),
        (0, 0, -1),
        type = 0,
        shadow=False
    )
)


from msvcrt import getwch
from time import time

def v_dot_u(v, u):
    return v[0]*u[0] + v[1]*u[1] + v[2]*u[2]
def len_v(v):
    return pyrender.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
cam = pyrender.Camera(x=-2.6842192755654612, y=3.6094236373901367, z=4.945387839223564, yaw=304.0, pitch=-20.0, roll=0.0, width=74, height=35, z_near=0.05, z_far=100.0, fov=75, fxaa=False, obj_buffer=True, mode=0)
step = 2
picked_obj = None
do_add_light = False
display_gs = False
show_y = False
aim_point = False
frame_index = -1
# 8&9 are reserved, because shift+8 is *, which will conflict with that in the numpad,
# and it's weird if only 8 is disabled so shift + 9 is also now.
keyboard_number_lookup={"!":1, "@":2, "#":3, "$":4, "%":5, "^":6, "&":7, ")":0}
from os import system
system("cls")
while True:
    frame_index += 1
    start = time()
    # PARTICLES.next_frame()

    


    # pyrender.Light.lights[-1].x = cam.x + cam.rotation[2][0] * 10 - cam.rotation[1][0] * 5
    # pyrender.Light.lights[-1].y = cam.y + cam.rotation[2][1] * 10 - cam.rotation[1][1] * 5
    # pyrender.Light.lights[-1].z = cam.z + cam.rotation[2][2] * 10 - cam.rotation[1][2] * 5
    
    # pyrender.Light.lights[0].shadow = False
    # pyrender.Light.lights[1].shadow = False
    # pyrender.Light.render_shadow(pyrender.Light.lights, pyrender.Object.objects)
    # pyrender.Light.lights[0].shadow = True
    # pyrender.Light.lights[1].shadow = True


    print("\033[F" * 900)
    frame, obj_buffer, _ = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, cam)
    # frame = PARTICLES.add_to_frame(frame, pyrender.Light.lights, cam)
    if do_add_light:
        frame = pyrender.add_lights(frame, cam, pyrender.Light.lights, True)
    if cam.fxaa:
        frame = pyrender.fxaa(frame, channel=0)
    if aim_point:
        frame[cam.height//2][cam.width//2] = (156, 220, 255)
    looking_at = obj_buffer[cam.height//2][cam.width//2] if obj_buffer != None else None
    if display_gs:
        pyrender.display_gs(frame)
    else:
        pyrender.display(frame, show_y)
    print(cam, "\t\t", pyrender.bias_scalar)
    print(f"Looking at: {looking_at}        |        Picked Object: {picked_obj.name if picked_obj!= None else 'None':{cam.width}}",)
    print(f"{1/time_elapsed if (time_elapsed:=time() - start) > 0 else 0:.3f}fps")
    
    if control.key_GL == None:
        continue
    else:
        key = control.key_GL
        control.key_GL = None
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
    if key == "w":
        # cam.x += cam.rotation[2][0] * step
        # cam.y += cam.rotation[2][1] * step
        # cam.z += cam.rotation[2][2] * step
        cam.x += pyrender.cos(cam.yaw * pyrender.pi / 180) * step * time_elapsed
        cam.z += pyrender.sin(cam.yaw * pyrender.pi / 180) * step * time_elapsed
    elif key == "W":
        # cam.x += cam.rotation[2][0] * step
        # cam.y += cam.rotation[2][1] * step
        # cam.z += cam.rotation[2][2] * step
        cam.x += pyrender.cos(cam.yaw * pyrender.pi / 180) * step * time_elapsed * 4
        cam.z += pyrender.sin(cam.yaw * pyrender.pi / 180) * step * time_elapsed * 4
    elif key == "s":
        # cam.x -= cam.rotation[2][0] * step
        # cam.y -= cam.rotation[2][1] * step
        # cam.z -= cam.rotation[2][2] * step
        cam.x -= pyrender.cos(cam.yaw * pyrender.pi / 180) * step * time_elapsed
        cam.z -= pyrender.sin(cam.yaw * pyrender.pi / 180) * step * time_elapsed
    elif key == "a":
        # cam.x -= cam.rotation[0][0] * step
        # cam.y -= cam.rotation[0][1] * step
        # cam.z -= cam.rotation[0][2] * step
        cam.x -= pyrender.cos((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
        cam.z -= pyrender.sin((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
    elif key == "d":
        # cam.x += cam.rotation[0][0] * step
        # cam.y += cam.rotation[0][1] * step
        # cam.z += cam.rotation[0][2] * step
        cam.x += pyrender.cos((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
        cam.z += pyrender.sin((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
    elif key == "c":
        # cam.x -= cam.rotation[1][0] * step
        # cam.y -= cam.rotation[1][1] * step
        # cam.z -= cam.rotation[1][2] * step
        cam.y -= step * time_elapsed
    elif key == " ":
        # cam.x += cam.rotation[1][0] * step
        # cam.y += cam.rotation[1][1] * step
        # cam.z += cam.rotation[1][2] * step
        cam.y += step * time_elapsed
    elif key == "4":
        cam.rotate(yaw = step)
    elif key == "6":
        cam.rotate(yaw = -step)
    elif key == "8":
        cam.rotate(pitch = step)
    elif key == "5":
        cam.rotate(pitch = -step)
    
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
    elif key == "t":
        if picked_obj != None:
            picked_obj.culling = not picked_obj.culling

    
    # shift + number
    elif key in "!@#$%^&)":
        cam.mode = keyboard_number_lookup[key]

    elif key == "B":
        pyrender.Light.render_shadow(pyrender.Light.lights, pyrender.Object.objects)
    

    elif key == "l":
        do_add_light = not do_add_light
    
    elif key == "x":
        aim_point = not aim_point
    
    elif key == "C":
        subprocess.run(["powershell", "Set-Clipboard", " -Value", repr(cam.stat())])

    elif key == "+":
        pyrender.bias_scalar += 0.1
    elif key == "-":
        pyrender.bias_scalar -= 0.1
    
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
                    for index, light in enumerate(pyrender.Light.lights):
                        if light.type in (0, 2) and light.shadow_map0 != None:
                            print(f"\t- {index}\t{light}")
                        elif light.type == 1 and light.shadow_map1 != None:
                            print(f"\t- {index}\t{light}")
                            

                elif len(command) == 2 and command[1].isdecimal():
                    light = pyrender.Light.lights[int(command[1])]
                    if light.type in (0, 2):
                        if light.shadow_map0 != None:
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
                                    light.shadow_map0, *light.shadow_properties[1:3]
                                )
                            )
                        else:
                            print("Shadow map No Found")
                    elif light.type == 1:
                        if light.shadow_map1 != None:
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
                                    light.shadow_map1, *light.shadow_properties[1:3]
                                )
                            )
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
                                    light.shadow_map2, *light.shadow_properties[1:3]
                                )
                            )
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
                                    light.shadow_map3, *light.shadow_properties[1:3]
                                )
                            )
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
                                    light.shadow_map4, *light.shadow_properties[1:3]
                                )
                            )
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
                                    light.shadow_map5, *light.shadow_properties[1:3]
                                )
                            )
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
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
                    control.command_mode_GL = False
                    break
            
            elif command[0] == "set-obj":
                # CodeUndone VsCode
                obj:pyrender.Object
                if len(command) >= 2:
                    for index, obj in enumerate(pyrender.Object.objects):
                        if obj.name == command[1]:
                            break
                    else:
                        if command[1] != "~":
                            print("Object No Found")
                            continue
                        obj = picked_obj
                if len(command) == 5:
                    try:
                        obj.set_position(eval(command[2]), eval(command[3]), eval(command[4]))
                    except Exception as exception:
                        print(exception)
                elif len(command) == 3:
                    if command[2] in ("h", "hidden"):
                        obj.hidden = not obj.hidden
                    elif command[2] in ("s", "shadow"):
                        obj.shadow = not obj.shadow
                    elif command[2] in ("ss", "shade_smooth"):
                        obj.shade_smooth = not obj.shade_smooth
                    elif command[2] in ("c", "culling"):
                        obj.culling = not obj.culling
                    elif command[2] in ("DELETE"):
                        del pyrender.Object.objects[index]
                elif len(command) == 4:
                    if command[2] == "t":
                        if command[3] != "DELETE":
                            obj.mtl.change_texture(command[3])
                        else:
                            obj.mtl.texture = None
                            obj.mtl.texture_path = None
                            obj.hastexture = False
                

            
            elif command[0] == "obj":
                if len(command) == 1 or len(command) == 2 and command[1] in ("--list", "l", "-l"):
                    for index, obj in enumerate(pyrender.Object.objects):
                        print(f"{index:{len(str(len(pyrender.Object.objects)))}} | {obj}")
                

            elif command[0] == "benchmark":
                if len(command) == 1:
                        frame_number = 120
                        records = []
                        for t in range(frame_number):
                            print(f"{t/frame_number:.3}% {t:{len(str(frame_number))}}/{frame_number} {'*' * (10 * t //frame_number)}{'.' * (10 * (frame_number - t) //frame_number)}",
                                  end="\n\033[F", flush=True)
                            start = time()
                            frame, obj_buffer, _ = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, cam)
                            end = time()
                            records.append(end - start)
                        records.sort(reverse=True)
                        print(f"Avg.: {frame_number/sum(records):.3f}fps {1000 * sum(records)/frame_number:.3f}ms | Mean: {1 / records[frame_number//2]}fps | Lowest: {1 / records[0]}fps")
            
            elif command[0] == "render":
                if len(command) == 1:
                    high_resolution_cam = pyrender.Camera(cam.x, cam.y, cam.z, cam.yaw, cam.pitch, cam.roll, 1280, 720, 0.01, 640, cam.fov, True, False, 0)
                    frame, _, _  = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, high_resolution_cam)
                    # frame = particles.Particles(density=10, position=(19.6, 0, 12.5), size=6).add_to_frame(frame, pyrender.Light.lights, high_resolution_cam)
                    frame = pyrender.fxaa(frame, channel=1)
                    pyrender.png.Png.write_as_bmp(frame, "rendered image.bmp")
                elif len(command) == 3 and command[1].isdecimal and command[2].isdecimal:
                    high_resolution_cam = pyrender.Camera(cam.x, cam.y, cam.z, cam.yaw, cam.pitch, cam.roll, int(command[1]), int(command[2]), 0.01, 640, cam.fov, True, False, 0)
                    frame, _, _  = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, high_resolution_cam)
                    # # frame = particles.Particles(density=10, position=(19.6, 0, 12.5), size=6).add_to_frame(frame, pyrender.Light.lights, high_resolution_cam)
                    frame = pyrender.fxaa(frame, channel=1)
                    pyrender.png.Png.write_as_bmp(frame, "rendered image.bmp")
                elif len(command) == 4 and command[1].isdecimal and command[2].isdecimal and command[3].isdecimal:
                    high_resolution_cam = pyrender.Camera(cam.x, cam.y, cam.z, cam.yaw, cam.pitch, cam.roll, int(command[1]), int(command[2]), 0.01, 640, cam.fov, True, False, int(command[3]))
                    frame, _, _  = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, high_resolution_cam)
                    # # frame = particles.Particles(density=10, position=(19.6, 0, 12.5), size=6).add_to_frame(frame, pyrender.Light.lights, high_resolution_cam)
                    frame = pyrender.fxaa(frame, channel=1)
                elif len(command) == 15:
                    high_resolution_cam = eval(f"pyrender.Camera({' '.join(command[1:])})")
                    frame, _, _  = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, high_resolution_cam)
                    # # frame = particles.Particles(density=10, position=(19.6, 0, 12.5), size=6).add_to_frame(frame, pyrender.Light.lights, high_resolution_cam)
                    if cam.fxaa:
                        frame = pyrender.fxaa(frame, channel=1)
                    pyrender.png.Png.write_as_bmp(frame, "rendered image.bmp")
            
            elif command[0] == "command":
                if len(command):
                    try:
                        exec(" ".join(command[1:]))
                    except Exception as exception:
                        print(exception)
            
            elif " ".join(command) in ("q", "quit", "exit"):
                system("cls")
                control.command_mode_GL = False
                break
            
            elif command == ["Q"]:
                exit()
