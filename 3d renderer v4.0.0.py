# 最后一次编辑
# 3/13/2023
# 缺少背后物体的显示
# 缺少debug体系
# 可以考虑相对位置
# 没完成的函数结尾处有pass

# To write a 3D Renderer, we need to clarify the progress specificly
# 
# So, what values do we need?
#
# - A list of vertices
# - Lines to be connected
# - The angle of field of view
# - Terminal size(Height and width)
# 
# SO there're things to be dealt with
#   - Input
#   - Lines and vertices
#   - Global settings
#   - Transform vertices
#   - Connect vertices
#   - Output the image

""" The following explains the functions of varibles in the main process
GLOBAL
all_shapes
    {count:<shapes number>, <name>:<>}
cam
    {"pos":[x,y,z], "ang":[α, β]}

MAIN
debug
w
h
fov
d

CLASS
Shape object has its own id, while vertices do not

"""
"""The following shows the format to be used in the program,
in case I forget

An empty line to separate code to make its logic more clear if necessary
    or just write a comment
Two empty lines to separate functions
Three empty lines to separate class
Four empty lines to separate functions and classed from the main

All funcs name should be in lower case and connected with underscore "_"
All class should begin with an upper case letter followed by all lower case letters

Use tiple single quote to quote code that is to perserved but will not be in use
Use double quote instead of single quote if possible

Lines of warning or exception that have yet to be finished
    should be marked '''Wait to be completed''' above
Functions that have yet to be finished should have "pass" an the end
"""
def Int(val):
    return int(round(val,0))


def vec_add_sub(vec1,vec2,add_or_sub):
    if add_or_sub == "+":
        return (vec1[0]+vec2[0], vec1[1]+vec2[1], vec1[2]+vec2[2])
    elif add_or_sub == "-":
        return (vec1[0]-vec2[0], vec1[1]-vec2[1], vec1[2]-vec2[2])


class Shape:
    def __init__(self,name=None) -> None:
        """A Shape object contains vertices in a polyhedron and functions 
        concerned with process these vertices"""
        global all_shapes
        # Set its id and create all_shapes varible if it doesn't exist
        if "all_shapes" in globals():
            self.id = all_shapes["count"] + 1
        else:
            # all_shapes = {"count":<vertices number>, <shape name>:<object>}
            all_shapes = {"count":0,}
            self.id = 1
        # Set its name
        if name == None:
            # I know it sounds strange, but I just want to call it Nameless
            # so be it
            self.name = f"Nameless shape {self.id}"
        else:
            self.name = name
        # self.vertices = {"P":[x,y,z,["Q"]]}
        self.vertices = {}
        # Add it to all_shapes
        all_shapes[self.name] = self
        all_shapes["count"] = len(all_shapes) - 1


    def add_vertex(self,name,x,y,z,connected_vertex=None):
        """Add a vertex into the polyhedron, 
        vertex name, coordinates are essential,
        to which vertices it connects is optional"""
        self.vertices[name] = [x, y, z, connected_vertex]
        for vertex in connected_vertex:
            if vertex in self.vertices:
                self.vertices[vertex][3].append(self.name)
            else:
                '''Wait to be completed'''
                print("Warning:")
    


    def add_lines(self,P:str,Q:str):
        """Add a new line, or in other words, connect P and Q
        If P and Q are the same vertex, the vertex will be connected to
        itself, which means it will be rendered as long as it's in front
        of the camera, inside or outside the view cone"""
        if P not in self.vertices or Q not in self.vertices:
            '''Wait to be completed'''
            raise Exception()
        if Q not in self.vertices[P][3]:
            self.vertices[P][3].append(Q)
        if P not in self.vertices[Q][3]:
            self.vertices[P][3].append(P)


    def move_vertex(self):
        pass


    def del_vertex(self):
        pass



class Renderer:
    def __init__(self) -> None:
        pass


    def rendering_main(all_shapes):
        # Take all vertices from repective shapes
        # all_vertices = {("P", 1): [x, y, z, [("Q",1)]]}
        all_vertcies = {}
        for shape in all_shapes.values():
            if type(shape) == int:
                continue
            for name, vertex in shape.vertices.items():
                all_vertcies[(name,shape.id)] = vertex
                for index,cvertex in enumerate(all_vertcies[(name,shape.id)][3]):
                    all_vertcies[(name,shape.id)][3][index] = (cvertex,shape.id)
        # Change the coordiante system
        # The change will be applied to all_vertices
        for name, vertex in all_vertcies.items():
            all_vertcies[name] = Renderer.change_coordinate_system(vertex)
        # Render the vertices from 3d to 2d  Hardest part
        vertices = {}
        for name, vertex in all_vertcies.items():
            if vertex[2] > 0 and name not in vertices:
                vertices[name] = Renderer.from_3d_to_2d(vertex)
        # Move vertices
        for name in vertices:
            vertices[name][0] += w/2
            vertices[name][1] += h/2
        return vertices
        pass


    def change_coordinate_system(vertex):
        x = vertex[0] - cam["pos"][0]
        y = vertex[1] - cam["pos"][1]
        z = vertex[2] - cam["pos"][2]
        vertex[0] = round(x * x_axis[0] + y * x_axis[1] + z * x_axis[2],12)
        vertex[1] = round(x * y_axis[0] + y * y_axis[1] + z * y_axis[2],12)
        vertex[2] = round(x * z_axis[0] + y * z_axis[1] + z * z_axis[2],12)
        return vertex
    

    def from_3d_to_2d(vertex,former_v=None):
        if vertex[2] > 0:
            return [vertex[0]/vertex[2]*d, vertex[1]/vertex[2]*d, vertex[3]]
        else:
            # more code here
            raise Exception()
        pass



def draw(vertices):
    # I. Define the function to calculate the line
    def cal_line(P,Q,debug=False):
        if debug == True:
            line = {}
            if Int(P[0]) in range(w) and Int(P[1]) in range(h):
                line[int(P[1])] = {int(P[0])}
            if Int(Q[0]) in range(w) and Int(Q[1]) in range(h):
                line[Int(Q[1])] = {Int(Q[0])}
            return line
        line = {y: set() for y in range(h)}
        # 1. k doesn't exist
        if P[0] == Q[0]:
            if Int(P[0]) in range(w):
                for y in range(
                                Int(max(min(P[1], Q[1]), 0)),
                                Int(min(max(P[1], Q[1]) + 1, h))
                                ):
                    line[y] = {Int(P[0])}
        # 2. |k| < 1
        elif abs(k := (P[1] - Q[1]) / (P[0] - Q[0])) < 1:
            for x in range(
                            Int(max(min(P[0], Q[0]), 0)),
                            Int(min(max(P[0], Q[0]) + 1, w))
                            ):
                y = Int(k * (x - P[0]) + P[1])
                if y in range(h):
                    line[y] = line[y] | {x}
        # 3. |k| >= 1
        else:
            m = (P[0] - Q[0]) / (P[1] - Q[1])
            for y in range(
                            Int(max(min(P[1], Q[1]), 0)),
                            Int(min(max(P[1], Q[1]) + 1, h))
                            ):
                x = Int(m * (y - P[1]) + P[0])
                if x in range(w):
                    line[y] = line[y] | {x}
        return line
    # II. Iterate all vertices to calculate lines
    lines = {}    # lines = {{P,Q}:{y:{x}}}
    for name,vertex in vertices.items():
        for c_name in vertex[2]:
            if (c_name, name) not in lines:
                lines[(name, c_name)] = cal_line(vertex, vertices[c_name])
    # III. Put all lines into the frame
    frame = {y: set() for y in range(h)}
    for line in lines.values():
        for y, x_s in line.items():
            frame[y] = frame[y] | x_s
    # IV. Print the frame a row after another
    print("\033[F" * (h + 10))
    for y in range(h-1, -1, -1):
        row = []
        for x in range(w):
            row.append("██" if x in frame[y] else "  ")
        print("".join(row))


'''
def draw(vertices):
    def cal_the_frame(vertices):
        # frame = {y:{x}}
        frame = {y:set() for y in range(h)}
        # Calculate all the lines and put all vertices into frame
        lines = {}
        for name, vertex in vertices.items():
            if Int(vertex[0]) in range(w) and Int(vertex[1]) in range(h):
                frame[Int(vertex[1])] = frame[Int(vertex[1])] | {Int(vertex[0])}
            for cnt_name in vertex[2]:
                if (cnt_name + name) in lines or (name + cnt_name) in lines:
                    continue
                else:
                    lines[name + cnt_name] = cal_the_line(vertex,vertices[cnt_name])

        # Put all the lines into frame
        for line in lines.values():
            for y, xs in line.items():
                frame[y] = frame[y] | xs

        return frame
        pass

    def cal_the_line(P,Q):
        """Return a line. line = {y:{x}}"""
        line = {
                    y:set() for y in range(
                                            Int(max(min(P[1], Q[1]), 0)),
                                            Int(min(max(P[1], Q[1]) + 1, h)),
                                            )
                    }
        # P[1] > h/2 and Q[1] > h/2 or P[1] < -h/2 and Q[1] < -h/2
        if len(line) == 0:
            return line
        # k does not exist
        if P[0] == Q[0]:
            for y in line:
                line[y] = {P[0]}
        # k < 1:
        elif (k:= (P[1] - Q[1]) / (P[0] - Q[0])) < 1:
            for x in range(
                            Int(max(min(P[0], Q[0]), 0)),
                            Int(min(max(P[0], Q[0]) + 1, w)),
                            ):
                y = Int(k * x + P[1])
                if y < 0 or y > h-1:
                    continue
                else:
                    line[y] = line[y] | {x}
        # k > 1
        else:
            m = (P[0] - Q[0]) / (P[1] - Q[1])
            for y in range(
                            Int(max(min(P[1], Q[1]), 0)),
                            Int(min(max(P[1], Q[1]) + 1, h)),
                            ):
                x = Int(m * y + P[0])
                if x < 0 or x > w-1:
                    continue
                else:
                    line[y] = line[y] | {x}
        return line

    # A frame should will be in the form of {y:{x}}, in which the
    # coordinate system is the same as the x-y one usually used and
    # x ∈ [0, w-1]    y ∈ [0, h-1]
    def draw_the_frame(frame,w,h,debug=False):
        print("\033[F" * (h+10))
        for y in range(h- 1,-1,-1):
            row = []
            if debug:
                row.append(f"{y:4d}|")
            for x in range(w):
                row.append("██" if x in frame[y] else "  ")
            print("".join(row))

    draw_the_frame(cal_the_frame(vertices),w,h,debug=debug)
'''


def move_cam(key):
    global cam
    if False:
        pass
    
    elif key == "Q":
        return "Quit"
    
    elif key == "w":
        cam["pos"] = vec_add_sub(cam["pos"], z_axis, "+")
    elif key == "s":
        cam["pos"] = vec_add_sub(cam["pos"], z_axis, "-")
    elif key == "a":
        cam["pos"] = vec_add_sub(cam["pos"], x_axis, "-")
    elif key == "d":
        cam["pos"] = vec_add_sub(cam["pos"], x_axis, "+")
    elif key == "e":
        cam["pos"] = vec_add_sub(cam["pos"], y_axis, "+")
    elif key == "f":
        cam["pos"] = vec_add_sub(cam["pos"], y_axis, "-")
    
    elif key == "8":
        cam["ang"][1] += 1
    elif key == "2":
        cam["ang"][1] -= 1
    elif key == "4":
        cam["ang"][0] += 1
    elif key == "6":
        cam["ang"][0] -= 1

    elif key == "c":
        cam["pos"] = [0,2,-30]
        cam["ang"] = [90,0]



class Debug:
    def __init__(self) -> None:
        pass
    

    def vec_len(vec_3d):
        if len(vec_3d) != 3:
            raise Exception()
        return vec_3d[0] ** 2 + vec_3d[1] ** 2 + vec_3d[2] ** 2




if __name__ == "__main__":
    import os
    os.system("cls")

    global cam
    cam = {"pos":[0,2,-30],"ang":[90,0]}


while __name__ == "__main__":
    from msvcrt import kbhit,getwch
    from os import system
    from shutil import get_terminal_size
    from math import sin,cos,tan,pi
    debug = False
    
    w,h = get_terminal_size()
    if debug == False:
        w, h = w//2 - 2, h - 2
    else:
        # When debug is on, the y coordinate will be shown, 
        # which takes 5 more colums
        w, h = w//2 - 7, h - 2
    '''
    w,h = 69,11
    '''
    fov = 72
    d = w / 2 / tan(fov / 360 * pi) #w/2 / tan(fov/2 / 180*pi)

    x_axis = (
            cos((cam["ang"][0]-90)/180*pi),
            0,
            sin((cam["ang"][0]-90)/180*pi),
            )
    y_axis = (
            cos((cam["ang"][0])/180*pi)*cos((cam["ang"][1]+90)/180*pi),
            sin((cam["ang"][1]+90)/180*pi),
            sin((cam["ang"][0])/180*pi)*cos((cam["ang"][1]+90)/180*pi),
            )
    z_axis = (
            cos((cam["ang"][0])/180*pi)*cos((cam["ang"][1])/180*pi),
            sin((cam["ang"][1])/180*pi),
            sin((cam["ang"][0])/180*pi)*cos((cam["ang"][1])/180*pi),
            )
    
    # '''
    cube = Shape("cube")
    cube.vertices = {
        "A":[-5,0,5,["B","D","A'"],],
        "B":[5,0,5,["A","C","B'"],],
        "C":[5,0,15,["B","D","C'"],],
        "D":[-5,0,15,["A","C","D'"],],
        "A'":[-5,10,5,["B'","D'","A"]],
        "B'":[5,10,5,["A'","C'","B"]],
        "C'":[5,10,15,["B'","D'","C"]],
        "D'":[-5,10,15,["A'","C'","D"]],
    }
    vertices = Renderer.rendering_main(all_shapes)
    # '''
    draw(vertices)
    # break
    '''Not sure whether it should be while or if'''
    '''
    while not kbhit():
        if move_cam(getwch()) == "Quit":
            break
            '''
    print(cam)
    if move_cam(getwch()) == "Quit":
            break
    pass

if __name__ == "__main__":
    pass