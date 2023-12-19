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