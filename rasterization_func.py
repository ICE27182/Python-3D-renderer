
           

def init_vs():
    # [x,  0    y,  1    z0, 2    u,  3    v,  4    sx, 5    sy, 6    sz, 7]
    def normal():
        normal = [random(), random(), random()]
        length = (normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2) ** 0.5
        return normal[0] / length, normal[1] / length, normal[2] / length
    A = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    B = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    C = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    return A, B, C


def rasterizeA(A, B, C):
    if A[1] > B[1]:
        A, B = B, A
    if B[1] > C[1]:
        B, C = C, B
    if A[1] > B[1]:
        A, B = B, A

    # The order is better than if A[1] != C[1]: ... else: ...
    if A[1] == C[1]:
        g = lambda y: A[1]
    else:
        g = lambda y: (A[0] - C[0]) / (A[1] - C[1]) * y + A[0] - A[1] * (A[0] - C[0]) / (A[1] - C[1])
    if A[1] == B[1]:
        f = lambda y: A[1]
    else:
        f = lambda y: (A[0] - B[0]) / (A[1] - B[1]) * y + A[0] - A[1] * (A[0] - B[0]) / (A[1] - B[1])
    
    for y in range(max(0, A[1]), min(height - 1, B[1])):
        m1 = (y - A[1]) / (B[1] - A[1])
        m2 = 1 - m1
        n1 = (y - A[1]) / (C[1] - A[1])
        n2 = 1 - n1
        # x, z, u, v, sx, sy, sz
        left = (int(f(y)), 
                m2 * A[2] + m1 * B[2], 
                m2 * A[3] + m1 * B[3], 
                m2 * A[4] + m1 * B[4], 
                m2 * A[5] + m1 * B[5], 
                m2 * A[6] + m1 * B[6], 
                m2 * A[7] + m1 * B[7], 
                )
        right = (int(g(y)), 
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
            t1 = (x - left[0]) / (right[0] - left[0])
            t2 = 1 - t1
            z = t2 * left[1] + t1 * right[1]
            if z < z_buffer[y][x]:
                z_buffer[y][x] = z
                u = int((t2 * left[2] + t1 * right[2]) * texture.width)
                v = int((t2 * left[3] + t1 * right[3]) * texture.height)
                color = texture.pixels[v][u]
                normal = (
                    t2 * left[4] + t1 * right[4],
                    t2 * left[5] + t1 * right[5],
                    t2 * left[6] + t1 * right[6],
                )
                # calculate the light
                luminance = 1
                frame[y][x] = (min(int(color[0] * luminance), 255), 
                               min(int(color[1] * luminance), 255), 
                               min(int(color[2] * luminance), 255))
    if B[1] == C[1]:
        f = lambda y: B[1]
    else:
        f = lambda y: (B[0] - C[0]) / (B[1] - C[1]) * y + B[0] - B[1] * (B[0] - C[0]) / (B[1] - C[1])
    for y in range(max(0, B[1]), min(height - 1, C[1])):
        m1 = (y - B[1]) / (C[1] - B[1])
        m2 = 1 - m1
        n1 = (y - A[1]) / (C[1] - A[1])
        n2 = 1 - n1
        # x, z, u, v, sx, sy, sz
        left = (int(f(y)), 
                m2 * B[2] + m1 * C[2], 
                m2 * B[3] + m1 * C[3], 
                m2 * B[4] + m1 * C[4], 
                m2 * B[5] + m1 * C[5], 
                m2 * B[6] + m1 * C[6], 
                m2 * B[7] + m1 * C[7], 
                )
        right = (int(g(y)), 
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
            t1 = (x - left[0]) / (right[0] - left[0])
            t2 = 1 - t1
            z = t2 * left[1] + t1 * right[1]
            if z < z_buffer[y][x]:
                z_buffer[y][x] = z
                u = int((t2 * left[2] + t1 * right[2]) * texture.width)
                v = int((t2 * left[3] + t1 * right[3]) * texture.height)
                color = texture.pixels[v][u]
                normal = (
                    t2 * left[4] + t1 * right[4],
                    t2 * left[5] + t1 * right[5],
                    t2 * left[6] + t1 * right[6],
                )
                # calculate the light
                luminance = 1
                frame[y][x] = (min(int(color[0] * luminance), 255), 
                               min(int(color[1] * luminance), 255), 
                               min(int(color[2] * luminance), 255))



def rasterizeB(A, B, C, texture):
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
                    luminance = 1
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
        

def rasterizeSolid(A, B, C):
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
            m1 = (y - A[1]) / (C[1] - A[1])
            m2 = 1 - m1
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

def display(frame):
    for row in frame:
        for pixel in row:
            print(f"\033[38;2;{pixel[0]};{pixel[1]};{pixel[2]}m██\033[0m", end="")
        print("")


import Readability.png_decoder
texture = Readability.png_decoder.Png("crafting_table_front",dir="E:\Programming\Python\PNG-Decoder\pics\\", from_pickle=False, to_pickle=False)
cola = Readability.png_decoder.Png("Cola_palette",dir="E:\Programming\Python\PNG-Decoder\pics\\", from_pickle=False, to_pickle=False)
texture.display()
width = 100
height = 48
frame = [[(32, 0, 0)] * width for _ in range(height)]

from random import uniform, random, seed
seed(0)
# z_buffer = [[random() for _ in range(width)] for _ in range(height)]
z_buffer = [[10 for _ in range(width)] for _ in range(height)]


A, B, C = init_vs()
while max(A[0], B[0], C[0]) - min(A[0], B[0], C[0]) < 0.4 * width or\
      max(A[1], B[1], C[1]) - min(A[1], B[1], C[1]) < 0.4 * height:
    A, B, C = init_vs()

# rasterizeA(A, B, C)
# display(frame)
rasterizeB(
    (0, 0, 0, 0, 0, 0, 0, 1),
    (16 * 2, 0, 0, 15/16, 0, 0, 0, 1),
    (16 * 2, 16 * 2, 0, 15/16, 15/16, 0, 0, 1),
    texture
)
rasterizeB(
    (0, 0, 0, 0, 0, 0, 0, 1),
    (0, 16 * 2, 0, 0, 15/16, 0, 0, 1),
    (16 * 2, 16 * 2, 0, 15/16, 15/16, 0, 0, 1),
    texture
)
rasterizeB(
    (0, 12, -1, 120/143, 6/320, 0, 0, 1),
    (99, 47, -1, 138/143, 268/320, 0, 0, 1),
    (50, 0, -1, 7/143, 29/320, 0, 0, 1),
    cola
)
# rasterizeA(
#     (0, 0, 0, 0, 0, 0, 0, 1),
#     (0, 16 * 2, 0, 0, 15/16, 0, 0, 1),
#     (16 * 2, 16 * 2, 0, 15/16, 15/16, 0, 0, 1)
# )
# rasterizeB(
#     (0, 0, 0, 0, 0, 0, 0, 1),
#     (24 * 2, 0, 0, 15/16, 0, 0, 0, 1),
#     (16 * 2, 16 * 2, 0, 15/16, 15/16, 0, 0, 1)
# )
# rasterizeB(
#     (0, 0, 0, 0, 0, 0, 0, 1),
#     (6 * 2, 16 * 2, 0, 0, 15/16, 0, 0, 1),
#     (16 * 2, 16 * 2, 0, 15/16, 15/16, 0, 0, 1)
# )

display(frame)
# while True:
#     A, B, C = init_vs()
#     rasterizeA(A, B, C)


# exit()
from timeit import timeit

print(
    timeit(
"""
z_buffer = [[10 for _ in range(width)] for _ in range(height)]
A, B, C = init_vs()
rasterizeB(A, B, C, texture)
""",
"""
def init_vs():
    # [x,  0    y,  1    z0, 2    u,  3    v,  4    sx, 5    sy, 6    sz, 7]
    def normal():
        normal = [random(), random(), random()]
        length = (normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2) ** 0.5
        return normal[0] / length, normal[1] / length, normal[2] / length
    A = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    B = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    C = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    return A, B, C


def rasterizeB(A, B, C, texture):
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
                    luminance = 1
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
        t1 = (B[0] - C[0]) / (B[1] - C[1])
        b1 = B[0] - B[1] * t1
        for y in range(B[1], C[1]):
            m1 = (y - A[1]) / (C[1] - A[1])
            m2 = 1 - m1
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
                    luminance = 1
                    frame[y][x] = (min(int(color[0] * luminance), 255), 
                                min(int(color[1] * luminance), 255), 
                                min(int(color[2] * luminance), 255))

import Readability.png_decoder
texture = Readability.png_decoder.Png("crafting_table_front",dir="E:/Programming/Python/PNG-Decoder/pics/", from_pickle=False, to_pickle=False)

width = 100
height = 48
frame = [[(0, 0, 0)] * width for _ in range(height)]

from random import uniform, random, seed
seed(0)
""",
number = 10**4
    )
)






print(
    timeit(
"""
z_buffer = [[10 for _ in range(width)] for _ in range(height)]
A, B, C = init_vs()
rasterizeA(A, B, C)
""",
"""
def init_vs():
    # [x,  0    y,  1    z0, 2    u,  3    v,  4    sx, 5    sy, 6    sz, 7]
    def normal():
        normal = [random(), random(), random()]
        length = (normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2) ** 0.5
        return normal[0] / length, normal[1] / length, normal[2] / length
    A = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    B = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    C = [int(uniform(-0.5, 1.5) * width), int(uniform(-0.5, 1.5) * height), random(), random(), random(), *normal()]
    return A, B, C



def rasterizeA(A, B, C):
    if A[1] > B[1]:
        A, B = B, A
    if B[1] > C[1]:
        B, C = C, B
    if A[1] > B[1]:
        A, B = B, A

    # The order is better than if A[1] != C[1]: ... else: ...
    if A[1] == C[1]:
        g = lambda y: A[1]
    else:
        g = lambda y: (A[0] - C[0]) / (A[1] - C[1]) * y + A[0] - A[1] * (A[0] - C[0]) / (A[1] - C[1])
    if A[1] == B[1]:
        f = lambda y: A[1]
    else:
        f = lambda y: (A[0] - B[0]) / (A[1] - B[1]) * y + A[0] - A[1] * (A[0] - B[0]) / (A[1] - B[1])
    
    for y in range(max(0, A[1]), min(height - 1, B[1])):
        m1 = (y - A[1]) / (B[1] - A[1])
        m2 = 1 - m1
        n1 = (y - A[1]) / (C[1] - A[1])
        n2 = 1 - n1
        # x, z, u, v, sx, sy, sz
        left = (int(f(y)), 
                m2 * A[2] + m1 * B[2], 
                m2 * A[3] + m1 * B[3], 
                m2 * A[4] + m1 * B[4], 
                m2 * A[5] + m1 * B[5], 
                m2 * A[6] + m1 * B[6], 
                m2 * A[7] + m1 * B[7], 
                )
        right = (int(g(y)), 
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
            t1 = (x - left[0]) / (right[0] - left[0])
            t2 = 1 - t1
            z = t2 * left[1] + t1 * right[1]
            if z < z_buffer[y][x]:
                z_buffer[y][x] = z
                u = int((t2 * left[2] + t1 * right[2]) * texture.width)
                v = int((t2 * left[3] + t1 * right[3]) * texture.height)
                color = texture.pixels[v][u]
                normal = (
                    t2 * left[4] + t1 * right[4],
                    t2 * left[5] + t1 * right[5],
                    t2 * left[6] + t1 * right[6],
                )
                # calculate the light
                luminance = 1
                frame[y][x] = (min(int(color[0] * luminance), 255), 
                               min(int(color[1] * luminance), 255), 
                               min(int(color[2] * luminance), 255))
    if B[1] == C[1]:
        f = lambda y: B[1]
    else:
        f = lambda y: (B[0] - C[0]) / (B[1] - C[1]) * y + B[0] - B[1] * (B[0] - C[0]) / (B[1] - C[1])
    for y in range(max(0, B[1]), min(height - 1, C[1])):
        m1 = (y - B[1]) / (C[1] - B[1])
        m2 = 1 - m1
        n1 = (y - A[1]) / (C[1] - A[1])
        n2 = 1 - n1
        # x, z, u, v, sx, sy, sz
        left = (int(f(y)), 
                m2 * B[2] + m1 * C[2], 
                m2 * B[3] + m1 * C[3], 
                m2 * B[4] + m1 * C[4], 
                m2 * B[5] + m1 * C[5], 
                m2 * B[6] + m1 * C[6], 
                m2 * B[7] + m1 * C[7], 
                )
        right = (int(g(y)), 
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
            t1 = (x - left[0]) / (right[0] - left[0])
            t2 = 1 - t1
            z = t2 * left[1] + t1 * right[1]
            if z < z_buffer[y][x]:
                z_buffer[y][x] = z
                u = int((t2 * left[2] + t1 * right[2]) * texture.width)
                v = int((t2 * left[3] + t1 * right[3]) * texture.height)
                color = texture.pixels[v][u]
                normal = (
                    t2 * left[4] + t1 * right[4],
                    t2 * left[5] + t1 * right[5],
                    t2 * left[6] + t1 * right[6],
                )
                # calculate the light
                luminance = 1
                frame[y][x] = (min(int(color[0] * luminance), 255), 
                               min(int(color[1] * luminance), 255), 
                               min(int(color[2] * luminance), 255))


import Readability.png_decoder
texture = Readability.png_decoder.Png("crafting_table_front",dir="E:/Programming/Python/PNG-Decoder/pics/", from_pickle=False, to_pickle=False)

width = 100
height = 48
frame = [[(0, 0, 0)] * width for _ in range(height)]

from random import uniform, random, seed
seed(0)
""",
number = 10**4
    )
)

