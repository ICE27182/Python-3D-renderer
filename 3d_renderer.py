

class Mesh:
    def __init__(self, faces) -> None:
        self.faces = faces
        pass


    def obj_loader(file):
        def parser(obj:str):
            obj:list = obj.split("\n")
            output = {"f":[]}
            # s:int = obj.index("s 0")
            s = next((index for index, item in enumerate(obj) if item.startswith("s ")))
            for item in obj[1: s]:
                item = item.split()
                if item[0] in output:
                    output[item[0]].append([float(value) for value in item[1:]])
                elif item[0] != "usemtl":
                    output[item[0]] = [[float(value) for value in item[1:]]]
            face_index = next((index for index, item in enumerate(obj[s + 1:], s + 1) if item.startswith("f")))
            for item in obj[face_index:]:
                # item = list(zip(*[list(map(int, value.split("/"))) for value in item[2:].split()]))
                # output["f"].append(item[:-1]+[item[-1][0]])
                try:
                    item = [list(map(int, value.split("/"))) for value in item[2:].split()]
                except ValueError:
                    item = [list(map(int, value.split("//"))) for value in item[2:].split()]
                output["f"].append([[value[0] for value in item], [value[1] for value in item], item[0][-1]])
            return obj[0][1:], output



        output = {}
        with open(file, "r") as model:
            model:str = model.read()
        while model[-1] == "\n":
            model = model[:-1]
        mesh_num = model.count("\no")
        print(f"{mesh_num} {'meshes have' if mesh_num > 1 else 'mesh has'} been found in {file}.")
        model = model.split("\no")[1:]
        for mesh in model:
            name, data = parser(mesh)
            output[name] = data
        return output
    

    def add_to_meshes(meshes, new):
        """new - dict {<name>:{"f":[...], "v":[...], ...}}"""
        for new_mesh in new:
            if new_mesh in meshes:
                num = 2
                while f"{new_mesh}_{num}" in meshes:
                    num += 1
                meshes[f"{new_mesh}_{num}"] = new[new_mesh]
                print(f"\"{new_mesh}\" -> \"{new_mesh}_{num}\" has been added. "
                      +"There's a name conflict so its name is changed")
            else:
                meshes[new_mesh] = new[new_mesh]
                print(f"\"{new_mesh}\" has been added. ")
        return meshes




class Rendering:
    def render(meshes:dict, fov, z_near, z_far, width, height, w=1):
        def mat4x4_x_vec4(mat, vec):
            if len(mat) != 4 or len(mat[0]) != 4 or len(mat[1]) != 4 or len(mat[2]) != 4 or len(mat[3]) != 4 or len(vec) != 4:
                raise Exception
            return [sum(m * v for m, v in zip(mat[row], vec)) for row in range(4)]
        tan_half_fov = math.tan(fov / 360 * math.pi)
        projection_matrix = [
            [-height / width / tan_half_fov,     0,                  0,                      0],
            [0,                                 1 / tan_half_fov,   0,                      0],
            [0,                                 0,                  -(z_far+z_near)/(z_far-z_near),   -z_near * z_far/(z_far-z_near)],
            [0,                                 0,                  -1,                     0],
                            ]
        for name,mesh in meshes.items():
            meshes[name]["projected_v"] = []
            for x, y, z, _ in mesh["v"]:

                # Temp
                # x, y, z, w = rotation((x, y, z, w), theta)
                z += -cam[2]

                coor = mat4x4_x_vec4(projection_matrix, [x, y, z, w])
                coor = [coor[0] / coor[3], coor[1] / coor[3], coor[2] / coor[3], coor[3]]
                coor[0] = (coor[0] + 1) * 0.5 * width
                coor[1] = (coor[1] + 1) * 0.5 * height
                meshes[name]["projected_v"].append(coor)
        return meshes
    



class Display:
    def __init__(self, size=None, bottom_bar=0) -> None:
        from shutil import get_terminal_size
        self.get_terminal_size = get_terminal_size
        Display.get_screen_size(self, size, bottom_bar)
        self.frame = {y:{x:"  " for x in range(self.width)} for y in range(self.height)}


    def get_screen_size(self, size=None, bottom_bar=0):
        """size - None/tuple (int, int)/list [int, int]
           bottom_bar - int - bottom_bar >= 0"""
        if size == None:
            w, h = self.get_terminal_size()
            # When printing a really long and complex string, bug character may appear from nowhere
            # so -3 in case such thing happens
            w = w // 2 - 3
            h = h - 3 - bottom_bar
        elif size[0] == None:
            w, _ = self.get_terminal_size()
            w = w // 2 - 3
            h = size[1] - 3 - bottom_bar
        elif size[1] == None:
            _, h = self.get_terminal_size()
            w = size[0] // 2 - 3
            h = h - 3 - bottom_bar
        self.width, self.height = w, h
    

    def new_frame(self):
        print("\033[F" * (self.height * 10))
        self.frame = {y:{x:"  " for x in range(self.width)} for y in range(self.height)}
    

    def add_triangle_edges(self, meshes, color="\033[38;2;127;127;127m██\033[0m"):
        def add_line(self, point1, point2, color):
            point1, point2 = [int(round(point1[0], 0)), int(round(point1[1], 0))], [int(round(point2[0], 0)), int(round(point2[1], 0))]
            if point1[0] == point2[0]:
                for y in range(max(0, min(point1[1], point2[1])), min(self.height - 1, max(point1[1], point2[1]))):
                    self.frame[y][int(point1[0])] = color
            elif abs(slope := (point1[1] - point2[1]) / (point1[0] - point2[0])) <= 1:
                for x in range(max(0, min(point1[0], point2[0])), min(self.width - 1, max(point1[0], point2[0]))):
                    self.frame[int(slope * (x - point1[0]) + point1[1])][x] = color
            else:
                slope = 1 / slope
                for y in range(max(0, min(point1[1], point2[1])), min(self.height - 1, max(point1[1], point2[1]))):
                    self.frame[y][int(slope * (y - point1[1]) + point1[0])] = color
        
        for mesh in meshes.values():
            for face in mesh["f"]:
                vec = [cam[index] - mesh["v"][face[0][0] - 1][index] for index in range(3)]
                if sum([vec[index] * mesh["vn"][face[2] - 1][index] for index in range(3)]) < 0:
                    continue
                p1, p2, p3 = mesh["projected_v"][face[0][0] - 1], mesh["projected_v"][face[0][1] - 1], mesh["projected_v"][face[0][2] - 1]
                add_line(self, p1, p2, color)
                add_line(self, p2, p3, color)
                add_line(self, p3, p1, color)


    


    def add_tiangle_faces(self, meshes):
        # Adopted from the MIGHTY CHATGPT
        def make_triangle(p1, p2, p3, color):
            # Define the drawing area dimensions
            width = int(max(p1[0], p2[0], p3[0]) + 1)
            height = int(max(p1[1], p2[1], p3[1]) + 1)
            # Function to check if a point lies inside the triangle using Barycentric coordinates
            def is_inside(x, y):
                denominator = ((p2[1] - p3[1]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[1] - p3[1]))
                if denominator == 0:
                    return False
                alpha = ((p2[1] - p3[1]) * (x - p3[0]) + (p3[0] - p2[0]) * (y - p3[1])) / denominator
                beta = ((p3[1] - p1[1]) * (x - p3[0]) + (p1[0] - p3[0]) * (y - p3[1])) / denominator
                gamma = 1 - alpha - beta
                return 0 <= alpha <= 1 and 0 <= beta <= 1 and 0 <= gamma <= 1

            # Loop through the grid and set points inside the triangle to the triangle symbol ('*')
            for y in range(height):
                for x in range(width):
                    if is_inside(x, y):
                        self.frame[y][x] = color

        light_vec = [0, 0, -1]
        for mesh in meshes.values():
            for face in mesh["f"]:
                vec = [cam[index] - mesh["v"][face[0][0] - 1][index] for index in range(3)]
                if sum([vec[index] * mesh["vn"][face[2] - 1][index] for index in range(3)]) <= 0:
                    continue
                # brightness in [31, 255]
                brightness = int((sum([light_vec[index] * mesh["vn"][face[2] - 1][index] for index in range(3)]) + 1) * 112 + 31)
                color = f"\033[38;2;{brightness};{brightness};{brightness}m██\033[0m"
                p1, p2, p3 = mesh["projected_v"][face[0][0] - 1], mesh["projected_v"][face[0][1] - 1], mesh["projected_v"][face[0][2] - 1]
                make_triangle(p1, p2, p3, color)


    

    def draw(self):
        """frame - dict {y:{x:str}}"""
        output = []
        for y in range(self.height):
            output.append(f"\n")
            for x in range(self.width):
                output.append(self.frame[y][x])
        print("".join(output))


def rotation(vec, theta):
    def sin(x):
        return math.sin(x /180 * math.pi)
    def cos(x):
        return math.cos(x /180 * math.pi)
    rotation_matrix = [[0 for _ in range(4)] for _ in range(4)]
    rotation_matrix[0][0] = cos(theta)
    rotation_matrix[0][1] = sin(theta)
    rotation_matrix[1][0] = -sin(theta)
    rotation_matrix[1][1] = cos(theta)
    rotation_matrix[2][2] = 1
    rotation_matrix[3][3] = 1
    vec = [sum(m * v for m, v in zip(rotation_matrix[row], vec)) for row in range(4)]

    rotation_matrix = [[0 for _ in range(4)] for _ in range(4)]
    rotation_matrix[0][0] = 1
    rotation_matrix[1][1] = cos(theta * 0.5)
    rotation_matrix[1][2] = sin(theta * 0.5)
    rotation_matrix[2][1] = -sin(theta * 0.5)
    rotation_matrix[2][2] = cos(theta * 0.5)
    rotation_matrix[3][3] = 1
    return [sum(m * v for m, v in zip(rotation_matrix[row], vec)) for row in range(4)]

    # rotation_matrix = [[0 for _ in range(4)] for _ in range(4)]
    # rotation_matrix[0][0] = cos(theta)
    # rotation_matrix[0][2] = sin(theta)
    # rotation_matrix[1][1] = 1
    # rotation_matrix[2][0] = -sin(theta)
    # rotation_matrix[2][2] = cos(theta)
    # rotation_matrix[3][3] = 1
    # return [sum(m * v for m, v in zip(rotation_matrix[row], vec)) for row in range(4)]

    


def keyinput():
    global key,pause
    from msvcrt import getwch
    while True:
        key = getwch()
        if key == " ":
            pause = not pause
        elif key == "Q":
            exit()


def change_meshes():
    def unit_normal(v, u):
        result = [v[1] * u[2] - v[2] * u[1],
                v[2] * u[0] - v[0] * u[2],
                v[0] * u[1] - v[1] * u[0]]
        length = math.sqrt(sum([result[index]**2 for index in range(3)]))
        return [result[index] / length for index in range(3)]
    for name, mesh in meshes.items():
        for index, vertex in enumerate(mesh["v"]):
            meshes[name]["v"][index] = rotation(vertex + [1], theta)
        meshes[name]["vn"] = []
        for face in mesh["f"]:
            p1, p2, p3 = [meshes[name]["v"][face[0][index] - 1] for index in range(3)]
            normal = unit_normal([p2[index] - p1[index] for index in range(3)], [p3[index] - p2[index] for index in range(3)])
            if normal not in meshes[name]["vn"]:
                meshes[name]["vn"].append(normal)
    return meshes



display = Display(bottom_bar=2)

import math
from threading import Thread
from os import system
system("cls")
key = None
pause = False
Thread(target=keyinput).start()
theta = 0
cam = [0, 0, -1.2]
fov = 80
meshes = {}
# meshes = Mesh.add_to_meshes(meshes, Mesh.obj_loader("cube_tri.obj"))
meshes = Mesh.add_to_meshes(meshes, Mesh.obj_loader("little_desk(triangulated&integrated).mtl.obj"))
# meshes = Mesh.add_to_meshes(meshes, Mesh.obj_loader("fox.obj"))
# meshes = Mesh.add_to_meshes(meshes, Mesh.obj_loader("utah_teapot.obj"))
# meshes = Mesh.add_to_meshes(meshes, Mesh.obj_loader("spaceship.obj"))




# Rendering.render(meshes, 70, 0.1, 100, display.width, display.height,)
# display.add_triangle_edges(meshes)
# display.draw()
while key != "Q":
    if not pause:
        display.new_frame()

        meshes = change_meshes()

        Rendering.render(meshes, 72, 0.01, 100, display.width, display.height,)
        # display.add_tiangle_faces(meshes)
        display.add_triangle_edges(meshes)
        display.draw()

        theta = 1
        pass