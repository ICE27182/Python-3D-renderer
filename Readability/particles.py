from random import seed, uniform
from winsound import Beep
# import pymain
seed(27182)
random_table = [uniform(-1, 1) for _ in range(255)]

class Particles:
    def __init__(self, density=10, position=(0, 0, 0), size=1) -> None:
        self.density = density
        self.position = position
        self.size = size
        self.density_r = 1 / density
        self.particles = [
            [x * self.density_r + position[0], y * self.density_r + position[1], z * self.density_r + position[2],] 
            for x in range(density * size) for y in range(density * size) for z in range(density * size)
        ]
        for particle in self.particles:
            particle[0] += random_table[int((particle[1] + particle[2]) * self.density) % 255] * self.density_r
            particle[1] += random_table[int((particle[0] + particle[2]) * self.density) % 255] * self.density_r
            particle[2] += random_table[int((particle[0] + particle[1]) * self.density) % 255] * self.density_r
            particle[0] = (particle[0] - self.position[0]) % self.size + self.position[0]
            particle[1] = (particle[1] - self.position[1]) % self.size + self.position[1]
            particle[2] = (particle[2] - self.position[2]) % self.size + self.position[2]
    
    def next_frame(self, time=0, percentage = 0.1):
        start_index = int(len(self.particles) * random_table[time % 255])
        end_index = int(len(self.particles) * percentage) + start_index
        for index in range(start_index, end_index):
            particle = self.particles[index % len(self.particles)]
            particle[0] += random_table[int((particle[1] + particle[2]) * self.density) % 255] * self.density_r * 0.01
            particle[1] += random_table[int((particle[0] + particle[2]) * self.density) % 255] * self.density_r * 0.01
            particle[2] += random_table[int((particle[0] + particle[1]) * self.density) % 255] * self.density_r * 0.01
            particle[0] = (particle[0] - self.position[0]) % self.size + self.position[0]
            particle[1] = (particle[1] - self.position[1]) % self.size + self.position[1]
            particle[2] = (particle[2] - self.position[2]) % self.size + self.position[2]
    
    def add_to_frame(self, frame:list, lights:list, cam) -> list:

        for particle in self.particles:
            x = particle[0] - cam.x
            y = particle[1] - cam.y
            z = particle[2] - cam.z
            x, y, z = (
                x * cam.rotation[0][0] + y * cam.rotation[0][1] + z * cam.rotation[0][2],
                x * cam.rotation[1][0] + y * cam.rotation[1][1] + z * cam.rotation[1][2],
                x * cam.rotation[2][0] + y * cam.rotation[2][1] + z * cam.rotation[2][2],
            )
            if z <= cam.z_near:
                continue

            x2d = cam.width // 2 + int(x * cam.rendering_plane_z / z)
            y2d = cam.height // 2 - int(y * cam.rendering_plane_z / z)
            if not (0 <= x2d < cam.width and 0 <= y2d < cam.height):
                continue
            
            
            for light in lights:
                distance_2 = (x - light.x_in_cam) * (x - light.x_in_cam) + (y - light.y_in_cam) * (y - light.y_in_cam) + (z - light.z_in_cam) * (z - light.z_in_cam)
                if distance_2 < 400:
                    frame[y2d][x2d] = (min(255, int(frame[y2d][x2d][0] + 50 / distance_2)), 
                                       min(255, int(frame[y2d][x2d][1] + 50 / distance_2)), 
                                       min(255, int(frame[y2d][x2d][2] + 50 / distance_2)))
        return frame



