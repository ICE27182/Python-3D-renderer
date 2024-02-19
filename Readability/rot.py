import pyrender, os
os.system("cls")
Obj = pyrender.Object
Cam = pyrender.Camera
Light = pyrender.Light
render = pyrender.render
display = pyrender.display

cam = Cam(0, 0, -15)
Light.lights.append(Light((0, 50, 0), (1, 1, 1), (0, -1, 0), type=0))
frame, _, _ = render(Obj.objects, Light.lights, cam)
display(frame)



Obj.objects = []
Obj.load_obj(Obj, "models/fox")
fox:Obj
fox = Obj.objects[0]
fox.rotate(2, 45)
fox.rotate(0, 45)

display(render(Obj.objects, Light.lights, cam)[0])




fox.rotate(0, -45)
fox.rotate(2, -45)

display(render(Obj.objects, Light.lights, cam)[0])
