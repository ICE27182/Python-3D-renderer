from pyrender import *

def render_just_for_reference(objects:list, lights:list, cam:Camera):
    def get_luminance(normal, x3d, y3d, z3d) -> list:
        # Default value for no light at all
        # can be adjusted according to needs
        luminance = [0.05, 0.05, 0.05]
        # CodeUndone VsCode
        light:Light
        for light in Light.lights:
            if light.hidden:
                continue
            if light.type == 0:
                # normalize b to 0-1
                b = - ((light.dirx_in_cam * normal[0] + 
                        light.diry_in_cam * normal[1] +
                        light.dirz_in_cam * normal[2]) - 1) / 2
                luminance[0] += light.r * b
                luminance[1] += light.g * b
                luminance[2] += light.b * b
            else:    # light.type == 1
                direction = (
                    light.x_in_cam - x3d,
                    light.y_in_cam - y3d,
                    light.z_in_cam - z3d,
                )
                length_2 = direction[0]**2 + direction[1]**2 + direction[2]**2
                b = max(0, 
                        (
                            (
                                direction[0] * normal[0] + 
                                direction[1] * normal[1] +
                                direction[2] * normal[2]
                            )
                        ) / 
                        length_2
                    )
                
                luminance[0] += light.r * b
                luminance[1] += light.g * b
                luminance[2] += light.b * b
            
            if obj.shadow and light.shadow:
                if light.type == 0 and light.shadow_map0 != None:
                    # return [
                    #     (x3d + 50) / 100,
                    #     (y3d + 50) / 100,
                    #     0, 0, 
                    #     # (cam.z_far - z3d) / (cam.z_far - cam.z_near)
                    #     ]
                    x3d -= light.x_in_cam
                    y3d -= light.y_in_cam
                    z3d -= light.z_in_cam
                    x3d, y3d, z3d = (
                        x3d * light.rotation0[0][0] + y3d * light.rotation0[0][1] + z3d * light.rotation0[0][2],
                        x3d * light.rotation0[1][0] + y3d * light.rotation0[1][1] + z3d * light.rotation0[1][2],
                        x3d * light.rotation0[2][0] + y3d * light.rotation0[2][1] + z3d * light.rotation0[2][2],
                    )
                    x2d = light.shadow_properties[0] // 2 + int(x3d * 10)
                    y2d = light.shadow_properties[0] // 2 - int(y3d * 10)
                    # return [x2d / light.shadow_properties[0] * 5,
                    #         y2d / light.shadow_properties[0] * 5,
                    #         (z3d - light.shadow_properties[1]) / (light.shadow_properties[2] - light.shadow_properties[1])]
                    if 0 <= x2d < Light.shadow_properties[0] and 0 <= y2d < Light.shadow_properties[0]:
                        # bias = (1 - (light.rotation0[2][0] * normal[0] + light.rotation0[2][1] * normal[1] + light.rotation0[2][2] * normal[2])) * 0.001
                        bias = 0.01
                        if z3d > light.shadow_map0[y2d][x2d] + bias:
                            return [luminance[0] * 0.5,
                                    luminance[1] * 0.5,
                                    luminance[2] * 0.5,]
                elif light.type == 1 and light.shadow_map1 != None:
                    x3d -= light.x_in_cam
                    y3d -= light.y_in_cam
                    z3d -= light.z_in_cam

                    
        return luminance
    

    def add_line(M, N):
        if M[8] == N[8]:
            if 0 <= M[8] < cam.width:
                if M[9] > N[9]:
                    M, N = N, M
                for y in range(max(0, M[9]), min(cam.height - 1, N[9])):
                    frame[y][M[8]] = (127, 127, 127)
        elif abs(k:=(M[9] - N[9]) / (M[8] - N[8])) <= 1:
            b = M[9] - k * M[8]
            if M[8] > N[8]:
                M, N = N, M
            for x in range(max(0, M[8]), min(cam.width - 1, N[8])):
                # CodeUndone
                y = int(k * x + b)
                if 0 <= y < cam.height:
                    frame[y][x] = (127, 127, 127)
                # frame[int(k * x + b)][x] = (127, 127, 127)
        else:
            t = 1 / k
            b = M[8] - t * M[9]
            if M[9] > N[9]:
                M, N = N, M
            for y in range(max(0, M[9]), min(cam.height - 1, N[9])):
                x = int(t * y + b)
                if 0 <= x < cam.width:
                    frame[y][x] = (127, 127, 127)
                # frame[y][int(t * y + b)] = (127, 127, 127)
        

    def rasterize_solid(A, B, C, normal):
        # Sorting by y, from lowest to highest in value but from top to bottom in what u see
        if A[9] > B[9]:
            A, B = B, A
        if B[9] > C[9]:
            B, C = C, B
        if A[9] > B[9]:
            A, B = B, A
        # Remove some of those out of screen
        if A[9] >= cam.height or C[9] < 0 or A[9] == C[9]:
            return
        
        if A[9] == B[9]:
            # If line AB can be seen, add line AB
            if A[8] < B[8]:
                left = A
                right = B
            else:
                left = B
                right = A
            if A[9] >= 0:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[A[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[A[9]][x] = obj
                        depth_buffer[A[9]][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[A[9]][x] = (min(int(127 * luminance[0]), 255), 
                                          min(int(127 * luminance[1]), 255), 
                                          min(int(127 * luminance[2]), 255))
            # The rest of the triangle
            t1 = (A[8] - C[8]) / (A[9] - C[9])
            b1 = A[8] - A[9] * t1
            t2 = (B[8] - C[8]) / (B[9] - C[9])
            b2 = B[8] - B[9] * t2
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            None, 
                            None, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )    
                else:
                    # x, z, u, v, 0, 0, 0, x2d, y2d
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )            
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
        elif B[9] == C[9]:
            # If line BC can be seen, add line BC
            if B[8] < C[8]:
                left = B
                right = C
            else:
                left = C
                right = B
            if B[9] < cam.height:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[B[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[B[9]][x] = obj
                        depth_buffer[B[9]][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[B[9]][x] = (min(int(127 * luminance[0]), 255), 
                                          min(int(127 * luminance[1]), 255), 
                                          min(int(127 * luminance[2]), 255))
            # The rest of the triangle
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            ) 
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
        else:
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (B[9] - A[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (n2 * A[0] + n1 * C[0],
                            n2 * A[1] + n1 * C[1],
                            n2 * A[2] + n1 * C[2],
                            None, 
                            None, 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (n2 * A[0] + n1 * C[0],
                            n2 * A[1] + n1 * C[1],
                            n2 * A[2] + n1 * C[2],
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
            t1 = (B[8] - C[8]) / (B[9] - C[9])
            b1 = B[8] - B[9] * t1
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - B[9]) / (C[9] - B[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                    min(int(127 * luminance[1]), 255), 
                                    min(int(127 * luminance[2]), 255))


    def rasterize_solid_corrected(A, B, C, normal):
        # Sorting by y, from lowest to highest in value but from top to bottom in what u see
        if A[9] > B[9]:
            A, B = B, A
        if B[9] > C[9]:
            B, C = C, B
        if A[9] > B[9]:
            A, B = B, A
        # Remove some of those out of screen
        if A[9] >= cam.height or C[9] < 0 or A[9] == C[9]:
            return
        
        if A[9] == B[9]:
            # If line AB can be seen, add line AB
            if A[8] < B[8]:
                left = A
                right = B
            else:
                left = B
                right = A
            if A[9] >= 0:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[A[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[A[9]][x] = obj
                        depth_buffer[A[9]][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # perspective correction
                        z3d_reciprocal = 1 / z3d
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[A[9]][x] = (min(int(127 * luminance[0]), 255), 
                                          min(int(127 * luminance[1]), 255), 
                                          min(int(127 * luminance[2]), 255))
            # The rest of the triangle
            t1 = (A[8] - C[8]) / (A[9] - C[9])
            b1 = A[8] - A[9] * t1
            t2 = (B[8] - C[8]) / (B[9] - C[9])
            b2 = B[8] - B[9] * t2
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            None, 
                            None, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )    
                else:
                    # x, z, u, v, 0, 0, 0, x2d, y2d
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )            
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
        elif B[9] == C[9]:
            # If line BC can be seen, add line BC
            if B[8] < C[8]:
                left = B
                right = C
            else:
                left = C
                right = B
            if B[9] < cam.height:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[B[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[B[9]][x] = obj
                        depth_buffer[B[9]][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[B[9]][x] = (min(int(127 * luminance[0]), 255), 
                                          min(int(127 * luminance[1]), 255), 
                                          min(int(127 * luminance[2]), 255))
            # The rest of the triangle
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            ) 
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
        else:
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (B[9] - A[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (n2 * A[0] + n1 * C[0],
                            n2 * A[1] + n1 * C[1],
                            n2 * A[2] + n1 * C[2],
                            None, 
                            None, 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                    right = (n2 * A[0] + n1 * C[0],
                            n2 * A[1] + n1 * C[1],
                            n2 * A[2] + n1 * C[2],
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                       min(int(127 * luminance[1]), 255), 
                                       min(int(127 * luminance[2]), 255))
            t1 = (B[8] - C[8]) / (B[9] - C[9])
            b1 = B[8] - B[9] * t1
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - B[9]) / (C[9] - B[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                    min(int(127 * luminance[1]), 255), 
                                    min(int(127 * luminance[2]), 255))


    def rasterize_test(A, B, C, normal):

        def line(left, right):
            # faster than max(...), min(...)
            if left[8] <= 0:
                x_start = 0
            else:
                x_start = left[8]
            if right[8] >= cam.width - 1:
                x_end = cam.width - 1
            else:
                x_end = right[8]

            for x in range(x_start, x_end):
                p1 = (x - left[8]) / (right[8] - left[8])
                p2 = 1 - p1
                z3d = 1 / (p2 * left[2] + p1 * right[2])
                if z3d < depth_buffer[y][x]:
                    if cam.obj_buffer:
                        obj_buffer[y][x] = obj
                    depth_buffer[y][x] = z3d
                    if obj.shade_smooth:
                        normal = (
                            p2 * left[5] + p1 * right[5],
                            p2 * left[6] + p1 * right[6],
                            p2 * left[7] + p1 * right[7],
                        )
                        length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                        normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                    # calculate the light
                    dominator_reciprocal = 1 / (p2 * left[2] + p1 * right[2])
                    x3d = (p2 * left[0] + p1 * right[0]) * dominator_reciprocal
                    y3d = (p2 * left[1] + p1 * right[1]) * dominator_reciprocal

                    luminance = get_luminance(normal, x3d, y3d, z3d)
                    frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                   min(int(127 * luminance[1]), 255), 
                                   min(int(127 * luminance[2]), 255))
        # Sorting by y, from lowest to highest in value but from top to bottom in what u see
        if A[9] > B[9]:
            A, B = B, A
        if B[9] > C[9]:
            B, C = C, B
        if A[9] > B[9]:
            A, B = B, A
        # Remove some of those out of screen
        if A[9] >= cam.height or C[9] < 0 or A[9] == C[9]:
            return
        
        # use the v / z3d for x3d, y3d, u, v, and transform z3d to its reciprocal, 1 / z3d
        # the order 20134 is because mutiplication is faster than division
        A[2] = 1 / A[2]
        A[0] = A[0] * A[2]
        A[1] = A[1] * A[2]
        B[2] = 1 / B[2]
        B[0] = B[0] * B[2]
        B[1] = B[1] * B[2]
        C[2] = 1 / C[2]
        C[0] = C[0] * C[2]
        C[1] = C[1] * C[2]
        if A[3] != None:
            A[3] = A[3] * A[2]
            A[4] = A[4] * A[2]
            B[3] = B[3] * B[2]
            B[4] = B[4] * B[2]
            C[3] = C[3] * C[2]
            C[4] = C[4] * C[2]

        tAC = (A[8] - C[8]) / (A[9] - C[9])
        bAC = A[8] - A[9] * tAC

        if A[9] == B[9]:
            if A[8] > B[8]:
                A, B = B, A
            line(A, B)

            tBC = (B[8] - C[8]) / (B[9] - C[9])
            bBC = B[8] - B[9] * tBC

            if B[9] <= 0:
                y_start = 0
            else:
                y_start = B[9]
            if C[9] >= cam.height - 1:
                y_end = cam.height - 1
            else:
                y_end = C[9]
            for y in range(y_start, y_end):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            A[3] * m2 + C[3] * m1, 
                            A[4] * m2 + C[4] * m1, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(tAC * y + bAC),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            B[3] * m2 + C[3] * m1, 
                            B[4] * m2 + C[4] * m1, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(tBC * y + bBC),
                            y, 
                            )    
                else:
                    # x, z, u, v, 0, 0, 0, x2d, y2d
                    left = (m2 * A[0] + m1 * C[0], 
                            m2 * A[1] + m1 * C[1], 
                            m2 * A[2] + m1 * C[2], 
                            A[3] * m2 + C[3] * m1, 
                            A[4] * m2 + C[4] * m1, 
                            None, 
                            None, 
                            None, 
                            int(tAC * y + bAC),
                            y, 
                            )            
                    right = (m2 * B[0] + m1 * C[0],
                            m2 * B[1] + m1 * C[1],
                            m2 * B[2] + m1 * C[2],
                            B[3] * m2 + C[3] * m1, 
                            B[4] * m2 + C[4] * m1, 
                            None, 
                            None, 
                            None, 
                            int(tBC * y + bBC),
                            y, 
                            )
                # CodeUndone Should be unnecessary to check left and right
                # because A is left to B and left is AC, right is BC
                if left[8] > right[8]:
                    left, right = right, left
                line(left, right)

        elif B[9] == C[9]:
            if B[8] > C[8]:
                B, C = C, B
            line(B, C)

            tAB = (B[8] - C[8]) / (B[9] - C[9])
            bAB = B[8] - B[9] * tAB

            if A[9] <= 0:
                y_start = 0
            else:
                y_start = A[9]
            if B[9] >= cam.height - 1:
                y_end = cam.height - 1
            else:
                y_end = B[9]
            for y in range(y_start, y_end):
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            A[3] * m2 + B[3] * m1, 
                            A[4] * m2 + B[4] * m1, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(tAB * y + bAB),
                            y, 
                            )            
                    right = (m2 * A[0] + m1 * C[0],
                            m2 * A[1] + m1 * C[1],
                            m2 * A[2] + m1 * C[2],
                            A[3] * m2 + C[3] * m1, 
                            A[4] * m2 + C[4] * m1, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(tAC * y + bAC),
                            y, 
                            )    
                else:
                    # x, z, u, v, 0, 0, 0, x2d, y2d
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            A[3] * m2 + B[3] * m1, 
                            A[4] * m2 + B[4] * m1, 
                            None, 
                            None, 
                            None, 
                            int(tAB * y + bAB),
                            y, 
                            )            
                    right = (m2 * A[0] + m1 * C[0],
                            m2 * A[1] + m1 * C[1],
                            m2 * A[2] + m1 * C[2],
                            A[3] * m2 + C[3] * m1, 
                            A[4] * m2 + C[4] * m1, 
                            None, 
                            None, 
                            None, 
                            int(tAC * y + bAC),
                            y, 
                            )
                # CodeUndone Should be unnecessary to check left and right
                # because A is left to B and left is AC, right is BC            
                if left[8] > right[8]:
                    left, right = right, left
                line(left, right)
        
        else:
            tAB = (A[8] - B[8]) / (A[9] - B[9])
            bAB = A[8] - A[9] * tAB

            if A[9] <= 0:
                y_start = 0
            else:
                y_start = A[9]
            if B[9] >= cam.height - 1:
                y_end = cam.height - 1
            else:
                y_end = B[9]
            for y in range(y_start, y_end):
                if A[9] <= 0:
                    y_start = 0
            else:
                y_start = A[9]
            if B[9] >= cam.height - 1:
                y_end = cam.height - 1
            else:
                y_end = B[9]
            for y in range(y_start, y_end):
                m2 = 1 - m1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            A[3] * m2 + B[3] * m1, 
                            A[4] * m2 + B[4] * m1, 
                            m2 * A[5] + m1 * B[5], 
                            m2 * A[6] + m1 * B[6], 
                            m2 * A[7] + m1 * B[7], 
                            int(tAB * y + bAB),
                            y, 
                            )            
                    right = (m2 * A[0] + m1 * C[0],
                            m2 * A[1] + m1 * C[1],
                            m2 * A[2] + m1 * C[2],
                            A[3] * m2 + C[3] * m1, 
                            A[4] * m2 + C[4] * m1, 
                            m2 * A[5] + m1 * C[5], 
                            m2 * A[6] + m1 * C[6], 
                            m2 * A[7] + m1 * C[7], 
                            int(tAC * y + bAC),
                            y, 
                            )    
                else:
                    # x, z, u, v, 0, 0, 0, x2d, y2d
                    left = (m2 * A[0] + m1 * B[0], 
                            m2 * A[1] + m1 * B[1], 
                            m2 * A[2] + m1 * B[2], 
                            A[3] * m2 + B[3] * m1, 
                            A[4] * m2 + B[4] * m1, 
                            None, 
                            None, 
                            None, 
                            int(tAB * y + bAB),
                            y, 
                            )            
                    right = (m2 * A[0] + m1 * C[0],
                            m2 * A[1] + m1 * C[1],
                            m2 * A[2] + m1 * C[2],
                            A[3] * m2 + C[3] * m1, 
                            A[4] * m2 + C[4] * m1, 
                            None, 
                            None, 
                            None, 
                            int(tAC * y + bAC),
                            y, 
                            )
                # CodeUndone Should be unnecessary to check left and right
                # because A is left to B and left is AC, right is BC            
                if left[8] > right[8]:
                    left, right = right, left
                line(left, right)

            t1 = (B[8] - C[8]) / (B[9] - C[9])
            b1 = B[8] - B[9] * t1
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - B[9]) / (C[9] - B[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                if obj.shade_smooth:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            n2 * A[5] + n1 * C[5], 
                            n2 * A[6] + n1 * C[6], 
                            n2 * A[7] + n1 * C[7], 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            m2 * B[5] + m1 * C[5], 
                            m2 * B[6] + m1 * C[6], 
                            m2 * B[7] + m1 * C[7], 
                            int(t1 * y + b1),
                            y, 
                            )  
                else:
                    # x, y, z, u, v, sx, sy, sz
                    left = (n2 * A[0] + n1 * C[0], 
                            n2 * A[1] + n1 * C[1], 
                            n2 * A[2] + n1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t2 * y + b2),
                            y, 
                            )  
                    right = (m2 * B[0] + m1 * C[0], 
                            m2 * B[1] + m1 * C[1], 
                            m2 * B[2] + m1 * C[2], 
                            None, 
                            None, 
                            None, 
                            None, 
                            None, 
                            int(t1 * y + b1),
                            y, 
                            )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        if obj.shade_smooth:
                            normal = (
                                p2 * left[5] + p1 * right[5],
                                p2 * left[6] + p1 * right[6],
                                p2 * left[7] + p1 * right[7],
                            )
                            length = sqrt(normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2])
                            normal = (normal[0]/length, normal[1]/length, normal[2]/length)
                        # calculate the light
                        x3d = p2 * left[0] + p1 * right[0]
                        y3d = p2 * left[1] + p1 * right[1]
                        luminance = get_luminance(normal, x3d, y3d, z3d)
                        frame[y][x] = (min(int(127 * luminance[0]), 255), 
                                    min(int(127 * luminance[1]), 255), 
                                    min(int(127 * luminance[2]), 255))

        

        
  

    
    def rasterize_full(A, B, C):
        return


    def depth(A, B, C):
        # Sorting by y, from lowest to highest in value but from top to bottom in what u see
        if A[9] > B[9]:
            A, B = B, A
        if B[9] > C[9]:
            B, C = C, B
        if A[9] > B[9]:
            A, B = B, A
        # Remove some of those out of screen
        if A[9] >= cam.height or C[9] < 0 or A[9] == C[9]:
            return
        
        if A[9] == B[9]:
            # If line AB can be seen, add line AB
            if A[8] < B[8]:
                left = A
                right = B
            else:
                left = B
                right = A
            if A[9] >= 0:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[A[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[A[9]][x] = obj
                        depth_buffer[A[9]][x] = z3d
                        frame[A[9]][x] = (
                            int(255 * (cam.z_far - z3d) / (cam.z_far - cam.z_near)),
                        ) * 3
            # The rest of the triangle
            t1 = (A[8] - C[8]) / (A[9] - C[9])
            b1 = A[8] - A[9] * t1
            t2 = (B[8] - C[8]) / (B[9] - C[9])
            b2 = B[8] - B[9] * t2
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                # x, z, u, v, s, x2d, y2d
                left = (m2 * A[0] + m1 * C[0], 
                        m2 * A[1] + m1 * C[1], 
                        m2 * A[2] + m1 * C[2], 
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t1 * y + b1),
                        y, 
                        )            
                right = (m2 * B[0] + m1 * C[0],
                        m2 * B[1] + m1 * C[1],
                        m2 * B[2] + m1 * C[2],
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t2 * y + b2),
                        y, 
                        )            
                
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        frame[y][x] = (
                            int(255 * (cam.z_far - z3d) / (cam.z_far - cam.z_near)),
                        ) * 3
        elif B[9] == C[9]:
            # If line BC can be seen, add line BC
            if B[8] < C[8]:
                left = B
                right = C
            else:
                left = C
                right = B
            if B[9] < cam.height:
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[B[9]][x]:
                        if cam.obj_buffer:
                            obj_buffer[B[9]][x] = obj
                        depth_buffer[B[9]][x] = z3d
                        frame[B[9]][x] = (
                            int(255 * (cam.z_far - z3d) / (cam.z_far - cam.z_near)),
                        ) * 3
            # The rest of the triangle
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (C[9] - A[9])
                m2 = 1 - m1
                # x, y, z, u, v, sx, sy, sz
                left = (m2 * A[0] + m1 * B[0], 
                        m2 * A[1] + m1 * B[1], 
                        m2 * A[2] + m1 * B[2], 
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t1 * y + b1),
                        y, 
                        )  
                right = (m2 * A[0] + m1 * C[0], 
                        m2 * A[1] + m1 * C[1], 
                        m2 * A[2] + m1 * C[2], 
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t2 * y + b2),
                        y, 
                        ) 
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        frame[y][x] = (
                            int(255 * (cam.z_far - z3d) / (cam.z_far - cam.z_near)),
                        ) * 3
        else:
            t1 = (A[8] - B[8]) / (A[9] - B[9])
            b1 = A[8] - A[9] * t1
            t2 = (A[8] - C[8]) / (A[9] - C[9])
            b2 = A[8] - A[9] * t2
            for y in range(max(0, A[9]), min(cam.height - 1, B[9])):
                m1 = (y - A[9]) / (B[9] - A[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                # x, y, z, u, v, sx, sy, sz
                left = (m2 * A[0] + m1 * B[0], 
                        m2 * A[1] + m1 * B[1], 
                        m2 * A[2] + m1 * B[2], 
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t1 * y + b1),
                        y, 
                        )  
                right = (n2 * A[0] + n1 * C[0],
                        n2 * A[1] + n1 * C[1],
                        n2 * A[2] + n1 * C[2],
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t2 * y + b2),
                        y, 
                        )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        frame[y][x] = (
                            int(255 * (cam.z_far - z3d) / (cam.z_far - cam.z_near)),
                        ) * 3
            t1 = (B[8] - C[8]) / (B[9] - C[9])
            b1 = B[8] - B[9] * t1
            for y in range(max(0, B[9]), min(cam.height - 1, C[9])):
                m1 = (y - B[9]) / (C[9] - B[9])
                m2 = 1 - m1
                n1 = (y - A[9]) / (C[9] - A[9])
                n2 = 1 - n1
                # x, y, z, u, v, sx, sy, sz
                left = (n2 * A[0] + n1 * C[0], 
                        n2 * A[1] + n1 * C[1], 
                        n2 * A[2] + n1 * C[2], 
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t2 * y + b2),
                        y, 
                        )  
                right = (m2 * B[0] + m1 * C[0], 
                        m2 * B[1] + m1 * C[1], 
                        m2 * B[2] + m1 * C[2], 
                        None, 
                        None, 
                        None, 
                        None, 
                        None, 
                        int(t1 * y + b1),
                        y, 
                        )  
                if left[8] > right[8]:
                    left, right = right, left
                for x in range(max(0, left[8]), min(cam.width - 1, right[8])):
                    p1 = (x - left[8]) / (right[8] - left[8])
                    p2 = 1 - p1
                    z3d = p2 * left[2] + p1 * right[2]
                    if z3d < depth_buffer[y][x]:
                        if cam.obj_buffer:
                            obj_buffer[y][x] = obj
                        depth_buffer[y][x] = z3d
                        frame[y][x] = (
                            int(255 * (cam.z_far - z3d) / (cam.z_far - cam.z_near)),
                        ) * 3
    
    # Just to cover 0, 1, 2, 3, 4 in a easier and faster way
    # Of course I know mode is not a number that can be campared with each other
    if cam.mode <= 5:
        depth_buffer = [[cam.z_far] * cam.width for _ in range(cam.height)]
    else:
        depth_buffer = None
    if cam.obj_buffer:
        obj_buffer = [[None] * cam.width for _ in range(cam.height)]
    else:
        obj_buffer = None
    # Do not need depth test for lines
    # elif cam.type in (6, 7): pass
    frame = [[(0, 0, 0)] * cam.width for _ in range(cam.height)]
    light:Light    # CodeUndone Vscode
    obj: Object    # CodeUndone Vscode
    # Put light in the same space as what the objects will be put in
    for light in lights:
        if light.hidden:
            continue
        # CodeUndone
        # update it only when rotating camera may help the perforamce
        # Move
        light.x_in_cam = light.x - cam.x
        light.y_in_cam = light.y - cam.y
        light.z_in_cam = light.z - cam.z
        # Rotation
        light.x_in_cam, light.y_in_cam, light.z_in_cam = (
            light.x_in_cam * cam.rotation[0][0] + light.y_in_cam * cam.rotation[0][1] + light.z_in_cam * cam.rotation[0][2],
            light.x_in_cam * cam.rotation[1][0] + light.y_in_cam * cam.rotation[1][1] + light.z_in_cam * cam.rotation[1][2],
            light.x_in_cam * cam.rotation[2][0] + light.y_in_cam * cam.rotation[2][1] + light.z_in_cam * cam.rotation[2][2],
        )
        if light.type == 0:
            light.dirx_in_cam, light.diry_in_cam, light.dirz_in_cam = (
                light.dirx * cam.rotation[0][0] + light.diry * cam.rotation[0][1] + light.dirz * cam.rotation[0][2],
                light.dirx * cam.rotation[1][0] + light.diry * cam.rotation[1][1] + light.dirz * cam.rotation[1][2],
                light.dirx * cam.rotation[2][0] + light.diry * cam.rotation[2][1] + light.dirz * cam.rotation[2][2],
            ) 
        light.update_rotation(cam)
    for obj in objects:
        if obj.hidden:
            continue
        for face in obj.faces:
            # Move the object
            A = [obj.v[face[0][0]][0] - cam.x,
                 obj.v[face[0][0]][1] - cam.y,
                 obj.v[face[0][0]][2] - cam.z,]
            B = [obj.v[face[0][1]][0] - cam.x,
                 obj.v[face[0][1]][1] - cam.y,
                 obj.v[face[0][1]][2] - cam.z,]
            C = [obj.v[face[0][2]][0] - cam.x,
                 obj.v[face[0][2]][1] - cam.y,
                 obj.v[face[0][2]][2] - cam.z,]
            A.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], None, None))
            B.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], None, None))
            C.extend((0, 0, Object.vn[face[2]][0], Object.vn[face[2]][1], Object.vn[face[2]][2], None, None))
            # [x, y, z, u, v, snx, sny, snz, x2d, y2d]
            #  0  1  2  3  4   5    6    7    8    9    
            if obj.hastexture or obj.hasnormal_map:
                A[3], A[4] = obj.vt[face[1][0]]
                B[3], B[4] = obj.vt[face[1][1]]
                C[3], C[4] = obj.vt[face[1][2]]
            if obj.shade_smooth:
                A[5], A[6], A[7] = obj.svn[face[3][0]]
                B[5], B[6], B[7] = obj.svn[face[3][1]]
                C[5], C[6], C[7] = obj.svn[face[3][2]]
            
            # Culling
            # Remove those impossible to be seen based on the normal
            if cam.mode!= 7 and (A[:3][0] * obj.vn[face[2]][0] + 
                                 A[:3][1] * obj.vn[face[2]][1] + 
                                 A[:3][2] * obj.vn[face[2]][2]) > 0:
                continue

            # Rotate the object
            Ax, Bx, Cx, = A[0], B[0], C[0],
            Ay, By, Cy, = A[1], B[1], C[1],
            Az, Bz, Cz, = A[2], B[2], C[2], 
            Asnx, Asny, Asnz = A[5], A[6], A[7]
            A[0] = cam.rotation[0][0] * Ax + cam.rotation[0][1] * Ay + cam.rotation[0][2] * Az
            A[1] = cam.rotation[1][0] * Ax + cam.rotation[1][1] * Ay + cam.rotation[1][2] * Az
            A[2] = cam.rotation[2][0] * Ax + cam.rotation[2][1] * Ay + cam.rotation[2][2] * Az
            B[0] = cam.rotation[0][0] * Bx + cam.rotation[0][1] * By + cam.rotation[0][2] * Bz
            B[1] = cam.rotation[1][0] * Bx + cam.rotation[1][1] * By + cam.rotation[1][2] * Bz
            B[2] = cam.rotation[2][0] * Bx + cam.rotation[2][1] * By + cam.rotation[2][2] * Bz
            C[0] = cam.rotation[0][0] * Cx + cam.rotation[0][1] * Cy + cam.rotation[0][2] * Cz
            C[1] = cam.rotation[1][0] * Cx + cam.rotation[1][1] * Cy + cam.rotation[1][2] * Cz
            C[2] = cam.rotation[2][0] * Cx + cam.rotation[2][1] * Cy + cam.rotation[2][2] * Cz
            A[5] = cam.rotation[0][0] * Asnx + cam.rotation[0][1] * Asny + cam.rotation[0][2] * Asnz
            A[6] = cam.rotation[1][0] * Asnx + cam.rotation[1][1] * Asny + cam.rotation[1][2] * Asnz
            A[7] = cam.rotation[2][0] * Asnx + cam.rotation[2][1] * Asny + cam.rotation[2][2] * Asnz
            if obj.shade_smooth:
                Bsnx, Bsny, Bsnz = B[5], B[6], B[7]
                Csnx, Csny, Csnz = C[5], C[6], C[7]
                B[5] = cam.rotation[0][0] * Bsnx + cam.rotation[0][1] * Bsny + cam.rotation[0][2] * Bsnz
                B[6] = cam.rotation[1][0] * Bsnx + cam.rotation[1][1] * Bsny + cam.rotation[1][2] * Bsnz
                B[7] = cam.rotation[2][0] * Bsnx + cam.rotation[2][1] * Bsny + cam.rotation[2][2] * Bsnz
                C[5] = cam.rotation[0][0] * Csnx + cam.rotation[0][1] * Csny + cam.rotation[0][2] * Csnz
                C[6] = cam.rotation[1][0] * Csnx + cam.rotation[1][1] * Csny + cam.rotation[1][2] * Csnz
                C[7] = cam.rotation[2][0] * Csnx + cam.rotation[2][1] * Csny + cam.rotation[2][2] * Csnz
                normal = None
            else:
                # "normal = (A[5], A[6], A[7])" is slightly faster than "normal = A[5:8]"
                normal = (A[5], A[6], A[7])

            # Clipping
            # Remove those too far or behind the camera
            if ((A[2] <= cam.z_near or A[2] >= cam.z_far) and
                (B[2] <= cam.z_near or B[2] >= cam.z_far) and
                (C[2] <= cam.z_near or C[2] >= cam.z_far)):
                continue
            inside = []
            outside = []
            if A[2] > cam.z_near:
                inside.append(A)
            else:
                outside.append(A)  
            if B[2] > cam.z_near:
                inside.append(B)
            else:
                outside.append(B)  
            if C[2] > cam.z_near:
                inside.append(C)
            else:
                outside.append(C)        
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
                        None, None
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
                        None, None
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
                        None, None
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
                        None, None
                    ]
                )
            
            inside[0][8] = cam.width // 2 + int(inside[0][0] * cam.rendering_plane_z / inside[0][2])
            inside[0][9] = cam.height // 2 - int(inside[0][1] * cam.rendering_plane_z / inside[0][2])
            inside[1][8] = cam.width // 2 + int(inside[1][0] * cam.rendering_plane_z / inside[1][2])
            inside[1][9] = cam.height // 2 - int(inside[1][1] * cam.rendering_plane_z / inside[1][2])  
            inside[2][8] = cam.width // 2 + int(inside[2][0] * cam.rendering_plane_z / inside[2][2])
            inside[2][9] = cam.height // 2 - int(inside[2][1] * cam.rendering_plane_z / inside[2][2])   
            if len(inside)  == 4:
                inside[3][8] = cam.width // 2 + int(inside[3][0] * cam.rendering_plane_z / inside[3][2])
                inside[3][9] = cam.height // 2 - int(inside[3][1] * cam.rendering_plane_z / inside[3][2])

            if cam.mode == 0:
                if obj.hasnormal_map and obj.hastexture:
                    pass
                elif obj.hastexture:
                    pass
                elif obj.hasnormal_map:
                    pass
                else:
                    rasterize_solid(inside[0], inside[1], inside[2], normal)
                    if len(inside) == 4:
                        rasterize_solid(inside[1], inside[2], inside[3], normal)
            elif cam.mode == 1:
                rasterize_solid(inside[0], inside[1], inside[2], normal)
                if len(inside) == 4:
                    rasterize_solid(inside[1], inside[2], inside[3], normal)
            elif cam.mode == 2:
                pass
            elif cam.mode == 3:
                pass
            elif cam.mode == 4:
                pass
            elif cam.mode == 5:
                depth(inside[0], inside[1], inside[2])
                if len(inside) == 4:
                    depth(inside[1], inside[2], inside[3])
            elif cam.mode in (6, 7):
                add_line(inside[0], inside[1])
                add_line(inside[1], inside[2])
                add_line(inside[0], inside[2])
                if len(inside) == 4:
                    add_line(inside[3], inside[1])
                    add_line(inside[3], inside[2])

    return frame, obj_buffer, depth_buffer

