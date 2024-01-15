# This version of code is optimized for Readability
# It would be easier to understand how the code works by reading the version
# However, it would perform way worse than the version optimized for Performace

# Undone part will be marked as CodeUndone

import math, png
png.Png.default_dir = ""
# Check if mtl file or/and png file exist(s)
from os.path import isfile
# Pause to show warning
from time import sleep
# Used to in shadow map
from collections import deque



class Object:
    # objects = [<Object>, ...]
    objects = []
    default_loading_dir = "E:/Programming/Python/Python-3D-renderer/models/"
    default_uv_map_properties = (192, 192, 127, 127, 127)
    # coordinates will be stored in lists instead of tuples so
    # it's easier to transform an object
    v = []
    vn = []
    # uv coordinates will be stored in tuples because there
    # seems to be no need to change them later
    vt = []


    def __init__(self, name) -> None:
        self.name = name
        self.faces_count = None
        self.shade_smooth = False
        # Material instance if exists
        self.mtl = None
        self.hastexture = False
        self.hasnormal_map = False
        self.faces = []
        self.hidden = False
        # if shadow == False, neither will it cast any shadow nor 
        # any shadow will be casted on it
        # It will be ignore during the shadow baking process right away
        # If an object does not have uv coordinates, it will be false
        # (because it require me to write a unwrapping function to 
        # assign the uv coordinates, which i don't intend to)
        self.shadow = True
        # texture if it has one, and if it does not, the uv_map will
        # be created according to Object.default_uv_map_size
        self.uv_map = None
        # [[x, y, z], [...], ...]
        self.svn = []


    def load_obj(filename:str, dir=default_loading_dir) -> dict:
        """
        Load an object or objects from an obj file.
        .obj is allowed to be missing
        """
        dir = dir.replace("\\", "/")
        if not filename.endswith(".obj"):
            filename += ".obj"
        if dir != "" and not dir.endswith("/"):
            dir += "/"
        filepath = dir + filename
        print(f"Starts to load the obj file: {filename} \n(Path: {filepath})")
        # Also, using line[...:...] may be faster than line.startswith
        with open(filepath, "r") as obj_file:
            # Will be added to the f value
            convert_to_left_hand = False
            if obj_file.readline(9) == "# Blender":
                convert_to_left_hand = True
            v_starting_at = len(Object.v)
            vt_starting_at = len(Object.vt)
            vn_starting_at = len(Object.vn)
            for line in obj_file.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith("mtllib "):
                    print(f"Loading MTL file: {dir + line[7:]}")
                    mtl_loaded = Material.load_mtl(line[7:], dir)
                elif line.startswith("o "):
                    current_obejct = Object(name = line[2:])
                    Object.objects.append(current_obejct)
                    print(f"Loading {current_obejct.name}")
                elif line.startswith("v "):
                    Object.v.append(list(map(float, line[2:].split())))
                    if convert_to_left_hand:
                        Object.v[-1][2] *= -1
                elif line.startswith("vt "):
                    Object.vt.append(tuple(map(float, line[3:].split())))
                    if convert_to_left_hand:
                        Object.vt[-1] = (Object.vt[-1][0], 1 - Object.vt[-1][1])
                elif line.startswith("vn "):
                    Object.vn.append(list(map(float, line[3:].split())))
                    if convert_to_left_hand:
                        Object.vn[-1][2] *= -1
                elif line in ("s 1", "s on"):
                    current_obejct.shade_smooth = True
                elif line.startswith("usemtl ") and mtl_loaded:
                    current_obejct.mtl = Material.materials[line[7:]]
                elif line.startswith("f "):
                    face = line[2:].split()
                    # v&vn
                    if "//" in face[0]:
                        face = (face[0].split("//"), face[1].split("//"), face[2].split("//"))
                        face = [
                            (int(face[0][0]) + v_starting_at - 1, 
                             int(face[1][0]) + v_starting_at - 1, 
                             int(face[2][0]) + v_starting_at - 1),
                             None,
                             int(face[0][2]) + vn_starting_at - 1,
                             [None, None, None],
                        ]
                    # v or v&vt&vn
                    else:
                        face = (face[0].split("/"), face[1].split("/"), face[2].split("/"))
                        # v
                        if len(face[0]) == 1:
                            face = [
                                (int(face[0][0]) + v_starting_at - 1, 
                                 int(face[1][0]) + v_starting_at - 1, 
                                 int(face[2][0]) + v_starting_at - 1),
                                None,
                                None,
                                [None, None, None],
                            ]
                        # v&vt
                        elif len(face[0]) == 2:
                            face = [
                                (int(face[0][0]) + v_starting_at - 1, 
                                 int(face[1][0]) + v_starting_at - 1, 
                                 int(face[2][0]) + v_starting_at - 1),
                                (int(face[0][1]) + vt_starting_at - 1, 
                                 int(face[1][1]) + vt_starting_at - 1,
                                 int(face[2][1]) + vt_starting_at - 1),
                                None,
                                [None, None, None],
                            ]
                        # v&vt&vn
                        else:    # elif len(face[0]) == 3:
                            face = [
                                (int(face[0][0]) + v_starting_at - 1, 
                                 int(face[1][0]) + v_starting_at - 1, 
                                 int(face[2][0]) + v_starting_at - 1),
                                (int(face[0][1]) + vt_starting_at - 1, 
                                 int(face[1][1]) + vt_starting_at - 1,
                                 int(face[2][1]) + vt_starting_at - 1),
                                int(face[0][2]) + vn_starting_at - 1,
                                [None, None, None],
                            ]
                    current_obejct.faces.append(face)

        print("Finish loading from files. Starts to post-process the object(s) loaded.")

        # So far, hastexture and hasnormal_map are all False, which will
        # be determined in the next step.
        # shadow is True by default, but will be disabled if the object
        # does not have uv coordinates, which should be created by
        # means like unwrapping in blender in advance.
        obj:Object    # CodeUndone 
        for obj in Object.objects:
            obj.faces_count = len(obj.faces)
            obj.calculate_face_normals()
            if obj.shade_smooth == True:
                obj.calculate_smooth_shading_normals()
            # If the object does not have uv coordinates, none of
            # shadow, texture or normal map will apply
            if obj.faces[0][1] == None:
                obj.shadow = False
                continue
            if obj.mtl != None:
                if obj.mtl.texture != None:
                    obj.hastexture = True
                    obj.uv_map = png.Png(obj.mtl.texture_path, "", to_pickle=False).pixels
                if Material.materials[obj.mtl].normal_map != None:
                    obj.hasnormal_map = True
            # No texture, create one
            if obj.uv_map == None:
                obj.uv_map = [
                    [Object.default_uv_map_properties[2:]] * 
                    Object.default_uv_map_properties[0]
                    for _ in range(Object.default_uv_map_properties[1])
                ]
        print("Obj loading done")
    

    def __str__(self):
        return (
            f"Name: {self.name}\n" + 
            f"Faces Count: {self.faces_count}\n" +
            f"Has Texture: {self.hastexture}\n" +
            f"Texture Path: {self.mtl.texture_path}\n" if self.hastexture else "" +
            f"Has Normal Map:{self.hasnormal_map}\n" 
            f"Normal Map Path: {self.mtl.normal_map_path}\n" if self.hasnormal_map else ""
        )

    
    def normalize_v3d(vector):
        # May be about left/right hand coordinate sys?
        length = - math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        return [vector[0] / length, vector[1] / length, vector[2] / length,]
    

    def cross_product_v3d(v, u):
        return [v[1] * u[2] - v[2] * u[1],
                v[2] * u[0] - v[0] * u[2],
                v[0] * u[1] - v[1] * u[0]]
    

    def dot_product_v3d(v, u):
        return v[0] * u[0] + v[1] * u[1] + v[2] * u[2]
    

    def vec_minus_vec_3d(v, u):
        return [v[0] - u[0], v[1] - u[1], v[2] - u[2]]


    def calculate_face_normals(self):
        """
        Check whether obj.faces stores the normal or not
        If not, it will go over every face and calculate the normal
        """
        if self.faces[0][2] != None:
            return
        for face in self.faces:
            normal = Object.normalize_v3d(
                        Object.cross_product_v3d(
                            Object.vec_minus_vec_3d(
                                Object.v[face[0][2]], 
                                Object.v[face[0][0]]
                            ),
                            Object.vec_minus_vec_3d(
                                Object.v[face[0][1]], 
                                Object.v[face[0][0]]
                            )
                        )
                     )
            try:
                index = Object.vn.index(normal)
            except ValueError:
                index = len(Object.vn)
                Object.vn.append(normal)
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
            return Object.normalize_v3d((sum(transformed_vecs[0]), sum(transformed_vecs[1]), sum(transformed_vecs[2])))
        if self.faces[0][2] == None:
            self.calculate_face_normals()
        # v_vn = {v: [([nx, ny, nz], face_index, vertex_index_in_a_face), (...)], 
        #         v: [(...), ...], 
        #         ...}
        v_vn = {}
        for findex, face in enumerate(self.faces):
            for i in (0, 1, 2):
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
    materials = {}
    def __init__(self, name):
        self.name = name
        if name in Material.materials:
            raise Exception("Name Collision: 2 or more materials share the same name.")
        else:
            Material.materials[name] = self
        self.texture = None
        self.normal_map = None
        self.texture_path = None
        self.normal_map_path = None


    def load_mtl(filename:str, dir:str):
        if not isfile(dir + filename):
            print("\033[1;31m" +
                  "WARNING: MTL FILE NO FOUND.\n")
            sleep(2)
            return False
        
        with open(dir + filename, "r") as mtl_file:
            for line in mtl_file.readlines():
                if line.startswith("#"):
                    continue
                elif line.startswith("newmtl "):
                    current_material = Material(line.strip()[7:])
                elif line.startswith("map_Kd "):
                    img = line.strip()[7:]
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
                            current_material.texture = png.Png(img, dir)
                            current_material.texture_path = dir + img
                    
                elif line.startswith("map_Bump "):
                    img = line.strip().split()[-1]
                    # Absolute path
                    if "/" in img:
                        if not isfile(img):
                            print("\033[1;31m" +
                                "WARNING: NORMAL MAP FILE NO FOUND.\n")
                            sleep(2)
                        else:
                            current_material.normal_map = png.Png(img)
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
        print("Finish loading materials.")
        return True



class Light:
    light_sources = []
    # (width, height, z_near, z_far, fxaa)
    default_shadow_properties = (256, 256, 0.1, 50, True)
    def __init__(self, x, y, z, strength=(1, 1, 1), direction=None, type=1) -> None:
        """
        type 0 for parallel light source
        type 1 for point light source
        direction is necessary if type == 0. 
        direction should be in the format of (x, y, z) or [x, y, z]
        """
        self.type = type
        self.strength = strength
        self.position = (x, y, z)
        if type == 0:
            if direction == None:
                raise Exception("direction is missing. "+ 
                                "It is required for parallel light source.")
            self.direction = tuple(direction)
            inversed_length = 1 / math.sqrt(self.direction[0] * self.direction[0] + 
                                            self.direction[1] * self.direction[1] +
                                            self.direction[2] * self.direction[2])
            if inversed_length != 1:
                self.direction = (self.direction[0] * inversed_length,
                                  self.direction[1] * inversed_length,
                                  self.direction[2] * inversed_length,)
        self.cam_space_position = None
        self.hidden = False
    

    def add_light(x, y, z, strength=(1, 1, 1), direction=None, type=1):
        Light.light_sources.append(Light(x, y, z, strength, direction, type))

    
    def add_shadows():
        light: Light    # CodeUndone Just for VsCode
        for light in Light.light_sources:
            if light.type == 0:
                Light.cast_shadow(Light.bake_shadow_parallel(light))
            elif light.type == 1:
                Light.cast_shadow(Light.bake_shadow_point(light)) 


    def bake_shadow_point(light) -> tuple:
        return
    

    def bake_shadow_parallel(light) -> tuple:
        return
    

    def cast_shadow(shadow_map, uv_distance) -> None:
        pass



class Camera:
    def __init__(self, x=0, y=0, z=0, yaw=90, pitch=0, z_near=0.1, z_far=50, fov=75) -> None:
        self.x, self.y, self.z = x, y, z
        self.z_near, self.z_far = z_near, z_far
        self.fov = fov
        self.yaw = 0
        self.pitch = 0
        self.update_rotation(yaw, pitch)

    
    def __str__(self) -> str:
        return (f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})  |  " +
                f"Yaw:{(self.yaw + 180) % 360 - 180:.3f} " + 
                f"Pitch:{(self.pitch + 180) % 360 - 180:.3f}  |  " 
                # + "Rotation: " +
                # f"X:({self.rotation[0][0]:.3f}, {self.rotation[0][1]:.3f}, {self.rotation[0][2]:.3f}) " +
                # f"Y:({self.rotation[1][0]:.3f}, {self.rotation[1][1]:.3f}, {self.rotation[1][2]:.3f}) " +
                # f"Z:({self.rotation[2][0]:.3f}, {self.rotation[2][1]:.3f}, {self.rotation[2][2]:.3f}) "
                )

    
    def update_rotation(self, delta_yaw=0, delta_pitch=0):
        self.yaw += delta_yaw
        self.pitch += delta_pitch
        yaw = self.yaw * math.pi / 180
        pitch = self.pitch * math.pi / 180
        self.rotation = [[math.sin(yaw), 0, -math.cos(yaw),],
                         [-math.sin(pitch) * math.cos(yaw), math.cos(pitch), -math.sin(pitch) * math.sin(yaw)],
                         [math.cos(yaw) * math.cos(pitch), math.sin(pitch), math.sin(yaw) * math.cos(pitch),]]
    

    def mat_multi_mat_3d(mat1, mat2):
        return (
            (mat2[0][0] * mat1[0][0] + mat2[1][0] * mat1[1][0] + mat2[2][0] * mat1[2][0], mat2[0][0] * mat1[0][1] + mat2[1][0] * mat1[1][1] + mat2[2][0] * mat1[2][1], mat2[0][0] * mat1[0][2] + mat2[1][0] * mat1[1][2] + mat2[2][0] * mat1[2][2]),
            (mat2[0][1] * mat1[0][0] + mat2[1][1] * mat1[1][0] + mat2[2][1] * mat1[2][0], mat2[0][1] * mat1[0][1] + mat2[1][1] * mat1[1][1] + mat2[2][1] * mat1[2][1], mat2[0][1] * mat1[0][2] + mat2[1][1] * mat1[1][2] + mat2[2][1] * mat1[2][2]),
            (mat2[0][2] * mat1[0][0] + mat2[1][2] * mat1[1][0] + mat2[2][2] * mat1[2][0], mat2[0][2] * mat1[0][1] + mat2[1][2] * mat1[1][1] + mat2[2][2] * mat1[2][1], mat2[0][2] * mat1[0][2] + mat2[1][2] * mat1[1][2] + mat2[2][2] * mat1[2][2]),
        )


    def yaw(self, theta):
        theta = theta * math.pi / 180
        r_mat = (
            (math.cos(theta), 0, math.sin(theta)),
            (0, 1, 0),
            (-math.sin(theta), 0, math.cos(theta))
        )
        self.rotation = Camera.mat_multi_mat_3d(self.rotation, r_mat,)
    def pitch(self, theta):
        theta = theta * math.pi / 180
        r_mat = (
            (1, 0, 0),
            (0, math.cos(theta), -math.sin(theta)),
            (0, math.sin(theta), math.cos(theta))
        )
        self.rotation = Camera.mat_multi_mat_3d(self.rotation, r_mat,)
    def roll(self, theta):
        theta = theta * math.pi / 180
        r_mat = (
            (math.cos(theta), -math.sin(theta), 0),
            (math.sin(theta), math.cos(theta), 0),
            (0, 0, 1)
        )
        self.rotation = Camera.mat_multi_mat_3d(self.rotation, r_mat,)



class Scene:
    objects = []
    light_sources = []
    def __init__(self) -> None:
        import os
        print("\033[0m")
        os.system("cls")
        self.cam = Camera()
        self.width, self.height = self.get_screen_size()
    

    def get_screen_size(self, width_reserved=3, height_reserved=3) -> tuple:
        import os
        width, height = os.get_terminal_size()
        return width // 2 - width_reserved, height - height_reserved


    def add_light(self, x, y, z, strength=(1, 1, 1), direction=None, type=1):
        Light.light_sources.append(Light(x, y, z, strength, direction, type))
    



def render(cam:Camera, width, height, projection_matrix, render_solid=False, in_lines=False, culling=True) -> list:
    def dot_product_v3d(v, u):
        return v[0] * u[0] + v[1] * u[1] + v[2] * u[2]
    
    def vec_minus_vec_3d(v, u) -> tuple:
        return v[0] - u[0],  v[1] - u[1],  v[2] - u[2]
    
    def vec_squared_len_3d(v) -> float:
        return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

    def mat_multiply_vec_4d(mat, vec):
        return [mat[0][0] * vec[0] + mat[0][1] * vec[1] + mat[0][2] * vec[2] + mat[0][3] * vec[3],
                mat[1][0] * vec[0] + mat[1][1] * vec[1] + mat[1][2] * vec[2] + mat[1][3] * vec[3],
                mat[2][0] * vec[0] + mat[2][1] * vec[1] + mat[2][2] * vec[2] + mat[2][3] * vec[3],
                mat[3][0] * vec[0] + mat[3][1] * vec[1] + mat[3][2] * vec[2] + mat[3][3] * vec[3],]

    def get_luminance(normal, x3d, y3d, z3d) -> list:
        # Default value for no light at all
        # can be adjusted according to needs
        luminance = [0.05, 0.05, 0.05]
        for light in Light.light_sources:
            if light.type == 0:
                b = - ((light.direction[0] * normal[0] + 
                        light.direction[1] * normal[1] +
                        light.direction[2] * normal[2]) - 1) / 2
                luminance[0] += light.strength[0] * b
                luminance[1] += light.strength[1] * b
                luminance[2] += light.strength[2] * b
            else:    # light.type == 1
                direction = (
                    light.cam_space_position[0] - x3d,
                    light.cam_space_position[1] - y3d,
                    light.cam_space_position[2] - z3d,
                )
                length = math.sqrt(direction[0]**2 + direction[1]**2 + direction[2]**2)
                b = max(0, 
                        (
                            (
                                direction[0] * normal[0] + 
                                direction[1] * normal[1] +
                                direction[2] * normal[2]
                            )
                        ) / 
                        length**2
                    )
                
                luminance[0] += light.strength[0] * b
                luminance[1] += light.strength[1] * b
                luminance[2] += light.strength[2] * b
        return luminance

    def rasterize(A, B, C):
        # CodeUndone Debugging xyz3d
        # if A[5:8] == [0, 0, -1]: return
        if A[9] > B[9]:
            A, B = B, A
        if B[9] > C[9]:
            B, C = C, B
        if A[9] > B[9]:
            A, B = B, A
        if A[9] >= height or C[9] < 0 or A[9] == C[9]:
            return
        

        if in_lines:
            # Won't update the z-buffer
            def line(P, Q):
                if P[8] == Q[8]:
                    for y in range(max(0, min(P[9], Q[9])), min(height - 1, max(P[9], Q[9]))):
                        if 0 <= (x:=int(P[8])) < width:
                            frame[y][x] = (127, 127, 127)
                elif abs(slope := (P[9] - Q[9]) / (P[8] - Q[8])) <= 1:
                    for x in range(max(0, min(P[8], Q[8])), min(width - 1, max(P[8], Q[8]))):
                        if 0 <= (y:=int(slope * (x - P[8]) + P[9])) < height:
                            frame[y][x] = (127, 127, 127)
                else:
                    slope = 1 / slope
                    for y in range(max(0, min(P[9], Q[9])), min(height - 1, max(P[9], Q[9]))):
                        if 0 <= (x:=int(slope * (y - P[9]) + P[8])) < width:
                            frame[y][x] = (127, 127, 127)
            line(A, B)
            line(B, C)
            line(C, A)
            
        elif render_solid or not obj.texture and not obj.normal_map:
            if obj.smooth_shading:
                pass
            else:    # flat shading
                
                pass
        elif obj.texture and obj.normal_map:
            # CodeUndone Assuming the size of the normal map is the same as that of the texture
            # [x, y, z, u, v, snx, sny, snz, x2d, y2d]
            #  0  1  2  3  4   5    6    7    8    9  
            if A[9] == B[9]:
                # If line AB can be seen, add line AB
                if A[8] < B[8]:
                    left = A
                    right = B
                else:
                    left = B
                    right = A
                if A[9] >= 0:
                    for x in range(max(0, left[8]), min(width - 1, right[8])):
                        p1 = (x - left[8]) / (right[8] - left[8])
                        p2 = 1 - p1
                        z3d = p2 * left[2] + p1 * right[2]
                        if z3d < z_buffer[A[9]][x]:
                            z_buffer[A[9]][x] = z3d
                            u_texture = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                            u_normal_map = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].normal_map.width)
                            v_texture = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                            v_normal_map = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].normal_map.height)
                            color = Material.materials[obj.mtl].texture.pixels[v_texture][u_texture]
                            normal = Material.materials[obj.mtl].normal_map.pixels[v_normal_map][u_normal_map]
                            normal = (2 * normal[0] / 255 - 1,
                                    2 * normal[1] / 255 - 1,
                                    2 * normal[2] / 255 - 1)
                            normal = (
                                cam.rotation[0][0] * normal[0] + cam.rotation[0][1] * normal[1] + cam.rotation[0][2] * normal[2], 
                                cam.rotation[1][0] * normal[0] + cam.rotation[1][1] * normal[1] + cam.rotation[1][2] * normal[2], 
                                cam.rotation[2][0] * normal[0] + cam.rotation[2][1] * normal[1] + cam.rotation[2][2] * normal[2], 
                            )
                            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                            # calculate the light
                            x3d = p2 * left[0] + p1 * right[0]
                            y3d = p2 * left[1] + p1 * right[1]
                            luminance = get_luminance(normal, x3d, y3d, z3d)
                            frame[A[9]][x] = (min(int(color[0] * luminance[0]), 255), 
                                        min(int(color[1] * luminance[1]), 255), 
                                        min(int(color[2] * luminance[2]), 255))
                # The rest of the triangle
                t1 = (A[8] - C[8]) / (A[9] - C[9])
                b1 = A[8] - A[9] * t1
                t2 = (B[8] - C[8]) / (B[9] - C[9])
                b2 = B[8] - B[9] * t2
                for y in range(max(0, B[9]), min(height - 1, C[9])):
                    m1 = (y - A[9]) / (C[9] - A[9])
                    m2 = 1 - m1
                    # x, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            m2 * A[3] + m1 * C[3], 
                            m2 * A[4] + m1 * C[4], 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            m2 * B[3] + m1 * C[3], 
                            m2 * B[4] + m1 * C[4], 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )                
                    if left[8] > right[8]:
                        left, right = right, left
                    for x in range(max(0, left[8]), min(width - 1, right[8])):
                        p1 = (x - left[8]) / (right[8] - left[8])
                        p2 = 1 - p1
                        z3d = p2 * left[2] + p1 * right[2]
                        if z3d < z_buffer[y][x]:
                            z_buffer[y][x] = z3d
                            u_texture = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                            u_normal_map = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].normal_map.width)
                            v_texture = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                            v_normal_map = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].normal_map.height)
                            color = Material.materials[obj.mtl].texture.pixels[v_texture][u_texture]
                            normal = Material.materials[obj.mtl].normal_map.pixels[v_normal_map][u_normal_map]
                            normal = (2 * normal[0] / 255 - 1,
                                    2 * normal[1] / 255 - 1,
                                    2 * normal[2] / 255 - 1)
                            normal = (
                                cam.rotation[0][0] * normal[0] + cam.rotation[0][1] * normal[1] + cam.rotation[0][2] * normal[2], 
                                cam.rotation[1][0] * normal[0] + cam.rotation[1][1] * normal[1] + cam.rotation[1][2] * normal[2], 
                                cam.rotation[2][0] * normal[0] + cam.rotation[2][1] * normal[1] + cam.rotation[2][2] * normal[2], 
                            )
                            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                            # calculate the light
                            x3d = p2 * left[0] + p1 * right[0]
                            y3d = p2 * left[1] + p1 * right[1]
                            luminance = get_luminance(normal, x3d, y3d, z3d)
                            frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                        min(int(color[1] * luminance[1]), 255), 
                                        min(int(color[2] * luminance[2]), 255))
            elif B[9] == C[9]:
                # If line BC can be seen, add line BC
                if B[8] < C[8]:
                    left = B
                    right = C
                else:
                    left = C
                    right = B
                if B[9] < height:
                    for x in range(max(0, left[8]), min(width - 1, right[8])):
                        p1 = (x - left[8]) / (right[8] - left[8])
                        p2 = 1 - p1
                        z3d = p2 * left[2] + p1 * right[2]
                        if z3d < z_buffer[B[9]][x]:
                            z_buffer[B[9]][x] = z3d
                            u_texture = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                            u_normal_map = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].normal_map.width)
                            v_texture = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                            v_normal_map = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].normal_map.height)
                            color = Material.materials[obj.mtl].texture.pixels[v_texture][u_texture]
                            normal = Material.materials[obj.mtl].normal_map.pixels[v_normal_map][u_normal_map]
                            normal = (2 * normal[0] / 255 - 1,
                                    2 * normal[1] / 255 - 1,
                                    2 * normal[2] / 255 - 1)
                            normal = (
                                cam.rotation[0][0] * normal[0] + cam.rotation[0][1] * normal[1] + cam.rotation[0][2] * normal[2], 
                                cam.rotation[1][0] * normal[0] + cam.rotation[1][1] * normal[1] + cam.rotation[1][2] * normal[2], 
                                cam.rotation[2][0] * normal[0] + cam.rotation[2][1] * normal[1] + cam.rotation[2][2] * normal[2], 
                            )
                            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                            # calculate the light
                            x3d = p2 * left[0] + p1 * right[0]
                            y3d = p2 * left[1] + p1 * right[1]
                            luminance = get_luminance(normal, x3d, y3d, z3d)
                            frame[B[9]][x] = (min(int(color[0] * luminance[0]), 255), 
                                        min(int(color[1] * luminance[1]), 255), 
                                        min(int(color[2] * luminance[2]), 255))
                # The rest of the triangle
                t1 = (A[8] - B[8]) / (A[9] - B[9])
                b1 = A[8] - A[9] * t1
                t2 = (A[8] - C[8]) / (A[9] - C[9])
                b2 = A[8] - A[9] * t2
                for y in range(max(0, A[9]), min(height - 1, B[9])):
                    m1 = (y - A[9]) / (C[9] - A[9])
                    m2 = 1 - m1
                    # x, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            m2 * A[3] + m1 * B[3], 
                            m2 * A[4] + m1 * B[4], 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            m2 * A[3] + m1 * C[3], 
                            m2 * A[4] + m1 * C[4], 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                    if left[8] > right[8]:
                        left, right = right, left
                    for x in range(max(0, left[8]), min(width - 1, right[8])):
                        p1 = (x - left[8]) / (right[8] - left[8])
                        p2 = 1 - p1
                        z3d = p2 * left[2] + p1 * right[2]
                        if z3d < z_buffer[y][x]:
                            z_buffer[y][x] = z3d
                            u_texture = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                            u_normal_map = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].normal_map.width)
                            v_texture = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                            v_normal_map = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].normal_map.height)
                            color = Material.materials[obj.mtl].texture.pixels[v_texture][u_texture]
                            normal = Material.materials[obj.mtl].normal_map.pixels[v_normal_map][u_normal_map]
                            normal = (2 * normal[0] / 255 - 1,
                                    2 * normal[1] / 255 - 1,
                                    2 * normal[2] / 255 - 1)
                            normal = (
                                cam.rotation[0][0] * normal[0] + cam.rotation[0][1] * normal[1] + cam.rotation[0][2] * normal[2], 
                                cam.rotation[1][0] * normal[0] + cam.rotation[1][1] * normal[1] + cam.rotation[1][2] * normal[2], 
                                cam.rotation[2][0] * normal[0] + cam.rotation[2][1] * normal[1] + cam.rotation[2][2] * normal[2], 
                            )
                            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                            # calculate the light
                            x3d = p2 * left[0] + p1 * right[0]
                            y3d = p2 * left[1] + p1 * right[1]
                            luminance = get_luminance(normal, x3d, y3d, z3d)
                            frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                        min(int(color[1] * luminance[1]), 255), 
                                        min(int(color[2] * luminance[2]), 255))
            else:
                t1 = (A[8] - B[8]) / (A[9] - B[9])
                b1 = A[8] - A[9] * t1
                t2 = (A[8] - C[8]) / (A[9] - C[9])
                b2 = A[8] - A[9] * t2
                for y in range(max(0, A[9]), min(height - 1, B[9])):
                    m1 = (y - A[9]) / (B[9] - A[9])
                    m2 = 1 - m1
                    n1 = (y - A[9]) / (C[9] - A[9])
                    n2 = 1 - n1
                    # x, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            m2 * A[3] + m1 * B[3], 
                            m2 * A[4] + m1 * B[4], 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (n2 * A[0] + n1 * C[0],
                            n2 * A[1] + n1 * C[1],
                            n2 * A[2] + n1 * C[2],
                            n2 * A[3] + n1 * C[3], 
                            n2 * A[4] + n1 * C[4], 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                    if left[8] > right[8]:
                        left, right = right, left
                    for x in range(max(0, left[8]), min(width - 1, right[8])):
                        p1 = (x - left[8]) / (right[8] - left[8])
                        p2 = 1 - p1
                        z3d = p2 * left[2] + p1 * right[2]
                        if z3d < z_buffer[y][x]:
                            z_buffer[y][x] = z3d
                            u_texture = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                            u_normal_map = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].normal_map.width)
                            v_texture = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                            v_normal_map = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].normal_map.height)
                            color = Material.materials[obj.mtl].texture.pixels[v_texture][u_texture]
                            normal = Material.materials[obj.mtl].normal_map.pixels[v_normal_map][u_normal_map]
                            normal = (2 * normal[0] / 255 - 1,
                                    2 * normal[1] / 255 - 1,
                                    2 * normal[2] / 255 - 1)
                            normal = (
                                cam.rotation[0][0] * normal[0] + cam.rotation[0][1] * normal[1] + cam.rotation[0][2] * normal[2], 
                                cam.rotation[1][0] * normal[0] + cam.rotation[1][1] * normal[1] + cam.rotation[1][2] * normal[2], 
                                cam.rotation[2][0] * normal[0] + cam.rotation[2][1] * normal[1] + cam.rotation[2][2] * normal[2], 
                            )
                            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                            # calculate the light
                            x3d = p2 * left[0] + p1 * right[0]
                            y3d = p2 * left[1] + p1 * right[1]
                            luminance = get_luminance(normal, x3d, y3d, z3d)
                            frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                        min(int(color[1] * luminance[1]), 255), 
                                        min(int(color[2] * luminance[2]), 255))
                t1 = (B[8] - C[8]) / (B[9] - C[9])
                b1 = B[8] - B[9] * t1
                for y in range(max(0, B[9]), min(height - 1, C[9])):
                    m1 = (y - B[9]) / (C[9] - B[9])
                    m2 = 1 - m1
                    n1 = (y - A[9]) / (C[9] - A[9])
                    n2 = 1 - n1
                    # x, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            n2 * A[3] + n1 * C[3], 
                            n2 * A[4] + n1 * C[4], 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            m2 * B[3] + m1 * C[3], 
                            m2 * B[4] + m1 * C[4], 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    if left[8] > right[8]:
                        left, right = right, left
                    for x in range(max(0, left[8]), min(width - 1, right[8])):
                        p1 = (x - left[8]) / (right[8] - left[8])
                        p2 = 1 - p1
                        z3d = p2 * left[2] + p1 * right[2]
                        if z3d < z_buffer[y][x]:
                            z_buffer[y][x] = z3d
                            u_texture = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                            u_normal_map = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].normal_map.width)
                            v_texture = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                            v_normal_map = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].normal_map.height)
                            color = Material.materials[obj.mtl].texture.pixels[v_texture][u_texture]
                            normal = Material.materials[obj.mtl].normal_map.pixels[v_normal_map][u_normal_map]
                            normal = (2 * normal[0] / 255 - 1,
                                    2 * normal[1] / 255 - 1,
                                    2 * normal[2] / 255 - 1)
                            normal = (
                                cam.rotation[0][0] * normal[0] + cam.rotation[0][1] * normal[1] + cam.rotation[0][2] * normal[2], 
                                cam.rotation[1][0] * normal[0] + cam.rotation[1][1] * normal[1] + cam.rotation[1][2] * normal[2], 
                                cam.rotation[2][0] * normal[0] + cam.rotation[2][1] * normal[1] + cam.rotation[2][2] * normal[2], 
                            )
                            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                            # calculate the light
                            x3d = p2 * left[0] + p1 * right[0]
                            y3d = p2 * left[1] + p1 * right[1]
                            luminance = get_luminance(normal, x3d, y3d, z3d)
                            frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                        min(int(color[1] * luminance[1]), 255), 
                                        min(int(color[2] * luminance[2]), 255))
        elif obj.texture:
            if obj.smooth_shading:
                # [x, y, z, u, v, snx, sny, snz, x2d, y2d]
                #  0  1  2  3  4   5    6    7    8    9    
                A[5:8] = (
                            cam.rotation[0][0] * A[5:8][0] + cam.rotation[0][1] * A[5:8][1] + cam.rotation[0][2] * A[5:8][2], 
                            cam.rotation[1][0] * A[5:8][0] + cam.rotation[1][1] * A[5:8][1] + cam.rotation[1][2] * A[5:8][2], 
                            cam.rotation[2][0] * A[5:8][0] + cam.rotation[2][1] * A[5:8][1] + cam.rotation[2][2] * A[5:8][2], 
                            )
                B[5:8] = (
                            cam.rotation[0][0] * B[5:8][0] + cam.rotation[0][1] * B[5:8][1] + cam.rotation[0][2] * B[5:8][2], 
                            cam.rotation[1][0] * B[5:8][0] + cam.rotation[1][1] * B[5:8][1] + cam.rotation[1][2] * B[5:8][2], 
                            cam.rotation[2][0] * B[5:8][0] + cam.rotation[2][1] * B[5:8][1] + cam.rotation[2][2] * B[5:8][2], 
                            )
                C[5:8] = (
                            cam.rotation[0][0] * C[5:8][0] + cam.rotation[0][1] * C[5:8][1] + cam.rotation[0][2] * C[5:8][2], 
                            cam.rotation[1][0] * C[5:8][0] + cam.rotation[1][1] * C[5:8][1] + cam.rotation[1][2] * C[5:8][2], 
                            cam.rotation[2][0] * C[5:8][0] + cam.rotation[2][1] * C[5:8][1] + cam.rotation[2][2] * C[5:8][2], 
                            )
                if A[9] == B[9]:
                    # If line AB can be seen, add line AB
                    if A[8] < B[8]:
                        left = A
                        right = B
                    else:
                        left = B
                        right = A
                    if A[9] >= 0:
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[A[9]][x]:
                                z_buffer[A[9]][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                normal = (
                                    p2 * left[5] + p1 * right[5],
                                    p2 * left[6] + p1 * right[6],
                                    p2 * left[7] + p1 * right[7],
                                )
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[A[9]][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                    # The rest of the triangle
                    t1 = (A[8] - C[8]) / (A[9] - C[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (B[8] - C[8]) / (B[9] - C[9])
                    b2 = B[8] - B[9] * t2
                    for y in range(max(0, B[9]), min(height - 1, C[9])):
                        m1 = (y - A[9]) / (C[9] - A[9])
                        m2 = 1 - m1
                        # x, z, u, v, sx, sy, sz
                        left = (m2 * A[0] + m1 * C[0], 
                                m2 * A[1] + m1 * C[1], 
                                m2 * A[2] + m1 * C[2], 
                                m2 * A[3] + m1 * C[3], 
                                m2 * A[4] + m1 * C[4], 
                                m2 * A[5] + m1 * C[5], 
                                m2 * A[6] + m1 * C[6], 
                                m2 * A[7] + m1 * C[7], 
                                int(t1 * y + b1),
                                y, 
                                )            
                        right = (m2 * B[0] + m1 * C[0],
                                m2 * B[1] + m1 * C[1],
                                m2 * B[2] + m1 * C[2],
                                m2 * B[3] + m1 * C[3], 
                                m2 * B[4] + m1 * C[4], 
                                m2 * B[5] + m1 * C[5], 
                                m2 * B[6] + m1 * C[6], 
                                m2 * B[7] + m1 * C[7], 
                                int(t2 * y + b2),
                                y, 
                                )                
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                normal = (
                                    p2 * left[5] + p1 * right[5],
                                    p2 * left[6] + p1 * right[6],
                                    p2 * left[7] + p1 * right[7],
                                )
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                elif B[9] == C[9]:
                    # If line BC can be seen, add line BC
                    if B[8] < C[8]:
                        left = B
                        right = C
                    else:
                        left = C
                        right = B
                    if B[9] < height:
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[B[9]][x]:
                                z_buffer[B[9]][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                normal = (
                                    p2 * left[5] + p1 * right[5],
                                    p2 * left[6] + p1 * right[6],
                                    p2 * left[7] + p1 * right[7],
                                )
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[B[9]][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                    # The rest of the triangle
                    t1 = (A[8] - B[8]) / (A[9] - B[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (A[8] - C[8]) / (A[9] - C[9])
                    b2 = A[8] - A[9] * t2
                    for y in range(max(0, A[9]), min(height - 1, B[9])):
                        m1 = (y - A[9]) / (C[9] - A[9])
                        m2 = 1 - m1
                        # x, z, u, v, sx, sy, sz
                        left = (m2 * A[0] + m1 * B[0], 
                                m2 * A[1] + m1 * B[1], 
                                m2 * A[2] + m1 * B[2], 
                                m2 * A[3] + m1 * B[3], 
                                m2 * A[4] + m1 * B[4], 
                                m2 * A[5] + m1 * B[5], 
                                m2 * A[6] + m1 * B[6], 
                                m2 * A[7] + m1 * B[7], 
                                int(t1 * y + b1),
                                y, 
                                )  
                        right = (m2 * A[0] + m1 * C[0], 
                                m2 * A[1] + m1 * C[1], 
                                m2 * A[2] + m1 * C[2], 
                                m2 * A[3] + m1 * C[3], 
                                m2 * A[4] + m1 * C[4], 
                                m2 * A[5] + m1 * C[5], 
                                m2 * A[6] + m1 * C[6], 
                                m2 * A[7] + m1 * C[7], 
                                int(t2 * y + b2),
                                y, 
                                )  
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                normal = (
                                    p2 * left[5] + p1 * right[5],
                                    p2 * left[6] + p1 * right[6],
                                    p2 * left[7] + p1 * right[7],
                                )
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                else:
                    t1 = (A[8] - B[8]) / (A[9] - B[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (A[8] - C[8]) / (A[9] - C[9])
                    b2 = A[8] - A[9] * t2
                    for y in range(max(0, A[9]), min(height - 1, B[9])):
                        m1 = (y - A[9]) / (B[9] - A[9])
                        m2 = 1 - m1
                        n1 = (y - A[9]) / (C[9] - A[9])
                        n2 = 1 - n1
                        # x, z, u, v, sx, sy, sz
                        left = (m2 * A[0] + m1 * B[0], 
                                m2 * A[1] + m1 * B[1], 
                                m2 * A[2] + m1 * B[2], 
                                m2 * A[3] + m1 * B[3], 
                                m2 * A[4] + m1 * B[4], 
                                m2 * A[5] + m1 * B[5], 
                                m2 * A[6] + m1 * B[6], 
                                m2 * A[7] + m1 * B[7], 
                                int(t1 * y + b1),
                                y, 
                                )  
                        right = (n2 * A[0] + n1 * C[0],
                                n2 * A[1] + n1 * C[1],
                                n2 * A[2] + n1 * C[2],
                                n2 * A[3] + n1 * C[3], 
                                n2 * A[4] + n1 * C[4], 
                                n2 * A[5] + n1 * C[5], 
                                n2 * A[6] + n1 * C[6], 
                                n2 * A[7] + n1 * C[7], 
                                int(t2 * y + b2),
                                y, 
                                )  
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                normal = (
                                    p2 * left[5] + p1 * right[5],
                                    p2 * left[6] + p1 * right[6],
                                    p2 * left[7] + p1 * right[7],
                                )
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                    t1 = (B[8] - C[8]) / (B[9] - C[9])
                    b1 = B[8] - B[9] * t1
                    for y in range(max(0, B[9]), min(height - 1, C[9])):
                        m1 = (y - B[9]) / (C[9] - B[9])
                        m2 = 1 - m1
                        n1 = (y - A[9]) / (C[9] - A[9])
                        n2 = 1 - n1
                        # x, z, u, v, sx, sy, sz
                        left = (n2 * A[0] + n1 * C[0], 
                                n2 * A[1] + n1 * C[1], 
                                n2 * A[2] + n1 * C[2], 
                                n2 * A[3] + n1 * C[3], 
                                n2 * A[4] + n1 * C[4], 
                                n2 * A[5] + n1 * C[5], 
                                n2 * A[6] + n1 * C[6], 
                                n2 * A[7] + n1 * C[7], 
                                int(t2 * y + b2),
                                y, 
                                )  
                        right = (m2 * B[0] + m1 * C[0], 
                                m2 * B[1] + m1 * C[1], 
                                m2 * B[2] + m1 * C[2], 
                                m2 * B[3] + m1 * C[3], 
                                m2 * B[4] + m1 * C[4], 
                                m2 * B[5] + m1 * C[5], 
                                m2 * B[6] + m1 * C[6], 
                                m2 * B[7] + m1 * C[7], 
                                int(t1 * y + b1),
                                y, 
                                )  
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                normal = (
                                    p2 * left[5] + p1 * right[5],
                                    p2 * left[6] + p1 * right[6],
                                    p2 * left[7] + p1 * right[7],
                                )
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
            else:    # flat shading
                normal = (
                    cam.rotation[0][0] * A[5:8][0] + cam.rotation[0][1] * A[5:8][1] + cam.rotation[0][2] * A[5:8][2], 
                    cam.rotation[1][0] * A[5:8][0] + cam.rotation[1][1] * A[5:8][1] + cam.rotation[1][2] * A[5:8][2], 
                    cam.rotation[2][0] * A[5:8][0] + cam.rotation[2][1] * A[5:8][1] + cam.rotation[2][2] * A[5:8][2], 
                )
                # [x, y, z, u, v, snx, sny, snz, x2d, y2d]
                #  0  1  2  3  4   5    6    7    8    9    
                if A[9] == B[9]:
                    # If line AB can be seen, add line AB
                    if A[8] < B[8]:
                        left = A
                        right = B
                    else:
                        left = B
                        right = A
                    if A[9] >= 0:
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[A[9]][x]:
                                z_buffer[A[9]][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[A[9]][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                    # The rest of the triangle
                    t1 = (A[8] - C[8]) / (A[9] - C[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (B[8] - C[8]) / (B[9] - C[9])
                    b2 = B[8] - B[9] * t2
                    for y in range(max(0, B[9]), min(height - 1, C[9])):
                        m1 = (y - A[9]) / (C[9] - A[9])
                        m2 = 1 - m1
                        # x, z, u, v, sx, sy, sz
                        left = (m2 * A[0] + m1 * C[0], 
                                m2 * A[1] + m1 * C[1], 
                                m2 * A[2] + m1 * C[2], 
                                m2 * A[3] + m1 * C[3], 
                                m2 * A[4] + m1 * C[4], 
                                0, 
                                0, 
                                0, 
                                int(t1 * y + b1),
                                y, 
                                )            
                        right = (m2 * B[0] + m1 * C[0], 
                                m2 * B[1] + m1 * C[1], 
                                m2 * B[2] + m1 * C[2], 
                                m2 * B[3] + m1 * C[3], 
                                m2 * B[4] + m1 * C[4], 
                                0, 
                                0, 
                                0, 
                                int(t2 * y + b2),
                                y, 
                                )                
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                elif B[9] == C[9]:
                    # If line BC can be seen, add line BC
                    if B[8] < C[8]:
                        left = B
                        right = C
                    else:
                        left = C
                        right = B
                    if B[9] < height:
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[B[9]][x]:
                                z_buffer[B[9]][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[B[9]][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                    # The rest of the triangle
                    t1 = (A[8] - B[8]) / (A[9] - B[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (A[8] - C[8]) / (A[9] - C[9])
                    b2 = A[8] - A[9] * t2
                    for y in range(max(0, A[9]), min(height - 1, B[9])):
                        m1 = (y - A[9]) / (C[9] - A[9])
                        m2 = 1 - m1
                        # x, z, u, v, sx, sy, sz
                        left = (m2 * A[0] + m1 * B[0],
                                m2 * A[1] + m1 * B[1],
                                m2 * A[2] + m1 * B[2],
                                m2 * A[3] + m1 * B[3], 
                                m2 * A[4] + m1 * B[4], 
                                0, 
                                0, 
                                0, 
                                int(t1 * y + b1),
                                y, 
                                )  
                        right = (m2 * A[0] + m1 * C[0], 
                                m2 * A[1] + m1 * C[1], 
                                m2 * A[2] + m1 * C[2], 
                                m2 * A[3] + m1 * C[3], 
                                m2 * A[4] + m1 * C[4], 
                                0, 
                                0, 
                                0, 
                                int(t2 * y + b2),
                                y, 
                                )  
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                else:
                    t1 = (A[8] - B[8]) / (A[9] - B[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (A[8] - C[8]) / (A[9] - C[9])
                    b2 = A[8] - A[9] * t2
                    for y in range(max(0, A[9]), min(height - 1, B[9])):
                        m1 = (y - A[9]) / (B[9] - A[9])
                        m2 = 1 - m1
                        n1 = (y - A[9]) / (C[9] - A[9])
                        n2 = 1 - n1
                        # x, z, u, v, sx, sy, sz
                        left = (m2 * A[0] + m1 * B[0],
                                m2 * A[1] + m1 * B[1],
                                m2 * A[2] + m1 * B[2],
                                m2 * A[3] + m1 * B[3], 
                                m2 * A[4] + m1 * B[4], 
                                0, 
                                0, 
                                0, 
                                int(t1 * y + b1),
                                y, 
                                )  
                        right = (n2 * A[0] + n1 * C[0],
                                n2 * A[1] + n1 * C[1],
                                n2 * A[2] + n1 * C[2],
                                n2 * A[3] + n1 * C[3], 
                                n2 * A[4] + n1 * C[4], 
                                0, 
                                0, 
                                0, 
                                int(t2 * y + b2),
                                y, 
                                )  
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
                    t1 = (B[8] - C[8]) / (B[9] - C[9])
                    b1 = B[8] - B[9] * t1
                    for y in range(max(0, B[9]), min(height - 1, C[9])):
                        m1 = (y - B[9]) / (C[9] - B[9])
                        m2 = 1 - m1
                        n1 = (y - A[9]) / (C[9] - A[9])
                        n2 = 1 - n1
                        # x, z, u, v, sx, sy, sz
                        left = (n2 * A[0] + n1 * C[0],
                                n2 * A[1] + n1 * C[1],
                                n2 * A[2] + n1 * C[2],
                                n2 * A[3] + n1 * C[3], 
                                n2 * A[4] + n1 * C[4], 
                                0, 
                                0, 
                                0, 
                                int(t2 * y + b2),
                                y, 
                                )  
                        right = (m2 * B[0] + m1 * C[0], 
                                m2 * B[1] + m1 * C[1], 
                                m2 * B[2] + m1 * C[2], 
                                m2 * B[3] + m1 * C[3], 
                                m2 * B[4] + m1 * C[4], 
                                0, 
                                0, 
                                0, 
                                int(t1 * y + b1),
                                y, 
                                )  
                        if left[8] > right[8]:
                            left, right = right, left
                        for x in range(max(0, left[8]), min(width - 1, right[8])):
                            p1 = (x - left[8]) / (right[8] - left[8])
                            p2 = 1 - p1
                            z3d = p2 * left[2] + p1 * right[2]
                            if z3d < z_buffer[y][x]:
                                z_buffer[y][x] = z3d
                                u = int((p2 * left[3] + p1 * right[3]) * Material.materials[obj.mtl].texture.width)
                                v = int((p2 * left[4] + p1 * right[4]) * Material.materials[obj.mtl].texture.height)
                                color = Material.materials[obj.mtl].texture.pixels[v][u]
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = get_luminance(normal, x3d, y3d, z3d)
                                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                                            min(int(color[1] * luminance[1]), 255), 
                                            min(int(color[2] * luminance[2]), 255))
        elif obj.normal_map:
            pass
        elif render_solid:
            pass

    
    # Initiate the z_buffer & frame
    z_buffer = [[cam.z_far] * width for _ in range(height)]
    frame = [[(0, 0, 0)] * width for _ in range(height)]

    light:Light    # CodeUndone Just for VSCode
    # Update the lights according to camera
    for light in Light.light_sources:
        if light.type == 1:
            position = (
                light.position[0] - cam.x,
                light.position[1] - cam.y,
                light.position[2] - cam.z,
            )
            light.cam_space_position = (
                cam.rotation[0][0] * position[0] + cam.rotation[0][1] * position[1] + cam.rotation[0][2] * position[2], 
                cam.rotation[1][0] * position[0] + cam.rotation[1][1] * position[1] + cam.rotation[1][2] * position[2], 
                cam.rotation[2][0] * position[0] + cam.rotation[2][1] * position[1] + cam.rotation[2][2] * position[2], 
            )
            pass
            
            

    obj:Object    # CodeUndone Just for VSCode
    for obj in Object.objects:
        for face in obj.faces:
            
            # Move the object
            A = Object.vec_minus_vec_3d(Object.v[face[0][0]], (cam.x, cam.y, cam.z))
            B = Object.vec_minus_vec_3d(Object.v[face[0][1]], (cam.x, cam.y, cam.z))
            C = Object.vec_minus_vec_3d(Object.v[face[0][2]], (cam.x, cam.y, cam.z))
            A.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], 0, 0))
            B.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], 0, 0))
            C.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], 0, 0))
            # [x, y, z, u, v, snx, sny, snz, x2d, y2d]
            #  0  1  2  3  4   5    6    7    8    9    
            if obj.texture or obj.normal_map:
                A[3], A[4] = Object.vt[face[1][0]]
                B[3], B[4] = Object.vt[face[1][1]]
                C[3], C[4] = Object.vt[face[1][2]]
            if obj.smooth_shading:
                A[5], A[6], A[7] = obj.svn[face[3][0]]
                B[5], B[6], B[7] = obj.svn[face[3][1]]
                C[5], C[6], C[7] = obj.svn[face[3][2]]
            
            # Culling
            if culling:
                # Remove those impossible to be seen based on the normal
                # cam_to_point = Object.vec_minus_vec_3d((cam.x, cam.y, cam.z), A[:3])
                if dot_product_v3d(A[:3], Object.vn[face[2]]) > 0:
                    continue

            # Rotate the object
            Ax, Bx, Cx, = A[0], B[0], C[0],
            Ay, By, Cy, = A[1], B[1], C[1],
            Az, Bz, Cz, = A[2], B[2], C[2],
            A[0] = cam.rotation[0][0] * Ax + cam.rotation[0][1] * Ay + cam.rotation[0][2] * Az
            A[1] = cam.rotation[1][0] * Ax + cam.rotation[1][1] * Ay + cam.rotation[1][2] * Az
            A[2] = cam.rotation[2][0] * Ax + cam.rotation[2][1] * Ay + cam.rotation[2][2] * Az
            B[0] = cam.rotation[0][0] * Bx + cam.rotation[0][1] * By + cam.rotation[0][2] * Bz
            B[1] = cam.rotation[1][0] * Bx + cam.rotation[1][1] * By + cam.rotation[1][2] * Bz
            B[2] = cam.rotation[2][0] * Bx + cam.rotation[2][1] * By + cam.rotation[2][2] * Bz
            C[0] = cam.rotation[0][0] * Cx + cam.rotation[0][1] * Cy + cam.rotation[0][2] * Cz
            C[1] = cam.rotation[1][0] * Cx + cam.rotation[1][1] * Cy + cam.rotation[1][2] * Cz
            C[2] = cam.rotation[2][0] * Cx + cam.rotation[2][1] * Cy + cam.rotation[2][2] * Cz

            # Clipping
            # Remove those are too far or behind the camera
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
                        0, 0
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
                        0, 0
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
                        0, 0
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
                        0, 0
                    ]
                )
            # len(inside) == 3    All in the Frustum
            # else:
            #     pass

            # Projection
            for vertex in inside:
                cx, cy, cz, cw = mat_multiply_vec_4d(projection_matrix, (vertex[0], vertex[1], vertex[2], 1))
                normalized_x2d, normalized_y2d, normalized_z2d = cx / cw, cy / cw, cz / cw
                vertex[8], vertex[9] = int(width * (0.5 - normalized_x2d)), int(height * (0.5 + normalized_y2d))
                # CodeUndone
                # if 0 <= vertex[8] < width and 0 <= vertex[9] < height:
                #     frame[vertex[9]][vertex[8]] = (127, 127, 0)
            
            # Rasterization
            if len(inside) == 3:
                rasterize(*inside)
            else:    # len(inside) = 4
                rasterize(*inside[:3])
                rasterize(*inside[:2], inside[3])
    # CodeUndone Debug the xyz3d solved
    # for row in z_buffer:
    #     for p in row:
    #         # if p != int(p):
    #         #     if p > round(p, 0):
    #         #         print(f"\033[42m{int(round(p, 0)):2d}", end="\033[0m")
    #         #     else:
    #         #         print(f"\033[41m{int(round(p, 0)):2d}", end="\033[0m")
    #         # else:
    #         #     print(f"{int(p):2d}", end="\033[0m")
    #         print(f"\033[38;2;{int(p*20)};{int(p*20)};{int(p*20)}m██", end="\033[0m")
    #     print("")
    # # exit()
    # print("\033[F"*10086)
    return frame


def display(frame):
    print("\033[F" * 1024)
    image = []
    for row in frame:
        for pixel in row:
            if pixel == (0, 0, 0):
                image.append("  ")
            # else:
            #     print(pixel, end="")
            else:
                image.append(f"\033[38;2;{pixel[0]};{pixel[1]};{pixel[2]}m██")
        image.append("\n")
    print("".join(image), end=f"\033[0m")




if __name__ == "__main__":
    Object.load_obj("Crafting_table", "E:\Programming\Python\Python-3D-renderer\models\Crafting_table")
    pass
    
    exit()
    scene = Scene()
    scene.load_obj("Crafting_table", )
    scene.add_light(3, 3, 3, (9, 9, 9))
    import os
    os.system("cls")
    # Object.load_obj("Furniture", "E:\Programming\Python\Python-3D-renderer\models\Furniture")
    # Object.load_obj("monkey")
    Object.load_obj("Crafting_table", "E:\Programming\Python\Python-3D-renderer\models\Crafting_table")
    # Object.objects[-1].calculate_smooth_shading_normals()
    # Object.objects[-1].smooth_shading = True
    # Object.objects[-1].calculate_face_normals()
    Light(3, 3, 3, (9, 9, 9),type=1)
    # Light(-3, -3, -3, (1.5, 1, 1),type=0)
    # exit()

    import os
    width, height = os.get_terminal_size()
    width = width // 2 - 3 
    height = height - 3
    # width, height = 40, 40
    cam = Camera(0, 0, -10, pitch=0)
    # cam = Camera(8.128, 3.999, -5.342, yaw=147, pitch=-22.5)
    cam = Camera(-6.328, 4.125, 3.105, yaw=-17.500, pitch=-32.500)
    cam = Camera(-4.950, 2.5, -4.950, yaw=-120, pitch=-30)
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





    from msvcrt import getwch
    while True:
        # print(f"{cam.x:3f} {cam.y:.3f} {cam.z:3f} {cam.rotation}")
        frame = render(cam, width, height, projection_matrix,
                    #    in_lines=True,
                    #    culling=False,
                       )
        display(frame)
        print(cam)

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
            os.system("cls")