# Undone part will be marked as CodeUndone

# import a few standard library for png decoding
try:
    import pickle
    pickle_loaded = True
except ModuleNotFoundError:
    pickle_loaded = False
    print("The standard library pickle seems to be missing." +
          "The module will still function but without the " +
          "capability to store or read decoded data")
try:
    from binascii import crc32
    crc32_loaded = True
except ModuleNotFoundError:
    crc32_loaded = False
    print("The standard library binascii seems to be missing." +
          "The module will still function but without " +
          "capability to do Cyclic Redundancy Check")
except ImportError:
    crc32_loaded = False
    print("The fucntion crc32 in the standard library binascii seems " +
          "to be missing. The module will still function but without " +
          "capability to do Cyclic Redundancy Check")
# IDAT includes Huffman and LZSS, so decompress is called to do the
# job.
from zlib import decompress
# Will be needed in Png.get_all_idat_data
from math import ceil

class Png:
    default_alpha = 0
    grayscale_palette = {
        1: [[0 for _ in range(3)], [255 for _ in range(3)] ],
        2: [[255 // 3 * i for _ in range(3)] for i in range(4)], 
        4: [[255 // 15 * i for _ in range(3)] for i in range(16)],
    }
    channels_lookup = (1, None, 3, 1, 2, None, 4)

    def __init__(self, filename, dir="", pickle_dir="",
                 from_pickle=True, to_pickle=True, crc=False) -> None:
        '''
        filename can be with or without ".png".
        Try to load the image from a pickle file if pickle has been successfully loaded
        and from_pickle == True.
        If failed, it will start the decoding procedure, after which it will store the
        self.pixels into a pickle file (only self.pixels is stored) if to_pickle == True
        '''
        # Decide whether to check crc
        self.crc = crc
        if crc == True and crc32_loaded == False:
            self.crc = False
            print("Cyclic Redundancy Check can not be implemented, for" +
                  "related function is not imported successfully.")
            
        # Work out the paths
        filename = filename + ".png" if filename[-4:] != ".png" else filename
        image_path = dir + filename
        self.name = filename
        self.path = image_path
        if pickle_loaded:
            pickle_path = f"{pickle_dir}{filename[:-4]}.pickle"

        # Pickle has been loaded and corresponding pickle file has been found
        decoded = False
        try:
            if from_pickle:
                with open(pickle_path, "rb") as image_pickle:
                    self.pixels = pickle.load(image_pickle)
                # Only self.pixels is read, whereas self.width and self.height
                # are necessary in self.__str__ and self.display
                with open(image_path, "rb") as image:
                    self.bin:bytes = image.read()
                    self.get_image_properties()
                    if self.color_type == 3:
                        self.get_palette()
            # Demanded in the arguement not to load from the pickle file that 
            # may exist
            else:
                self.decode(image_path)
                decoded = True
        # Pickle has been loaded while failing to find corresponding pickle file
        except FileNotFoundError:
            self.decode(image_path)
            decoded = True
        # Failed to load the pickle module
        except NameError:
            self.decode(image_path)
            decoded = True
        # Store the pickle file after decoding the image
        if to_pickle == True and pickle_loaded == True and decoded:
            with open(pickle_path, "wb") as image_pickle:
                pickle.dump(self.pixels, image_pickle)


    def __str__(self):
        color_type = ("Grayscale", None, "RGB", "Indexed", "Grayscale-alpha", None, "RGB-alpha")
        s = f"Name: {self.name}\t\tPath: {self.path}"
        s += f"Size: {self.width} x {self.height}\n"
        s += f"Color Type = {color_type[self.color_type]}({self.color_type})\n"
        s += f"Channel(s): {Png.channels_lookup[self.color_type]}\n"
        s += f"Bit Depth: {self.bit_depth}"
        return s


    def check_crc(image_bytes:bytes, chunk_starting_index:int) -> None:
        """Check if the data matches the crc part. Raise Exception if not."""
        chunk_length = Png.get_chunk_length(image_bytes, chunk_starting_index)
        # Check if the crc value calculated according to the chunk
        if (crc32(image_bytes[chunk_starting_index+4:chunk_starting_index+8+chunk_length]) !=
            int.from_bytes(image_bytes[chunk_starting_index+chunk_length+8:chunk_starting_index+chunk_length+12])
            ):
            raise Exception("CRC Failed")


    def get_chunk_length(image_bytes:bytes, chunk_starting_index:int) -> int:
        return int.from_bytes(image_bytes[chunk_starting_index:chunk_starting_index+4])


    def decode(self, image_path) -> None:
        """
        Take the path of the image and then read the binary before decoding it.
        Store a list of tuples, in form of 
        [[[r, g, b, alpha], [...], ...], [...], ...] in self.pixels
        """
        # Check whether crc can be carried out if it is demanded.
        # I can write python code to do the check but since it may not
        # be so important. So ...
        with open(image_path, "rb") as image:
            self.bin:bytes = image.read()

        # Validation:
        # Check whether png HEADER and IHDR chunk exist
        if self.bin[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
            raise Exception("This is not a valid png image.")
        
        # Read the IHDR chunk to get the properties
        self.get_image_properties()

        # Get palette if the color type is 3
        if self.color_type == 3:
            self.get_palette()
        elif self.color_type == 0 and self.bit_depth <= 4:
            self.palette = Png.grayscale_palette[self.bit_depth]
        
        # Start to deal with IDAT chuck
        bytes_rows = self.get_all_idat_data()
        defiltered_bytes_rows = self.defilter(bytes_rows)
        self.pixels = self.interpret_bytes_to_color(defiltered_bytes_rows)
        

    def get_image_properties(self) -> None:
        """Get all fundamental properties of the image. Store in the instance."""
        if self.crc == True:
            Png.check_crc(self.bin, 8)

        self.width = int.from_bytes(self.bin[16:20])
        self.height = int.from_bytes(self.bin[20:24])
        # Ranging in 1, 2, 4, 8, 16
        self.bit_depth = self.bin[24]
        # Ranging in 0, 2, 3, 4, 6
        # 0 - Grayscale - 1 channel
        # 2 - RGB - 3 channels 
        # 3 - Palette - 1 channel
        # 4 - Grayscale Alpha - 2 channels
        # 6 - RGB Alpha - 4 channels
        self.color_type = self.bin[25]
        self.channels = Png.channels_lookup[self.color_type]
        # default 0
        self.compression_method = self.bin[26]
        # default 0
        self.filter_method = self.bin[27]
        # 0 - no interlace
        # 1 - Adam7 algorithm
        self.interlace_method = self.bin[28]
    

    def get_palette(self) -> None:
        """Get self.palette [[r, g, b, Png.default_alpha], [...], ...]"""
        # Validation 
        # Not really necessary tho
        if b'PLTE' not in self.bin:
            raise Exception("The image is encoded with palette while " +
                            "it doesn't have the required chunk, \"PLTE\".")
        
        palette_chunk_index = self.bin.index(b'PLTE', 37) - 4

        if self.crc == True:
            Png.check_crc(self.bin, palette_chunk_index)

        palette_length = Png.get_chunk_length(self.bin, palette_chunk_index)
        palette = self.bin[palette_chunk_index+8:palette_chunk_index+8+palette_length]

        self.palette = []
        # len(palette) should always be divisible by 3
        for color_index in range(len(palette) // 3):
            self.palette.append([palette[color_index * 3],
                                 palette[color_index * 3 + 1],
                                 palette[color_index * 3 + 2],
                                 Png.default_alpha])
        

    def get_all_idat_data(self) -> list:
        """
        Collect every IDAT chunk, for there may be more than one of them, and then 
        decompress it. After that, separate them by row.
        Return a list [b'...', ...]
        What's worth noting is that the first byte of every row represent the filter 
        type instead of pixel data
        """
        # Identify all starting indices of idat chucks since there can be multiple of them
        idat_chunks_indices = []
        start_finding_index = 0
        for _ in range(self.bin.count(b'IDAT')):
            idat_chunks_indices.append(self.bin.index(b'IDAT', start_finding_index) - 4)
            start_finding_index = (idat_chunks_indices[-1] + 
                                   Png.get_chunk_length(self.bin, idat_chunks_indices[-1]) +
                                   8)
        # Check crc
        if self.crc == True:
            for idat_chunk_index in idat_chunks_indices:
                Png.check_crc(self.bin, idat_chunk_index)
        # Merge all chunks into one bytes
        idat_data = b''
        for idat_chunk_index in idat_chunks_indices:
            idat_data += self.bin[idat_chunk_index + 8 :
                                  idat_chunk_index + 8 +
                                  Png.get_chunk_length(self.bin,idat_chunk_index)]
        # Decompress (Huffman & LZSS)
        self.idat_data = decompress(idat_data)
        # Store the data as rows [b'...', b'...', ...]
        rows = []
        row_length = ceil(self.width * self.channels * self.bit_depth / 8 + 1)
        for row_num in range(self.height):
            rows.append(self.idat_data[row_num * row_length:(row_num + 1) * row_length])

        return rows

                 
    def defilter(self, rows:list,) -> list:
        """
        rows = [b'...', ...]
        Return a list containing bytes. [[int, int, ...], [...], ...]
        """
        if self.bit_depth == 16:
            left_distance = self.channels * 2
        else:
            left_distance = self.channels
        def left_value(x) -> int:
            """
            return the value of the pixel left to the pixel whose 
            x value is given, 0 if doesn't exist
            """
            if x - left_distance >= 0:
                return row[x - left_distance]
            else:
                return 0
        
        def upper_value(x, y) -> int:
            """
            return the value of the pixel right above the pixel whose 
            coordinate is given, 0 if doesn't exist
            """
            if y != 0:
                return defiltered_bytes[y - 1][x]
            else:
                return 0

        def upper_left_value(x, y) -> int:
            """
            return the value of the pixel on the upper-left to the 
            pixel whose coordinate is given, 0 if doesn't exist
            """
            if x - left_distance < 0 or y == 0:
                return 0
            else:
                return defiltered_bytes[y - 1][x - left_distance]
        
        def paeth_decide_which_pixel_to_add(x, y) -> tuple:
            """
            return the value of the value of a pixel, which is decided
            by paeth method
            """
            l = left_value(x)
            u = upper_value(x, y)
            ul = upper_left_value(x, y)
            v = u + l - ul
            vl = abs(v - l)
            vu = abs(v - u)
            vul = abs(v - ul)
            min_v = min(vl, vu, vul)
            if min_v == vl:
                return l
            elif min_v == vu:
                return u
            else:
                return ul

        defiltered_bytes = []
        
        for row_index, filtered_row in enumerate(rows):
            # None
            if filtered_row[0] == 0:
                defiltered_bytes.append(list(filtered_row[1:]))
            # Sub
            elif filtered_row[0] == 1:
                row = []
                for byte_index in range(len(filtered_row) - 1):
                    row.append(
                        (filtered_row[byte_index + 1] + left_value(byte_index) ) % 256
                    )
                defiltered_bytes.append(row)
            # Up
            elif filtered_row[0] == 2:
                row = []
                for byte_index in range(len(filtered_row) - 1):
                    row.append(
                        (
                            filtered_row[byte_index + 1] + 
                            upper_value(byte_index, row_index)
                        ) % 256
                    )
                defiltered_bytes.append(row)
            # Average
            elif filtered_row[0] == 3:
                row = []
                for byte_index in range(len(filtered_row) - 1):
                    row.append(
                        (
                            filtered_row[byte_index + 1] + 
                            (
                                left_value(byte_index) + 
                                upper_value(byte_index, row_index)
                            ) // 2
                        ) % 256
                    )
                defiltered_bytes.append(row)
            # Paeth
            elif filtered_row[0] == 4:
                row = []
                for byte_index in range(len(filtered_row) - 1):
                    row.append(
                        (
                            filtered_row[byte_index + 1] +
                            paeth_decide_which_pixel_to_add(byte_index, row_index)
                        ) % 256
                    )
                defiltered_bytes.append(row)

        return defiltered_bytes
    

    def interpret_bytes_to_color(self, rows:list) -> list:
        """
        rows = [[int, int, ...], [...], ...]
        return [[[r, g, b, a], [...], ...], [...], ...]
        """
        def get_digits(num:int) -> tuple:
            if self.bit_depth == 1:
                return tuple(map(int, format(num, "08b")))
            elif self.bit_depth == 2:
                return num // 64, num % 64 // 16, num % 16 // 4, num % 4
            elif self.bit_depth == 4:
                return num // 16, num % 16
            elif self.bit_depth == 8:
                return num,
            
        pixels = []
        # Indexed
        if self.color_type == 3:
            for row in rows:
                new_row = []
                for byte in row:
                    for value in get_digits(byte):
                        new_row.append(self.palette[value])
                pixels.append(new_row)
        # Grayscale
        elif self.color_type == 0:
            for row in rows:
                if self.bit_depth == 8 :
                    pixels.append([[value, value, value, Png.default_alpha]
                                   for value in row])
                elif self.bit_depth == 16:
                    pixels.append([
                                    [int.from_bytes(row[i*2:i*2+2]),
                                     int.from_bytes(row[i*2:i*2+2]),
                                     int.from_bytes(row[i*2:i*2+2]),
                                     Png.default_alpha]
                                   for i in range(len(row) // 2)
                                   ])
                else: # elif self.bit_depth in (1, 2, 4):
                    new_row = []
                    for byte in row:
                        for value in get_digits(byte):
                            new_row.append(self.palette[value] + [Png.default_alpha])
                    pixels.append(new_row)
        # Grayscale with alpha
        elif self.color_type == 4:
            # Either 8 or 16
            if self.bit_depth == 8:
                for row in rows:
                    new_row = []
                    for byte_index in range(0, self.width * 2, 2):
                        new_row.append([row[byte_index],
                                        row[byte_index],
                                        row[byte_index],
                                        row[byte_index + 1]])
                    pixels.append(new_row)
            elif self.bit_depth == 16:
                for row in rows:
                    new_row = []
                    for byte_index in range(0, self.width * 4, 4):
                        v = int.from_bytes(row[byte_index : byte_index + 2])
                        a = int.from_bytes(row[byte_index + 2: byte_index + 4])
                        new_row.append([v, v, v, a])
                    pixels.append(new_row)
        # RGB-alpha
        elif self.color_type == 6:
            # Either 8 or 16
            if self.bit_depth == 8:
                for row in rows:
                    new_row = []
                    for byte_index in range(0, self.width * self.channels, self.channels):
                        channels = []
                        for channel in range(self.channels):
                            channels.append(row[byte_index + channel])
                        new_row.append(channels)
                    pixels.append(new_row)
            elif self.bit_depth == 16:
                for row in rows:
                    new_row = []
                    for byte_index in range(0, self.width * self.channels * 2, self.channels * 2):
                        channels = []
                        for channel in range(self.channels):
                            channels.append(
                                            int.from_bytes(
                                                row[byte_index + channel:
                                                    byte_index + channel + 2]
                                                )
                                            )
                        new_row.append(channels)
                    pixels.append(new_row)
        # RGB
        else: # elif self.color_type  == 2:
            # Either 8 or 16
            if self.bit_depth == 8 or self.bit_depth==16:
                for row in rows:
                    new_row = []
                    for byte_index in range(0, self.width * self.channels, self.channels):
                        channels = []
                        for channel in range(self.channels):
                            channels.append(row[byte_index + channel])
                        channels.append(Png.default_alpha)
                        new_row.append(channels)
                    pixels.append(new_row)

            elif self.bit_depth == 16:
                for row in rows:
                    new_row = []
                    for byte_index in range(0, self.width * self.channels * 2, self.channels * 2):
                        channels = []
                        for channel in range(self.channels):
                            channels.append(
                                int.from_bytes(
                                    row[byte_index + channel:byte_index + channel + 2]
                                )
                            )
                        channels.append(Png.default_alpha)
                        new_row.append(channels)
                    pixels.append(new_row)
        
        return pixels



# os for clearing screen and get terminal size
import math, os

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
        # if self.mtl exists, it is a string
        self.mtl = None
        self.texture = False
        self.normal_map = False
        # [[vA_index, vB_index, vC_index], 
        #  [vtA_index, vtB_index, vtC_index],
        #  vn_index,
        #  [snvA_index, snvB_index, snvC_index]]
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
        try:
            with open(dir + filename, "r") as mtl_file:
                print("Starts too load materials. It might take a rather long time " +
                      "as it involves decoding images or reading large pickle files.")
                for line in mtl_file.readlines():
                    if line.startswith("#"):
                        continue
                    elif line.startswith("newmtl "):
                        current_material = Material(line.strip()[7:])
                    elif line.startswith("map_Kd "):
                        img = line.strip()[7:]
                        # Absolute path
                        if "/" in img:
                            current_material.texture = Png(line.strip()[7:])
                        # Relative path
                        else:
                            current_material.texture = Png(line.strip()[7:], dir)
                        # So it won't be out of index range when uv mapping
                        # But indeed not the best option
                        current_material.texture.width -= 1
                        current_material.texture.height -= 1
                    elif line.startswith("map_Bump "):
                        img = line.strip().split()[-1]
                        # Absolute path
                        if "/" in img:
                            current_material.normal_map = Png(line.strip().split()[-1])
                        # Relative path
                        else:
                            current_material.normal_map = Png(line.strip().split()[-1], dir)
                        
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
            length = math.sqrt(self.direction[0] ** 2 + 
                               self.direction[1] ** 2 +
                               self.direction[2] ** 2)
            if length != 1:
                self.direction = (self.direction[0] / length,
                                  self.direction[1] / length,
                                  self.direction[2] / length,)
        else:    # type == 1
            self.position = (x, y, z)
            self.cam_space_position = (0, 0, 0)
        Light.light_sources.append(self)


class Camera:
    def __init__(self, x=0, y=0, z=0, 
                 yaw=90, pitch=0, roll=0,
                 width=None, height=None,
                 z_near=0.1, z_far=50, 
                 fov=75) -> None:
        self.x, self.y, self.z = x, y, z
        self.z_near, self.z_far = z_near, z_far
        self.fov = fov
        self.width = width
        self.height = height
        # Used in projection
        self.fov_scalar = math.tan(fov * math.pi / 360) * 0.5
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
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
        


def render(cam:Camera, projection_matrix, render_solid=False, in_lines=False, culling=True) -> list:
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
                vertex[8] = width * vertex[0] / vertex[2] * cam.fov_scalar
                vertex[9] = height * vertex[1] / vertex[2] * cam.fov_scalar
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
    os.system("cls")
    # Object.load_obj("Furniture", "E:\Programming\Python\Python-3D-renderer\models\Furniture")
    # Object.load_obj("monkey")
    Object.load_obj("Crafting_table", "E:\Programming\Python\Python-3D-renderer\models\Crafting_table")
    Object.objects[-1].calculate_smooth_shading_normals()
    Light(3, 3, 3, (9, 94, 9),type=1)
    # Light(-3, -3, -3, (1.5, 1, 1),type=0)
    # exit()

    
    # width, height = 40, 40
    cam = Camera(0, 0, -10, pitch=0)
    # cam = Camera(8.128, 3.999, -5.342, yaw=147, pitch=-22.5)
    cam = Camera(-6.328, 4.125, 3.105, yaw=-17.500, pitch=-32.500)
    cam = Camera(-4.950, 2.5, -4.950, yaw=-120, pitch=-30)





    from msvcrt import getwch
    while True:
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
        elif key == "r":
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