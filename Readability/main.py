from Readability.renderer_OLD import *
import png

if __name__ == "__main__":
    import os
    os.system("cls")
    Object.load_obj("Furniture", "E:\Programming\Python\Python-3D-renderer\models\Furniture")
    # Object.load_obj("monkey")
    # Object.load_obj("Crafting_table", "E:\Programming\Python\Python-3D-renderer\models\Crafting_table")
    # Object.objects[-1].calculate_smooth_shading_normals()
    # Object.objects[-1].smooth_shading = True
    # Object.objects[-1].calculate_face_normals()
    Light(-2, 3, 2, (9, 6, 6), type=1)
    # Light(-3, 0, 3, (0, 8, 18), type=1)
    # Light(0, -3, -5, (1, 4, 0.5), type=1)
    # Light(3, 0, 3, (2, 0, 0.5), type=0)
    # Light(-3, -3, -3, (1.5, 1, 1),type=0)
    # Object.load_obj("Tetrahedron")

    # exit()

    import os
    width, height = os.get_terminal_size()
    width = width // 2 - 3 
    height = height - 3
    # width, height = 40, 40
    cam = Camera(6.189, 3.412, -11.278, 120, -7.5)
    # cam = Camera(8.128, 3.999, -5.342, yaw=147, pitch=-22.5)
    # cam = Camera(6, 6, 6, yaw=-135, pitch=-35)
    # cam = Camera(-7.628, 4.950, 13.864, yaw=-60, pitch=-17.5)
    # Better use height/width because the variable will only be used in
    # deciding projecttion_matrix[1][1] where it either multiplies to
    # a value or divides a value. Multiplication, which is considered 
    # faster, uses height / width
    aspect_ratio_h_w = height / width
    projection_matrix = (
        (cam.z_near / (cam.z_near * math.tan(0.5 * cam.fov * math.pi / 180)), 0, 0, 0),
        (0, cam.z_near / (cam.z_near * math.tan(0.5 * cam.fov * math.pi / 180) * aspect_ratio_h_w), 0, 0),
        (0, 0, (cam.z_near + cam.z_far) / (cam.z_near - cam.z_far), 2 * cam.z_near * cam.z_far / (cam.z_near - cam.z_far)),
        (0, 0, -1 ,0)
    )



    from time import sleep, time
    pi = math.pi
    t = 0
    d = 5
    rounds = 5
    from msvcrt import getwch
    time_elapse = []
    avg_fps = 0
    while (-(d / (rounds * pi / 2)**4) * (t - rounds * pi / 2) ** 4 + d) >= 0:
        start = time()
        frame = render(cam, width, height, projection_matrix,
                    #    in_lines=True,
                    #    culling=False,
                       )
        time_elapse.append(1 / (time() - start))
        if len(time_elapse) == 10:
            avg_fps = round(sum(time_elapse) / 10, 1)
            time_elapse.clear()
        display(frame)
        print(cam, avg_fps, "fps")
        # cam = Camera(
        #     math.cos(t) * (-(d / (rounds * pi / 2)**4) * (t - rounds * pi / 2) ** 4 + d),
        #     t / (2 * pi) * 4 * d / rounds - d,
        #     math.sin(t) * (-(d / (rounds * pi / 2)**4) * (t - rounds * pi / 2) ** 4 + d),
        #     t / pi * 180 - 180,
        #     180 - math.asin(t / (2 * pi) * 4 / rounds - 1)/ pi * 180 - 180,
        # )
        # t += pi/32
        # sleep(1/60)

        key = getwch()
        if key == "Q":
            break

        step = 0.2
        if key == "w":
            cam.x += cam.rotation[2][0] * step
            cam.y += cam.rotation[2][1] * step
            cam.z += cam.rotation[2][2] * step
        elif key == "s":
            cam.x -= cam.rotation[2][0] * step
            cam.y -= cam.rotation[2][1] * step
            cam.z -= cam.rotation[2][2] * step
        elif key == "a" :
            cam.x -= cam.rotation[0][0] * step
            cam.y -= cam.rotation[0][1] * step
            cam.z -= cam.rotation[0][2] * step
        elif key == "d":
            cam.x += cam.rotation[0][0] * step
            cam.y += cam.rotation[0][1] * step
            cam.z += cam.rotation[0][2] * step
        elif key == " ":
            cam.x += cam.rotation[1][0] * step
            cam.y += cam.rotation[1][1] * step
            cam.z += cam.rotation[1][2] * step
        elif key == "c":
            cam.x -= cam.rotation[1][0] * step
            cam.y -= cam.rotation[1][1] * step
            cam.z -= cam.rotation[1][2] * step
        elif key == "4":
            cam.update_rotation(delta_yaw=2.5)
        elif key == "6":
            cam.update_rotation(delta_yaw=-2.5)
        elif key == "8":
            cam.update_rotation(delta_pitch=2.5)
        elif key == "5":
            cam.update_rotation(delta_pitch=-2.5)
        elif key == "C":
            cam = Camera()
        elif key == "+":
            cam.z_near += 0.1
        elif key == "-":
            cam.z_near -= 0.1
        elif key == "R":
            os.system("clr")
            width, height = os.get_terminal_size()
            width = width // 2 - 3 
            height = height - 3
            aspect_ratio_h_w = height / width
            projection_matrix = (
                (cam.z_near / (cam.z_near * math.tan(0.5 * cam.fov * math.pi / 180)), 0, 0, 0),
                (0, cam.z_near / (cam.z_near * math.tan(0.5 * cam.fov * math.pi / 180) * aspect_ratio_h_w), 0, 0),
                (0, 0, (cam.z_near + cam.z_far) / (cam.z_near - cam.z_far), 2 * cam.z_near * cam.z_far / (cam.z_near - cam.z_far)),
                (0, 0, -1 ,0)
            )
            print("\033[F"*500)
        elif key == "P":
            png.Png.write_image(frame)
        