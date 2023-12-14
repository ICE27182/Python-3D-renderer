

class Mesh:
    def __init__(self, name, v=None, vn=None, vt=None, f=None,) -> None:
        import math
        self.sqrt = math.sqrt
        self.sin = lambda x: math.sin(x * math.pi / 180)
        self.cos = lambda x: math.cos(x * math.pi / 180)
        self.name = name
        self.v = [] if v == None else v
        self.vn = [] if vn == None else vn
        self.vt = [] if vt == None else vt
        self.f = [] if f == None else f
        if self.v != []:
            def relative_v_calculation(v):
                return (v[0] - self.center[0], v[1] - self.center[1], v[2] - self.center[2])
            self.center = list(map(sum, (zip(*self.v))))
            self.center = [self.center[i] / len(self.v) for i in range(3)]
            self.relative_v = map(relative_v_calculation, self.v)


    
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
        def relative_v_calculation(v):
            return (v[0] - mesh.center[0], v[1] - mesh.center[1], v[2] - mesh.center[2])
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
                        line[0][index] -= (v_max + 1)
                    line[-1] -= (vn_max + 1)
                    outputs[name].f.append(line)
                # It is supposed to be cases like "f 1/2/1 2/3/1 3/2/1", but I'm not sure if things like "f 1/2/ 2/3/ 3/2/" exist, which would be a problem
                elif "/" in line[0]:
                    line = [list(map(int, value.split("/"))) for value in line]
                    line = [[value[0] for value in line], [value[1] for value in line], line[0][-1]]
                    for index in range(len(line[0])):
                        line[0][index] -= (v_max + 1)
                        line[1][index] -= (vt_max + 1)
                    line[-1] -= (vn_max + 1)
                    outputs[name].f.append(line)
                else:
                    line = list(map(int, line))
                    line = [[val - v_max - 1 for val in line], [], None]
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
            mesh.center = list(map(sum, (zip(*mesh.v))))
            mesh.center = [mesh.center[i] / len(mesh.v) for i in range(3)]
            mesh.relative_v = tuple(map(relative_v_calculation, mesh.v))

        return outputs


    def get_normal(self):
        self.vn = []
        for index, face in enumerate(self.f):
            v = Tool.vec3_minus_vec3(self.v[face[0][1]], self.v[face[0][0]])
            u = Tool.vec3_minus_vec3(self.v[face[0][2]], self.v[face[0][0]])
            normal = [v[1] * u[2] - v[2] * u[1],
                      v[2] * u[0] - v[0] * u[2],
                      v[0] * u[1] - v[1] * u[0]]
            length = self.sqrt(sum([normal[index]**2 for index in range(3)]))
            if length == 0:
                print(f"There might be an issue with the mesh \"{self.name}\". The {self.f.index(face) + 1}th face is either a line or a point.")
                continue
            normal = [normal[0] / length, normal[1] / length, normal[2] / length]
            if normal in self.vn:
                self.f[index][-1] = self.vn.index(normal)
            else:
                self.f[index][-1] = len(self.vn)
                self.vn.append(normal)


    def move_mesh(self, destination):
        def relative_v_calculation(v):
            return (v[0] - self.center[0], v[1] - self.center[1], v[2] - self.center[2])
        self.relative_v = tuple(map(relative_v_calculation, self.v))
        self.center = destination
        for index, distance in enumerate(self.relative_v):
            self.v[index][0] = self.center[0] + distance[0]
            self.v[index][1] = self.center[1] + distance[1]
            self.v[index][2] = self.center[2] + distance[2]
    

    def rotate_mesh(self, x_degree=0, y_degree=0, z_degree=0):
        for index, vertex in enumerate(self.v):
            vertex[0] -= self.center[0]
            vertex[1] -= self.center[1]
            vertex[2] -= self.center[2]
            # x axis
            vertex = [vertex[0],
                      self.cos(x_degree) * vertex[1] - self.sin(x_degree) * vertex[2],
                      self.sin(x_degree) * vertex[1] + self.cos(x_degree) * vertex[2]]
            # y_axis
            vertex = [self.cos(y_degree) * vertex[0] + self.sin(y_degree) * vertex[2],
                      vertex[1],
                      -self.sin(y_degree) * vertex[0] + self.cos(y_degree) * vertex[2]]
            # z axis
            vertex = [self.cos(z_degree) * vertex[0] - self.sin(z_degree) * vertex[1],
                      self.sin(z_degree) * vertex[0] + self.cos(z_degree) * vertex[1],
                      vertex[2]]
            vertex[0] += self.center[0]
            vertex[1] += self.center[1]
            vertex[2] += self.center[2]
            self.v[index] = vertex

            
            


class Display:
    def __init__(self, fov=40, size=None, z_near=0.01, z_far=100, bottom_bar_height=0) -> None:
        import math
        self.ceil = math.ceil
        self.fov_trans = lambda degree : math.tan(degree * math.pi / 360)
        self.fov = fov
        self.size = size
        self.z_near = z_near
        self.z_far = z_far
        self.bottom_bar_height = bottom_bar_height
        from shutil import get_terminal_size
        self.get_terminal_size = get_terminal_size
        self.refresh()


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
        else:
            w, h = self.size
        self.width, self.height = w, h
    

    def new_frame(self):
        self.frame = {y:{x:"  " for x in range(self.width)} for y in range(self.height)}


    def refresh(self):
        from os import system
        system("cls")
        self.get_screen_size()
        self.frame = {y:{x:"  " for x in range(self.width)} for y in range(self.height)}
        tan_half_fov = self.fov_trans(self.fov)
        self.projection_matrix = ((-self.height / self.width / tan_half_fov, 0, 0, 0),
                         (0, 1 / tan_half_fov, 0, 0),
                         (0, 0, -(self.z_far+self.z_near)/(self.z_far-self.z_near), -self.z_near * self.z_far/(self.z_far-self.z_near)),
                         (0, 0, -1, 0),)


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
    
                
    def draw(self):
        """frame - dict {y:{x:str}}"""
        print("\033[F" * (self.height * 2))
        output = []
        for y in range(self.height):
            output.append("\n")
            for x in range(self.width):
                output.append(self.frame[y][x])
        print("".join(output), f"\n{self.bottom_bar_info}")




class Tool:
    def vec3_plus_vec3(v, u) -> list:
        return [v[0] + u[0], v[1] + u[1], v[2] + u[2]]
    
    def vec3_minus_vec3(v, u) -> list:
        return [v[0] - u[0], v[1] - u[1], v[2] - u[2]]




def calculate_camera_matrix(cam, math) -> list:
    trans = math.pi / 180
    cos_beta = math.cos(cam[4] * trans)
    cos_alpha = math.cos(cam[3] * trans)
    sin_beta = math.sin(cam[4] * trans)
    sin_alpha = math.sin(cam[3] * trans)
    return (( sin_alpha, 0, - cos_alpha),
            (-sin_beta * cos_alpha, cos_beta, -sin_beta * sin_alpha),
            ( cos_beta * cos_alpha, sin_beta,  cos_beta * sin_alpha),)




def render(meshes, display, cam, min_brightness, max_brightnss, light_dir, culling, faces, edges) -> None:
    display.new_frame()
    z_buffer = [[-1 for _ in range(display.width)] for _ in range(display.height)]
    for mesh in meshes.values():
        for face in mesh.f:
            # Get the three coordinates
            tri = [mesh.v[face[0][0]], mesh.v[face[0][1]], mesh.v[face[0][2]]]

            # culling
            normal = mesh.vn[face[-1]]
            cam_to_plane = (cam[0] - tri[0][0], cam[1] - tri[0][1], cam[2] - tri[0][2])
            # Dot product value and culling setting determine if faces not facing the camera should be rendered
            if culling and (normal[0] * cam_to_plane[0] + normal[1] * cam_to_plane[1] + normal[2] * cam_to_plane[2]) <= 0:
                continue

            # Light
            color = int(min_brightness + (max_brightnss - min_brightness) * ((normal[0] * light_dir[0] + normal[1] * light_dir[1] + normal[2] * light_dir[2]) + 1) / 2)
            color = f"\033[38;2;{color};{color};{color}m██\033[0m"

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
            

            # Clipping
            inside = []
            outside = []
            # Still, not using loop because of performance
            if tri[0][2] >= display.z_near:
                inside.append(tri[0])
            else:
                outside.append(tri[0])
            if tri[1][2] >= display.z_near:
                inside.append(tri[1])
            else:
                outside.append(tri[1])
            if tri[2][2] >= display.z_near:
                inside.append(tri[2])
            else:
                outside.append(tri[2])
            
            if len(inside) == 3:
                pass
            elif len(inside) == 0:
                continue
            elif len(inside) == 1:
                # Compute the parameter t where the line intersects the plane
                t = (display.z_near - outside[0][2]) / (inside[0][2] - outside[0][2])
                # Calculate the intersection point
                inside.append((outside[0][0] + t * (inside[0][0] - outside[0][0]),
                                outside[0][1] + t * (inside[0][1] - outside[0][1]),
                                outside[0][2] + t * (inside[0][2] - outside[0][2])))
                # Compute the parameter t where the line intersects the plane
                t = (display.z_near - outside[1][2]) / (inside[0][2] - outside[1][2])
                # Calculate the intersection point
                inside.append((outside[1][0] + t * (inside[0][0] - outside[1][0]),
                                outside[1][1] + t * (inside[0][1] - outside[1][1]),
                                outside[1][2] + t * (inside[0][2] - outside[1][2])))
            # elif len(inside) == 2:
            else:
                # Compute the parameter t where the line intersects the plane
                t = (display.z_near - outside[0][2]) / (inside[0][2] - outside[0][2])
                # Calculate the intersection point
                inside.append((outside[0][0] + t * (inside[0][0] - outside[0][0]),
                                outside[0][1] + t * (inside[0][1] - outside[0][1]),
                                outside[0][2] + t * (inside[0][2] - outside[0][2])))
                # Compute the parameter t where the line intersects the plane
                t = (display.z_near - outside[0][2]) / (inside[1][2] - outside[0][2])
                # Calculate the intersection point
                inside.append((outside[0][0] + t * (inside[1][0] - outside[0][0]),
                                outside[0][1] + t * (inside[1][1] - outside[0][1]),
                                outside[0][2] + t * (inside[1][2] - outside[0][2])))
            for index, point in enumerate(inside):
                point = [display.projection_matrix[0][0] * point[0] + display.projection_matrix[0][1] * point[1] + display.projection_matrix[0][2] * point[2] + display.projection_matrix[0][3],
                            display.projection_matrix[1][0] * point[0] + display.projection_matrix[1][1] * point[1] + display.projection_matrix[1][2] * point[2] + display.projection_matrix[1][3],
                            display.projection_matrix[2][0] * point[0] + display.projection_matrix[2][1] * point[1] + display.projection_matrix[2][2] * point[2] + display.projection_matrix[2][3],
                            display.projection_matrix[3][0] * point[0] + display.projection_matrix[3][1] * point[1] + display.projection_matrix[3][2] * point[2] + display.projection_matrix[3][3],]
                point = [point[0] / point[3], point[1] / point[3], point[2] / point[3], point[3]]
                point[0] = (point[0] + 1) * 0.5 * display.width
                point[1] = (point[1] + 1) * 0.5 * display.height
                inside[index] = point
            v = (inside[-3][0] - inside[-2][0] , inside[-3][1] - inside[-2][1], inside[-3][2] - inside[-2][2])
            u = (inside[-1][0] - inside[-2][0] , inside[-1][1] - inside[-2][1], inside[-1][2] - inside[-2][2])
            normal = [v[1] * u[2] - v[2] * u[1],
                        v[2] * u[0] - v[0] * u[2],
                        v[0] * u[1] - v[1] * u[0]]
            if normal[2] == 0:
                continue
            if faces:
                if len(inside) == 3:
                    for y in range(int(max(0, min(inside[0][1], inside[1][1], inside[2][1]))), int(min(display.height, max(inside[0][1], inside[1][1], inside[2][1]) + 1))):
                        for x in range(int(max(0, min(inside[0][0], inside[1][0], inside[2][0]))), int(min(display.width, max(inside[0][0], inside[1][0], inside[2][0]) + 1))):
                            z = inside[0][2] - (normal[0] * (x - inside[0][0]) + normal[1] * (y - inside[0][1])) / normal[2]
                            if z >= z_buffer[y][x]:
                                vec1 = (inside[0][0] - x, inside[0][1] - y)
                                vec2 = (inside[1][0] - x, inside[1][1] - y)
                                vec3 = (inside[2][0] - x, inside[2][1] - y)
                                cp23 = vec2[0] * vec3[1] -  vec2[1] * vec3[0]
                                if (vec1[0] * vec2[1] -  vec1[1] * vec2[0]) * cp23 > 0 and cp23 * (vec3[0] * vec1[1] -  vec3[1] * vec1[0]) > 0:
                                    display.frame[y][x] = color
                                    z_buffer[y][x] = z
                # elif len(inside) == 4:
                else:
                    for y in range(int(max(0, min(inside[0][1], inside[1][1], inside[2][1]))), int(min(display.height, max(inside[0][1], inside[1][1], inside[2][1]) + 1))):
                        for x in range(int(max(0, min(inside[0][0], inside[1][0], inside[2][0]))), int(min(display.width, max(inside[0][0], inside[1][0], inside[2][0]) + 1))):
                            z = inside[0][2] - (normal[0] * (x - inside[0][0]) + normal[1] * (y - inside[0][1])) / normal[2]
                            if z >= z_buffer[y][x]:
                                vec1 = (inside[0][0] - x, inside[0][1] - y)
                                vec2 = (inside[1][0] - x, inside[1][1] - y)
                                vec3 = (inside[2][0] - x, inside[2][1] - y)
                                cp23 = vec2[0] * vec3[1] -  vec2[1] * vec3[0]
                                if (vec1[0] * vec2[1] -  vec1[1] * vec2[0]) * cp23 > 0 and cp23 * (vec3[0] * vec1[1] -  vec3[1] * vec1[0]) > 0:
                                    display.frame[y][x] = color
                                    z_buffer[y][x] = z
                                    pass
                    for y in range(int(max(0, min(inside[1][1], inside[2][1], inside[3][1]))), int(min(display.height, max(inside[1][1], inside[2][1], inside[3][1]) + 1))):
                        for x in range(int(max(0, min(inside[1][0], inside[2][0], inside[3][0]))), int(min(display.width, max(inside[1][0], inside[2][0], inside[3][0]) + 1))):
                            z = inside[1][2] - (normal[0] * (x - inside[1][0]) + normal[1] * (y - inside[1][1])) / normal[2]
                            if z >= z_buffer[y][x]:
                                vec1 = (inside[1][0] - x, inside[1][1] - y)
                                vec2 = (inside[2][0] - x, inside[2][1] - y)
                                vec3 = (inside[3][0] - x, inside[3][1] - y)
                                cp23 = vec2[0] * vec3[1] -  vec2[1] * vec3[0]
                                if (vec1[0] * vec2[1] -  vec1[1] * vec2[0]) * cp23 > 0 and cp23 * (vec3[0] * vec1[1] -  vec3[1] * vec1[0]) > 0:
                                    display.frame[y][x] = color
                                    z_buffer[y][x] = z
            if edges:
                if len(inside) == 3:
                    display.line(inside[0], inside[1])
                    display.line(inside[1], inside[2])
                    display.line(inside[2], inside[0])
                # elif len(inside) == 4:
                else:
                    display.line(inside[0], inside[1])
                    display.line(inside[1], inside[2])
                    display.line(inside[2], inside[0])
                    display.line(inside[1], inside[3])
                    display.line(inside[2], inside[3])




def keyinput() -> None:
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
    Thread(target=keyinput, daemon=True).start()

    meshes = {}
    # filename = "cube.obj"
    # filename = "little_desk(triangulated&integrated).mtl.obj"
    # filename = "models\\spaceship.obj"
    filename = "models\\playground.obj"
    filename = "models\\utpot_b.obj"
    filename = "models\\fox.obj"
    filename = "room.obj"

    meshes.update(Mesh.load_obj(filename, meshes))
    # meshes.update(Mesh.load_obj("cube.obj", meshes))

    display = Display(fov=50, bottom_bar_height=5, )

    cam = [4, 0.0, 0, -180, 0]
    import math
    cam.append(calculate_camera_matrix(cam, math))
    light_dir = (0, 0.5, -0.5*3**0.5)
    step = 0.1
    culling = True
    max_brightnss = 255
    min_brightness = 16
    faces, edges = True, False

    from time import time
    frame_start_time = time()

    while True:
        if not pause:
            render(meshes, display, cam, min_brightness, max_brightnss, light_dir, culling, faces, edges)
            

        display.bottom_bar_info = f"resolution:{display.width} x {display.height} \nframe generation time:{(fgt:=time()-frame_start_time):.3f}s {1/fgt if fgt != 0 else -1:.3f}fps\n" + f"{cam[:5]}"
        display.bottom_bar_info += f"          \n{sum([len(mesh.f) for mesh in meshes.values()])} Triangles"
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
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                key = None
            elif key == "a":
                cam[:3] = Tool.vec3_minus_vec3(cam[:3], [val * step for val in cam[5][0]])
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                key = None
            elif key == "s":
                cam[:3] = Tool.vec3_minus_vec3(cam[:3], [val * step for val in cam[5][2]])
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                # meshes["Cube_2"].get_normal()
                key = None
            elif key == "d":
                cam[:3] = Tool.vec3_plus_vec3(cam[:3], [val * step for val in cam[5][0]])
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                # meshes["Cube_2"].get_normal()
                key = None
            elif key == "e":
                cam[1] += step
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                key = None
            elif key == "f":
                cam[1] -= step
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                key = None
            elif key == "8":
                cam[4] += 2
                cam[4] = max(-90, min(90, cam[4]))
                cam[5] = calculate_camera_matrix(cam, math)
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                # meshes["Cube_2"].rotate_mesh(x_degree = -2 * cam[5][0][0], z_degree = -2 * cam[5][0][2],)
                # meshes["Cube_2"].get_normal()

                key = None
            elif key == "2":
                cam[4] -= 2
                cam[4] = max(-90, min(90, cam[4]))
                cam[5] = calculate_camera_matrix(cam, math)
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                # meshes["Cube_2"].rotate_mesh(x_degree = 2 * cam[5][0][0], z_degree = 2 * cam[5][0][2],)
                # meshes["Cube_2"].get_normal()
                key = None
            elif key == "4":
                cam[3] += 4
                cam[5] = calculate_camera_matrix(cam, math)
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                # meshes["Cube_2"].rotate_mesh(y_degree = -4,)
                # meshes["Cube_2"].get_normal()
                key = None
            elif key == "6":
                cam[3] -= 4
                cam[5] = calculate_camera_matrix(cam, math)
                # meshes["Cube_2"].move_mesh((cam[0] + cam[5][2][0], cam[1] + cam[5][2][1], cam[2] + cam[5][2][2]))
                # meshes["Cube_2"].rotate_mesh(y_degree = 4,)
                # meshes["Cube_2"].get_normal()
                key = None
            elif key == "7":
                display.fov += 1
                tan_half_fov = display.fov_trans(display.fov)
                display.projection_matrix = ((-display.height / display.width / tan_half_fov, 0, 0, 0),
                                             (0, 1 / tan_half_fov, 0, 0),
                                             (0, 0, -(display.z_far+display.z_near)/(display.z_far-display.z_near), -display.z_near * display.z_far/(display.z_far-display.z_near)),
                                             (0, 0, -1, 0),)
                key = None
            elif key == "9":
                display.fov -= 1
                tan_half_fov = display.fov_trans(display.fov)
                display.projection_matrix = ((-display.height / display.width / tan_half_fov, 0, 0, 0),
                                             (0, 1 / tan_half_fov, 0, 0),
                                             (0, 0, -(display.z_far+display.z_near)/(display.z_far-display.z_near), -display.z_near * display.z_far/(display.z_far-display.z_near)),
                                             (0, 0, -1, 0),)
                key = None
            elif key == "5":
                display.fov = 50
                tan_half_fov = display.fov_trans(display.fov)
                display.projection_matrix = ((-display.height / display.width / tan_half_fov, 0, 0, 0),
                                             (0, 1 / tan_half_fov, 0, 0),
                                             (0, 0, -(display.z_far+display.z_near)/(display.z_far-display.z_near), -display.z_near * display.z_far/(display.z_far-display.z_near)),
                                             (0, 0, -1, 0),)
                key = None
            elif key == "1":
                edges = not edges
                key = None
            elif key == "3":
                faces = not faces
                key = None
            elif key == "0":
                culling = not culling
                key = None

        


if __name__ == "__main__":
    main()