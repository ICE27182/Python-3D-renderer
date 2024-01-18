from png import *
from Readability.pyrender import display
dreso = 512
uv_map = [[None] * dreso for _ in range(dreso)]

texture = Png("texture")

print(texture.height, texture.width)

x_scalar = texture.width / dreso
y_scalar = texture.height / dreso

for y in range(dreso):
    for x in range(dreso):
        uv_map[y][x] = texture.pixels[int(y * y_scalar)][int(x * x_scalar)]

display(uv_map)
