

def gunshot():
    def sound():
        import winsound
        winsound.PlaySound("example\\pa.wav", winsound.SND_FILENAME)
        shot[0] = False
    import threading

    threading.Thread(target=sound, daemon=True).start()



def muzzle_flash():
    meshes["Flash"].move_mesh((cam[0] + gun_position[aiming][0] * cam[5][0][0] + (gun_position[aiming][1] + 0.01) * cam[5][1][0] + (gun_position[aiming][2] + 0.35) * cam[5][2][0],
                                cam[1] + gun_position[aiming][0] * cam[5][0][1] + (gun_position[aiming][1] + 0.01) * cam[5][1][1] + (gun_position[aiming][2] + 0.35) * cam[5][2][1], 
                                cam[2] + gun_position[aiming][0] * cam[5][0][2] + (gun_position[aiming][1] + 0.01) * cam[5][1][2] + (gun_position[aiming][2] + 0.35) * cam[5][2][2]))
    for face in meshes["Flash"].f:
        # Get the three coordinates
        tri = [meshes["Flash"].v[face[0][0]], meshes["Flash"].v[face[0][1]], meshes["Flash"].v[face[0][2]]]

        # culling
        normal = meshes["Flash"].vn[face[-1]]
        cam_to_plane = (cam[0] - tri[0][0], cam[1] - tri[0][1], cam[2] - tri[0][2])
        # Dot product value and culling setting determine if faces not facing the camera should be rendered
        if culling and (normal[0] * cam_to_plane[0] + normal[1] * cam_to_plane[1] + normal[2] * cam_to_plane[2]) <= 0:
            continue

        # Change the coordinate system
        # Here the same points would be calculated several times as different faces may contain the same points
        # Will try to store them and see if it improve performance later
        # I don't use function here for the sake of performace
        tri[0] = [tri[0][0] - cam[0], tri[0][1] - cam[1], tri[0][2] - cam[2]]
        tri[1] = [tri[1][0] - cam[0], tri[1][1] - cam[1], tri[1][2] - cam[2]]
        tri[2] = [tri[2][0] - cam[0], tri[2][1] - cam[1], tri[2][2] - cam[2]]
        tri[0] = [cam[5][0][0] * tri[0][0] + cam[5][0][1] * tri[0][1] + cam[5][0][2] * tri[0][2],
                    cam[5][1][0] * tri[0][0] + cam[5][1][1] * tri[0][1] + cam[5][1][2] * tri[0][2],
                    cam[5][2][0] * tri[0][0] + cam[5][2][1] * tri[0][1] + cam[5][2][2] * tri[0][2]]
        tri[1] = [cam[5][0][0] * tri[1][0] + cam[5][0][1] * tri[1][1] + cam[5][0][2] * tri[1][2],
                    cam[5][1][0] * tri[1][0] + cam[5][1][1] * tri[1][1] + cam[5][1][2] * tri[1][2],
                    cam[5][2][0] * tri[1][0] + cam[5][2][1] * tri[1][1] + cam[5][2][2] * tri[1][2]]
        tri[2] = [cam[5][0][0] * tri[2][0] + cam[5][0][1] * tri[2][1] + cam[5][0][2] * tri[2][2],
                    cam[5][1][0] * tri[2][0] + cam[5][1][1] * tri[2][1] + cam[5][1][2] * tri[2][2],
                    cam[5][2][0] * tri[2][0] + cam[5][2][1] * tri[2][1] + cam[5][2][2] * tri[2][2]]
        # Projection
        tri[0] = [display.projection_matrix[0][0] * tri[0][0] + display.projection_matrix[0][1] * tri[0][1] + display.projection_matrix[0][2] * tri[0][2] + display.projection_matrix[0][3],
                  display.projection_matrix[1][0] * tri[0][0] + display.projection_matrix[1][1] * tri[0][1] + display.projection_matrix[1][2] * tri[0][2] + display.projection_matrix[1][3],
                  display.projection_matrix[2][0] * tri[0][0] + display.projection_matrix[2][1] * tri[0][1] + display.projection_matrix[2][2] * tri[0][2] + display.projection_matrix[2][3],
                  display.projection_matrix[3][0] * tri[0][0] + display.projection_matrix[3][1] * tri[0][1] + display.projection_matrix[3][2] * tri[0][2] + display.projection_matrix[3][3]]
        tri[1] = [display.projection_matrix[0][0] * tri[1][0] + display.projection_matrix[0][1] * tri[1][1] + display.projection_matrix[0][2] * tri[1][2] + display.projection_matrix[0][3],
                  display.projection_matrix[1][0] * tri[1][0] + display.projection_matrix[1][1] * tri[1][1] + display.projection_matrix[1][2] * tri[1][2] + display.projection_matrix[1][3],
                  display.projection_matrix[2][0] * tri[1][0] + display.projection_matrix[2][1] * tri[1][1] + display.projection_matrix[2][2] * tri[1][2] + display.projection_matrix[2][3],
                  display.projection_matrix[3][0] * tri[1][0] + display.projection_matrix[3][1] * tri[1][1] + display.projection_matrix[3][2] * tri[1][2] + display.projection_matrix[3][3]]
        tri[2] = [display.projection_matrix[0][0] * tri[2][0] + display.projection_matrix[0][1] * tri[2][1] + display.projection_matrix[0][2] * tri[2][2] + display.projection_matrix[0][3],
                  display.projection_matrix[1][0] * tri[2][0] + display.projection_matrix[1][1] * tri[2][1] + display.projection_matrix[1][2] * tri[2][2] + display.projection_matrix[1][3],
                  display.projection_matrix[2][0] * tri[2][0] + display.projection_matrix[2][1] * tri[2][1] + display.projection_matrix[2][2] * tri[2][2] + display.projection_matrix[2][3],
                  display.projection_matrix[3][0] * tri[2][0] + display.projection_matrix[3][1] * tri[2][1] + display.projection_matrix[3][2] * tri[2][2] + display.projection_matrix[3][3]]
        tri[0] = [tri[0][0] / tri[0][3], tri[0][1] / tri[0][3], tri[0][2] / tri[0][3], tri[0][3]]
        tri[1] = [tri[1][0] / tri[1][3], tri[1][1] / tri[1][3], tri[1][2] / tri[1][3], tri[1][3]]
        tri[2] = [tri[2][0] / tri[2][3], tri[2][1] / tri[2][3], tri[2][2] / tri[2][3], tri[2][3]]
        tri[0][0] = (tri[0][0] + 1) * 0.5 * display.width
        tri[1][0] = (tri[1][0] + 1) * 0.5 * display.width
        tri[2][0] = (tri[2][0] + 1) * 0.5 * display.width
        tri[0][1] = (tri[0][1] + 1) * 0.5 * display.height
        tri[1][1] = (tri[1][1] + 1) * 0.5 * display.height
        tri[2][1] = (tri[2][1] + 1) * 0.5 * display.height
        v = (tri[0][0] - tri[1][0] , tri[0][1] - tri[1][1], tri[0][2] - tri[1][2])
        u = (tri[2][0] - tri[1][0] , tri[2][1] - tri[1][1], tri[2][2] - tri[1][2])
        normal = [v[1] * u[2] - v[2] * u[1],
                    v[2] * u[0] - v[0] * u[2],
                    v[0] * u[1] - v[1] * u[0]]
        for y in range(int(max(0, min(tri[0][1], tri[1][1], tri[2][1]))), int(min(display.height, max(tri[0][1], tri[1][1], tri[2][1]) + 1))):
            for x in range(int(max(0, min(tri[0][0], tri[1][0], tri[2][0]))), int(min(display.width, max(tri[0][0], tri[1][0], tri[2][0]) + 1))):
                z = tri[0][2] - (normal[0] * (x - tri[0][0]) + normal[1] * (y - tri[0][1])) / normal[2]
                if z >= rdr.z_buffer[y][x][0]:
                    vec1 = (tri[0][0] - x, tri[0][1] - y)
                    vec2 = (tri[1][0] - x, tri[1][1] - y)
                    vec3 = (tri[2][0] - x, tri[2][1] - y)
                    cp23 = vec2[0] * vec3[1] -  vec2[1] * vec3[0]
                    if (vec1[0] * vec2[1] -  vec1[1] * vec2[0]) * cp23 > 0 and cp23 * (vec3[0] * vec1[1] -  vec3[1] * vec1[0]) > 0:
                        display.frame[y][x] = f"\033[38;2;{randint(191, 255)};{randint(95, 159)};{randint(0, 31)}m██\033[0m"
                        rdr.z_buffer[y][x] = (z, "Flash")
                
    

import renderer as rdr
meshes = {}
meshes.update(rdr.Mesh.load_obj("example\\gun.obj", meshes))
meshes.update(rdr.Mesh.load_obj("example\\flash.obj", meshes))
meshes.update(rdr.Mesh.load_obj("example\\field.obj", meshes))
meshes.update(rdr.Mesh.load_obj("example\\enemy.obj", meshes))
meshes["Enemy"].move_mesh((-6.370, 0.5, 6.235))
meshes["Enemy"].facing = 0
meshes.update(rdr.Mesh.load_obj("example\\enemy.obj", meshes))
meshes["Enemy_2"].move_mesh((-6.110, 0.5, -7.854))
meshes["Enemy_2"].facing = 0
meshes.update(rdr.Mesh.load_obj("example\\enemy.obj", meshes))
meshes["Enemy_3"].move_mesh((0, 0.5, 0))
meshes["Enemy_3"].facing = 0

culling, faces, edges = True, True, False
global shot
shot = [False, False]
flash_frames_left = 0
gun_position = {False:(0.1, -0.05, 0.3), True:(0, -0.023, 0.3)}
aiming = False
fgt = 0
velocity = 0

display = rdr.Display(bottom_bar_height=3)
step = 0.3
cam = [-2.088, 1.700, -11.507, 136 ,-12]
cam = [-22.751, 1.700, -24.371, 40, 0]
cam.append(rdr.calculate_camera_matrix(cam))
meshes["Pistol"].rotate_mesh(y_degree = 180 - cam[3])
meshes["Pistol"].rotate_mesh(x_degree = (-cam[4] - 2) * cam[5][0][0], z_degree = (-cam[4] - 2) * cam[5][0][2], )
meshes["Flash"].rotate_mesh(y_degree = 180 - cam[3])
meshes["Flash"].rotate_mesh(x_degree = (-cam[4] - 2) * cam[5][0][0], z_degree = (-cam[4] - 2) * cam[5][0][2], )


rdr.keyinput()

from time import time, sleep
start_time = time()

from random import randint
from copy import deepcopy
import math

while rdr.key != "Q":

    if not rdr.pause:
        cam[1] -= velocity * fgt
        velocity += 9.81 * fgt
        if -5 <= cam[0] <= 25 and -25 <= cam[2] <= -15 and cam[1] <= 2.5:
            cam[1] = 2.5
            velocity = 0
        elif -25 <= cam[0] <= 25 and -25 <= cam[2] <= 25 and cam[1] <= 1.7:
            cam[1] = 1.7
            velocity = 0
        
        for enemy in meshes.values():
            if "Enemy" not in enemy.name:
                continue
            if sum([(cam[index] - enemy.center[index])**2 for index in (0, 1, 2)]) <= 64:
                vec = (cam[0] - enemy.center[0], cam[2] - enemy.center[2])
                if vec[0] != 0:
                    theta = math.atan(vec[1]/vec[0]) * 180 / math.pi if vec[0] > 0 else math.atan(vec[1]/vec[0]) * 180 / math.pi - 180
                else:
                    theta = 90 * vec[1] / abs(vec[1]) if vec[1] != 0 else 0
                enemy.rotate_mesh(y_degree = enemy.facing - theta)
                enemy.facing = theta
                length = math.sqrt(vec[0]**2 + vec[1]**2)
                vec = (vec[0]/length, vec[1]/length) if length != 0 else (0, 0)
                enemy.move_mesh([enemy.center[0] + fgt * vec[0], enemy.center[1], enemy.center[2] + fgt * vec[1]])

    meshes["Pistol"].move_mesh((cam[0] + gun_position[aiming][0] * cam[5][0][0] + gun_position[aiming][1] * cam[5][1][0] + gun_position[aiming][2] * cam[5][2][0],
                                cam[1] + gun_position[aiming][0] * cam[5][0][1] + gun_position[aiming][1] * cam[5][1][1] + gun_position[aiming][2] * cam[5][2][1], 
                                cam[2] + gun_position[aiming][0] * cam[5][0][2] + gun_position[aiming][1] * cam[5][1][2] + gun_position[aiming][2] * cam[5][2][2]))
    display.new_frame()

    rdr.render(meshes, display, cam, culling=culling, faces=faces, edges=edges, 
               hidden=("Flash",)
               )
    if flash_frames_left > 0:
        muzzle_flash()
        flash_frames_left -= 1
    
    display.frame[display.height//2][display.width//2] = "\033[31;1m██\033[0m"

    display.bottom_bar_info = f"Resolution: {display.width} x {display.height}    " +\
                              f"Frame Generation Time: {(fgt:=time()-start_time):.3f}s {1/fgt if fgt != 0 else -1:.3f}fps        " +\
                              f"\nCamera(x y z): {cam[0]:.3f}, {cam[1]:.3f}, {cam[2]:.3f}  {(sum([val**2 for val in cam[:3]]))**0.5:.3f}    " +\
                              f"Looking Direction: horizontal~{(cam[3] + 180) % 360 - 180:.3f}° vertical~{cam[4]:.3f}        " +\
                              f"\n{sum([len(mesh.f) for mesh in meshes.values()])} Triangles"

    start_time = time()
    sleep(max(0, 1 / 25 - fgt))
    display.draw()

    # rdr.key_control(cam, display, step)
    if flash_frames_left == 1:
            meshes["Pistol"].v = deepcopy(pistol_v)
            meshes["Pistol"].get_normal()
            shot[1] = False

    if rdr.key != None:
        if rdr.key == "r":
            display.refresh()
            rdr.key = None
        elif rdr.key == "w":
            movement = [val * step for val in cam[5][2]]
            movement = [step * math.cos(cam[3] * math.pi / 180), 0, step * math.sin(cam[3] * math.pi / 180)]
            cam[:3] = [cam[:3][index] + movement[index] for index in (0, 1, 2)]
            rdr.key = None
        elif rdr.key == "a":
            movement = [val * step for val in cam[5][0]]
            cam[:3] = [cam[:3][index] - movement[index] for index in (0, 1, 2)]
            rdr.key = None
        elif rdr.key == "s":
            movement = [val * step for val in cam[5][2]]
            movement = [step * math.cos(cam[3] * math.pi / 180), 0, step * math.sin(cam[3] * math.pi / 180)]
            cam[:3] = [cam[:3][index] - movement[index] for index in (0, 1, 2)]
            meshes["Pistol"].get_normal()
            rdr.key = None
        elif rdr.key == "d":
            movement = [val * step for val in cam[5][0]]
            cam[:3] = [cam[:3][index] + movement[index] for index in (0, 1, 2)]
            meshes["Pistol"].get_normal()
            rdr.key = None
        elif rdr.key == " ":
            if velocity == 0:
                velocity -= 5
            # cam[1] += step
            # meshes["Pistol"].move_mesh((cam[0] + gun_position[aiming][0] * cam[5][0][0] + gun_position[aiming][1] * cam[5][1][0] + gun_position[aiming][2] * cam[5][2][0],
            #                             cam[1] + gun_position[aiming][0] * cam[5][0][1] + gun_position[aiming][1] * cam[5][1][1] + gun_position[aiming][2] * cam[5][2][1], 
            #                             cam[2] + gun_position[aiming][0] * cam[5][0][2] + gun_position[aiming][1] * cam[5][1][2] + gun_position[aiming][2] * cam[5][2][2]))
            rdr.key = None
        elif rdr.key == "8":
            if cam[4] <= 88:
                cam[4] += 2
                cam[5] = rdr.calculate_camera_matrix(cam)

                meshes["Pistol"].rotate_mesh(x_degree = -2 * cam[5][0][0], z_degree = -2 * cam[5][0][2],)
                meshes["Flash"].rotate_mesh(x_degree = -2 * cam[5][0][0], z_degree = -2 * cam[5][0][2],)
            rdr.key = None
        elif rdr.key == "2":
            if cam[4] >= -88:
                cam[4] -= 2
                cam[4] = max(-90, min(90, cam[4]))
                cam[5] = rdr.calculate_camera_matrix(cam)

                meshes["Pistol"].rotate_mesh(x_degree = 2 * cam[5][0][0], z_degree = 2 * cam[5][0][2],)
                meshes["Flash"].rotate_mesh(x_degree = 2 * cam[5][0][0], z_degree = 2 * cam[5][0][2],)
            rdr.key = None
        elif rdr.key == "4":
            cam[3] += 4
            cam[5] = rdr.calculate_camera_matrix(cam)
            meshes["Pistol"].rotate_mesh(y_degree = -4,)
            meshes["Flash"].rotate_mesh(y_degree = -4,)
            rdr.key = None
        elif rdr.key == "6":
            cam[3] -= 4
            cam[5] = rdr.calculate_camera_matrix(cam)
            meshes["Pistol"].rotate_mesh(y_degree = 4,)
            meshes["Flash"].rotate_mesh(y_degree = 4)
            rdr.key = None
        elif rdr.key == "7":
            display.fov += 1
            tan_half_fov = display.fov_trans(display.fov)
            display.projection_matrix = ((-display.height / display.width / tan_half_fov, 0, 0, 0),
                                            (0, 1 / tan_half_fov, 0, 0),
                                            (0, 0, -(display.z_far+display.z_near)/(display.z_far-display.z_near), -display.z_near * display.z_far/(display.z_far-display.z_near)),
                                            (0, 0, -1, 0),)
            rdr.key = None
        elif rdr.key == "9":
            display.fov -= 1
            tan_half_fov = display.fov_trans(display.fov)
            display.projection_matrix = ((-display.height / display.width / tan_half_fov, 0, 0, 0),
                                            (0, 1 / tan_half_fov, 0, 0),
                                            (0, 0, -(display.z_far+display.z_near)/(display.z_far-display.z_near), -display.z_near * display.z_far/(display.z_far-display.z_near)),
                                            (0, 0, -1, 0),)
            rdr.key = None
        elif rdr.key == "5":
            display.fov = 40
            tan_half_fov = display.fov_trans(display.fov)
            display.projection_matrix = ((-display.height / display.width / tan_half_fov, 0, 0, 0),
                                            (0, 1 / tan_half_fov, 0, 0),
                                            (0, 0, -(display.z_far+display.z_near)/(display.z_far-display.z_near), -display.z_near * display.z_far/(display.z_far-display.z_near)),
                                            (0, 0, -1, 0),)
            rdr.key = None
        elif rdr.key == "\r":
            if shot == [False, False]:
                shot = [True, True]
                pistol_v = deepcopy(meshes["Pistol"].v)
                meshes["Pistol"].rotate_mesh(x_degree = -10 * cam[5][0][0], z_degree = -10 * cam[5][0][2])
                gunshot()
                if rdr.z_buffer[display.height//2][display.width//2][1] in ("Enemy", "Enemy_2", "Enemy_3"):
                    meshes.pop(rdr.z_buffer[display.height//2][display.width//2][1])
                flash_frames_left = 5
            rdr.key = None
        elif rdr.key == "e":
            aiming = not aiming
            if aiming:
                meshes["Pistol"].rotate_mesh(x_degree = 2 * cam[5][0][0], z_degree = 2 * cam[5][0][2],)
            else:
                meshes["Pistol"].rotate_mesh(x_degree = -2 * cam[5][0][0], z_degree = -2 * cam[5][0][2],)
            
            rdr.key = None
    
        