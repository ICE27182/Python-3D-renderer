# Undone part will be marked as CodeUndone
import math

class Object:
    # objects = [<Object>, ...]
    objects = []
    default_loading_dir = "E:\\Programming\\Python\\Python-3D-renderer\\models\\"
    v = []
    vt = []
    vn = []
    def __init__(self, name) -> None:
        self.name = name
        self.smooth_shading = False
        # name(str) if exists
        self.mtl = None
        self.texture = False
        self.normal_map = False
        self.faces = []
    
    
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


    def load_obj(filename:str, dir=default_loading_dir) -> dict:
        """
        Load an object or objects from an obj file.
        """
        if not filename.endswith(".obj"):
            filename += ".obj"
        if dir != Material.default_loading_dir and not dir.endswith("\\"):
            dir += "\\"
        filepath = dir + filename

        # Can be optimized here by rearranging the if/elif order
        # Also, using line[...:...] may be faster than line.startswith
        # Not tested yet
        # Currently, it follows the order of how every group is stored in
        # the file
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
                    Material.load_mtl(line[7:], dir)
                elif line.startswith("o "):
                    current_obejct = Object(name = line[2:])
                    Object.objects.append(current_obejct)
                elif line.startswith("v "):
                    Object.v.append(list(map(float, line[2:].split())))
                    if convert_to_left_hand:
                        Object.v[-1][2] *= -1
                elif line.startswith("vt "):
                    Object.vt.append(list(map(float, line[2:].split())))
                    if convert_to_left_hand:
                        Object.vt[-1][1] = 1 - Object.vt[-1][1]
                elif line.startswith("vn "):
                    Object.vn.append(list(map(float, line[2:].split())))
                    if convert_to_left_hand:
                        Object.vn[-1][2] *= -1
                elif line in ("s 1", "s on"):
                    current_obejct.smooth_shading = True
                elif line.startswith("usemtl "):
                    current_obejct.mtl = line[7:]
                elif line.startswith("f "):
                    # v&vn
                    if "//" in line:
                        face = [group for group in zip(*[vertex.split("/") for vertex in line[2:].split()])]
                        
                        face[0] = list(map(lambda s: int(s) + v_starting_at - 1, face[0]))
                        face[1] = None
                        face[2] = vn_starting_at + int(face[2][0]) - 1
                    # v or v&vt&vn
                    else:
                        face = [list(group) for group in zip(*[list(map(int, vertex.split("/"))) for vertex in line[2:].split()])]
                        # v&vt&vn
                        if len(face) == 3:
                            face[0] = list(map(lambda n: n + v_starting_at - 1, face[0]))
                            face[1] = list(map(lambda n: n + vt_starting_at - 1, face[1]))
                            face[2] = vn_starting_at + face[2][0] - 1
                        # v
                        else:
                            face[0] = list(map(lambda n: n + v_starting_at - 1, face[0]))
                            face.extend((None, None))
                    current_obejct.faces.append(face)
        for obj in Object.objects:
            if obj.smooth_shading == True:
                obj.calculate_smooth_shading_normals()
            if obj.mtl != None:
                if Material.materials[obj.mtl].texture != None:
                    obj.texture = True
                if Material.materials[obj.mtl].normal_map != None:
                    obj.normal_map = True
            obj.calculate_face_normals()


    def calculate_face_normals(self):
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
        Average all normals on each vertex, stored in self.svn and self.faces[:][3]
        """
        def average_many_vectors_v3d(vectors):
            vectors = map(lambda ele: Object.vn[ele[0]], vectors)
            transformed_vecs = tuple(zip(*vectors))
            return Object.normalize_v3d((sum(transformed_vecs[0]), sum(transformed_vecs[1]), sum(transformed_vecs[2])))
        if self.faces[0][2] == None:
            self.calculate_face_normals()
        # v_vn = {v: [vn, vn, ...], v: ..., ...}
        self.svn = []
        if len(self.faces[0]) == 3:
            # CodeUndone 
            # map lambda +
            # or
            # for extend
            self.faces = list(map(lambda face: face + [[0, 0, 0]], self.faces))
        v_vn = {}
        for findex, face in enumerate(self.faces):
            for i in (0, 1, 2):
                if face[0][i] in v_vn:
                    v_vn[face[0][i]].append((face[2], findex, i))
                else:
                    v_vn[face[0][i]] = [(face[2], findex, i)]
        for vns in v_vn.values():
            avg = average_many_vectors_v3d(vns)
            self.svn.append(avg)
            for vn_fi_i in vns:
                self.faces[vn_fi_i[1]][3][vn_fi_i[2]] = len(self.svn) - 1
            


class Material(Object):
    materials = {}
    def __init__(self, name):
        self.name = name
        if name in Material.materials:
            raise Exception("Name Collision: 2 or more materials share the same name.")
        else:
            Material.materials[name] = self
        self.texture = None
        self.normal_map = None


    def load_mtl(filename:str, dir:str):
        import png_decoder
        try:
            with open(dir + filename, "r") as mtl_file:
                print("Starts too load materials. It might take a rather long time " +
                      "as it involves decoding images or reading large pickle files.")
                convert_to_left_hand = False
                if mtl_file.readline(9) == "# Blender":
                    convert_to_left_hand = True
                for line in mtl_file.readlines():
                    if line.startswith("#"):
                        continue
                    elif line.startswith("newmtl "):
                        current_material = Material(line.strip()[7:])
                    elif line.startswith("map_Kd "):
                        current_material.texture = png_decoder.Png(line.strip()[7:], dir)
                        # So it won't be out of index range when uv mapping
                        # But indeed not the best option
                        current_material.texture.width -= 1
                        current_material.texture.height -= 1
                    elif line.startswith("map_Bump "):
                        current_material.normal_map = png_decoder.Png(line.strip().split()[-1], dir)
                        # So it won't be out of index range when uv mapping
                        # But indeed not the best option
                        current_material.normal_map.width -= 1
                        current_material.normal_map.height -= 1
                    # There are other informations such as ambient value, transparancy
                    # values that are not supported in the renderer (partially due to the
                    # fact that I myself don't even know what they are exactly), 
                    # so they will not be loaded
            print("Finish loading materials.")
        except FileNotFoundError as e:
            print("\033[31mFailed to load the mtl File")
            print(e, end="\033[0m\n")



class Light:
    light_sources = []
    def __init__(self, x, y, z, strength=(1, 1, 1), type=0) -> None:
        """
        type 0 for parallel light source
        type 1 for point light source
        if type 0, xyz is the direction of the light
        if type 1, xyz is the position of the light source
        """
        self.strength = strength
        self.type = type
        if type == 0:
            self.direction = (x, y, z)
        else:    # type == 1
            self.position == (x, y, z)
        self.len = math.sqrt(x * x + y * y + z * z)
        self.squared_len = x * x + y * y + z * z
        Light.light_sources.append(self)


class Camera:
    def __init__(self, x=0, y=0, z=0, z_near=0.1, z_far=50, yaw=90, pitch=0, fov=75) -> None:
        self.x, self.y, self.z = x, y, z
        self.z_near, self.z_far = z_near, z_far
        self.fov = fov
        self.yaw = 0
        self.pitch = 0
        self.update_rotation(yaw, pitch)

    
    def __str__(self) -> str:
        return (f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})  |  " +
                f"Yaw:{(self.yaw + 180) % 360 - 180:.3f} " + 
                f"Pitch:{(self.pitch + 180) % 360 - 180:.3f}  |  " + 
                f"Rotation: " +
                f"X:({cam.rotation[0][0]:.3f}, {cam.rotation[0][1]:.3f}, {cam.rotation[0][2]:.3f}) " +
                f"Y:({cam.rotation[1][0]:.3f}, {cam.rotation[1][1]:.3f}, {cam.rotation[1][2]:.3f}) " +
                f"Z:({cam.rotation[2][0]:.3f}, {cam.rotation[2][1]:.3f}, {cam.rotation[2][2]:.3f}) ")

    
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

    def luminance():

        return 1

    def rasterize(A, B, C):
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
            if obj.smooth_shading:
                pass
            else:    # flat shading
                pass
        elif obj.texture:
            if obj.smooth_shading:
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
                                normal = (
                                    p2 * left[5] + p1 * right[5],
                                    p2 * left[6] + p1 * right[6],
                                    p2 * left[7] + p1 * right[7],
                                )
                                # calculate the light
                                x3d = p2 * left[0] + p1 * right[0]
                                y3d = p2 * left[1] + p1 * right[1]
                                luminance = 1
                                frame[A[9]][x] = (min(int(color[0] * luminance), 255), 
                                            min(int(color[1] * luminance), 255), 
                                            min(int(color[2] * luminance), 255))
                    # The rest of the triangle
                    t1 = (A[8] - C[8]) / (A[9] - C[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (B[8] - C[8]) / (B[9] - C[9])
                    b2 = B[8] - B[9] * t2
                    for y in range(max(0, B[9]), min(height - 1, C[9])):
                        m1 = (y - A[9]) / (C[9] - A[9])
                        m2 = 1 - m1
                        # x, z, u, v, sx, sy, sz
                        left = (A[0],
                                A[1],
                                A[2],
                                m2 * A[3] + m1 * C[3], 
                                m2 * A[4] + m1 * C[4], 
                                m2 * A[5] + m1 * C[5], 
                                m2 * A[6] + m1 * C[6], 
                                m2 * A[7] + m1 * C[7], 
                                int(t1 * y + b1),
                                y, 
                                )            
                        right = (B[0],
                                B[1],
                                B[2],
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
                                luminance = 1
                                frame[y][x] = (min(int(color[0] * luminance), 255), 
                                            min(int(color[1] * luminance), 255), 
                                            min(int(color[2] * luminance), 255))
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
                                luminance = 1
                                frame[B[9]][x] = (min(int(color[0] * luminance), 255), 
                                            min(int(color[1] * luminance), 255), 
                                            min(int(color[2] * luminance), 255))
                    # The rest of the triangle
                    t1 = (A[8] - B[8]) / (A[9] - B[9])
                    b1 = A[8] - A[9] * t1
                    t2 = (A[8] - C[8]) / (A[9] - C[9])
                    b2 = A[8] - A[9] * t2
                    for y in range(max(0, A[9]), min(height - 1, B[9])):
                        m1 = (y - A[9]) / (C[9] - A[9])
                        m2 = 1 - m1
                        # x, z, u, v, sx, sy, sz
                        left = (A[0],
                                A[1],
                                A[2],
                                m2 * A[3] + m1 * B[3], 
                                m2 * A[4] + m1 * B[4], 
                                m2 * A[5] + m1 * B[5], 
                                m2 * A[6] + m1 * B[6], 
                                m2 * A[7] + m1 * B[7], 
                                int(t1 * y + b1),
                                y, 
                                )  
                        right = (A[0],
                                A[1],
                                A[2],
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
                                luminance = 1
                                frame[y][x] = (min(int(color[0] * luminance), 255), 
                                            min(int(color[1] * luminance), 255), 
                                            min(int(color[2] * luminance), 255))
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
                        left = (A[0],
                                A[1],
                                A[2],
                                m2 * A[3] + m1 * B[3], 
                                m2 * A[4] + m1 * B[4], 
                                m2 * A[5] + m1 * B[5], 
                                m2 * A[6] + m1 * B[6], 
                                m2 * A[7] + m1 * B[7], 
                                int(t1 * y + b1),
                                y, 
                                )  
                        right = (A[0],
                                A[1],
                                A[2],
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
                                luminance = 1
                                frame[y][x] = (min(int(color[0] * luminance), 255), 
                                            min(int(color[1] * luminance), 255), 
                                            min(int(color[2] * luminance), 255))
                    t1 = (B[8] - C[8]) / (B[9] - C[9])
                    b1 = B[8] - B[9] * t1
                    for y in range(max(0, B[9]), min(height - 1, C[9])):
                        m1 = (y - B[9]) / (C[9] - B[9])
                        m2 = 1 - m1
                        n1 = (y - A[9]) / (C[9] - A[9])
                        n2 = 1 - n1
                        # x, z, u, v, sx, sy, sz
                        left = (A[0],
                                A[1],
                                A[2],
                                n2 * A[3] + n1 * C[3], 
                                n2 * A[4] + n1 * C[4], 
                                n2 * A[5] + n1 * C[5], 
                                n2 * A[6] + n1 * C[6], 
                                n2 * A[7] + n1 * C[7], 
                                int(t2 * y + b2),
                                y, 
                                )  
                        right = (B[0],
                                B[1],
                                B[2],
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
                                luminance = 1
                                frame[y][x] = (min(int(color[0] * luminance), 255), 
                                            min(int(color[1] * luminance), 255), 
                                            min(int(color[2] * luminance), 255))
            else:    # flat shading
                pass
        elif obj.normal_map:
            pass
        elif render_solid:
            pass

    
    # Initiate the z_buffer & frame
    z_buffer = [[cam.z_far] * width for _ in range(height)]
    frame = [[(0, 0, 0)] * width for _ in range(height)]

    obj:Object    # CodeUndone Just for VSCode
    for obj in Object.objects:
        for face in obj.faces:
            # Move the object
            A = Object.vec_minus_vec_3d(Object.v[face[0][0]], (cam.x, cam.y, cam.z))
            B = Object.vec_minus_vec_3d(Object.v[face[0][1]], (cam.x, cam.y, cam.z))
            C = Object.vec_minus_vec_3d(Object.v[face[0][2]], (cam.x, cam.y, cam.z))
            A.extend((0, 0, 0, 0, 0, 0, 0))
            B.extend((0, 0, 0, 0, 0, 0, 0))
            C.extend((0, 0, 0, 0, 0, 0, 0))
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
                if 0 <= vertex[8] < width and 0 <= vertex[9] < height:
                    frame[vertex[9]][vertex[8]] = (127, 127, 0)
            
            # Rasterization
            if len(inside) == 3:
                rasterize(*inside)
            else:    # len(inside) = 4
                rasterize(*inside[:3])
                rasterize(*inside[:2], inside[3])
            
    return frame


def display(frame):
    print("\033[F" * (height * 2))
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
    import os
    os.system("cls")
    # Object.load_obj("Furniture", "E:\Programming\Python\Python-3D-renderer\models\Furniture")
    # Object.load_obj("monkey")
    Object.load_obj("Crafting_table", "E:\Programming\Python\Python-3D-renderer\models\Crafting_table")
    Object.objects[-1].calculate_smooth_shading_normals()
    Object.objects[-1].smooth_shading = True
    # Object.objects[-1].calculate_face_normals()
    # exit()

    import os
    width, height = os.get_terminal_size()
    width = width // 2 - 3 
    height = height - 3
    # cam = Camera(0, 0, -10, pitch=0)
    cam = Camera(8.128, 3.999, -5.342, yaw=147, pitch=-22.5)
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
