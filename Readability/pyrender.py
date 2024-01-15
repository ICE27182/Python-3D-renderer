

# Used to read texture and normal map, 
# as well as storing screen shot in bmp
import png
from math import pi, cos, sin, sqrt, tan
# Used for showing warning
from time import sleep
# Used in shadow map
from collections import deque
# Check if mtl and png file exist
from os.path import isfile
# To automatically decide screen resolution
# To clear the screen by system("cls")
from os import get_terminal_size, system

def normalize_v3d(vector):
    length = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    return [vector[0] / length, vector[1] / length, vector[2] / length,]

def cross_product_v3d(v, u):
    return [v[1] * u[2] - v[2] * u[1],
            v[2] * u[0] - v[0] * u[2],
            v[0] * u[1] - v[1] * u[0]]

def dot_product_v3d(v, u):
    return v[0] * u[0] + v[1] * u[1] + v[2] * u[2]

def vec_minus_vec_3d(v, u):
    return [v[0] - u[0], v[1] - u[1], v[2] - u[2]]




class Object:
    # [Object, Object, ...]
    objects = []
    # [[x, y, z], [...], ...]
    v = []
    # [(u, v), (...), ...]
    vt = []
    # [[x, y, z], [...], ...]
    vn = []
    # {name: Material}
    materials = {}
    # Remember to add / at the end
    default_obj_dir = "./"
    # In case a unwrapped object does not have texture,
    # a uv map will be created so it can still have where
    # shadow will be casted
    # (resolution, r, g, b)   pixel number = resolution x resolution
    default_uv_map_properties = (192, 127, 127, 127)
    def __init__(self, name:str) -> None:
        self.name = name
        # [
        #   [
        #       (v_idx, v_idx, v_idx), 
        #       (vt_idx, vt_idx, vt_idx), 
        #       vn_idx
        #   ],
        #   [...],
        #   ...]
        self.faces = []
        self.svn = []
        self.uv_map = None
        self.mtl = None
        self.face_count = None
        self.shade_smooth = False
        self.shadow = True
        self.hastexture = False
        self.hasnormal_map = False
    

    def __str__(self):
        return (f"{self.name} | {self.face_count} faces | "
                f"Shading {'smooth' if self.shade_smooth else 'flat'}")

    def load_obj(self, file:str, dir:str=None):
        """
        file can either be the name of the file or the path
        If path is entered, dir should be None
        
        """
        dir = dir.replace("\\", "/") if type(dir) == str else None
        if dir == None:
            dir = Object.default_obj_dir
        elif not dir.endswith("/") and dir != "":
            dir += "/"
        if not file.endswith(".obj"):
            file += ".obj"
        file = file.replace("\\", "/")
        # file is given as path
        if "/" in file:
            # dir should be None, but if it is None, it has been changed to
            # Object.default_obj_dir by now
            if dir != Object.default_obj_dir:
                raise Exception("dir should remain None if file is given as a path")
            # Separate the name and the dir
            file = file.split("/")
            dir = "/".join(file[:-1]) + "/"
            file = file[-1]
        filepath = dir + file
        print(f"Starts to load obj file: {file} \n(Path: {filepath})")
        with open(filepath, "r") as obj_file:
            # Will be added to the f value
            convert_to_left_hand = False
            # Blender uses right hand coordinate system, whereas my
            # renderer uses left hand one.
            if obj_file.readline(9) == "# Blender":
                convert_to_left_hand = True
            # The index stored in obj starts at 1 instead of 0,
            # so later the value stored in self.faces will be
            # substracted by 1. Given that it also needs to be
            # substracted by the length of the already stored value,
            # I think it's a good idea to merge the two steps so
            # It won't be necessary to do one more subtraction 
            # every time it add a vertex information.
            v_offset = len(self.v) - 1
            vt_offset = len(self.vt) - 1
            vn_offset = len(self.vn) - 1
            for line in obj_file.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith("mtllib "):
                    print(f"Loading MTL file: {dir + line[7:]}")
                    mtl_loaded = Material.load_mtl(self, line[7:], dir)
                    print(f"Finish loading {dir + line[7:]}")
                elif line.startswith("o "):
                    current_obejct = Object(name = line[2:])
                    self.objects.append(current_obejct)
                    print(f"Loading {current_obejct.name}")
                elif line.startswith("v "):
                    self.v.append(list(map(float, line[2:].split())))
                    if convert_to_left_hand:
                        self.v[-1][0] *= -1
                elif line.startswith("vt "):
                    self.vt.append(tuple(map(float, line[3:].split())))
                    if convert_to_left_hand:
                        self.vt[-1] = (self.vt[-1][0], 1 - self.vt[-1][1])
                elif line.startswith("vn "):
                    self.vn.append(list(map(float, line[3:].split())))
                    if convert_to_left_hand:
                        self.vn[-1][0] *= -1
                elif line in ("s 1", "s on"):
                    current_obejct.shade_smooth = True
                elif line.startswith("usemtl ") and mtl_loaded:
                    current_obejct.mtl = self.materials[line[7:]]
                elif line.startswith("f "):
                    face = line[2:].split()
                    # v&vn
                    if "//" in face[0]:
                        face = (face[0].split("//"), face[1].split("//"), face[2].split("//"))
                        face = [
                            (int(face[0][0]) + v_offset, 
                             int(face[1][0]) + v_offset, 
                             int(face[2][0]) + v_offset),
                             None,
                             int(face[0][1]) + vn_offset,
                             [None, None, None],
                        ]
                    # v or v&vt&vn
                    else:
                        face = (face[0].split("/"), face[1].split("/"), face[2].split("/"))
                        # v
                        if len(face[0]) == 1:
                            face = [
                                (int(face[0][0]) + v_offset, 
                                 int(face[1][0]) + v_offset, 
                                 int(face[2][0]) + v_offset),
                                None,
                                None,
                                [None, None, None],
                            ]
                        # v&vt
                        elif len(face[0]) == 2:
                            face = [
                                (int(face[0][0]) + v_offset, 
                                 int(face[1][0]) + v_offset, 
                                 int(face[2][0]) + v_offset),
                                (int(face[0][1]) + vt_offset, 
                                 int(face[1][1]) + vt_offset,
                                 int(face[2][1]) + vt_offset),
                                None,
                                [None, None, None],
                            ]
                        # v&vt&vn
                        else:    # elif len(face[0]) == 3:
                            face = [
                                (int(face[0][0]) + v_offset, 
                                 int(face[1][0]) + v_offset, 
                                 int(face[2][0]) + v_offset),
                                (int(face[0][1]) + vt_offset, 
                                 int(face[1][1]) + vt_offset,
                                 int(face[2][1]) + vt_offset),
                                int(face[0][2]) + vn_offset,
                                [None, None, None],
                            ]
                    current_obejct.faces.append(face)

        print("Finish loading from files. Starts to post-process the object(s) loaded.")

        # So far, hastexture and hasnormal_map are all False, which will
        # be determined in the next step.
        # shadow is True by default, but will be disabled if the object
        # does not have uv coordinates, which should be created by
        # means like unwrapping in blender in advance.
        obj:Object    # CodeUndone VsCode 
        for obj in Object.objects:
            obj.face_count = len(obj.faces)
            obj.calculate_face_normals()
            if obj.shade_smooth:
                obj.calculate_smooth_shading_normals()
            # If the object does not have uv coordinates, none of
            # shadow, texture or normal map will apply
            if obj.faces[0][1] == None:
                obj.shadow = False
                continue
            if obj.mtl != None:
                if obj.mtl.texture_path != None:
                    obj.hastexture = True
                    obj.uv_map = png.Png(obj.mtl.texture_path, "", to_pickle=False).pixels
                if obj.mtl.normal_map != None:
                    obj.hasnormal_map = True
            # No texture, create one
            if obj.uv_map == None:
                obj.uv_map = [
                    [Object.default_uv_map_properties[2:]] * 
                    Object.default_uv_map_properties[0]
                    for _ in range(Object.default_uv_map_properties[0])
                ]
        print(f"{file} has finished loading\n")
    

    def change_default_loading_dir(self, dir:str):
        dir = dir.replace("\\", "/")
        if not dir.endswith("/"):
            dir += "/"
        self.default_obj_dir = dir

    
    def calculate_face_normals(self):
        """
        Check whether obj.faces stores the normal or not
        If not, it will go over every face and calculate the normal
        """
        if self.faces[0][2] != None:
            return
        for face in self.faces:
            normal = normalize_v3d(
                        cross_product_v3d(
                            vec_minus_vec_3d(
                                self.v[face[0][2]], 
                                self.v[face[0][0]]
                            ),
                            vec_minus_vec_3d(
                                self.v[face[0][1]], 
                                self.v[face[0][0]]
                            )
                        )
                     )
            try:
                index = self.vn.index(normal)
            except ValueError:
                index = len(self.vn)
                self.vn.append(normal)
            face[2] = index


    def calculate_smooth_shading_normals(self):
        """
        Check if obj.faces stores normals or not. Calculate the normal values first
        if it does not include them.
        Average all normals on each vertex, stored in self.svn and self.faces[:][3]
        """
        def average_many_vectors_v3d(vectors):
            # transformed_vecs = [(x1, x2, ...), (y1, y2, ...), (z1, z2, ...)]
            transformed_vecs = tuple(zip(*tuple(zip(*vectors))[0]))
            return normalize_v3d((sum(transformed_vecs[0]), sum(transformed_vecs[1]), sum(transformed_vecs[2])))
        if self.faces[0][2] == None:
            self.calculate_face_normals()
        # v_vn = {v: [([nx, ny, nz], face_index, vertex_index_in_a_face), (...)], 
        #         v: [(...), ...], 
        #         ...}
        v_vn = {}
        for findex, face in enumerate(self.faces):
            for i in (0, 1, 2):
                # CodeUndone donno which is faster, if-in-else or try-except
                if face[0][i] in v_vn:
                    v_vn[face[0][i]].append((Object.vn[face[2]], findex, i))
                else:
                    v_vn[face[0][i]] = [(Object.vn[face[2]], findex, i)]
        for vns in v_vn.values():
            avg = average_many_vectors_v3d(vns)
            for vn_fi_i in vns:
                self.faces[vn_fi_i[1]][3][vn_fi_i[2]] = len(self.svn)
            self.svn.append(avg)



class Material:
    def __init__(self, name:str) -> None:
        self.name = name
        self.normal_map = None
        self.texture_path = None
        self.normal_map_path = None
        
    
    def load_mtl(self, filename:str, dir:str) -> bool:
        if not isfile(dir + filename):
            print("\033[1;31mWARNING: MTL FILE NO FOUND.\n\033[0m")
            sleep(2)
            return False
        with open(dir + filename, "r") as mtl_file:
            for line in mtl_file.readlines():
                if line.startswith("#"):
                    continue
                elif line.startswith("newmtl "):
                    name = line.strip()[7:]
                    if name in self.materials:
                        raise Exception("Name Collision: " +
                                        "2 or more materials share the same name.")
                    else:
                        current_material = Material(name)
                        self.materials[name] = current_material
                elif line.startswith("map_Kd "):
                    img = line.strip()[7:].replace("\\", "/")
                    # Absolute path
                    if "/" in img:
                        if not isfile(img):
                            print("\033[1;31m" +
                                  "WARNING: TEXTURE FILE NO FOUND.\n")
                            sleep(2)
                        else:
                            # CodeUndone The line can be delete
                            # current_material.texture = png.Png(img, "")
                            # store the image in pickle
                            png.Png(img, "")
                            current_material.texture_path = img
                    # Relative path
                    else:
                        if not isfile(dir + img):
                            print("\033[1;31m" +
                                "WARNING: TEXTURE FILE NO FOUND.\n")
                            sleep(2)
                        else:
                            # Store png in pickle first so it would be
                            # faster to load it later
                            if not isfile(dir + img[:-4] + ".pickle"):
                                png.Png(img, dir)
                            current_material.texture_path = dir + img
                    
                elif (line.lower().startswith("map_bump ") or 
                      line.lower().startswith("bump ")):
                    img = line.strip().split()[-1]
                    # Absolute path
                    if "/" in img:
                        if not isfile(img):
                            print("\033[1;31m" +
                                "WARNING: NORMAL MAP FILE NO FOUND.\n")
                            sleep(2)
                        else:
                            current_material.normal_map = png.Png(img, "")
                            current_material.normal_map_path = img
                    # Relative path
                    else:
                        if not isfile(dir + img):
                            print("\033[1;31m" +
                                "WARNING: NORMAL MAP FILE NO FOUND.\n")
                            sleep(2)
                        else:
                            current_material.normal_map = png.Png(img, dir)
                            current_material.normal_map_path = dir + img
                # There are other informations such as ambient value, transparancy
                # values that are not supported in the renderer (partially due to the
                # fact that I myself don't even know what they are exactly), 
                # so they will not be loaded
        return True



class Light:
    lights = []
    # 0 resolution  1 z_near    2 z_far
    default_shadow_properties = (256, 0.01, 50)
    def __init__(self, position, strength=(1, 1, 1), direction=None, type=1) -> None:
        self.x, self.y, self.z = position
        self.r, self.g, self.b = strength
        if type == 0 and direction == None:
            raise Exception("Parallel light source (type 0) requires direction")
        if type == 1:
            self.dirx = None
            self.diry = None
            self.dirz = None
        elif type == 0:
            self.dirx, self.diry, self.dirz = normalize_v3d(direction)
            self.dirx_in_cam = None
            self.diry_in_cam = None
            self.dirz_in_cam = None
        self.type = type
        self.hidden = False
        self.x_in_cam = None
        self.y_in_cam = None
        self.z_in_cam = None
    

    def render_shadow(self, objs) -> tuple:
        pass

    
    def extract_shadow():
        pass



class Camera:
    modes_look_up = (
        "Full", # 0
        "Solid", # 1
        "Performance", # 2
        "Material", # 3
        "Depth", # 4
        "Shadow", # 5
        "LineCulling", # 6
        "LineNoCulling", #7
    )
    def __init__(self, 
                 x=0, y=0, z=0, 
                 yaw=90, pitch=0, roll=0,
                 width=None, height=None,
                 z_near=0.05, z_far=100,
                 fov=100,
                 fxaa=True,
                 obj_buffer = False,
                 mode=0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.yaw = float(yaw)
        self.pitch = float(pitch)
        self.roll = float(roll)
        self.width, self.height = self.get_width_and_height(width, height)
        self.z_near = float(z_near)
        self.z_far = float(z_far)
        self.fov = fov
        self.fxaa = fxaa
        if mode >= 6 and obj_buffer:
            print("\033[31;1m" +
                  "Warning! Camera mode 6 and 7 do not support obj_buffer. " +
                  "Obj_buffer is set to false")
            self.obj_buffer = False
        else:
            self.obj_buffer = obj_buffer
        self.mode = mode
        self.rotation = self.get_rotation_mat()
        self.rendering_plane_z = self.width * 0.5 / tan(fov * pi / 360)
    

    def __str__(self):
        return (f"{self.x:.3f}, {self.y:.3f}, {self.z:.3f}  |  " + 
                f"{self.yaw:.3f}, {self.pitch:.3f}, {self.roll:.3f}")

    def get_rotation_mat(self) -> tuple:
        yaw = self.yaw * pi / 180
        pitch = self.pitch * pi / 180
        sin_yaw = sin(yaw)
        cos_yaw = cos(yaw)
        sin_pitch = sin(pitch)
        cos_pitch = cos(pitch)
        return ((sin_yaw, 0, -cos_yaw,),
                (-sin_pitch * cos_yaw, cos_pitch, -sin_pitch * sin_yaw),
                (cos_yaw * cos_pitch, sin_pitch, sin_yaw * cos_pitch,))
    

    def get_width_and_height(self, 
                             width=None, height=None, 
                             width_reserved=2, height_reserved=3) -> tuple:
        if width == height == None:
            width, height = get_terminal_size()
            width = width // 2 - 2 * width_reserved
            height = height - height_reserved
        elif width == None:
            width, _ = get_terminal_size()
            width = width // 2 - 2 * width_reserved
        elif height == None:
            _, height = get_terminal_size()
            height = height - height_reserved
        if height <= 0 or width <= 0:
            raise Exception("The width and/or height are/is less than 1, " +
                            "with reserved spaced applied.\n" + 
                            f"width:{width}   height:{height}")
        return width, height


    def rotate(self, yaw=0, pitch=0, roll=0):
        """
        The values of yaw, pitch and roll here are relative, not absolute.
        So if you want to look left, you may set yaw as -30 and leave the
        other two as 0
        The method will update self.rotation automatically, so don't 
        worry about it
        """
        self.yaw += yaw
        self.pitch += pitch
        self.roll += roll
        self.rotation = self.get_rotation_mat()



class Scene(Object, Light, Camera):
    def __init__(self) -> None:
        self.objects = []
        self.v = []
        self.vt = []
        self.vn = []
        self.materials = {}
        self.default_obj_dir = Object.default_obj_dir
        self.default_uv_map_properties = Object.default_uv_map_properties
        self.lights = []
        self.cam = Camera()
    

    def render(self):
        pass


    def display(frame) -> None:
        frame_in_str = []
        for row in frame:
            for pixel in row:
                if pixel == (0, 0, 0):
                    frame_in_str.append("  ")
                else:
                    frame_in_str.append(
                        f"\033[38;2{pixel[0]};{pixel[1]};{pixel[2]}m██"
                    )
            frame_in_str.append("\n")
        print("".join(frame_in_str), end="\033[0m")


    def mainloop(self):
        while True:
            pass


def render(objects:list, lights:list, cam:Camera):
    def get_luminance(normal, x3d, y3d, z3d) -> list:
        # Default value for no light at all
        # can be adjusted according to needs
        luminance = [0.05, 0.05, 0.05]
        # CodeUndone VsCode
        light:Light
        for light in Light.lights:
            if light.type == 0:
                # normalize b to 0-1
                b = - ((light.dirx_in_cam * normal[0] + 
                        light.diry_in_cam * normal[1] +
                        light.dirz_in_cam * normal[2]) - 1) / 2
                luminance[0] += light.r * b
                luminance[1] += light.g * b
                luminance[2] += light.b * b
            else:    # light.type == 1
                direction = (
                    light.x_in_cam - x3d,
                    light.y_in_cam - y3d,
                    light.z_in_cam - z3d,
                )
                length_sqrd = sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
                b = max(0, 
                        (
                            (
                                direction[0] * normal[0] + 
                                direction[1] * normal[1] +
                                direction[2] * normal[2]
                            )
                        ) / 
                        length_sqrd
                    )
                
                luminance[0] += light.r * b
                luminance[1] += light.g * b
                luminance[2] += light.b * b
        return luminance
    

    def add_line(M, N):
        if M[8] == N[8]:
            if 0 <= M[8] < cam.width:
                if M[9] > N[9]:
                    M, N = N, M
                for y in range(max(0, M[9]), min(cam.height - 1, N[9])):
                    frame[y][M[8]] = (127, 127, 127)
        elif abs(k:=(M[9] - N[9]) / (M[8] - N[8])) <= 1:
            b = M[9] - k * M[8]
            if M[8] > N[8]:
                M, N = N, M
            for x in range(max(0, M[8]), min(cam.width - 1, N[8])):
                # CodeUndone
                y = int(k * x + b)
                if 0 <= y < cam.height:
                    frame[y][x] = (127, 127, 127)
                # frame[int(k * x + b)][x] = (127, 127, 127)
        else:
            t = 1 / k
            b = M[8] - t * M[9]
            if M[9] > N[9]:
                M, N = N, M
            for y in range(max(0, M[9]), min(cam.height - 1, N[9])):
                x = int(t * y + b)
                if 0 <= x < cam.width:
                    frame[y][x] = (127, 127, 127)
                # frame[y][int(t * y + b)] = (127, 127, 127)
        

    def rasterize_solid(A, B, C, normal):
        if A[9] > B[9]:
            A, B = B, A
        if B[9] > C[9]:
            B, C = C, B
        if A[9] > B[9]:
            A, B = B, A

        if A[9] >= cam.height or C[9] < 0 or A[9] == C[9]:
            return
        
        
        
        if A[9] == B[9]:
            # If line AB can be seen, add line AB
            if A[8] < B[8]:
                left = A
                right = B
            else:
                left = B
                right = A
            if A[9] >= 0:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[A[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[A[9][x]] = obj
                        depth_buffer[A[9]][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[A[9]][x] = (min(int(127 * luminance[0]), 255), 
                                          min(int(127 * luminance[1]), 255), 
                                          min(int(127 * luminance[2]), 255))
            # The rest of the triangle
            t1 = (A[8] - C[8]) / (A[9] - C[9])
            b1 = A[8] - A[9] * t1
            t2 = (B[8] - C[8]) / (B[9] - C[9])
            b2 = B[8] - B[9] * t2
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            None, 
                            None, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )    
                else:
                    # x, z, u, v, 0, 0, 0, x2d, y2d
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )            
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
        elif B[9] == C[9]:
            # If line BC can be seen, add line BC
            if B[8] < C[8]:
                left = B
                right = C
            else:
                left = C
                right = B
            if B[9] < cam.height:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[B[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[B[9]][x] = obj
                        depth_buffer[B[9]][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[B[9]][x] = (min(int(127 * luminance[0]), 255), 
                                          min(int(127 * luminance[1]), 255), 
                                          min(int(127 * luminance[2]), 255))
            # The rest of the triangle
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            ) 
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
        else:
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (B[9] - A[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (n2 * A[0] + n1 * C[0],
                            n2 * A[1] + n1 * C[1],
                            n2 * A[2] + n1 * C[2],
                            None, 
                            None, 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (n2 * A[0] + n1 * C[0],
                            n2 * A[1] + n1 * C[1],
                            n2 * A[2] + n1 * C[2],
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
            t1 = (B[8] - C[8]) / (B[9] - C[9])
            b1 = B[8] - B[9] * t1
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - B[9]) / (C[9] - B[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                    min(int(127 * luminance[1]), 255), 
                                    min(int(127 * luminance[2]), 255))
    
    
    def rasterize_full(A, B, C):
        return

    
    # Just to cover 0, 1, 2, 3, 4 in a easier and faster way
    # Of course I know mode is not a number that can be campared with each other
    if cam.mode < 5:
        depth_buffer = [[cam.z_far] * cam.width for _ in range(cam.height)]
    # Shadow requires a different type of depth buffer
    if cam.mode == 5:
        # [
        #     [
        #         DEQUE:(z, u, v, obj), 
        #         ...
        #     ], 
        #     ...
        # ]
        shadow_buffer = [[deque()] * cam.width for _ in range(cam.height)]
        # [(obj_index, u_gap, v_gap), ...]
        uv_gap = []
    obj_buffer = None
    if cam.obj_buffer:
        obj_buffer = [[None] * cam.width for _ in range(cam.height)]
    # Do not need depth test for lines
    # elif cam.type in (6, 7):
    frame = [[(0, 0, 0)] * cam.width for _ in range(cam.height)]
    light:Light    # CodeUndone Vscode
    obj: Object    # CodeUndone Vscode
    # Put light in the same space as what the objects will be put in
    for light in lights:
        # Move
        light.x_in_cam = light.x - cam.x
        light.y_in_cam = light.y - cam.y
        light.z_in_cam = light.z - cam.z
        # Rotation
        light.x_in_cam, light.y_in_cam, light.z_in_cam = (
            light.x_in_cam * cam.rotation[0][0] + light.y_in_cam * cam.rotation[0][1] + light.z_in_cam * cam.rotation[0][2],
            light.x_in_cam * cam.rotation[1][0] + light.y_in_cam * cam.rotation[1][1] + light.z_in_cam * cam.rotation[1][2],
            light.x_in_cam * cam.rotation[2][0] + light.y_in_cam * cam.rotation[2][1] + light.z_in_cam * cam.rotation[2][2],
        )
        if light.type == 0:
            light.dirx_in_cam, light.diry_in_cam, light.dirz_in_cam = (
                light.dirx * cam.rotation[0][0] + light.diry * cam.rotation[0][1] + light.dirz * cam.rotation[0][2],
                light.dirx * cam.rotation[1][0] + light.diry * cam.rotation[1][1] + light.dirz * cam.rotation[1][2],
                light.dirx * cam.rotation[2][0] + light.diry * cam.rotation[2][1] + light.dirz * cam.rotation[2][2],
            ) 
        # Although only in Shadow will obj_index be needed, it only take a little more
    # time each loop, same as something like "a = 1", which is acceptable as the
    # for loop goes once a frame
    for obj_index, obj in enumerate(objects):
        for face in obj.faces:
            # Move the object
            A = vec_minus_vec_3d(obj.v[face[0][0]], (cam.x, cam.y, cam.z))
            B = vec_minus_vec_3d(obj.v[face[0][1]], (cam.x, cam.y, cam.z))
            C = vec_minus_vec_3d(obj.v[face[0][2]], (cam.x, cam.y, cam.z))
            A.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], None, None))
            B.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], None, None))
            C.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], None, None))
            # [x, y, z, u, v, snx, sny, snz, x2d, y2d]
            #  0  1  2  3  4   5    6    7    8    9    
            if obj.hastexture or obj.hasnormal_map:
                A[3], A[4] = obj.vt[face[1][0]]
                B[3], B[4] = obj.vt[face[1][1]]
                C[3], C[4] = obj.vt[face[1][2]]
            if obj.shade_smooth:
                A[5], A[6], A[7] = obj.svn[face[3][0]]
                B[5], B[6], B[7] = obj.svn[face[3][1]]
                C[5], C[6], C[7] = obj.svn[face[3][2]]
            
            # Culling
            # if cam.mode <= 4 or cam.mode == 6:
            #     # Remove those impossible to be seen based on the normal
            #     # cam_to_point = vec_minus_vec_3d((cam.x, cam.y, cam.z), A[:3])
            #     if dot_product_v3d(A[:3], obj.vn[face[2]]) > 0:
            #         continue

            # Rotate the object
            Ax, Bx, Cx, = A[0], B[0], C[0],
            Ay, By, Cy, = A[1], B[1], C[1],
            Az, Bz, Cz, = A[2], B[2], C[2], 
            Asnx, Asny, Asnz = A[5], A[6], A[7]
            A[0] = cam.rotation[0][0] * Ax + cam.rotation[0][1] * Ay + cam.rotation[0][2] * Az
            A[1] = cam.rotation[1][0] * Ax + cam.rotation[1][1] * Ay + cam.rotation[1][2] * Az
            A[2] = cam.rotation[2][0] * Ax + cam.rotation[2][1] * Ay + cam.rotation[2][2] * Az
            B[0] = cam.rotation[0][0] * Bx + cam.rotation[0][1] * By + cam.rotation[0][2] * Bz
            B[1] = cam.rotation[1][0] * Bx + cam.rotation[1][1] * By + cam.rotation[1][2] * Bz
            B[2] = cam.rotation[2][0] * Bx + cam.rotation[2][1] * By + cam.rotation[2][2] * Bz
            C[0] = cam.rotation[0][0] * Cx + cam.rotation[0][1] * Cy + cam.rotation[0][2] * Cz
            C[1] = cam.rotation[1][0] * Cx + cam.rotation[1][1] * Cy + cam.rotation[1][2] * Cz
            C[2] = cam.rotation[2][0] * Cx + cam.rotation[2][1] * Cy + cam.rotation[2][2] * Cz
            A[5] = cam.rotation[0][0] * Asnx + cam.rotation[0][1] * Asny + cam.rotation[0][2] * Asnz
            A[6] = cam.rotation[1][0] * Asnx + cam.rotation[1][1] * Asny + cam.rotation[1][2] * Asnz
            A[7] = cam.rotation[2][0] * Asnx + cam.rotation[2][1] * Asny + cam.rotation[2][2] * Asnz
            if obj.shade_smooth:
                Bsnx, Bsny, Bsnz = B[5], B[6], B[7]
                Csnx, Csny, Csnz = C[5], C[6], C[7]
                B[5] = cam.rotation[0][0] * Bsnx + cam.rotation[0][1] * Bsny + cam.rotation[0][2] * Bsnz
                B[6] = cam.rotation[1][0] * Bsnx + cam.rotation[1][1] * Bsny + cam.rotation[1][2] * Bsnz
                B[7] = cam.rotation[2][0] * Bsnx + cam.rotation[2][1] * Bsny + cam.rotation[2][2] * Bsnz
                C[5] = cam.rotation[0][0] * Csnx + cam.rotation[0][1] * Csny + cam.rotation[0][2] * Csnz
                C[6] = cam.rotation[1][0] * Csnx + cam.rotation[1][1] * Csny + cam.rotation[1][2] * Csnz
                C[7] = cam.rotation[2][0] * Csnx + cam.rotation[2][1] * Csny + cam.rotation[2][2] * Csnz
                normal = None
            else:
                # Suprisingly, "normal = (A[5], A[6], A[7])" is slightly
                # faster than "normal = A[5:8]"
                normal = (A[5], A[6], A[7])

            # Clipping
            # Remove those too far or behind the camera
            if ((A[2] <= cam.z_near or A[2] >= cam.z_far) and
                (B[2] <= cam.z_near or B[2] >= cam.z_far) and
                (C[2] <= cam.z_near or C[2] >= cam.z_far)):
                continue
            inside = []
            outside = []
            # Can optimize here, remove the for loop
            for vertex in (A, B, C):
                if vertex[2] > cam.z_near:
                    inside.append(vertex)
                else:
                    outside.append(vertex)
            # Clip into two triangles
            if len(inside) == 2:
                # Compute the parameter t where the line intersects the plane
                t = (cam.z_near - outside[0][2]) / (inside[0][2] - outside[0][2])
                # Calculate the intersection point
                inside.append(
                    [   
                        # x, y, z
                         outside[0][0] + t * (inside[0][0] - outside[0][0]),
                         outside[0][1] + t * (inside[0][1] - outside[0][1]),
                         outside[0][2] + t * (inside[0][2] - outside[0][2]),
                        # u, v
                         outside[0][3] + t * (inside[0][3] - outside[0][3]),
                         outside[0][4] + t * (inside[0][4] - outside[0][4]),
                        # snx, sny, snz
                         outside[0][5] + t * (inside[0][5] - outside[0][5]),
                         outside[0][6] + t * (inside[0][6] - outside[0][6]),
                         outside[0][7] + t * (inside[0][7] - outside[0][7]),
                        # x2d, y2d
                        None, None
                    ]
                )
                # Compute the parameter t where the line intersects the plane
                t = (cam.z_near - outside[0][2]) / (inside[1][2] - outside[0][2])
                # Calculate the intersection point
                inside.append(
                    [ 
                        # x, y, z
                         outside[0][0] + t * (inside[1][0] - outside[0][0]),
                         outside[0][1] + t * (inside[1][1] - outside[0][1]),
                         outside[0][2] + t * (inside[1][2] - outside[0][2]),
                        # u, v
                         outside[0][3] + t * (inside[1][3] - outside[0][3]),
                         outside[0][4] + t * (inside[1][4] - outside[0][4]),
                        # snx, sny, snz
                         outside[0][5] + t * (inside[1][5] - outside[0][5]),
                         outside[0][6] + t * (inside[1][6] - outside[0][6]),
                         outside[0][7] + t * (inside[1][7] - outside[0][7]),
                        # x2d, y2d
                        None, None
                    ]
                )
            elif len(inside) == 1:
                # Compute the parameter t where the line intersects the plane
                t = (cam.z_near - outside[0][2]) / (inside[0][2] - outside[0][2])
                # Calculate the intersection point
                inside.append(
                    [
                        # x, y, z
                         outside[0][0] + t * (inside[0][0] - outside[0][0]),
                         outside[0][1] + t * (inside[0][1] - outside[0][1]),
                         outside[0][2] + t * (inside[0][2] - outside[0][2]),
                        # u, v
                         outside[0][3] + t * (inside[0][3] - outside[0][3]),
                         outside[0][4] + t * (inside[0][4] - outside[0][4]),
                        # snx, sny, snz
                         outside[0][5] + t * (inside[0][5] - outside[0][5]),
                         outside[0][6] + t * (inside[0][6] - outside[0][6]),
                         outside[0][7] + t * (inside[0][7] - outside[0][7]),
                        # x2d, y2d
                        None, None
                    ]
                )
                # Compute the parameter t where the line intersects the plane
                t = (cam.z_near - outside[1][2]) / (inside[0][2] - outside[1][2])
                # Calculate the intersection point
                inside.append(
                    [
                        # x, y, z
                         outside[1][0] + t * (inside[0][0] - outside[1][0]),
                         outside[1][1] + t * (inside[0][1] - outside[1][1]),
                         outside[1][2] + t * (inside[0][2] - outside[1][2]),
                        # u, v
                         outside[1][3] + t * (inside[0][3] - outside[1][3]),
                         outside[1][4] + t * (inside[0][4] - outside[1][4]),
                        # snx, sny, snz
                         outside[1][5] + t * (inside[0][5] - outside[1][5]),
                         outside[1][6] + t * (inside[0][6] - outside[1][6]),
                         outside[1][7] + t * (inside[0][7] - outside[1][7]),
                        # x2d, y2d
                        None, None
                    ]
                )
            
            for vertex in inside:
                x = vertex[0] * cam.rendering_plane_z / vertex[2]
                y = vertex[1] * cam.rendering_plane_z / vertex[2]
                vertex[8] = cam.width // 2 + int(x)
                vertex[9] = cam.height // 2 - int(y)

            if cam.mode == 0:
                pass
            elif cam.mode == 1:
                rasterize_solid(inside[0], inside[1], inside[2], normal)
                if len(inside) == 4:
                    rasterize_solid(inside[1], inside[2], inside[3], normal)
            elif cam.mode == 2:
                pass
            elif cam.mode == 3:
                pass
            elif cam.mode == 4:
                pass
            elif cam.mode in (6, 7):
                add_line(inside[0], inside[1])
                add_line(inside[1], inside[2])
                add_line(inside[0], inside[2])
                if len(inside) == 4:
                    add_line(inside[3], inside[1])
                    add_line(inside[3], inside[2])

        
        if cam.mode != 5:
            return frame, obj_buffer
        else:
            return shadow_buffer, uv_gap


def display(frame) -> None:
    frame_in_str = []
    for row in frame:
        for pixel in row:
            if pixel == (0, 0, 0):
                frame_in_str.append("  ")
            else:
                frame_in_str.append(
                    f"\033[38;2;{pixel[0]};{pixel[1]};{pixel[2]}m██"
                )
        frame_in_str.append("\n")
    print("".join(frame_in_str), end="\033[0m")



if __name__ == "__main__":
    # render(None, None, None)
    # exit()
    Object.default_obj_dir = "models/"
    Object.load_obj(Object, "cube")
    cam = Camera(x=0.0, y = 1.8, z=-2.0, mode=1, 
                        #   width=74, height=37
                        )
    frame, _ = render(Object.objects, Light.lights, cam)
    display(frame)

    from msvcrt import getwch
    step = 0.2
    while True:
        print("\033[F" * 300)
        frame, _ = render(Object.objects, Light.lights, cam)
        display(frame)
        print(cam)
        

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