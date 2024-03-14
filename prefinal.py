135, 69

import pyrender
import subprocess
# import particles
from math import sin, cos, pi, sqrt, tan
import control
from time import time


pyrender.Object.default_obj_dir = "models/Final/"



pyrender.Object.load_obj(pyrender.Object, "plane")
pyrender.Object.load_obj(pyrender.Object, "Porsche 911")
pyrender.Object.load_obj(pyrender.Object, "Scene")


for obj in pyrender.Object.objects:
    if obj.name in ("Road_light_1", "Road_light_2", "Road_light_3"):
        obj.culling = False
        obj.shadow = False
    elif obj.name in ("Appartment_shadow_wall", "Shop_shadow_wall"):
        obj.hidden = True
    elif obj.name == "Shop_top":
        obj.culling = False
    elif obj.name == "Sun":
        obj.culling = False
    elif obj.name == "Road_light_pole":
        obj.shade_smooth = True
        obj.calculate_smooth_shading_normals()
    elif obj.name == "Skybox":
        obj.no_lighting = True
    elif obj.name in ("Pedestrian_traffic_light_traffic_light_cover_1", "Pedestrian_traffic_light_traffic_light_cover_2", "Pedestrian_traffic_light_traffic_light_cover_3", "Pedestrian_traffic_light_traffic_light_cover_4"):
        obj.culling = False
    elif obj.name == "Pedestrian_traffic_light_1":
        Pedestrian_traffic_light_1 = obj
        obj.no_lighting = True
    elif obj.name == "Pedestrian_traffic_light_2":
        Pedestrian_traffic_light_2 = obj
        obj.no_lighting = True
    elif obj.name == "Pedestrian_traffic_light_3":
        Pedestrian_traffic_light_3 = obj
        obj.no_lighting = True
    elif obj.name == "Pedestrian_traffic_light_4":
        Pedestrian_traffic_light_4 = obj
        obj.no_lighting = True
    elif obj.name == "Traffic_light":
        Traffic_light = obj
        obj.no_lighting = True     
    

# Steering Wheel
cam = pyrender.Camera(x=0, y=1.75, z=-2, yaw=90.0, pitch=0.0, roll=0.0, width=119, height=60, z_near=0.05, z_far=600.0, fov=75, fxaa=False, obj_buffer=True, mode=0)
# Porsche 911
cam = pyrender.Camera(x=22.287827951426433, y=1.75, z=12.827173315035669, yaw=50.0, pitch=-10.0, roll=0.0, width=131, height=66, z_near=0.05, z_far=600.0, fov=90, fxaa=False, obj_buffer=True, mode=0)
# Starting
cam = pyrender.Camera(x=14.045889468842741, y=1.75, z=30.730934008959064, yaw=65.0, pitch=15.0, roll=0.0, width=131, height=66, z_near=0.05, z_far=600.0, fov=100, fxaa=False, obj_buffer=True, mode=0)
# Plane
cam = pyrender.Camera(x=33.25462876156318, y=3.75, z=71.92420835646186, yaw=65.0, pitch=5.0, roll=0.0, z_near=0.05, z_far=600.0, fov=100, fxaa=False, obj_buffer=True, mode=0)

# falling speed
cam.velocity = 0.0

# Sunset
pyrender.Light.lights.append(
    pyrender.Light(
        (20.0, 53.0, -48.0),
        (255 / 512, 121 / 512, 7 / 512,),
        (0, -0.5, 3**0.5*0.5),
        type=0
    )
)

# Road Light
pyrender.Light.lights.append(
    pyrender.Light(
        (23.1, 6.25, 16.0),
        (16, 16, 16),
        (0, -1, 0),
        size=120,
        type=2
    )
)

pyrender.Light.lights.append(
    pyrender.Light(
        (23.1, 6.25, 31.0),
        (16, 16, 16),
        (0, -1, 0),
        size=120,
        type=2
    )
)

pyrender.Light.lights.append(
    pyrender.Light(
        (23.1, 6.25, 46.0),
        (16, 16, 16),
        (0, -1, 0),
        size=120,
        type=2
    )
)

# Runway light
pyrender.Light.lights.append(
    pyrender.Light(
        (36, 2.1, 73.464 + 6),
        (156 / 8, 220 / 8, 255 / 8),
        (-4, 1.65, -6.0),
        size = 75,
        type=2,
        shadow=True,
    )
)
pyrender.Light.lights.append(
    pyrender.Light(
        (36, 2.1, 73.464 - 6),
        (156 / 8, 220 / 8, 255 / 8),
        (-4, 1.65, 6.0),
        size = 75,
        type=2,
        shadow=True,
    )
)



def v_dot_u(v, u):
    return v[0]*u[0] + v[1]*u[1] + v[2]*u[2]
def len_v(v):
    return sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

step = 2
picked_obj = None
do_add_light = False
show_obj_dir = False
display_gs = False
show_y = False
aim_point = False
frame_index = -1
time_elapsed = 0

vehicles = []
for obj in pyrender.Object.objects:
    if obj.name == "Plane":
        plane = obj
        plane.calculate_smooth_shading_normals()
        plane.shade_smooth = True
        vehicles.append(plane)
        plane.seat = (0.0, 1.0, -2.0)
        plane.aboard_range = ((-3.0, 3.0), (-5.0, 5.0),(-7.5, 7.5))
        plane.velocity = 0.0
        plane.v0 = plane.v[:]
        plane.vn0 = plane.vn[:]
        plane.rotate("y", -90)
        plane.set_position(32, 3, 73.464)
    elif obj.name == "Porsche_911":
        car = obj
        car.calculate_smooth_shading_normals()
        car.shade_smooth = True
        vehicles.append(car)
        car.seat = (-0.45, 1.1, 2.0)
        car.steering_wheel = (-0.45, 0.8, 2.78)
        car.aboard_range = ((-5.0, 5.0), (-5.0, 5.0),(-7.5, 7.5))
        car.velocity = 0.0
        car.acceleration = 0.0
        car.set_position(24, 0, 12)
    elif obj.name == "Steering_Wheel":
        steering_wheel = obj
        steering_wheel.z_r_max = 0
        steering_wheel.culling = False
        steering_wheel.v_o = steering_wheel.v[:]
        steering_wheel.vn_o = steering_wheel.vn[:]

vehicle_3rd = False

on_car = False
passed_slope_turning_point = False
high_torque = False

on_plane = False


pyrender.Light.render_shadow(pyrender.Light.lights, pyrender.Object.objects)

# 8&9 are reserved, because shift+8 is *, which will conflict with that in the numpad,
# and it's weird if only 8 is disabled so shift + 9 is also now.
keyboard_number_lookup={"!":1, "@":2, "#":3, "$":4, "%":5, "^":6, "&":7, ")":0}
from os import system
system("cls")
while True:
    frame_index += 1
    start = time()
    # PARTICLES.next_frame()

    # Physics
    if on_car:
        # Turning
        if car.velocity != 0 and steering_wheel.z_r != 0:
            if car.velocity > 0:
                degree = -steering_wheel.z_r * time_elapsed
            else:
                degree = steering_wheel.z_r * time_elapsed
            if degree > 90:
                degree = 90
            elif degree < -90:
                degree = -90

            car.rotate("y", degree)
            cam.rotate(yaw = degree)

            theta = -degree * pi / 180
            if car.velocity > 0:
                car.velocity -= sin(abs(theta)) * 2.5
            else:
                car.velocity += sin(abs(theta)) * 2.5
            if abs(car.velocity) < 0.05:
                car.velocity = 0
            rotation = (
                (cos(theta), 0, sin(theta),),
                (0, 1, 0,),
                (-sin(theta), 0, cos(theta),),
            )
            car.seat = (
                car.seat[0] * rotation[0][0] + car.seat[2] * rotation[0][2], 
                car.seat[1], 
                car.seat[0] * rotation[2][0] + car.seat[2] * rotation[2][2],
            )
            car.steering_wheel = (
                car.steering_wheel[0] * rotation[0][0] + car.steering_wheel[2] * rotation[0][2], 
                car.steering_wheel[1], 
                car.steering_wheel[0] * rotation[2][0] + car.steering_wheel[2] * rotation[2][2],
            )
        
        # Slope
        if 58 < car.center[2] < 60:
            if car.x_r == 0 and passed_slope_turning_point == False:
                car.rotate("x", 15)
                passed_slope_turning_point = True
            elif car.x_r == 15 and passed_slope_turning_point == False:
                car.rotate("x", -15)
                passed_slope_turning_point = True
        elif 67.464 < car.center[2] < 70:
            if car.x_r == 0 and passed_slope_turning_point == False:
                car.rotate("x", 15)
                passed_slope_turning_point = True
            elif car.x_r == 15 and passed_slope_turning_point == False:
                car.rotate("x", -15)
                passed_slope_turning_point = True
        else:
            passed_slope_turning_point = False

        # friction CodeUndone Bad Code
        car.velocity += car.acceleration * time_elapsed
        friction_a = time_elapsed * 0.25
        if car.acceleration == 0.0 and abs(car.velocity) < friction_a:
            car.velocity = 0.0
        elif car.velocity > friction_a:
            car.velocity -= friction_a
        elif car.velocity < -friction_a:
            car.velocity += friction_a

        # Moving
        if car.center[2] < 60:
            y = 0
        elif 60 <= car.center[2] <= 67.464:
            # 2 / 7.74157 = 0.25834552939520017
            y = 0.25834552939520017 * (car.center[2] - 60)
        elif car.center[2] < 67.464:
            y = 2
            
        car.set_position(
            car.center[0] + car.rotation[2][0] * car.velocity * time_elapsed,
            y,
            car.center[2] + car.rotation[2][2] * car.velocity * time_elapsed,
        )
        steering_wheel.set_position(
            car.center[0] + car.steering_wheel[0],
            y + car.steering_wheel[1],
            car.center[2] + car.steering_wheel[2],
        )
        if vehicle_3rd:
            cam.x = car.center[0] - car.rotation[2][0] * 2
            cam.y = car.center[1] + 4 - car.rotation[2][1]
            cam.z = car.center[2] - car.rotation[2][2] * 3
        else:
            cam.x = car.center[0] + car.seat[0]
            cam.y = car.center[1] + car.seat[1]
            cam.z = car.center[2] + car.seat[2]

        if high_torque and car.velocity < 2:
            car.acceleration = 10.0
        else:
            car.acceleration = 0.0

    elif on_plane:
        distance = plane.velocity * time_elapsed
        plane.set_position(
            plane.center[0] + plane.rotation[2][0] * distance,
            plane.center[1] + plane.rotation[2][1] * distance,
            plane.center[2] + plane.rotation[2][2] * distance,
        )
        if vehicle_3rd:
            cam.x = plane.center[0] - plane.rotation[2][0] * 8 + plane.rotation[1][0] * 2
            cam.y = plane.center[1] - plane.rotation[2][1] * 8 + plane.rotation[1][1] * 2
            cam.z = plane.center[2] - plane.rotation[2][2] * 8 + plane.rotation[1][2] * 2
        else:

            cam.x = plane.center[0] + plane.seat[0] * plane.rotation[0][0] + plane.seat[1] * plane.rotation[0][1] + plane.seat[2] * plane.rotation[0][2]
            cam.y = plane.center[1] + plane.seat[0] * plane.rotation[1][0] + plane.seat[1] * plane.rotation[1][1] + plane.seat[2] * plane.rotation[1][2]
            cam.z = plane.center[2] + plane.seat[0] * plane.rotation[2][0] + plane.seat[1] * plane.rotation[2][1] + plane.seat[2] * plane.rotation[2][2]
    else:
        distance = cam.velocity * time_elapsed
        if distance != 0:
            cam.y += distance
            cam.x += pyrender.cos(cam.yaw * pyrender.pi / 180) * 2 * time_elapsed
            cam.z += pyrender.sin(cam.yaw * pyrender.pi / 180) * 2 * time_elapsed

        if cam.z < 60.0 and cam.y > 1.75:
            cam.velocity -= 9.81 * time_elapsed
        elif cam.z < 60.0 and cam.y < 1.75:
            cam.velocity = 0.0
            cam.y = 1.75
        elif cam.z > 67.464 and cam.y > 3.75:
            cam.velocity -= 9.81 * time_elapsed
        elif cam.z > 67.464 and cam.y < 3.75:
            cam.velocity = 0.0
            cam.y = 3.75


    frame, obj_buffer, _ = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, cam)
    # frame = PARTICLES.add_to_frame(frame, pyrender.Light.lights, cam)
    if show_obj_dir:
        frame = pyrender.add_obj_dir(frame, cam, pyrender.Object.objects)
    if do_add_light:
        frame = pyrender.add_lights(frame, cam, pyrender.Light.lights, True)
    if cam.fxaa:
        frame = pyrender.fxaa(frame, channel=0)
    if aim_point:
        frame[cam.height//2][cam.width//2] = (156, 220, 255)
    looking_at = obj_buffer[cam.height//2][cam.width//2] if obj_buffer is not None else None
    
    print("\033[F" * 900, flush=True)
    if display_gs:
        pyrender.display_gs(frame)
    else:
        pyrender.display(frame, show_y)
    print(cam, "\t\t", pyrender.bias_scalar, flush=True)
    print(cam.rotation, " " * 50, flush=True)
    # print(f"Looking at: {looking_at}        |        Picked Object: {picked_obj.name if picked_objis not None else 'None':{cam.width}}")
    print(f"{1/time_elapsed if (time_elapsed:=time() - start) > 0 else 0:.3f}fps  Speed: {abs(car.velocity) if on_car else (abs(plane.velocity)) if on_plane else step:.3f}m/s     {steering_wheel.z_r_max}          ")
    

    if control.key_GL is None:
        x_r = steering_wheel.x_r
        y_r = steering_wheel.y_r
        steering_wheel.rotate("y", -y_r)
        steering_wheel.rotate("x", -x_r)
        if abs(steering_wheel.z_r) <= steering_wheel.z_r_max % 5:
            steering_wheel.rotate("z", -steering_wheel.z_r)
            steering_wheel.z_r_max = 0
        elif steering_wheel.z_r > 0:
            steering_wheel.rotate("z", -steering_wheel.z_r_max // 5)
        elif steering_wheel.z_r < 0:
            steering_wheel.rotate("z", steering_wheel.z_r_max // 5)
        else:
            steering_wheel.z_r_max = 0
        steering_wheel.rotate("x", x_r)
        steering_wheel.rotate("y", y_r)
        continue
    else:
        key = control.key_GL
        control.key_GL = None

    if key == "w":
        # cam.x += cam.rotation[2][0] * step
        # cam.y += cam.rotation[2][1] * step
        # cam.z += cam.rotation[2][2] * step
        if on_car:
            high_torque = False
            car.acceleration = 4.0 if car.velocity < 20.0 else 0.0
        elif on_plane:
            center = plane.center
            plane.center = [0, 0, 0]
            plane.v = plane.v0[:]
            plane.vn = plane.vn0[:]
            x_r = plane.x_r
            y_r = plane.y_r
            z_r = plane.z_r
            plane.x_r = 0
            plane.y_r = 0
            plane.z_r = 0
            plane.rotation = (
                (1, 0, 0),
                (0, 1, 0),
                (0, 0, 1)
            )
            plane.rotate("z", z_r)
            plane.rotate("x", x_r - 5)
            plane.rotate("y", y_r)
            plane.set_position(*center)
            cam.pitch = 0
            cam.roll = 0
            cam.yaw = 0
            cam.rotation = plane.rotation
        else:
            cam.x += pyrender.cos(cam.yaw * pyrender.pi / 180) * step * time_elapsed
            cam.z += pyrender.sin(cam.yaw * pyrender.pi / 180) * step * time_elapsed
    elif key == "W":
        # cam.x += cam.rotation[2][0] * step
        # cam.y += cam.rotation[2][1] * step
        # cam.z += cam.rotation[2][2] * step
        if on_car:
            high_torque = not high_torque
        elif on_plane:
            pass
        else:
            cam.x += pyrender.cos(cam.yaw * pyrender.pi / 180) * step * time_elapsed * 4
            cam.z += pyrender.sin(cam.yaw * pyrender.pi / 180) * step * time_elapsed * 4
    elif key == "s":
        # cam.x -= cam.rotation[2][0] * step
        # cam.y -= cam.rotation[2][1] * step
        # cam.z -= cam.rotation[2][2] * step
        if on_car:
            high_torque = False
            car.acceleration = -2.0 if car.velocity > -20.0 else 0.0
        elif on_plane:
            center = plane.center
            plane.center = [0, 0, 0]
            plane.v = plane.v0[:]
            plane.vn = plane.vn0[:]
            x_r = plane.x_r
            y_r = plane.y_r
            z_r = plane.z_r
            plane.x_r = 0
            plane.y_r = 0
            plane.z_r = 0
            plane.rotation = (
                (1, 0, 0),
                (0, 1, 0),
                (0, 0, 1)
            )
            plane.rotate("z", z_r)
            plane.rotate("x", x_r + 5)
            plane.rotate("y", y_r)
            plane.set_position(*center)
            cam.pitch = 0
            cam.roll = 0
            cam.yaw = 0
            cam.rotation = plane.rotation
        else:
            cam.x -= pyrender.cos(cam.yaw * pyrender.pi / 180) * step * time_elapsed
            cam.z -= pyrender.sin(cam.yaw * pyrender.pi / 180) * step * time_elapsed
    elif key == "a":
        # cam.x -= cam.rotation[0][0] * step
        # cam.y -= cam.rotation[0][1] * step
        # cam.z -= cam.rotation[0][2] * step
        if on_car:
            if abs(steering_wheel.z_r) < 180:
                steering_wheel.set_position(0, 0, 0)
                steering_wheel.v = steering_wheel.v_o[:]
                steering_wheel.vn = steering_wheel.vn_o[:]
                z_r = steering_wheel.z_r
                steering_wheel.x_r = 0
                steering_wheel.y_r = 0
                steering_wheel.z_r = 0
                steering_wheel.rotate("z", z_r - 2.5)
                steering_wheel.z_r_max = abs(steering_wheel.z_r)

                steering_wheel.rotate("x", -30)
                steering_wheel.rotate("y", car.y_r)
                
        elif on_plane:
            center = plane.center
            plane.center = [0, 0, 0]
            plane.v = plane.v0[:]
            plane.vn = plane.vn0[:]
            x_r = plane.x_r
            y_r = plane.y_r
            z_r = plane.z_r
            plane.x_r = 0
            plane.y_r = 0
            plane.z_r = 0
            plane.rotation = (
                (1, 0, 0),
                (0, 1, 0),
                (0, 0, 1)
            )
            plane.rotate("z", z_r)
            plane.rotate("x", x_r)
            plane.rotate("y", y_r + 5)
            plane.set_position(*center)
            cam.pitch = 0
            cam.roll = 0
            cam.yaw = 0
            cam.rotation = plane.rotation
        else:
            cam.x -= pyrender.cos((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
            cam.z -= pyrender.sin((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
    elif key == "d":
        # cam.x += cam.rotation[0][0] * step
        # cam.y += cam.rotation[0][1] * step
        # cam.z += cam.rotation[0][2] * step
        if on_car:
            
            if abs(steering_wheel.z_r) < 180:
                steering_wheel.set_position(0, 0, 0)
                steering_wheel.v = steering_wheel.v_o[:]
                steering_wheel.vn = steering_wheel.vn_o[:]
                z_r = steering_wheel.z_r
                steering_wheel.x_r = 0
                steering_wheel.y_r = 0
                steering_wheel.z_r = 0
                steering_wheel.rotate("z", z_r + 2.5)
                steering_wheel.z_r_max = abs(steering_wheel.z_r)

                steering_wheel.rotate("x", -30)
                steering_wheel.rotate("y", car.y_r)
        elif on_plane:
            center = plane.center
            plane.center = [0, 0, 0]
            plane.v = plane.v0[:]
            plane.vn = plane.vn0[:]
            x_r = plane.x_r
            y_r = plane.y_r
            z_r = plane.z_r
            plane.x_r = 0
            plane.y_r = 0
            plane.z_r = 0
            plane.rotation = (
                (1, 0, 0),
                (0, 1, 0),
                (0, 0, 1)
            )
            plane.rotate("z", z_r)
            plane.rotate("x", x_r)
            plane.rotate("y", y_r - 5)
            plane.set_position(*center)
            cam.pitch = 0
            cam.roll = 0
            cam.yaw = 0
            cam.rotation = plane.rotation

            
        else:
            cam.x += pyrender.cos((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
            cam.z += pyrender.sin((cam.yaw - 90) * pyrender.pi / 180) * step * time_elapsed
    
    elif key == "q" and on_plane:
        center = plane.center
        plane.center = [0, 0, 0]
        plane.v = plane.v0[:]
        plane.vn = plane.vn0[:]
        x_r = plane.x_r
        y_r = plane.y_r
        z_r = plane.z_r
        plane.x_r = 0
        plane.y_r = 0
        plane.z_r = 0
        plane.rotation = (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)
        )
        plane.rotate("z", z_r - 5)
        plane.rotate("x", x_r)
        plane.rotate("y", y_r)
        plane.set_position(*center)
        cam.pitch = 0
        cam.roll = 0
        cam.yaw = 0
        cam.rotation = plane.rotation

    elif key == "e" and on_plane:
        center = plane.center
        plane.center = [0, 0, 0]
        plane.v = plane.v0[:]
        plane.vn = plane.vn0[:]
        x_r = plane.x_r
        y_r = plane.y_r
        z_r = plane.z_r
        plane.x_r = 0
        plane.y_r = 0
        plane.z_r = 0
        plane.rotation = (
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)
        )
        plane.rotate("z", z_r + 5)
        plane.rotate("x", x_r)
        plane.rotate("y", y_r)
        plane.set_position(*center)
        cam.pitch = 0
        cam.roll = 0
        cam.yaw = 0
        cam.rotation = plane.rotation
    
    
    elif key == "c":
        # cam.x -= cam.rotation[1][0] * step
        # cam.y -= cam.rotation[1][1] * step
        # cam.z -= cam.rotation[1][2] * step
        if on_plane:
            delta_v = 5 * time_elapsed
            if plane.velocity <= delta_v:
                plane.velocity = 0
            else:
                plane.velocity -= delta_v
        elif not on_car:
            cam.y -= step * time_elapsed
    elif key == " ":
        # cam.x += cam.rotation[1][0] * step
        # cam.y += cam.rotation[1][1] * step
        # cam.z += cam.rotation[1][2] * step
        if on_car and car.velocity != 0:
            brake_a = time_elapsed * 10.0
            if car.acceleration == 0.0 and abs(car.velocity) < brake_a:
                car.velocity = 0.0
            elif car.velocity > brake_a:
                car.velocity -= brake_a
            elif car.velocity < -brake_a:
                car.velocity += brake_a
        elif on_plane:
            plane.velocity += 5 * time_elapsed if plane.velocity < 100 else 0
        else:
            cam.velocity = 4.85
    elif key == "4":
        cam.rotate(yaw = step * 2.5)
    elif key == "6":
        cam.rotate(yaw = -step * 2.5)
    elif key == "8":
        cam.rotate(pitch = step * 2.5)
    elif key == "5":
        cam.rotate(pitch = -step * 2.5)
    elif key == "7":
        cam.rotate(roll = -step * 2.5)
    elif key == "9":
        cam.rotate(roll = step * 2.5)
    
    elif key == "+":
        cam.fov -= 5 if cam.fov > 10 else 0
        cam.rendering_plane_z = cam.width * 0.5 / tan(cam.fov * pi / 360)
    elif key == "-":
        cam.fov += 5 if cam.fov < 170 else 0
        cam.rendering_plane_z = cam.width * 0.5 / tan(cam.fov * pi / 360)
    elif key == "*":
        cam.fov = 100
        cam.rendering_plane_z = cam.rendering_plane_z = cam.width * 0.5 / tan(cam.fov * pi / 360)

    elif key == "f":
        # Get off
        if on_car or on_plane:
            on_car, on_plane = False, False
            cam.x -= 1
            cam.y = -1
            car.velocity = 0
            car.acceleration = 0
            vehicle_3rd = False
            continue
        # Get in/on
        for vehicle in vehicles:
            if (
                vehicle.aboard_range[0][0] < cam.x - vehicle.center[0] < vehicle.aboard_range[0][1] and
                vehicle.aboard_range[1][0] < cam.y - vehicle.center[1] < vehicle.aboard_range[1][1] and
                vehicle.aboard_range[2][0] < cam.z - vehicle.center[2] < vehicle.aboard_range[2][1] and
                not on_car and not on_plane):
                if vehicle.name == "Porsche_911":
                    on_car = True
                    cam.x = car.center[0] + car.seat[0]
                    cam.y = car.center[1] + car.seat[1]
                    cam.z = car.center[2] + car.seat[2]
                    cam.yaw = 90
                    cam.pitch = 0
                    cam.rotation = car.rotation
                elif vehicle.name == "Plane":
                    on_plane = True
                    cam.x = plane.center[0] + plane.seat[0]
                    cam.y = plane.center[1] + plane.seat[1]
                    cam.z = plane.center[2] + plane.seat[2]
                    cam.yaw = 0
                    cam.pitch = 0
                    cam.rotation = plane.rotation
    
    elif key == "v":
        if on_plane or on_car:
            vehicle_3rd = not vehicle_3rd
            cam.pitch = 0
            cam.rotate(pitch=-30)

    elif key == "F":
        cam.fxaa = not cam.fxaa
    
    elif key == "r":
        cam.width, cam.height = cam.get_width_and_height(height_reserved=6)
        w, h = cam.get_width_and_height()
        w += 3
        h += 3
        # frame = [[(0, 0, 0)] * w for _ in range(h)]
        pyrender.display(frame)
        system("cls")
        cam.rendering_plane_z = cam.width * 0.5 / pyrender.tan(cam.fov * pyrender.pi / 360)
    
    elif key == "P":
        pyrender.png.Png.write_as_bmp(frame, "screenshot.bmp")
    
    elif key == "\r":
        picked_obj = obj_buffer[cam.height//2][cam.width//2] if obj_buffer is not None else None

    elif key == "h":
        if picked_obj is not None:
            picked_obj.hidden = not picked_obj.hidden
    elif key == "H":
        for obj in pyrender.Object.objects:
            obj.hidden = False
    elif key in "uiojkl":
        # CodeUndone VsCode
        picked_obj:pyrender.Object
        if picked_obj is None:
            continue
        if key == "i":
            picked_obj.rotate("x", -5)
        elif key == "k":
            picked_obj.rotate("x", 5)
        if key == "l":
            picked_obj.rotate("y", -5)
        elif key == "j":
            picked_obj.rotate("y", 5)
        if key == "o":
            picked_obj.rotate("z", -5)
        elif key == "u":
            picked_obj.rotate("z", 5)
    
    # shift + number
    elif key in "!@#$%^&)":
        cam.mode = keyboard_number_lookup[key]
    
    elif key == "T":
        Pedestrian_traffic_light_1.mtl, Pedestrian_traffic_light_2.mtl = Pedestrian_traffic_light_2.mtl, Pedestrian_traffic_light_1.mtl
        Pedestrian_traffic_light_3.mtl, Pedestrian_traffic_light_4.mtl = Pedestrian_traffic_light_4.mtl, Pedestrian_traffic_light_3.mtl
        for index in range(len(Traffic_light.vt)):
            Traffic_light.vt[index] = (Traffic_light.vt[index][0], Traffic_light.vt[index][1] + 0.5)

    elif key == "B":
        pyrender.Light.render_shadow(pyrender.Light.lights, pyrender.Object.objects)
    
    elif key == "L":
        do_add_light = not do_add_light
    elif key == "O":
        show_obj_dir = not show_obj_dir
    
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
                        if light.type in (0, 2) and light.shadow_map0 is not None:
                            print(f"\t- {index}\t{light}")
                        elif light.type == 1 and light.shadow_map1 is not None:
                            print(f"\t- {index}\t{light}")
                            

                elif len(command) == 2 and command[1].isdecimal():
                    light = pyrender.Light.lights[int(command[1])]
                    if light.type in (0, 2):
                        if light.shadow_map0 is not None:
                            pyrender.display(
                                pyrender.convert_depth_to_frame(
                                    light.shadow_map0, *light.shadow_properties[1:3]
                                )
                            )
                        else:
                            print("Shadow map No Found")
                    elif light.type == 1:
                        if light.shadow_map1 is not None:
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
        
