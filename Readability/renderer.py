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
        length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        return [vector[0] / length, vector[1] / length, vector[2] / length,]
    

    def cross_product_v3d(v, u):
        return [v[1] * u[2] - v[2] * u[1],
                v[0] * u[2] - v[2] * u[0],
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
            v_starting_at = len(Object.v)
            vt_starting_at = len(Object.vt)
            vn_starting_at = len(Object.vn)
            for line in obj_file.readlines():
                line = line.strip()
                if line.startswith("#"):
                    continue
                elif line.startswith("mtllib "):
                    Material.load_mtl(dir + line[7:])
                elif line.startswith("o "):
                    current_obejct = Object(name = line[2:])
                    Object.objects.append(current_obejct)
                elif line.startswith("v "):
                    Object.v.append(list(map(float, line[2:].split())))
                elif line.startswith("vt "):
                    Object.vt.append(list(map(float, line[2:].split())))
                elif line.startswith("vn "):
                    Object.vn.append(list(map(float, line[2:].split())))
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


    def load_mtl(file_path):
        import png_decoder
        try:
            with open(file_path, "r") as mtl_file:
                print("Starts too load materials. It might take a rather long time " +
                      "as it involves decoding images or reading large pickle files.")
                for line in mtl_file.readlines():
                    if line.startswith("#"):
                        continue
                    elif line.startswith("newmtl "):
                        current_material = Material(line.strip()[7:])
                    elif line.startswith("map_Kd "):
                        current_material.texture = png_decoder.Png(line.strip()[7:], "")
                    elif line.startswith("map_Bump "):
                        current_material.normal_map = png_decoder.Png(line.strip().split()[-1], "")
                    # There are other informations such as ambient value, transparancy
                    # values that are not supported in the renderer (partially due to the
                    # fact that I myself don't even know what they are exactly), 
                    # so they will not be loaded
            print("Finish loading materials.")
        except FileNotFoundError as e:
            print("Failed to load the mtl File")
            print(e)



class Light:
    light_sources = []
    def __init__(self, x, y, z, strength=1, type=0) -> None:
        """
        type 0 for parallel light source
        type 1 for point light source
        if type 0, xyz is the direction of the light
        if type 1, xyz is the position of the light source
        """
        self.coor = (x, y, z)
        self.strength = strength
        self.type = type
        self.len = math.sqrt(x * x + y * y + z * z)
        self.squared_len = x * x + y * y + z * z
        Light.light_sources.append(self)


def render(cam, width, height, projection_matrix, render_solid=False) -> list:
    class TriVertex:
        def __init__(self, coor, uv=(0, 0), snv=(0, 0, 0)) -> None:
            self.x, self.y, self.z = coor
            self.u, self.v = uv
            self.snx, self.sny, self.snz = snv
            # self.cx, cy, cz, cw
            # self.nx, ny, nz
            # self.x2d, y2d
        
        def coor(self):
            return self.x, self.y, self.z

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

    def rasterize(A, B, C, texture):
        if A[1] > B[1]:
            A, B = B, A
        if B[1] > C[1]:
            B, C = C, B
        if A[1] > B[1]:
            A, B = B, A
        if C[1] >= height:
            return
        elif A[1] < 0:
            return
        
        if A[1] == B[1]:
            if B[1] == C[1]:
                return
            # If line AB can be seen, add line AB
            if A[1] < height:
                if A[0] < B[0]:
                    left = A
                    right = B
                else:
                    left = B
                    right = A
                for x in range(max(0, left[0]), min(width - 1, right[0])):
                    p1 = (x - left[0]) / (right[0] - left[0])
                    p2 = 1 - p1
                    z = p2 * left[2] + p1 * right[2]
                    if z < z_buffer[A[1]][x]:
                        z_buffer[A[1]][x] = z
                        u = int((p2 * left[3] + p1 * right[3]) * texture.width)
                        v = int((p2 * left[4] + p1 * right[4]) * texture.height)
                        color = texture.pixels[v][u]
                        normal = (
                            p2 * left[4] + p1 * right[4],
                            p2 * left[5] + p1 * right[5],
                            p2 * left[6] + p1 * right[6],
                        )
                        # calculate the light
                        luminance = 1
                        frame[A[1]][x] = (min(int(color[0] * luminance), 255), 
                                    min(int(color[1] * luminance), 255), 
                                    min(int(color[2] * luminance), 255))
            # The rest of the triangle
            t1 = (A[0] - C[0]) / (A[1] - C[1])
            b1 = A[0] - A[1] * t1
            t2 = (B[0] - C[0]) / (B[1] - C[1])
            b2 = B[0] - B[1] * t2
            for y in range(B[1], C[1]):
                m1 = (y - A[1]) / (C[1] - A[1])
                m2 = 1 - m1
                # x, z, u, v, sx, sy, sz
                left = (int(t1 * y + b1), 
                        m2 * A[2] + m1 * C[2], 
                        m2 * A[3] + m1 * C[3], 
                        m2 * A[4] + m1 * C[4], 
                        m2 * A[5] + m1 * C[5], 
                        m2 * A[6] + m1 * C[6], 
                        m2 * A[7] + m1 * C[7], 
                        )
                right = (int(t2 * y + b2), 
                        m2 * B[2] + m1 * C[2], 
                        m2 * B[3] + m1 * C[3], 
                        m2 * B[4] + m1 * C[4], 
                        m2 * B[5] + m1 * C[5], 
                        m2 * B[6] + m1 * C[6], 
                        m2 * B[7] + m1 * C[7], 
                        )
                if left[0] > right[0]:
                    left, right = right, left
                for x in range(max(0, left[0]), min(width - 1, right[0])):
                    p1 = (x - left[0]) / (right[0] - left[0])
                    p2 = 1 - p1
                    z = p2 * left[1] + p1 * right[1]
                    if z < z_buffer[y][x]:
                        z_buffer[y][x] = z
                        u = int((p2 * left[2] + p1 * right[2]) * texture.width)
                        v = int((p2 * left[3] + p1 * right[3]) * texture.height)
                        color = texture.pixels[v][u]
                        normal = (
                            p2 * left[4] + p1 * right[4],
                            p2 * left[5] + p1 * right[5],
                            p2 * left[6] + p1 * right[6],
                        )
                        # calculate the light
                        luminance = calculate_luminance()
                        frame[y][x] = (min(int(color[0] * luminance), 255), 
                                    min(int(color[1] * luminance), 255), 
                                    min(int(color[2] * luminance), 255))
        elif B[1] == C[1]:
            # If line BC can be seen, add line BC
            if B[1] >= 0:
                if B[0] < C[0]:
                    left = B
                    right = C
                else:
                    left = C
                    right = B
                for x in range(max(0, left[0]), min(width - 1, right[0])):
                    p1 = (x - left[0]) / (right[0] - left[0])
                    p2 = 1 - p1
                    z = p2 * left[2] + p1 * right[2]
                    if z < z_buffer[B[1]][x]:
                        z_buffer[B[1]][x] = z
                        u = int((p2 * left[3] + p1 * right[3]) * texture.width)
                        v = int((p2 * left[4] + p1 * right[4]) * texture.height)
                        color = texture.pixels[v][u]
                        normal = (
                            p2 * left[4] + p1 * right[4],
                            p2 * left[5] + p1 * right[5],
                            p2 * left[6] + p1 * right[6],
                        )
                        # calculate the light
                        luminance = 1
                        frame[B[1]][x] = (min(int(color[0] * luminance), 255), 
                                    min(int(color[1] * luminance), 255), 
                                    min(int(color[2] * luminance), 255))
            # The rest of the triangle
            t1 = (A[0] - B[0]) / (A[1] - B[1])
            b1 = A[0] - A[1] * t1
            t2 = (A[0] - C[0]) / (A[1] - C[1])
            b2 = A[0] - A[1] * t2
            for y in range(A[1], B[1]):
                m1 = (y - A[1]) / (C[1] - A[1])
                m2 = 1 - m1
                # x, z, u, v, sx, sy, sz
                left = (int(t1 * y + b1), 
                        m2 * A[2] + m1 * B[2], 
                        m2 * A[3] + m1 * B[3], 
                        m2 * A[4] + m1 * B[4], 
                        m2 * A[5] + m1 * B[5], 
                        m2 * A[6] + m1 * B[6], 
                        m2 * A[7] + m1 * B[7], 
                        )
                right = (int(t2 * y + b2), 
                        m2 * A[2] + m1 * C[2], 
                        m2 * A[3] + m1 * C[3], 
                        m2 * A[4] + m1 * C[4], 
                        m2 * A[5] + m1 * C[5], 
                        m2 * A[6] + m1 * C[6], 
                        m2 * A[7] + m1 * C[7], 
                        )
                if left[0] > right[0]:
                    left, right = right, left
                for x in range(max(0, left[0]), min(width - 1, right[0])):
                    p1 = (x - left[0]) / (right[0] - left[0])
                    p2 = 1 - p1
                    z = p2 * left[1] + p1 * right[1]
                    if z < z_buffer[y][x]:
                        z_buffer[y][x] = z
                        u = int((p2 * left[2] + p1 * right[2]) * texture.width)
                        v = int((p2 * left[3] + p1 * right[3]) * texture.height)
                        color = texture.pixels[v][u]
                        normal = (
                            p2 * left[4] + p1 * right[4],
                            p2 * left[5] + p1 * right[5],
                            p2 * left[6] + p1 * right[6],
                        )
                        # calculate the light
                        luminance = 1
                        frame[y][x] = (min(int(color[0] * luminance), 255), 
                                    min(int(color[1] * luminance), 255), 
                                    min(int(color[2] * luminance), 255))
        else:
            t1 = (A[0] - B[0]) / (A[1] - B[1])
            b1 = A[0] - A[1] * t1
            t2 = (A[0] - C[0]) / (A[1] - C[1])
            b2 = A[0] - A[1] * t2
            for y in range(A[1], B[1]):
                m1 = (y - A[1]) / (B[1] - A[1])
                m2 = 1 - m1
                n1 = (y - A[1]) / (C[1] - A[1])
                n2 = 1 - n1
                # x, z, u, v, sx, sy, sz
                left = (int(t1 * y + b1), 
                        m2 * A[2] + m1 * B[2], 
                        m2 * A[3] + m1 * B[3], 
                        m2 * A[4] + m1 * B[4], 
                        m2 * A[5] + m1 * B[5], 
                        m2 * A[6] + m1 * B[6], 
                        m2 * A[7] + m1 * B[7], 
                        )
                right = (int(t2 * y + b2), 
                        n2 * A[2] + n1 * C[2], 
                        n2 * A[3] + n1 * C[3], 
                        n2 * A[4] + n1 * C[4], 
                        n2 * A[5] + n1 * C[5], 
                        n2 * A[6] + n1 * C[6], 
                        n2 * A[7] + n1 * C[7], 
                        )
                if left[0] > right[0]:
                    left, right = right, left
                for x in range(max(0, left[0]), min(width - 1, right[0])):
                    p1 = (x - left[0]) / (right[0] - left[0])
                    p2 = 1 - p1
                    z = p2 * left[1] + p1 * right[1]
                    if z < z_buffer[y][x]:
                        z_buffer[y][x] = z
                        u = int((p2 * left[2] + p1 * right[2]) * texture.width)
                        v = int((p2 * left[3] + p1 * right[3]) * texture.height)
                        color = texture.pixels[v][u]
                        normal = (
                            p2 * left[4] + p1 * right[4],
                            p2 * left[5] + p1 * right[5],
                            p2 * left[6] + p1 * right[6],
                        )
                        # calculate the light
                        luminance = 1
                        frame[y][x] = (min(int(color[0] * luminance), 255), 
                                    min(int(color[1] * luminance), 255), 
                                    min(int(color[2] * luminance), 255))
            t1 = (B[0] - C[0]) / (B[1] - C[1])
            b1 = B[0] - B[1] * t1
            for y in range(B[1], C[1]):
                m1 = (y - B[1]) / (C[1] - B[1])
                m2 = 1 - m1
                n1 = (y - A[1]) / (C[1] - A[1])
                n2 = 1 - n1
                # x, z, u, v, sx, sy, sz
                left = (int(t2 * y + b2), 
                        m2 * A[2] + m1 * C[2], 
                        m2 * A[3] + m1 * C[3], 
                        m2 * A[4] + m1 * C[4], 
                        m2 * A[5] + m1 * C[5], 
                        m2 * A[6] + m1 * C[6], 
                        m2 * A[7] + m1 * C[7], 
                        )
                right = (int(t1 * y + b1), 
                        n2 * B[2] + n1 * C[2], 
                        n2 * B[3] + n1 * C[3], 
                        n2 * B[4] + n1 * C[4], 
                        n2 * B[5] + n1 * C[5], 
                        n2 * B[6] + n1 * C[6], 
                        n2 * B[7] + n1 * C[7], 
                        )
                if left[0] > right[0]:
                    left, right = right, left
                for x in range(max(0, left[0]), min(width - 1, right[0])):
                    p1 = (x - left[0]) / (right[0] - left[0])
                    p2 = 1 - p1
                    z = p2 * left[1] + p1 * right[1]
                    if z < z_buffer[y][x]:
                        z_buffer[y][x] = z
                        u = int((p2 * left[2] + p1 * right[2]) * texture.width)
                        v = int((p2 * left[3] + p1 * right[3]) * texture.height)
                        color = texture.pixels[v][u]
                        normal = (
                            p2 * left[4] + p1 * right[4],
                            p2 * left[5] + p1 * right[5],
                            p2 * left[6] + p1 * right[6],
                        )
                        # calculate the light
                        luminance = 1
                        frame[y][x] = (min(int(color[0] * luminance), 255), 
                                    min(int(color[1] * luminance), 255), 
                                    min(int(color[2] * luminance), 255))

    def calculate_luminance(normal) -> float:
        for light in Light.light_sources:
            if light.type == 0:
                return dot_product_v3d(normal, light.coor) / light.len * light.strength
            else:    # elif light.type == 1:

                point_to_light = vec_minus_vec_3d(light.coor, coor)
                return dot_product_v3d(normal, point_to_light) / vec_squared_len_3d * light.strength



    # Initiate the z_buffer & frame
    z_buffer = [[cam[8]] * width for _ in range(height)]
    frame = [[(0, 0, 0)] * width for _ in range(height)]

    obj:Object    # CodeUndone Just for VSCode
    for obj in Object.objects:
        for face in obj.faces:
            # Move the object
            tri = [TriVertex(Object.vec_minus_vec_3d(Object.v[face[0][0]], cam)),
                   TriVertex(Object.vec_minus_vec_3d(Object.v[face[0][1]], cam)),
                   TriVertex(Object.vec_minus_vec_3d(Object.v[face[0][2]], cam))]
            if obj.texture or obj.normal_map:
                tri[0].u, tri[1].v = Object.vt[face[1][0]]
                tri[1].u, tri[1].v = Object.vt[face[1][1]]
                tri[2].u, tri[1].v = Object.vt[face[1][2]]
            if obj.smooth_shading:
                tri[0].snx, tri[0].sny, tri[0].snz = obj.svn[face[3][0]]
                tri[1].snx, tri[1].sny, tri[1].snz = obj.svn[face[3][1]]
                tri[2].snx, tri[2].sny, tri[2].snz = obj.svn[face[3][2]]
            """ CodeUndone A less coherent version probably
            # tri: [[x, y, z, [u, v], [xn, yn, zn]], [...], [...]]
            tri = [Object.vec_minus_vec_3d(Object.v[face[0][0]], cam) + [None, None], 
                   Object.vec_minus_vec_3d(Object.v[face[0][1]], cam) + [None, None], 
                   Object.vec_minus_vec_3d(Object.v[face[0][2]], cam) + [None, None]]
            if obj.texture or obj.normal_map:
                tri[0][3] = Object.vt[face[1][0]]
                tri[1][3] = Object.vt[face[1][1]]
                tri[2][3] = Object.vt[face[1][2]]
            if obj.smooth_shading:
                tri[0][3] = obj.svn[face[3][0]]
                tri[1][3] = obj.svn[face[3][1]]
                tri[2][3] = obj.svn[face[3][2]]
            """
            
            # Rotate the object
            # CodeUndone

            # Culling
            # Remove those are too far or behind the camera
            if ((tri[0].z <= cam[7] or tri[0].z >= cam[8]) and
                (tri[1].z <= cam[7] or tri[1].z >= cam[8]) and
                (tri[2].z <= cam[7] or tri[2].z >= cam[8])):
                continue
            # Remove those impossible to be seen based on the normal
            cam_to_point = Object.vec_minus_vec_3d(cam, tri[0].coor())
            if dot_product_v3d(cam_to_point, Object.vn[face[2]]) > 0:
                continue

            # Clipping
            inside = []
            outside = []
            for vertex in tri:
                if vertex.z > cam[7]:
                    inside.append(vertex)
                else:
                    outside.append(vertex)
            # Clip into two triangles
            if len(inside) == 2:
                # Compute the parameter t where the line intersects the plane
                t = (cam[7] - outside[0].z) / (inside[0].z - outside[0].z)
                # Calculate the intersection point
                inside.append(
                    TriVertex(
                        (outside[0].x + t * (inside[0].x - outside[0].x),
                         outside[0].y + t * (inside[0].y - outside[0].y),
                         outside[0].z + t * (inside[0].z - outside[0].z)
                        ),
                        (
                         outside[0].u + t * (inside[0].u - outside[0].u),
                         outside[0].v + t * (inside[0].v - outside[0].v),
                        ),
                        (
                         outside[0].snx + t * (inside[0].snx - outside[0].snx),
                         outside[0].sny + t * (inside[0].sny - outside[0].sny),
                         outside[0].snz + t * (inside[0].snz - outside[0].snz),
                        )
                    )
                )
                # Compute the parameter t where the line intersects the plane
                t = (cam[7] - outside[0].z) / (inside[1].z - outside[0].z)
                # Calculate the intersection point
                inside.append(
                    TriVertex(
                        (outside[0].x + t * (inside[1].x - outside[0].x),
                         outside[0].y + t * (inside[1].y - outside[0].y),
                         outside[0].z + t * (inside[1].z - outside[0].z)
                        ),
                        (
                         outside[0].u + t * (inside[1].u - outside[0].u),
                         outside[0].v + t * (inside[1].v - outside[0].v),
                        ),
                        (
                         outside[0].snx + t * (inside[1].snx - outside[0].snx),
                         outside[0].sny + t * (inside[1].sny - outside[0].sny),
                         outside[0].snz + t * (inside[1].snz - outside[0].snz),
                        )
                    )
                )
            elif len(inside) == 1:
                # Compute the parameter t where the line intersects the plane
                t = (cam[7] - outside[0].z) / (inside[0].z - outside[0].z)
                # Calculate the intersection point
                inside.append(
                    TriVertex(
                        (outside[0].x + t * (inside[0].x - outside[0].x),
                         outside[0].y + t * (inside[0].y - outside[0].y),
                         outside[0].z + t * (inside[0].z - outside[0].z)
                        ),
                        (
                         outside[0].u + t * (inside[0].u - outside[0].u),
                         outside[0].v + t * (inside[0].v - outside[0].v),
                        ),
                        (
                         outside[0].snx + t * (inside[0].snx - outside[0].snx),
                         outside[0].sny + t * (inside[0].sny - outside[0].sny),
                         outside[0].snz + t * (inside[0].snz - outside[0].snz),
                        )
                    )
                )
                # Compute the parameter t where the line intersects the plane
                t = (cam[7] - outside[1].z) / (inside[0].z - outside[1].z)
                # Calculate the intersection point
                inside.append(
                    TriVertex(
                        (outside[1].x + t * (inside[0].x - outside[1].x),
                         outside[1].y + t * (inside[0].y - outside[1].y),
                         outside[1].z + t * (inside[0].z - outside[1].z)
                        ),
                        (
                         outside[1].u + t * (inside[0].u - outside[1].u),
                         outside[1].v + t * (inside[0].v - outside[1].v),
                        ),
                        (
                         outside[1].snx + t * (inside[0].snx - outside[1].snx),
                         outside[1].sny + t * (inside[0].sny - outside[1].sny),
                         outside[1].snz + t * (inside[0].snz - outside[1].snz),
                        )
                    )
                )
            # len(inside) == 3    All in the Frustum
            # else:
            #     pass

            # Projection
            for vertex in inside:
                vertex:TriVertex
                vertex.cx, vertex.cy, vertex.cz, vertex.cw = mat_multiply_vec_4d(projection_matrix, 
                                                                                 (vertex.x, vertex.y, vertex.z, 1)
                                                                                 )
                vertex.nx, vertex.ny, vertex.nz = vertex.cx / vertex.cw, vertex.cy / vertex.cw, vertex.cz / vertex.cw
            
                vertex.x2d, vertex.y2d = int(width * (0.5 - vertex.nx)), int(height * (0.5 + vertex.ny))
                # CodeUndone
                if 0 <= vertex.x2d < width and 0 <= vertex.y2d < height:
                    frame[vertex.y2d][vertex.x2d] = "\033[46m  \033[0m"
            
            # Rasterization
            if len(inside) == 3:
                rasterize(
                    (inside[0].x2d, inside[0].y2d, inside[0].z, inside[0].u, inside[0].v, inside[0].snx, inside[0].sny, inside[0].snz),
                    (inside[1].x2d, inside[1].y2d, inside[1].z, inside[1].u, inside[1].v, inside[1].snx, inside[1].sny, inside[1].snz),
                    (inside[2].x2d, inside[2].y2d, inside[2].z, inside[2].u, inside[2].v, inside[2].snx, inside[2].sny, inside[2].snz),
                )
            
            else:    # elif len(inside) == 4 
                pass
            
    return frame


def display(frame):
    for row in frame:
        for pixel in row:
            if pixel == (0, 0, 0):
                print("  ", end="")
            else:
                print(pixel, end="")
        print("")




if __name__ == "__main__":
    import os
    os.system("cls")
    # Object.load_obj("Furniture", "E:\Programming\Python\Python-3D-renderer\models\Furniture")
    # Object.load_obj("monkey")
    Object.load_obj("cube")
    
    cam = [0.2,   # 0 x
           0.2,   # 1 y
           -5,   # 2 z
           0,   # 3 xr
           0,   # 4 yr
           0,   # 5 zr
           60,  # 6 fov
           0.01,# 7 z_near
           50,  # 8 z_far
           ]
    
    import os
    width, height = os.get_terminal_size()
    width = width // 2 - 3 
    height = height - 3
    # Better use height/width because the variable will only be used in
    # deciding projecttion_matrix[1][1] where it either multiplies to
    # a value or divides a value. Multiplication, which is considered 
    # faster, uses height / width
    aspect_ratio_h_w = height / width
    projection_matrix = (
        (cam[7] / (cam[7] * math.tan(0.5 * cam[6] * math.pi / 180)), 0, 0, 0),
        (0, cam[7] / (cam[7] * math.tan(0.5 * cam[6] * math.pi / 180) * aspect_ratio_h_w), 0, 0),
        (0, 0, (cam[7] + cam[8]) / (cam[7] - cam[8]), 2 * cam[7] * cam[8] / (cam[7] - cam[8])),
        (0, 0, -1 ,0)
    )

    from msvcrt import getwch
    while True:
        print("\033[F" * (height * 2))
        frame = render(cam, width, height, projection_matrix)
        display(frame)
        key = getwch()
        if key == "Q":
            break

        step = 0.2
        if key == "w":
            cam[2] += step
        elif key == "s":
            cam[2] -= step
        elif key == "a" :
            cam[0] -= step
        elif key == "d":
            cam[0] += step
        elif key == "u":
            cam[1] += step
        elif key == "j":
            cam[1] -= step
