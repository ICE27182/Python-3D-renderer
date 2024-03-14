# import a few standard library
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
from zlib import decompress, compress
import zlib
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
    default_dir = "./"

    def __init__(self, filename, dir=None, pickle_dir="",
                 from_pickle=True, to_pickle=True, crc=False) -> None:
        '''
        filename can be with or without ".png".
        Try to load the image from a pickle file if pickle has been successfully loaded
        and from_pickle == True.
        If failed, it will start the decoding procedure, after which it will store the
        self.pixels into a pickle file (only self.pixels is stored) if to_pickle == True
        '''
        if dir is None:
            dir = Png.default_dir
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
            int.from_bytes(image_bytes[chunk_starting_index+chunk_length+8:chunk_starting_index+chunk_length+12], byteorder="big")
            ):
            raise Exception("CRC Failed")


    def get_chunk_length(image_bytes:bytes, chunk_starting_index:int) -> int:
        return int.from_bytes(image_bytes[chunk_starting_index:chunk_starting_index+4], byteorder="big")


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

        self.width = int.from_bytes(self.bin[16:20], byteorder="big")
        self.height = int.from_bytes(self.bin[20:24], byteorder="big")
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
        self.idat_data = zlib.decompress(idat_data)

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
                                    [int.from_bytes(row[i*2:i*2+2], byteorder="big"),
                                     int.from_bytes(row[i*2:i*2+2], byteorder="big"),
                                     int.from_bytes(row[i*2:i*2+2], byteorder="big"),
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
                        v = int.from_bytes(row[byte_index : byte_index + 2], byteorder="big")
                        a = int.from_bytes(row[byte_index + 2: byte_index + 4], byteorder="big")
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
                                                    byte_index + channel + 2], 
                                                byteorder="big"
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
                                    row[byte_index + channel:byte_index + channel + 2],
                                    byteorder="big"
                                )
                            )
                        channels.append(Png.default_alpha)
                        new_row.append(channels)
                    pixels.append(new_row)
        
        return pixels


    def display(self, rescale = True):
        """
        A pretty basic display function. Would work. Supports rescaling
        image according to the size of the terminal by skipping some 
        pixels. Print X with red background if anything goes wrong
        """
        if rescale:
            try:
                import os
                w, h = os.get_terminal_size()
                w //= 2
                scalar = max(max(1, self.width // w), max(1, self.height // h))
            except ModuleNotFoundError:
                print("Unable to load os module. Unable to rescale the image accordingly")
                scalar = 1
        else:
            scalar = 1

        for y in range(0, self.height, scalar):
            for x in range(0, self.width, scalar):
                try:
                    if self.bit_depth != 16:
                        color = ";".join(map(str, self.pixels[y][x][:-1]))
                    else:
                        color = ";".join(map(lambda v: str(v//256), self.pixels[y][x][:-1]))
                    print(f"\033[38;2;{color}m██", end="")
                except:
                    print(f"\033[41mXX\033[0m", end="")
            print("\033[0m")


    def write_as_bmp(img, path="image.bmp"):
        """
        Donno how to compress the idat chunk properly without 
        writing the whole function myself and dumping the zlib
        """
        if not path.endswith(".bmp"):
            path += ".bmp"
        if isinstance(img, Png):
            img = img.pixels

        width = len(img[0])
        height = len(img)
        size = 54 + 4 * ceil(width/4) * height * 3
        header = (b'BM' + 
                  size.to_bytes(4, "little") + 
                  (0).to_bytes(2, "little") + 
                  (0).to_bytes(2, "little") + 
                  (54).to_bytes(4, "little"))

        dib_header = (
            (40).to_bytes(4, "little") +
            width.to_bytes(4, "little") + 
            height.to_bytes(4, "little") +
            (1).to_bytes(2, "little") +
            (24).to_bytes(2, "little") +      # bit depth
            (0).to_bytes(4, "little") +       # No compression
            (0).to_bytes(4, "little") + 
            (1).to_bytes(4, "little") +
            (1).to_bytes(4, "little") +
            (0).to_bytes(4, "little") +
            (0).to_bytes(4, "little")
        )
        pixels = []
        img.reverse()
        for row in img:
            for pixel in row:
                pixels.append(pixel[2].to_bytes(1, 'little'))
                pixels.append(pixel[1].to_bytes(1, 'little'))
                pixels.append(pixel[0].to_bytes(1, 'little'))
            pixels.append(b'\x00' * (width % 4))
        pixels = b''.join(pixels)
        with open(path, "wb") as image_file:
            image_file.write(header + dib_header + b"\x00" * 6 + pixels)
    

    
def bytes_to_hex(bytes:bytes, start:int=0) -> str:
    """Take bytes type and return a string of hex in upper case, separated with space by 2 digits"""
    return " ".join(bytes[index + start : index + 1 + start].hex().upper() for index in range(len(bytes) - start))


def print_bytes(bytes:bytes, start:int=0, group_size:int=4) -> None:
    """Take bytes type and print a formated string"""
    # Initiate a list where each element is a string in formate of
    # index_n+1 ... index_n+group_size | hex_n+1 ... hex_n+group_size
    output = []
    # Loop through the bytes in groups of 'group_size'
    for index in range(len(bytes[start:]) // group_size):
        output.append("\t".join(str(index * group_size + i + start) for i in range(group_size)) +
                      "\t|\t" +
                      "\t".join(
                          bytes[index * group_size + i + start :
                                index * group_size + i + start + 1].hex().upper() 
                                for i in range(group_size)))
    if len(bytes[start:]) % group_size != 0:
        # Create a line for the remaining bytes (if any)
        index += 1
        output.append("\t".join(str(index * group_size + i + start) for i in range(group_size)) +
                    "\t|\t" +
                    "\t".join(bytes[index * group_size + i + start :
                                index * group_size + i + start + 1].hex().upper() 
                                for i in range(len(bytes[start:]) % group_size)))
    print("\n".join(output))
    


if __name__ == "__main__":
    Png.default_dir = "./pics/"
    # img = Png("16bit", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("white_and_black_plet", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("PLET_web_pink", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("PLET_diamond_pickaxe", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("720p_505", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("ice", from_pickle=False, to_pickle=True, crc=True)
    # img.display()
    # img = Png("Cola", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("multiIDAT_PNG", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("319", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("i", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("ehDpw", from_pickle=False, to_pickle=False, crc=False)
    # img = Png("Cola_palette", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("furnace_front_on", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("grass_block_snow", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("PLET_redstone_block", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("4bit_pirot_grayscale", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("palette_pirot", from_pickle=False, to_pickle=False, crc=True)
    # img.display()
    # img = Png("desktop", from_pickle=True, to_pickle=True, crc=False)


    # img = Png("Cola", from_pickle=False, to_pickle=False, crc=True)
    # i = img.bin.index(b"IDAT") + 4
    # # exit()
    # img.get_all_idat_data()


    img1 = Png("Image", from_pickle=False, to_pickle=False, crc=True)
    img1.display()
    from random import random as rd
    for y in range(img1.height):
        for x in range(img1.width):
            img1.pixels[y][x][0] *= 1 + rd()
            img1.pixels[y][x][0] = min(255, max(0, int(img1.pixels[y][x][0])))
            img1.pixels[y][x][1] *= 1 + rd()
            img1.pixels[y][x][1] = min(255, max(0, int(img1.pixels[y][x][1])))
            img1.pixels[y][x][2] *= 1 + rd()
            img1.pixels[y][x][2] = min(255, max(0, int(img1.pixels[y][x][2])))
    img1.write_as_bmp()
    
