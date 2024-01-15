from Readability import png

def fxaa(pixels, threshold = 64) -> list:
    width = len(pixels[0])
    height = len(pixels)
    frame = pixels[0:1] + [[None] * width for _ in range(height - 2)]

    frame.append(pixels[height - 1])

    for y in range(1, height - 1):
        frame[y][0] = pixels[y][0]
        frame[y][width - 1] = pixels[y][width - 1]
        for x in range(1, width - 1):
            if (
                abs(pixels[y - 1][x][1] - pixels[y][x][1]) +
                abs(pixels[y + 1][x][1] - pixels[y][x][1]) +
                abs(pixels[y][x - 1][1] - pixels[y][x][1]) +
                abs(pixels[y][x + 1][1] - pixels[y][x][1])
                ) > threshold * 2:
                # frame[y][x] = [255, 0, 0]
                frame[y][x] = [(pixels[y-1][x-1][0] + pixels[y-1][x][0] + pixels[y-1][x+1][0] +
                               pixels[y][x-1][0] + pixels[y][x][0] + pixels[y][x+1][0] + 
                               pixels[y+1][x-1][0] + pixels[y+1][x][0] + pixels[y+1][x+1][0])//9,
                               (pixels[y-1][x-1][1] + pixels[y-1][x][1] + pixels[y-1][x+1][1] +
                               pixels[y][x-1][1] + pixels[y][x][1] + pixels[y][x+1][1] + 
                               pixels[y+1][x-1][1] + pixels[y+1][x][1] + pixels[y+1][x+1][1])//9,
                               (pixels[y-1][x-1][2] + pixels[y-1][x][2] + pixels[y-1][x+1][2] +
                               pixels[y][x-1][2] + pixels[y][x][2] + pixels[y][x+1][2] + 
                               pixels[y+1][x-1][2] + pixels[y+1][x][2] + pixels[y+1][x+1][2])//9,]
            else:
                frame[y][x] = pixels[y][x]
    return frame

def display(frame):
    image = []
    for row in frame:
        for pixel in row:
            if pixel == [0, 0, 0]:
                image.append("  ")
            # else:
            #     print(pixel, end="")
            else:
                image.append(f"\033[38;2;{pixel[0]};{pixel[1]};{pixel[2]}m██")
        image.append("\n")
    print("".join(image), end=f"\033[0m")

img = png.Png("fxaatest", "", from_pickle=False)
img = png.Png("crafting_table_front", "models/Crafting_table/", from_pickle=False)
img.display()
aa_img_pixels = fxaa(img.pixels)
display(aa_img_pixels)
