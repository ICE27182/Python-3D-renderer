

class Mesh:
    def __init__(self, name, v=None, vn=None, vt=None, f=None,) -> None:
        from math import sqrt
        self.sqrt = sqrt
        self.name = name
        self.v = [] if v == None else v
        self.vn = [] if vn == None else vn
        self.vt = [] if vt == None else vt
        self.f = [] if f == None else f

    
    def load_obj(filename, meshes, directory=".") -> dict:
        """Load mesh(es) from a given obj file"""
        def check_name_collision(name:str) -> str:
            if name in meshes:
                num = 2
                while f"{name}_{num}" in meshes:
                    num += 1
                print(f"There's a name collison with the mesh \"{name}\" in the file {filename}." +
                      f"So its name has been changed from \"{name}\" to \"{name}_{num}\"")
                return f"{name}_{num}"
            else:
                return name
        outputs = {}
        with open(f"{directory}\\{filename}", "r") as obj:
            obj:str = obj.read()
        
        if obj[0] == "#":
            meshes_num = obj.count("\no ")
            if meshes_num == 0:
                meshes_num = 1
                # Its name won't be defined later by o line, which doesn't exist. So are these max values
                name = filename[:-4]
                name = check_name_collision(name)
                outputs[name] = Mesh(name)
                v_max, vn_max, vt_max = 0, 0, 0,
        elif obj[:2] == "v ":
            meshes_num = 1
            # Its name won't be defined later by o line, which doesn't exist. So are these max values
            name = filename[:-4]
            name = check_name_collision(name)
            outputs[name] = Mesh(name)  
            v_max, vn_max, vt_max = 0, 0, 0,
        elif obj[:2] == "o ":
            # In case the mesh's name ends with "o ", not using obj.count("o ")
            meshes_num = obj.count("\no ") + 1
        else:
            raise Exception("Idk what's in the file. So, check it.")
        
        print(f"{meshes_num} {'meshes have' if meshes_num > 1 else 'mesh has'} been found in {filename}.")

        obj = obj.split("\n")
        v, vn, vt, = 0, 0, 0,

        for line in obj:
            if line == "" or line[0] in ("#", "\n", " "):
                continue
            elif line[0] == "f":
                # f 1 2 3 or f 1//1 2//1 3//1 or f 1/2/1 2/3/1 3/2/1
                line = line[2:].split()
                if "//" in line[0]:
                    line = [[int(line[index].split("//")[0]) for index in range(len(line))], [], int(line[0].split("//")[-1])]
                    for index in range(len(line[0])):
                        line[0][index] -= v_max
                    line[-1] -= vn_max
                    outputs[name].f.append(line)
                # It is supposed to be cases like "f 1/2/1 2/3/1 3/2/1", but I'm not sure if things like "f 1/2/ 2/3/ 3/2/" exist, which would be a problem
                elif "/" in line[0]:
                    line = [list(map(int, value.split("/"))) for value in line]
                    line = [[value[0] for value in line], [value[1] for value in line], line[0][-1]]
                    for index in range(len(line[0])):
                        line[0][index] -= v_max
                        line[1][index] -= vt_max
                    line[-1] -= vn_max
                    outputs[name].f.append(line)
                else:
                    line = list(map(int, line))
                    line = [[val - v_max for val in line], [], None]
                    outputs[name].f.append(line)
            elif line[:2] == "vt":
                vt += 1
                line = list(map(float, line[3:].split()))
                outputs[name].vt.append(line)
            elif line[:2] == "vn":
                vn += 1
                line = list(map(float, line[3:].split()))
                outputs[name].vn.append(line)
            elif line[0] == "v":
                v += 1
                line = list(map(float, line[2:].split()))
                outputs[name].v.append(line)
            elif line[0] == "o":
                if "name" in vars():
                    print(f"\"{name}\" has been loaded.")
                    if name == line[2:]:
                        raise Exception("Name Collision. Two or more meshes in the file have the same name.")
                name = line[2:]
                name = check_name_collision(name)
                outputs[name] = Mesh(name)
                v_max, vn_max, vt_max, = v, vn, vt,
        
        print(f"{name} has been loaded.")

        for mesh in outputs.values():
            if mesh.vn == []:
                mesh.get_normal()
                print(f"All normals of \"{mesh.name}\" have been calculated.")
            else:
                print(f"\"{mesh.name}\" has all its normals stored in the file.")

        return outputs


    def get_normal(self):
        self.vn = []
        for face in self.f:
            v = Tool.vec3_minus_vec3(self.v[face[0][1] - 1], self.v[face[0][0] - 1])
            u = Tool.vec3_minus_vec3(self.v[face[0][2] - 1], self.v[face[0][0] - 1])
            normal = [v[1] * u[2] - v[2] * u[1],
                      v[2] * u[0] - v[0] * u[2],
                      v[0] * u[1] - v[1] * u[0]]
            length = self.sqrt(sum([normal[index]**2 for index in range(3)]))
            if length == 0:
                print(f"There might be an issue with the mesh \"{self.name}\". The {self.f.index(face) + 1}th face is either a line or a point.")
                continue
            normal = [normal[0] / length, normal[1] / length, normal[2] / length]
            if normal in self.vn:
                face[-1] = self.vn.index(normal) + 1
            else:
                self.vn.append(normal)
                face[-1] = len(self.vn)




def projection(meshes:dict, cam, z_near, z_far, display, w=1):
    # Although as long as z_near, z_far and display instance don't change, projection matrix won't change, 
    # which means it's basically a constant and don't need to be recalculate each frame, the amount of time
    # used for the calculation is less than 10**-7 seconds (according to timeit). so whatever...
    projection_matrix = ((-display.height / display.width / display.tan_half_fov, 0, 0, 0),
                         (0, 1 / display.tan_half_fov, 0, 0),
                         (0, 0, -(z_far+z_near)/(z_far-z_near), -z_near * z_far/(z_far-z_near)),
                         (0, 0, -1, 0),)
    for name,mesh in meshes.items():
        meshes[name].pv = []
        for x, y, z, in mesh.v:

            x -= cam[0]
            y -= cam[1]
            z -= cam[2]

            x, y, z = Tool.mat3_times_vec3c(cam[5], (x, y, z))

            coor = Tool.mat4_times_vec4c(projection_matrix, (x, y, z, w))
            coor = [coor[0] / coor[3], coor[1] / coor[3], coor[2] / coor[3], coor[3]]
            coor[0] = (coor[0] + 1) * 0.5 * display.width
            coor[1] = (coor[1] + 1) * 0.5 * display.height
            meshes[name].pv.append(coor)




class Display:
    def __init__(self, fov=80, size=None, bottom_bar_height=0) -> None:
        import math
        self.ceil = math.ceil
        self.tan_half_fov = math.tan(fov * math.pi / 360)
        self.bottom_bar_height = bottom_bar_height
        self.size = size
        from shutil import get_terminal_size
        self.get_terminal_size = get_terminal_size
        self.get_screen_size()
        self.frame = {y:{x:"  " for x in range(self.width)} for y in range(self.height)}


    def get_screen_size(self) -> None:
        if self.size == None:
            w, h = self.get_terminal_size()
            # When printing a really long and complex string, bug character may appear from nowhere
            # so -3 in case such thing happens
            w = w // 2 - 3
            h = h - 3 - self.bottom_bar_height
        elif self.size[0] == None:
            w, _ = self.get_terminal_size()
            w = w // 2 - 3
            h = self.size[1] - 3 - self.bottom_bar_height
        elif self.size[1] == None:
            _, h = self.get_terminal_size()
            w = self.size[0] // 2 - 3
            h = h - 3 - self.bottom_bar_height
        self.width, self.height = w, h
    

    def new_frame(self):
        print("\033[F" * (self.height * 2))
        self.frame = {y:{x:"  " for x in range(self.width)} for y in range(self.height)}


    def refresh(self):
        from os import system
        system("cls")
        self.get_screen_size()
        self.frame = {y:{x:"  " for x in range(self.width)} for y in range(self.height)}


    def line(self, point1, point2, color="\033[38;2;127;127;127m██\033[0m"):
        point1, point2 = [int(round(point1[0], 0)), int(round(point1[1], 0))], [int(round(point2[0], 0)), int(round(point2[1], 0))]
        if point1[0] == point2[0]:
            for y in range(max(0, min(point1[1], point2[1])), min(self.height - 1, max(point1[1], point2[1]))):
                if 0 <= (x:=int(point1[0])) < self.width:
                    self.frame[y][x] = color
        elif abs(slope := (point1[1] - point2[1]) / (point1[0] - point2[0])) <= 1:
            for x in range(max(0, min(point1[0], point2[0])), min(self.width - 1, max(point1[0], point2[0]))):
                if 0 <= (y:=int(slope * (x - point1[0]) + point1[1])) < self.height:
                    self.frame[y][x] = color
        else:
            slope = 1 / slope
            for y in range(max(0, min(point1[1], point2[1])), min(self.height - 1, max(point1[1], point2[1]))):
                if 0 <= (x:=int(slope * (y - point1[1]) + point1[0])) < self.width:
                    self.frame[y][x] = color


    def edges(self, meshes, culling=True, cam=None):
        for mesh in meshes.values():
            for face in mesh.f:
                if culling and Tool.dot_product_vec3(mesh.vn[face[-1] - 1], (cam[0] - mesh.v[face[0][0] - 1][0], cam[1] - mesh.v[face[0][0] - 1][1], cam[2] - mesh.v[face[0][0] - 1][2])) <= 0:
                    continue
                self.line(mesh.pv[face[0][0] - 1], mesh.pv[face[0][1] - 1])
                self.line(mesh.pv[face[0][1] - 1], mesh.pv[face[0][2] - 1])
                self.line(mesh.pv[face[0][2] - 1], mesh.pv[face[0][0] - 1])
    

    def faces(self, meshes, cam):
        def is_inside(x, y):
            """Based on cross product. The best performance algorithm I can find currently."""
            vec1 = (p1[0] - x, p1[1] - y)
            vec2 = (p2[0] - x, p2[1] - y)
            vec3 = (p3[0] - x, p3[1] - y)
            cp23 = vec2[0] * vec3[1] -  vec2[1] * vec3[0]
            return  (vec1[0] * vec2[1] -  vec1[1] * vec2[0]) * cp23 > 0 and cp23 * (vec3[0] * vec1[1] -  vec3[1] * vec1[0]) > 0
        
        light = (0, 0.5, 0.5*3**0.5)

        for mesh in meshes.values():
            for face in mesh.f:
                color = Tool.normalized_color((Tool.dot_product_vec3(light, mesh.vn[face[-1] - 1]) + 1) / 2, 16)
                if Tool.dot_product_vec3(mesh.vn[face[-1] - 1], (cam[0] - mesh.v[face[0][0] - 1][0], cam[1] - mesh.v[face[0][0] - 1][1], cam[2] - mesh.v[face[0][0] - 1][2])) <= 0:
                    continue
                p1 = mesh.pv[face[0][0] - 1]
                p2 = mesh.pv[face[0][1] - 1]
                p3 = mesh.pv[face[0][2] - 1]
                w = int(max(p1[0], p2[0], p3[0]) + 1)
                h = int(max(p1[1], p2[1], p3[1]) + 1)
                for y in range(h):
                    for x in range(w):
                        if is_inside(x, y) and 0 <= x < self.width and 0 <= y < self.height:
                            self.frame[y][x] = color

                
    def draw(self):
        """frame - dict {y:{x:str}}"""
        output = []
        for y in range(self.height):
            output.append(f"\n")
            for x in range(self.width):
                output.append(self.frame[y][x])
        print("".join(output), f"\n{self.bottom_bar_info}")




class Tool:
    def mat4_times_vec4c(mat, vec) -> list:
        # It's several times faster than [sum(m * v for m, v in zip(mat[row], vec)) for row in range(4)]
        return [mat[0][0] * vec[0] + mat[0][1] * vec[1] + mat[0][2] * vec[2] + mat[0][3] * vec[3],
                mat[1][0] * vec[0] + mat[1][1] * vec[1] + mat[1][2] * vec[2] + mat[1][3] * vec[3],
                mat[2][0] * vec[0] + mat[2][1] * vec[1] + mat[2][2] * vec[2] + mat[2][3] * vec[3],
                mat[3][0] * vec[0] + mat[3][1] * vec[1] + mat[3][2] * vec[2] + mat[3][3] * vec[3],]
    
    def mat3_times_vec3c(mat, vec) -> list:
        # It's several times faster than [sum(m * v for m, v in zip(mat[row], vec)) for row in range(4)]
        return [mat[0][0] * vec[0] + mat[0][1] * vec[1] + mat[0][2] * vec[2],
                mat[1][0] * vec[0] + mat[1][1] * vec[1] + mat[1][2] * vec[2],
                mat[2][0] * vec[0] + mat[2][1] * vec[1] + mat[2][2] * vec[2],]

    def dot_product_vec3(v, u) -> float:
        return v[0] * u[0] + v[1] * u[1] + v[2] * u[2]

    def vec3_plus_vec3(v, u) -> list:
        return [v[0] + u[0], v[1] + u[1], v[2] + u[2]]
    
    def vec3_minus_vec3(v, u) -> list:
        return [v[0] - u[0], v[1] - u[1], v[2] - u[2]]
    
    def normalized_color(val, min=0, max=255):
        val = int(min + (max - min) * val)
        return f"\033[38;2;{val};{val};{val}m██\033[0m"


def calculate_camera_matrix(cam, math) -> list:
    trans = math.pi / 180
    cos_beta = math.cos(cam[4] * trans)
    cos_alpha = math.cos(cam[3] * trans)
    sin_beta = math.sin(cam[4] * trans)
    sin_alpha = math.sin(cam[3] * trans)
    return (( sin_alpha, 0, - cos_alpha),
            (-sin_beta * cos_alpha, cos_beta, -sin_beta * sin_alpha),
            ( cos_beta * cos_alpha, sin_beta,  cos_beta * sin_alpha),)



def keyinput():
    global key, pause
    from msvcrt import getwch
    while True:
        key = getwch()
        if key == " ":
            pause = not pause
            key = None
        elif key == "Q":
            break
            


def main() -> None:
    # Start a new thread for capture key input
    from threading import Thread
    global key, pause
    key, pause = None, False
    step = 0.1
    Thread(target=keyinput, daemon=True).start()

    meshes = {}
    # filename = "fox.obj"
    # filename = "cube.obj"
    # filename = "utpot_b.obj"
    # filename = "little_desk(triangulated&integrated).mtl.obj"
    filename = "models\\spaceship.obj"

    meshes.update(Mesh.load_obj(filename, meshes))

    display = Display(fov=50, bottom_bar_height=5)
    cam = [0, 0, -5, 90, 0]
    import math
    cam.append(calculate_camera_matrix(cam, math))

    from time import time
    frame_start_time = time()
    while True:
        
        if not pause:
            projection(meshes, cam, z_near=0.05, z_far=100, display=display)
            display.faces(meshes, cam)
            # display.edges(meshes, culling=True, cam=cam)

            
        display.bottom_bar_info = f"resolution:{display.width} x {display.height} \nframe generation time:{(fgt:=time()-frame_start_time):.3f}s {1/fgt if fgt != 0 else -1:.3f}fps\n" + f"{cam[:5]}"
        frame_start_time = time()
        display.draw()
        
        if key != None:
            if key == "Q":
                break
            elif key == "r":
                display.refresh()
                key = None
            elif key == "w":
                cam[:3] = Tool.vec3_plus_vec3(cam[:3], [val * step for val in cam[5][2]])
                key = None
            elif key == "a":
                cam[:3] = Tool.vec3_minus_vec3(cam[:3], [val * step for val in cam[5][0]])
                key = None
            elif key == "s":
                cam[:3] = Tool.vec3_minus_vec3(cam[:3], [val * step for val in cam[5][2]])
                key = None
            elif key == "d":
                cam[:3] = Tool.vec3_plus_vec3(cam[:3], [val * step for val in cam[5][0]])
                key = None
            elif key == "e":
                cam[1] += step
                key = None
            elif key == "f":
                cam[1] -= step
                key = None
            elif key == "8":
                cam[4] += 2
                cam[4] = max(-90, min(90, cam[4]))
                cam[5] = calculate_camera_matrix(cam, math)
                key = None
            elif key == "2":
                cam[4] -= 2
                cam[4] = max(-90, min(90, cam[4]))
                cam[5] = calculate_camera_matrix(cam, math)
                key = None
            elif key == "4":
                cam[3] += 4
                cam[5] = calculate_camera_matrix(cam, math)
                key = None
            elif key == "6":
                cam[3] -= 4
                cam[5] = calculate_camera_matrix(cam, math)
                key = None
        display.new_frame()

main()

