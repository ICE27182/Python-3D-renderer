import pyrender
pyrender.Object.default_obj_dir = "models/"
pyrender.Object.load_obj(pyrender.Object, "sphere")
pyrender.Object.objects[-1].calculate_face_normals()
pyrender.Object.objects[-1].calculate_smooth_shading_normals()
cam = pyrender.Camera(x=0.0, y = 1.8, z=-2.0, mode=1, 
                    #   width=74, height=37,
                      )
frame, _ = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, cam)
pyrender.display(frame)

pyrender.Light.lights.append(
    pyrender.Light(
        (3, 3, 3),
        (1, 1, 1)
    )
)
# pyrender.Light.lights.append(
#     pyrender.Light(
#         (3, 3, 3),
#         (1, 1, 1),
#         (-1, -1, -1),
#         0
#     )
# )

from msvcrt import getwch
step = 0.2
while True:
    print("\033[F" * 300)
    frame, _ = pyrender.render(pyrender.Object.objects, pyrender.Light.lights, cam)
    pyrender.display(frame)
    print(cam)
    
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
        cam.rotate(yaw = step * 50)
    elif key == "6":
        cam.rotate(yaw = step * -50)
    elif key == "8":
        cam.rotate(pitch = step * 50)
    elif key == "5":
        cam.rotate(pitch = step * -50)

    elif key == "Q":
        break
