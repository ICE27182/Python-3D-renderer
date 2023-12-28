"""
# [x, y, z, u, v, snx, sny, snz, x2d, y2d]
#  0  1  2  3  4   5    6    7    8    9    
A[5:8] = (
            cam.rotation[0][0] * normal[0] + cam.rotation[0][1] * normal[1] + cam.rotation[0][2] * normal[2], 
            cam.rotation[1][0] * normal[0] + cam.rotation[1][1] * normal[1] + cam.rotation[1][2] * normal[2], 
            cam.rotation[2][0] * normal[0] + cam.rotation[2][1] * normal[1] + cam.rotation[2][2] * normal[2], 
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
"""
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
                # calculate the light
                x3d = p2 * left[0] + p1 * right[0]
                y3d = p2 * left[1] + p1 * right[1]
                luminance = get_luminance(normal, x3d, y3d, z3d)
                frame[y][x] = (min(int(color[0] * luminance[0]), 255), 
                            min(int(color[1] * luminance[1]), 255), 
                            min(int(color[2] * luminance[2]), 255))