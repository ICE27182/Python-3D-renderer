

def Int(x):
    return int(round(x,0))
def sin(x):
    return math.sin(x/180*math.pi)
def cos(x):
    return math.cos(x/180*math.pi)
def tan(x):
    return math.tan(x/180*math.pi)
def dot_production_3d(vec1,vec2):
    # if len(vec1) == len(vec2) == 3:
        return vec1[0]*vec2[0]+vec1[1]*vec2[1]+vec1[2]*vec2[2]
    # else:
    #     raise Exception("Dot production\n",vec1,vec2)

def del_lines(lines,time):
    """It is Good"""
    sleep(time)
    print("\033[F"*lines,end="",flush=True)
    print(" "*(w*lines),end="",flush=True)
    print("\033[F"*lines,flush=True)

def vertices_processing(all_vertices):
    vertices = {}
    for name in all_vertices:
        vertex = change_coordinate_system(all_vertices[name])
        if vertex[2] <= 0:
            continue
        else:
            vertices[name] = process_vertex(vertex)
            if abs(vertex[0]/vertex[2]) > k_half_fov and abs(vertex[1]/vertex[2]) > k_half_fov_h:
                for connected_vertex_name in vertex[3]:
                    cnt_vtx = all_vertices[connected_vertex_name]
                    cnt_vtx = change_coordinate_system(cnt_vtx)
                    if cnt_vtx[2] <= 0:
                        vertices[connected_vertex_name] = process_vertex(cnt_vtx,vertex)
    return vertices
                    
def change_coordinate_system(vertex):
    p = vertex[0:3]

    # 1. Move the vertex
    for index in range(3):
        p[index] -= cam["pos"][index]
    # 2. Rotate the coordiante system to a new one based on the camera
    p[0] = dot_production_3d(p,axis_x)
    p[1] = dot_production_3d(p,axis_y)
    p[2] = dot_production_3d(p,axis_z)
    return p + [vertex[3]]

def process_vertex_decorator(func):
    def second_process(vertex,Q=None):
        p = func(vertex,Q)
        p = [p[0] + w / 2, h / 2 - p[1], p[2]]
        return p
    return second_process
@process_vertex_decorator
def process_vertex(vertex,Q=None):
    p = vertex[0:3]
    # 3. Get the 2d coordinates
    #
    # 2种能看到的情况
    #   1 两顶点z均大于0
    #   2 其中至少一顶点在视锥内
    # 所以
    #   1 先计算视锥内的点
    #   2 再计算与视锥内的点相连的点
        # q = change_coordinate_system(all_vertices[connected_vertex])
    #   3 最后计算没有计算过的所有z>0的点
    # 怎么计算呢
    #   1 z>0的点直接连线求交点就好了
    #   2 z=0的点 x或y若大于0就w/2 等于0就0 小于0就-w/2
    #   --------------------------------
    #   2 z<0反视锥外的点可以求交点然后取相反数
    #   3 反视锥内的点必然与视锥内的点相连(不然就不会去算它了)
    if p[2] < 0 and abs(p[2]/p[0]) > k_half_fov and abs(p[2]/p[1]) > k_half_fov_h:
        # if Q == None:
        #     raise Exception()
        q = Q[0:3]
        # Divide the x-y plane into four parts: U, D, L and R
        k = h / w
        # Find which unit P is in
        if p[0] > 0:
            if abs(p[1]/p[0]) <= k:
                p_unit = "R"
            elif p[1] > 0:   # and abs(p[1]/p[0]) > k
                p_unit = "U"
            else:   # p[1] < 0 and abs(p[1]/p[0]) > k
                p_unit = "D"
        elif p[0] < 0:
            if abs(p[1]/p[0]) <= k:
                p_unit = "L"
            elif p[1] > 0:   # and abs(p[1]/p[0]) > k
                p_unit = "U"
            else:   # p[1] < 0 and abs(p[1]/p[0]) > k
                p_unit = "D"
        else:   # p[0] == 0
            if p[1] > 0:
                p_unit = "U"
            elif p[2] < 0:
                p_unit = "D"
            else:   # p[0:2] == [0,0]
                p_unit = None
        # Find which unit Q is in
        if q[0] > 0:
            if abs(q[1]/q[0]) <= k:
                q_unit = "R"
            elif q[1] > 0:   # and abs(q[1]/q[0]) > k
                q_unit = "U"
            else:   # q[1] < 0 and abs(q[1]/q[0]) > k
                q_unit = "D"
        elif q[0] < 0:
            if abs(q[1]/q[0]) <= k:
                q_unit = "L"
            elif q[1] > 0:   # and abs(q[1]/q[0]) > k
                q_unit = "U"
            else:   # q[1] < 0 and abs(q[1]/q[0]) > k
                q_unit = "D"
        else:   # q[0] == 0
            if q[1] > 0:
                q_unit = "U"
            elif q[2] < 0:
                q_unit = "D"
            else:   # q[0:2] == [0,0]
                q_unit = None
        # Find which plane the line PQ crosses
        if p_unit == "U" and q_unit in ("U","D"):
            # plane = p_unit
            z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * h/2/d)
            x = (p[0] - q[0]) / (p[2] - q[2]) * (z - p[2]) + p[0]
            return [x*d/z, h/2, vertex[3]]
        elif p_unit == "D" and q_unit in ("U","D"):
            # plane = p_unit
            z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * -h/2/d)
            x = (p[0] - q[0]) / (p[2] - q[2]) * (z - p[2]) + p[0]
            return [x*d/z, h/2, vertex[3]]
        elif p_unit == "L" and q_unit in ("L","R"):
            # plane = p_unit
            z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * -w/2/d)
            y = (p[1] - q[1]) / (p[2] - q[2]) * (z - p[2]) + p[1]
            return [y*d/z, h/2, vertex[3]]
        elif p_unit == "R" and q_unit in ("L","R"):
            # plane = p_unit
            z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * w/2/d)
            y = (p[1] - q[1]) / (p[2] - q[2]) * (z - p[2]) + p[1]
            return [y*d/z, h/2, vertex[3]]
        elif p_unit == None:
            if q_unit == "U":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * h/2/d)
                x = (p[0] - q[0]) / (p[2] - q[2]) * (z - p[2]) + p[0]
                return [x*d/z, h/2, vertex[3]]
            elif q_unit == "D":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * -h/2/d)
                x = (p[0] - q[0]) / (p[2] - q[2]) * (z - p[2]) + p[0]
                return [x*d/z, h/2, vertex[3]]
            elif q_unit == "L":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * -w/2/d)
                y = (p[1] - q[1]) / (p[2] - q[2]) * (z - p[2]) + p[1]
                return [y*d/z, h/2, vertex[3]]
            elif q_unit == "R":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * w/2/d)
                y = (p[1] - q[1]) / (p[2] - q[2]) * (z - p[2]) + p[1]
                return [y*d/z, h/2, vertex[3]]
        elif q_unit == None:
            if p_unit == "U":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * h/2/d)
                x = (p[0] - q[0]) / (p[2] - q[2]) * (z - p[2]) + p[0]
                return [x*d/z, h/2, vertex[3]]
            elif p_unit == "D":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * -h/2/d)
                x = (p[0] - q[0]) / (p[2] - q[2]) * (z - p[2]) + p[0]
                return [x*d/z, h/2, vertex[3]]
            elif p_unit == "L":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * -w/2/d)
                y = (p[1] - q[1]) / (p[2] - q[2]) * (z - p[2]) + p[1]
                return [y*d/z, h/2, vertex[3]]
            elif p_unit == "R":
                # plane = p_unit
                z = ((q[0] - p[0]) * p[2] - (q[2] - p[2]) * p[0]) / ((q[0] - p[0]) - (q[2] - p[2]) * w/2/d)
                y = (p[1] - q[1]) / (p[2] - q[2]) * (z - p[2]) + p[1]
                return [y*d/z, h/2, vertex[3]]
        elif None == p_unit == q_unit:  # O is on line PQ
            return [0, 0, vertex[3]]
        else:
            if p[0] == q[0]:
                x = p[0]
            elif (p_unit,q_unit) in (("U","R"),("R","U"),("D","L"),("L","D")):
                z = ((q[1] - p[1]) * p[0] - (q[0] - p[0]) * p[1]) / ((q[1] - p[1]) - (q[0] - p[0]) * k)
                z = (q[2] - p[2]) / (q[0] - p[0]) * (x - p[0]) + p[2]
                z_l = 2 * d / w * abs(x)
                if z > z_l:
                    plane = q_unit
                elif z < z_l:
                    plane = p_unit
                else:   # z == z_l
                    return [w/2*(x/abs(x)), h/2*(x/abs(x)), vertex[3]]
            else:   # (p_unit,q_unit) in (("U","L"),("L","U"),("D","R"),("R","D"))
                x = ((q[1] - p[1]) * p[0] - (q[0] - p[0]) * p[1]) / ((q[1] - p[1]) - (q[0] - p[0]) * -k)
                z = (q[2] - p[2]) / (q[0] - p[0]) * (x - p[0]) + p[2]
                z_l = -2 * d / w * abs(x)
                if z > z_l:
                    plane = q_unit
                elif z < z_l:
                    plane = p_unit
                else:   # z == z_l
                    return [w/2*(x/abs(x)), -h/2*(x/abs(x)), vertex[3]]     
                # Get the x or y coordinate, based on which plane line PQ crosses
                if plane == "U":
                    return [d/z*x, h/2, vertex[3]]
                elif plane == "D":
                    return [d/z*x, -h/2, vertex[3]]
                elif plane == "L":
                    y = (q[1] - p[1]) / (q[0] - p[0]) * (x - p[0]) + p[1]
                    return [-w/2, d/z*y, vertex[3]]
                elif plane == "R":
                    y = (q[1] - p[1]) / (q[0] - p[0]) * (x - p[0]) + p[1]
                    return [w/2, d/z*y, vertex[3]]
    # Out of the reversed view cone
    else:
        return [p[0]/p[2]*d,p[1]/p[2]*d,vertex[3]]

    """
    # 3.1 
    if p[2] == 0 and connected_vertex != None:
        if p[0:2] == [0,0]:
            return [0,0,None]
        elif p[0] == 0:
            return [0,h/2] if p[1] > 0 else [0,-h/2,None]
        elif p[1] == 0:
            return [w/2,0] if p[0] > 0 else [-w/2,0,None]
        elif abs(k := p[1]/p[0]) >= h/w:
            if p[1] > 0:
                return [h/2/k,h/2,None]
            else:   # elif p[1] < 0:
                return [[-h/2/k,-h/2],None]
        else:   #elif abs(k) <h/w
            if p[0] > 0:
                return [w/2,k*w/2,None]
            else:   #elif p[0] < 0:
                return [-w/2,-k*w/2,None]
    # 3.2 Be in the view cone
    cos_x = p[2] / math.sqrt(p[0]**2 + p[2]**2)
    cos_y = p[2] / math.sqrt(p[1]**2 + p[2]**2)
    if cos_x > cos_half_fov and cos_y > cos_half_fov_v:
        return [p[0]/p[2]*d,p[1]/p[2]*d,"In cone"]
    # 3.3 z > 0
    elif p[2] > 0:
        return [p[0]/p[2]*d,p[1]/p[2]*d,"z > 0"]
    # 3.4 Be in the anti-cone
    elif cos_x < -cos_half_fov and cos_y < -cos_half_fov_v:
        pass
    # 3.5 z < 0
    elif p[2] < 0:
        return [-p[0]/p[2]*d,-p[1]/p[2]*d,"z < 0"]
    #
    else:
        raise Exception()

        

    if p == [0,0,0]:
        p = [0,0]
    else:
        # 3.1 向量OP在zx/zy平面上投影于z轴正半轴的夹角的余弦值
        #     (实在是不会用英语了 我大概真得从小学课程学起了)
        cos_x = p[2] / math.sqrt(p[0]**2 + p[2]**2)
        cos_y = p[2] / math.sqrt(p[1]**2 + p[2]**2)
        # 3.2.1 Be in front(>) of the camera. Calculate in the first turn
        if p[2] > 0:
            p = [p[0] / p[2] * d, p[1] / p[2] * d]
        # 3.2.2 Be behind(<=) the camera. Calculate in the second turn
        elif connected_vertex in all_vertices[name][3]:
            q = all_vertices[connected_vertex][0:3]
            # O on line PQ
            if [0,0] == p[0:2] == q[0:2]:
                pos = [0,0]
            else:
                # x - z
                # 1 斜率不存在
                if p[0] == q[0]:
                    if p[0] > 0:
                        pos = [w/2]
                    else:   # elif p[0] < 0
                        pos = [-w/2]
                # 2 计算交点 交点数量为2
                elif (k := (p[2]-q[2])/(p[0]-q[0])) != (k0 := w/2/d):
                    # z = k(x-p[0])+p[2]
                    # z = k0·x
                    x1 = (k*p[0]-p[2]) / (k-k0)
                    # z = -k0·x
                    x2 = (k*p[0]-p[2]) / (k+k0)
                    if k0 * x1 < k0 * x2:   # z1 < z2
                        pos = [x1,k0 * x1]
                    else:   # z1 >= z2
                        pos = [x2,k0 * x2]
                # 3 计算交点 交点数量1
                elif k == k0:
                    pos = [(k*p[0]-p[2]) / (k+k0), k0 * (k*p[0]-p[2]) / (k+k0)]
                # 4 计算交点 交点数量1
                elif k == -k0:
                    pos = [(k*p[0]-p[2]) / (k-k0), k0 * (k*p[0]-p[2]) / (k-k0)]
                # 不到啊
                else:
                    raise Exception()
                # y - z
                # 1 斜率不存在
                if p[1] == q[1]:
                    if p[1] > 1:
                        pos = [w/2]
                    else:   # elif p[1] < 1
                        pos = [-w/2]
                # 2 计算交点 交点数量为2
                elif (k := (p[2]-q[2])/(p[1]-q[1])) != (k1 := h/2/d):
                    # z = k(y-p[1])+p[2]
                    # z = k1·y
                    y1 = (k*p[1]-p[2]) / (k-k1)
                    # z = -k1·y
                    y2 = (k*p[1]-p[2]) / (k+k1)
                    if k1 * y1 < k1 * y2:   # z1 <  z2
                        pos = [y1,k1 * y1]
                    else:                   # z1 >= z2
                        pos = [y2,k1 * y2]
                # 3 计算交点 交点数量1
                elif k == k1:
                    pos = [(k*p[1]-p[2]) / (k+k1), k1 * (k*p[1]-p[2]) / (k+k1)]
                # 4 计算交点 交点数量1
                elif k == -k1:
                    pos = [(k*p[1]-p[2]) / (k-k1), k1 * (k*p[1]-p[2]) / (k-k1)]
                # 不到啊
                else:
                    raise Exception()   
                    
    # 4. Transform the [x,y] to the cooridinate in another coordinate system
    # pos = [p[0]+w/2, -p[1]+h/2]
    # return pos
    """

def draw(vertices):
    frame={y:set() for y in range(h)}
    lines = {}  # {"PQ":{y:x, ...}, ...}
    for vertex in vertices:
        for cnt_vtx in vertices[vertex][2]:
            if vertex + cnt_vtx not in lines and cnt_vtx + vertex not in lines:
                # Vertices in front of the cam but not in the view cone will
                # all be calculated, but as only when the vertices they're
                # connected to are also in front of the cam can the line be
                # seen, they do not necessarily connect to all the vertices
                # as listed.
                if cnt_vtx in vertices:
                    lines[vertex + cnt_vtx] = line_cal(vertices[vertex], vertices[cnt_vtx])
    for line in lines.values():
        for y in line:
            frame[y] = frame[y] | line[y]
    print("\033[F"*(h+10))
    for y in frame:
        for x in range(w):
            print("██" if x in frame[y] else "  ", end="")
        print("")
    # print(axis_x,axis_y,axis_z,end="")
    print(cam["pos"], cam["ang"], end="")

    
def line_cal(p, q):
    p,q = (Int(p[0]),Int(p[1])),(Int(q[0]),Int(q[1]))
    line = {}
    if p[0] == q[0]:
        for y in range(
            max(min(p[1],q[1]), -h),
            min(max(p[1],q[1]), h),
                    ):
            if y in range(h) and p[0] in range(w):
                line[y] = {p[0]}
    elif abs(p[1]-q[1]) > abs(p[0] - q[0]): # k > 1 (or doesn't exist)
        k = (p[0] - q[0]) / (p[1]-q[1])
        for y in range(
            max(min(p[1],q[1]), -h),
            min(max(p[1],q[1]), h),
                    ):
            if y in range(h) and (x := Int(k * (y - p[1]) + p[0])) in range(w):
                line[y] = {x} if y not in line else line[y] | {x}
    else:   # abs(p[1]-q[1]) <= abs(p[0] - q[0])
        k = (p[1]-q[1]) / (p[0] - q[0])
        for x in range(
            max(min(p[0],q[0]), -w),
            min(max(p[0],q[0]), w),
                    ):
            if x in range(w) and (y := Int(k * (x - p[0]) + p[1])) in range(h):
                line[y] = {x} if y not in line else line[y] | {x}
    return line
    # if p[0] in range(w) and p[1] in range(h):
    #     line[p[1]]={p[0]}
    # if q[0] in range(w) and q[1] in range(h):
    #     line[q[1]]={q[0] }
    # return line

def key_input(key):
    global cam
    if key == "None":
        pass
    elif key == "Q":
        exit(0),
    elif key == "C":
        system("cls"),
    
    if key == "w":
        cam["pos"][2] += 1
    elif key == "s":
        cam["pos"][2] += -1
    elif key == "a":
        cam["pos"][0] += -1
    elif key == "d":
        cam["pos"][0] += 1
    elif key == "e":
        cam["pos"][1] += 1
    elif key == "f":
        cam["pos"][1] += -1

    elif key == "8":
        cam["ang"][1] += 1
    elif key == "2":
        cam["ang"][1] += -1
    elif key == "4":
        cam["ang"][0] += -1
    elif key == "6":
        cam["ang"][0] += 1

    elif key == "c":
        cam["pos"] = [0,2,-30]
        cam["ang"] = [90,0]
    
    else:
        print(error_strings["KeyInputError"] + f"The key you pressed:{key}")
        Thread(target=del_lines,daemon=True,args=(4,1)).start()
    



if __name__ == "__main__":
    # global key  # Take key input
    global cam
    import math
    from threading import Thread    # del_lines()
    from msvcrt import getwch
    from time import sleep  # del_lines()
    from os import system # clear when starting to run the program
    from shutil import get_terminal_size

    system("cls")
    w,h = get_terminal_size()
    w,h = w//2-4,h-4

    fov = 72
    d = w/2 / tan(fov/2)
    # cos_half_fov = d/math.sqrt((w/2)**2+d**2)
    # cos_half_fov_v = d/math.sqrt((h/2)**2+d**2)
    k_half_fov = w/2/d
    k_half_fov_h = h/2/d

    cam = {"pos":[0,2,-30],"ang":[90,0]}
    all_vertices = {
        "A":[-5,0,5,
            # ["A"] 
            ["B","D","A'"],
             ],
        "B":[5,0,5,["A","C","B'"],],
        "C":[5,0,15,["B","D","C'"],],
        "D":[-5,0,15,["A","C","D'"],],
        "A'":[-5,10,5,["B'","D'","A"]],
        "B'":[5,10,5,["A'","C'","B"]],
        "C'":[5,10,15,["B'","D'","C"]],
        "D'":[-5,10,15,["A'","C'","D"]],
    }
    error_strings = {
        "KeyInputError":"""
Key Input Error
The key you press hasn't been bounded.
"""
    }
    key = None
    # Thread(target=key_input,daemon=True).start()
    # key_bounding = {
    #     None: lambda: None,
    #     "Q": lambda: exit(0),
    #     "C": lambda: system("cls"),

    #     "w": lambda: key_input("w"),
    #     "a": lambda: key_input("a"),
    #     "s": lambda: key_input("s"),
    #     "d": lambda: key_input("d"),
    #     "e": lambda: key_input("e"),
    #     "f": lambda: key_input("f"),
    #     "c": lambda: key_input("c"),
        
    # }

    while True:
        w,h = get_terminal_size()
        w,h = w//2-4,h-4
        # Get the axis based on the camera
        axis_x = (
            cos(cam["ang"][0]-90),
            0,
            sin(cam["ang"][0]-90),
            )
        axis_y = (
                cos(cam["ang"][0])*cos(cam["ang"][1]+90),
                sin(cam["ang"][1]+90),
                sin(cam["ang"][0])*cos(cam["ang"][1]+90),
                )
        axis_z = (
                cos(cam["ang"][0])*cos(cam["ang"][1]),
                sin(cam["ang"][1]),
                sin(cam["ang"][0])*cos(cam["ang"][1]),
                )
        
        vertices = vertices_processing(all_vertices)

        draw(vertices)

        key_input(getwch())
            
        key = None
        
    pass